# Kaggle cell 2 of the X-APP resume run: locate the uploaded epoch-4
# checkpoint, set the run constants, and train epochs 5-7 via the resume
# patch (see patches/resume_patch.py).

import os, glob, sys
DST = "/kaggle/working/RBLJAN"
os.chdir(DST)
sys.path.insert(0, DST)
os.makedirs(os.path.join(DST, "model", "X-APP"), exist_ok=True)

hits = [p for p in glob.glob("/kaggle/input/**/*.pt", recursive=True) if "214121_4" in p]
assert len(hits) == 1, hits
print("resume checkpoint:", hits[0])

import utils, model, train
for m in (utils, train):
    m.EXP_PERCENT = 1.0; m.TEST_PERCENT = 0.1; m.BATCH_SIZE = 128; m.EPOCHS = 8
print("CLASSES n =", len(utils.CLASSES), "| EPOCHS =", train.EPOCHS)
os.environ["RBLJAN_RESUME_CKPT"] = hits[0]
os.environ["RBLJAN_RESUME_EPOCH"] = "4"
train.train_RBLJAN(is_save=True)
print("=== X-APP RESUME DONE ===")
print(sorted(os.listdir(os.path.join(DST, "model", "X-APP"))))
