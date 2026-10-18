# Submission instructions

First follow [dev/README.md](../README.md) to generate the 15 test outputs.
The default output folder is `dev/submissions/btc/`.

## Add the dev garments

The competition also requires an output for every dev garment ID.
To process one dev garment, pass its photos to the internal utility:

```bash
dev/btc-sartiq/backend/.venv/bin/python dev/btc-sartiq/scripts/validate_studio.py --views /path/to/photo1.jpg /path/to/photo2.jpg
```

Copy the generated image from
`dev/btc-sartiq/validation/<folder>_<name>_studio.png` to
`dev/submissions/btc/<garment_id>/front.png`. Use the exact ID from the manifest.
Repeat for every dev garment.

## Validate and package

Run from `neural-wave-2026/`, with the scorer dependencies installed
(see [scoring setup](how-to-score.md)):

```bash
dev/.score-venv/bin/python scripts/make_submission.py \
  --submissions dev/submissions \
  --team btc \
  --dataset /path/to/sartiq_neural_wave_2026 \
  --zip
```

Replace the dataset path. If you used a different output folder or team name,
update `--submissions` and `--team` too.

The validator must report **0 errors**. Also check that every dev and test garment
has an output: a missing garment scores 0.

## Hand in

Submit through the channel announced by the organisers:

1. The output archive, with one image per garment.
2. The pipeline source, dependencies, and run instructions.
3. The capture protocol, explaining how to photograph a garment from scratch.

See the [official submission rules](../../docs/SUBMISSION.md) for all requirements.
