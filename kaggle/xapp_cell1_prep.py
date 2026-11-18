# Kaggle cell 1 of the X-APP resume run (notebook "notebook2d2350b2f7", version 3).
# Inputs attached to the notebook: the "RBLJAN - Xiao Task2" notebook output
# (authors' code + raw X-APP pcaps) and the dataset "xapp-ckpt" (the epoch-4
# discriminator checkpoint 20261117-214121_4.pt, uploaded from my laptop).
# This cell: installs deps, restores the code + raw pcaps, switches CLASSES to
# X-APP, applies the resume patch, re-runs the authors' preprocessing, and
# re-draws the 23.0% subset (seed 41) with >1500-byte packets truncated.

import os, glob, shutil, sys, subprocess

try:
    import dpkt, scapy
    print("dpkt+scapy present")
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "dpkt", "scapy"])
    import dpkt, scapy
    print("dpkt+scapy installed")

SRC = "/kaggle/input/notebooks/yasirali21/rbljan-xiao-task2/RBLJAN"
DST = "/kaggle/working/RBLJAN"
assert os.path.exists(os.path.join(SRC, "utils.py")), "Input attach nahi hai"

if os.path.exists(DST):
    shutil.rmtree(DST)
os.makedirs(DST)
for f in glob.glob(os.path.join(SRC, "*.py")):
    shutil.copy2(f, DST)
os.makedirs(os.path.join(DST, "data"), exist_ok=True)
shutil.copytree(os.path.join(SRC, "data", "X-APP"), os.path.join(DST, "data", "X-APP"))
for cand in ("service-names-port-numbers.csv", "ports.pkl"):
    p = os.path.join(SRC, "data", cand)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(DST, "data", cand))
        print("ports file copied:", cand)
if not (os.path.exists(os.path.join(DST, "data", "service-names-port-numbers.csv"))
        or os.path.exists(os.path.join(DST, "data", "ports.pkl"))):
    import urllib.request
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/ws0407/RBLJAN/master/data/service-names-port-numbers.csv",
        os.path.join(DST, "data", "service-names-port-numbers.csv"))
    print("ports csv downloaded from repo")
shutil.rmtree(os.path.join(DST, "__pycache__"), ignore_errors=True)
os.chdir(DST)
sys.path.insert(0, DST)
print("restored | X-APP label folders:", len(os.listdir(os.path.join(DST, "data", "X-APP"))))

upath = os.path.join(DST, "utils.py")
XAPP = "CLASSES = ['vimeo', 'spotify', 'voipbuster', 'sinauc', 'cloudmusic', 'weibo', 'baidu', 'tudou', 'amazon', 'thunder', 'gmail', 'pplive', 'qq', 'taobao', 'yahoomail', 'itunes', 'twitter', 'jd', 'sohu', 'youtube', 'youku', 'netflix', 'aimchat', 'kugou', 'skype', 'facebook', 'google', 'mssql', 'ms-exchange']"
out, seen = [], False
for ln in open(upath).read().splitlines():
    s = ln.strip()
    if "CLASSES" in ln and "'vimeo'" in ln:
        if not seen:
            out.append(XAPP); seen = True
    elif s.startswith("CLASSES = ["):
        out.append("# " + ln)
    elif s.startswith("BATCH_SIZE"):
        out.append("BATCH_SIZE = 128")
    else:
        out.append(ln)
open(upath, "w").write("\n".join(out) + "\n")
active = [l for l in open(upath).read().splitlines() if l.startswith("CLASSES = [")]
assert len(active) == 1 and "'vimeo'" in active[0], active
print("utils ok: 1 active CLASSES (X-APP), BATCH_SIZE 128")

tpath = os.path.join(DST, "train.py")
src = open(tpath).read()
if "RBLJAN_RESUME_CKPT" not in src:
    a_def = src.index("def train_RBLJAN(")
    a = src.index("cur_epoch, cur_loss = 0, 0", a_def)
    le = src.index("\n", a) + 1
    patch = ("    import os as _os\n"
             "    _resume = _os.environ.get('RBLJAN_RESUME_CKPT')\n"
             "    if _resume:\n"
             "        _ckpt = torch.load(_resume, map_location='cpu', weights_only=False)\n"
             "        D_model.load_state_dict(_ckpt.state_dict())\n"
             "        cur_epoch = int(_os.environ.get('RBLJAN_RESUME_EPOCH', '0'))\n"
             "        print('RESUME: D weights loaded from {} ; next epoch {}'.format(_resume, cur_epoch + 1))\n")
    src = src[:le] + patch + src[le:]
    open(tpath, "w").write(src)
print("patch ok:", "RBLJAN_RESUME_CKPT" in open(tpath).read())

# --- preprocessing: raw pcaps -> full pkls (authors' own code) ---
from data_preprocessing import PCAP_DPKT
proc = PCAP_DPKT([os.path.join(DST, "data", "X-APP")],
                 os.path.join(DST, "data", "X-APP_PKL_FULL") + "/")
proc.get_idx_saved()

# --- trim to the same ~550k subset (seed 41); truncate packets > 1500 ---
import pickle, random
FULL = os.path.join(DST, "data", "X-APP_PKL_FULL")
TRIM = os.path.join(DST, "data", "X-APP_PKL")
os.makedirs(TRIM, exist_ok=True)
CLASSES29 = ['vimeo', 'spotify', 'voipbuster', 'sinauc', 'cloudmusic', 'weibo', 'baidu', 'tudou', 'amazon', 'thunder', 'gmail', 'pplive', 'qq', 'taobao', 'yahoomail', 'itunes', 'twitter', 'jd', 'sohu', 'youtube', 'youku', 'netflix', 'aimchat', 'kugou', 'skype', 'facebook', 'google', 'mssql', 'ms-exchange']
frac = 550000 / 2391484
random.seed(41)
tf = tt = tlong = 0
for c in CLASSES29:
    pk = pickle.load(open(os.path.join(FULL, c + ".pkl"), "rb"))
    tf += len(pk)
    sub = random.sample(pk, int(frac * len(pk)))
    tlong += sum(1 for p in sub if len(p) > 1500)
    sub = [p[:1500] for p in sub]
    tt += len(sub)
    pickle.dump(sub, open(os.path.join(TRIM, c + ".pkl"), "wb"))
print("PREP DONE | full:", tf, "| trimmed:", tt, "| truncated over 1500:", tlong)
