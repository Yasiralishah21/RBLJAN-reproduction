# Verified results

All figures are from the authors' released code path. The code's headline "D test accuracy / f1-score" is the mean of the real-test and generated-test figures; both components are listed separately wherever the headline is quoted. Test sets: USTC-TFC 40,576 packets; X-WEB 56,576; X-APP 54,912.

## USTC-TFC (10 malware classes, RBLJAN with GAN, 50% subset, batch 128)

| Epoch | Real-test accuracy | Real-test macro F1 |
|---|---|---|
| 1 | 0.9120 | 0.9067 |
| 2 | 0.9200 | 0.9111 |
| 3 | 0.9366 | 0.9338 |
| 4 | 0.9381 | 0.9346 |
| 5 | 0.9482 | 0.9434 |
| 13 (final) | 0.9592 | 0.9534 |

Training stopped at epoch 13 of the planned 25 (slow CUDA memory growth caused an out-of-memory error at epoch 14; epoch 13 was a new best and the curve had largely saturated). Epochs 6-12 per-epoch values were not captured during the run; the epoch-13 real-only figures were regenerated from the saved checkpoint on the identical split, a method first validated on the epoch-5 checkpoint, which reproduced its live values exactly. Epoch-13 headline as printed during training: D accuracy 0.9794 / F1 0.9765. Paper (Table VI, 10-fold CV, full data): average F1 0.9786; weakest class Miuref 0.8895. In my run Miuref is also weakest (F1 0.8034): a fixed set of ~570 Cridex packets is classified as Miuref in every epoch and in both model variants, pinning Cridex recall at 0.8874 and capping Miuref precision at 0.6726. Virut recovers from 0.4988 (first run, epoch 1) to 0.8983 at epoch 13.

## Ablation: RBLJAN without the GAN (USTC-TFC, same split)

| Epoch | Accuracy | Macro F1 |
|---|---|---|
| 1 | 0.9245 | 0.9234 |
| 2 | 0.9449 | 0.9417 |
| 3 | 0.9513 | 0.9483 |
| 4 | 0.9555 | 0.9514 |

Above the GAN variant's real-test F1 at every matched epoch (+1.7 points at epoch 4). Reported as observed, with caveats: early-epoch comparison only (the GAN run continued to epoch 13), the two model classes differ in the payload path by the authors' design, and single runs carry a few points of variance (two identical-configuration epoch-1 runs differed by ~3 F1 points). GAN-run observation: the generator's loss rose steadily (2.03 -> 8.89 by epoch 11) while the discriminator kept improving - in this configuration the adversarial term behaved more like a regulariser than a competing generator. Note: the no-GAN path's per-label table in the released code has precision and recall interchanged relative to its own confusion matrix; the values here are matrix-derived (F1 and accuracy are unaffected).

## X-WEB (20 websites, 15% subset, batch 128)

| Epoch | Real-test accuracy | Real-test macro F1 | Generated-test accuracy | Generated-test macro F1 |
|---|---|---|---|---|
| 1 | 0.9324 | 0.9192 | 0.9889 | 0.9882 |
| 2 | 0.9444 | 0.9312 | 0.9944 | 0.9938 |
| 3 | 0.9581 | 0.9507 | 0.9971 | 0.9969 |
| 4 (resumed) | 0.9618 | 0.9542 | 0.9980 | 0.9978 |
| 5 | 0.9620 | 0.9542 | 0.9983 | 0.9980 |
| 6 | 0.9671 | 0.9615 | 0.9989 | 0.9986 |

Headline at epoch 6: accuracy 0.9830 / F1 0.9801. Errors concentrate in a cluster of Chinese portals (qqmail F1 0.5709 -> 0.6623 -> 0.7864 -> ... -> 0.8473 across epochs 1-6; youku 0.8532 at epoch 6); nine classes reach F1 >= 0.99 at epoch 6. Paper: average F1 0.9990 (10-fold CV, full data).

## X-APP (29 applications, 23.0% subset, batch 128)

| Epoch | Real-test accuracy | Real-test macro F1 | Generated-test accuracy | Generated-test macro F1 |
|---|---|---|---|---|
| 1 | 0.9565 | 0.8780 | 0.9535 | 0.8744 |
| 2 | 0.9621 | 0.8955 | 0.9607 | 0.8928 |
| 3 | 0.9709 | 0.9170 | 0.9713 | 0.9165 |
| 4 | 0.9745 | 0.9213 | 0.9738 | 0.9199 |
| 5 (resumed) | 0.9737 | 0.9250 | 0.9932 | 0.9788 |
| 6 | 0.9740 | 0.9285 | 0.9971 | 0.9912 |
| 7 | 0.9768 | 0.9358 | 0.9987 | 0.9955 |

Headline at epoch 7: accuracy 0.9878 / F1 0.9656 (generated component inflated after the resume - see deviation 7). Real-test accuracy is nearly flat after epoch 4 while macro F1 gains +1.45 points over epochs 5-7, concentrated in small classes: ms-exchange F1 0.6491 -> 0.9487 (smallest class: 1,719 packets before subsetting, 39 in the test split), amazon 0.6700 -> 0.7485, weibo 0.7240 -> 0.7878. Weakest at epoch 7: baidu 0.6100 (recall 0.4649), itunes 0.6191. Twelve classes reach F1 >= 0.99 at epoch 7. The continuation run's subset was re-drawn with the same fraction and seed and reproduced the original test split exactly (identical per-class supports). 38,422 subset packets (7.0%) longer than 1,500 bytes were truncated to the model's input length. Paper (Table III, 10-fold CV, full data): average F1 0.9993, best on 22 of 29 applications; weakest Aimchat 0.9955, Gmail 0.9958.

## ISCX-VPN (12 classes)

Not run. CIC registration completed on 18 November 2026 and the download index opened, but the ~28 GB raw-pcap download could not be completed from the available connections (the portal did not accept downloads from them); public mirrors provide flow-level CSV features, not the raw pcaps the code requires. Ready to run as a follow-up as soon as the raw dataset is available.
