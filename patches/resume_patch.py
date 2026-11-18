# Resume patch for train.py (RBLJAN, authors' code at github.com/ws0407/RBLJAN).
# Insert this block inside train_RBLJAN, immediately AFTER the line:
#     cur_epoch, cur_loss = 0, 0
# (that anchor appears in all three train functions - target the one inside
# train_RBLJAN). It loads a saved discriminator checkpoint (the released
# save_model pickles the whole DataParallel-wrapped model, so state_dict
# keys match) and continues the epoch loop from RBLJAN_RESUME_EPOCH.
# The generator and both optimisers restart fresh - the authors never save
# them - so a resumed run is a genuine continuation for the classifier but
# not bit-exact. Disclosed as deviation 7 in the report.

    import os as _os
    _resume = _os.environ.get('RBLJAN_RESUME_CKPT')
    if _resume:
        _ckpt = torch.load(_resume, map_location='cpu', weights_only=False)
        D_model.load_state_dict(_ckpt.state_dict())
        cur_epoch = int(_os.environ.get('RBLJAN_RESUME_EPOCH', '0'))
        print('RESUME: D weights loaded from {} ; next epoch {}'.format(_resume, cur_epoch + 1))
