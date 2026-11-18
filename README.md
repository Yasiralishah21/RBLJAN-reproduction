# RBLJAN Reproduction (IEEE TDSC 2024)

Reproduction of **"RBLJAN: Robust Byte-Label Joint Attention Network for Network Traffic Classification"** (Xiao et al., IEEE Transactions on Dependable and Secure Computing, 2024; DOI: 10.1109/TDSC.2024.3478838), using the authors' public code: https://github.com/ws0407/RBLJAN

By **Yasir Ali Shah** (BS Computer Science, DHA Suffa University, Karachi), as a reproduction task for Prof. Xi Xiao, Tsinghua Shenzhen International Graduate School. November 2026.

Environment: Kaggle notebooks, 2 x NVIDIA T4 (14.56 GiB each), 30 GiB RAM, PyTorch 2.11.0, Python 3.13. (The paper used a 2080Ti with 128 GB RAM; the released code targets PyTorch 1.10.)

## What this repository contains

The complete code exactly as it ran on Kaggle: the authors' code (from the repository linked above, included here with attribution) with my four patches applied. Every patch is marked inline with a `# PATCH` comment and documented in `patches/PATCHES.md`.

- `model.py`, `train.py`, `utils.py`, `eval.py`, `data_preprocessing.py` - the full codebase as run. (`utils.py` ships with the authors' released defaults; the Kaggle cells set the CLASSES list and BATCH_SIZE=128 per dataset at runtime.)
- `kaggle/` - the exact notebook cells used for the resumed X-WEB and X-APP training runs (restore, preprocessing, subset trimming, checkpoint resume, training).
- `patches/` - the four minimal changes to the released code: three one-line fixes (P1-P3) and a checkpoint-resume patch, each documented in `patches/PATCHES.md`.
- `results/` - the verified results tables (`results/results.md`).
- `original-authors-code/` - the authors' five code files exactly as released (unmodified, errors included), kept so every patch can be diffed line by line.

## Headline results (real-test, released single-split protocol)

| Dataset | Epochs | Real-test accuracy | Real-test macro F1 | Paper (10-fold CV, full data) |
|---|---|---|---|---|
| USTC-TFC (10 malware classes) | 13 | 0.9592 | 0.9534 | avg F1 0.9786 (Table VI) |
| X-WEB (20 websites) | 6 | 0.9671 | 0.9615 | avg F1 0.9990 |
| X-APP (29 applications) | 7 | 0.9768 | 0.9358 | avg F1 0.9993 (Table III) |
| USTC-TFC ablation (no GAN) | 4 | 0.9555 | 0.9514 | - |
| ISCX-VPN (12 classes) | - | not run (dataset access, see below) | | |

## Protocol deviations (all hardware-forced, fully disclosed)

1. The released code does not implement the paper's 10-fold cross-validation; `get_dataloader` makes one stratified 90/10 train/test split (random_state=41). I ran the released protocol as-is.
2. Batch size 256 -> 128 (batch 256 reproducibly exhausts the T4's memory in the discriminator backward pass).
3. USTC-TFC trained on a 50% stratified subset (the authors' own EXP_PERCENT=0.5, seed 41): the loader materialises all packets in RAM and the full set exceeds 30 GiB.
4. X-WEB trained on a 15% stratified per-class subset (566,883 of 3,779,281 packets, seed 41), trimmed on disk before loading, because the loader's memory peak is set by the full packet set regardless of EXP_PERCENT.
5. X-APP trained on a 23.0% stratified per-class subset (549,984 of 2,391,484 packets, seed 41), trimmed on disk, same reason.
6. ISCX-VPN was not run: I completed the CIC registration (18 November) and the download index opened, but the ~28 GB raw-pcap download could not be completed from the connections available to me; public mirrors provide flow-level CSVs, not the raw pcaps this code requires. It can be run as soon as the raw dataset is available.
7. X-WEB epochs 4-6 and X-APP epochs 5-7 are resumed continuations of their epoch-3 / epoch-4 checkpoints. The released code saves only the discriminator, so classifier weights were reloaded exactly while the generator and both optimisers were re-initialised at each resume point. Data, split and hyperparameters are unchanged. Consequence: generated-test figures after a resume are not comparable to those before it (a fresh generator produces easier samples for a trained classifier); real-test figures are unaffected.
8. In the regenerated X-APP subset, 38,422 packets (7.0%) were longer than the model's 1,500-byte input length and were truncated to 1,500 bytes. The released loader pads shorter packets but never truncates longer ones, which makes batching fail outright.

## How to run

1. Clone this repository - the code is complete and the patches are already applied (see `patches/PATCHES.md` for what differs from the authors' release).
2. Prepare data and train with the cells in `kaggle/` (X-APP versions shown; the X-WEB resume used the same pattern). The cells set the dataset's CLASSES list and BATCH_SIZE=128 in `utils.py` at runtime.

Full per-epoch numbers and per-class analysis are in `results/results.md` and in the accompanying report.
