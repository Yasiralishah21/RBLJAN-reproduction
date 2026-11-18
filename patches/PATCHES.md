# Patches to the released code (all minimal and disclosed)

Base code: https://github.com/ws0407/RBLJAN (branch `master`)

## P1 - train.py: GPU-selection probe (environment fix, no effect on model or data)
The released code builds `gpus_idx` by scraping `nvidia-smi` output, which fails on Kaggle. Replace the scraped value with a fixed device list in both places it is computed:

```python
gpus_idx = list(range(DEVICE_COUNT))
```

## P2 - model.py: RBLJAN_GAN head_p 20 -> 25 (bug fix; required for the no-GAN ablation)
`RBLJAN_GAN.__init__` sets `self.head_p = 20`, but the payload length is 1450 and 1450 is not divisible by 20, so `ATT_LABEL` raises an error on any dataset - the no-GAN ablation path, which builds `RBLJAN_GAN`, cannot run as released. Set `self.head_p = 25`, the value in the otherwise identical `RBLJAN_Classifier` (1450 / 25 = 58).

## P3 - model.py: .long() casts in RBLJAN_GAN.forward (bug fix)
`RBLJAN_GAN.forward` passes float tensors to `nn.Embedding` (which requires Long indices) for both the header and payload slices. `RBLJAN_Classifier` casts the header slice with `.long()`; add the same cast to both slice lines in `RBLJAN_GAN.forward`. The byte values are exact integers in float32, so the cast is lossless.

Note: the two classes also differ in the payload path by the authors' own design (RBLJAN_Classifier: one-hot + linear; RBLJAN_GAN: embedding). Kept as released.

## Resume patch - train.py: continue training from a saved discriminator checkpoint
The released code saves only the discriminator (`save_model` pickles the whole DataParallel-wrapped model) and its `is_load` stubs point at a hardcoded 2022 checkpoint, so a long run cannot be resumed as released. The snippet in `resume_patch.py` is inserted into `train_RBLJAN` immediately after the line `cur_epoch, cur_loss = 0, 0`. It reads the checkpoint path and epoch from the environment variables `RBLJAN_RESUME_CKPT` / `RBLJAN_RESUME_EPOCH`, loads the saved model's weights into the freshly built discriminator, and sets `cur_epoch` so the loop continues at the next epoch.

Disclosure: the generator and both optimisers restart fresh at a resume point (the authors never save them), so a resumed run is a genuine continuation for the classifier but not bit-exact. This is deviation 7 in the report.
