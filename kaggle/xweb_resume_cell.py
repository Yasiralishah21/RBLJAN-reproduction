# Kaggle cell of the X-WEB resume run (notebook "notebook2d2350b2f7", version 1).
# Restores the code + the on-disk 15% X-WEB subset + the epoch-3 checkpoint from
# the "RBLJAN - Xiao Task2" notebook output, switches CLASSES to X-WEB (with a
# duplicate-line guard), applies the resume patch, and trains epochs 4-6.
# A second small cell afterwards only listed the saved checkpoints.

import os, glob, shutil, sys
SRC = "/kaggle/input/notebooks/yasirali21/rbljan-xiao-task2/RBLJAN"
DST = "/kaggle/working/RBLJAN"
assert os.path.exists(os.path.join(SRC, "utils.py")), "Input attach nahi hai"

if os.path.exists(DST):
    shutil.rmtree(DST)
os.makedirs(DST)
for f in glob.glob(os.path.join(SRC, "*.py")):
    shutil.copy2(f, DST)

# restore data, skipping ONLY the X-WEB_PKL_FULL folder under data (name-based
# skips collide across parents, so the walk is scoped by parent folder)
def ignore_scoped(dirpath, names):
    if os.path.basename(dirpath) == "data" and "X-WEB_PKL_FULL" in names:
        print("skip:", os.path.join(dirpath, "X-WEB_PKL_FULL"))
        return ["X-WEB_PKL_FULL"]
    return []
shutil.copytree(os.path.join(SRC, "data"), os.path.join(DST, "data"), ignore=ignore_scoped)

# restore the model folder (epoch 1-3 checkpoints incl. 20261117-173113_3.pt)
shutil.copytree(os.path.join(SRC, "model"), os.path.join(DST, "model"), dirs_exist_ok=True)
shutil.rmtree(os.path.join(DST, "__pycache__"), ignore_errors=True)
os.chdir(DST)
sys.path.insert(0, DST)
print("restored | model/X-WEB:", sorted(os.listdir(os.path.join(DST, "model", "X-WEB"))))

# --- utils.py: exactly one active CLASSES line (X-WEB), BATCH_SIZE 128 ---
upath = os.path.join(DST, "utils.py")
XWEB = "CLASSES = ['amazon', 'baidu', 'bing', 'douban', 'facebook', 'google', 'imdb', 'instagram', 'iqiyi', 'jd', 'neteasemusic', 'qqmail', 'reddit', 'taobao', 'ted', 'tieba', 'twitter', 'weibo', 'youku', 'youtube']"
out, seen = [], False
for ln in open(upath).read().splitlines():
    s = ln.strip()
    if "CLASSES" in ln and "'amazon'" in ln and "'iqiyi'" in ln:
        if not seen:
            out.append(XWEB); seen = True
        # later duplicates of the X-WEB line are dropped
    elif s.startswith("CLASSES = ["):
        out.append("# " + ln)
    elif s.startswith("BATCH_SIZE"):
        out.append("BATCH_SIZE = 128")
    else:
        out.append(ln)
open(upath, "w").write("\n".join(out) + "\n")
active = [l for l in open(upath).read().splitlines() if l.startswith("CLASSES = [")]
assert len(active) == 1 and "'iqiyi'" in active[0], active
print("utils ok: 1 active CLASSES (X-WEB), BATCH_SIZE 128")

# --- train.py: resume patch inside train_RBLJAN only ---
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

# --- train epochs 4-6, resuming the epoch-3 checkpoint ---
import utils, model, train
for m in (utils, train):
    m.EXP_PERCENT = 1.0; m.TEST_PERCENT = 0.1; m.BATCH_SIZE = 128; m.EPOCHS = 7
print("CLASSES n =", len(utils.CLASSES), "| EPOCHS =", train.EPOCHS)
os.environ["RBLJAN_RESUME_CKPT"] = os.path.join(DST, "model", "X-WEB", "20261117-173113_3.pt")
os.environ["RBLJAN_RESUME_EPOCH"] = "3"
train.train_RBLJAN(is_save=True)
print("=== X-WEB RESUME DONE ===")
