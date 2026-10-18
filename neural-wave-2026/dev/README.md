# Run the pipeline on the 15 test garments

Run all commands below from `neural-wave-2026/`. You need Python 3.10+,
the test dataset, and a fal.ai API key with available credits.

## 1. Install dependencies

```bash
python3 -m venv dev/btc-sartiq/backend/.venv
dev/btc-sartiq/backend/.venv/bin/python -m pip install -r dev/btc-sartiq/backend/requirements.txt
cp -n dev/btc-sartiq/backend/.env.example dev/btc-sartiq/backend/.env
```

Open `dev/btc-sartiq/backend/.env` and set your key:

```dotenv
FAL_API_KEY=your_key_here
```

## 2. Set the dataset path

Replace the path below with your dataset folder. It must contain
`test/inputs.jsonl` and the photos listed in that file.

```bash
DATASET="/path/to/sartiq_neural_wave_2026"
```

## 3. Check the inputs, then generate

```bash
# Check all 15 garments without spending API credits.
python3 dev/run_pipeline.py --dataset "$DATASET" --dry-run

# Generate the images. This makes paid API calls.
python3 dev/run_pipeline.py --dataset "$DATASET"
```

The script uses the backend environment automatically and processes `g01`–`g15`,
using all listed photos for each garment (1–5 photos, main view first).

## 4. Find your results

```text
dev/submissions/btc/g01/front.png
...
dev/submissions/btc/g15/front.png
```

Check that the terminal reports **Completed 15/15 garments**, then inspect every
image, including any marked `review_required`. If a garment fails, the script
continues with the others and lists the missing IDs at the end.

**Already have results?** Existing images are never overwritten. Choose a new
output folder for another run:

```bash
python3 dev/run_pipeline.py --dataset "$DATASET" --out dev/submissions-new
```

Use `--team your-team` to change the default team name `btc`.

For validation and hand-in, see [Submission instructions](doc/how-to-submit.md).
The full submission also requires all dev garment outputs, the pipeline source,
and a capture protocol.
