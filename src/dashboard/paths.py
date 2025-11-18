from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

DATA_RAW = ROOT / 'data' / 'raw'

DATA_PROCESSED = ROOT / 'data' / 'processed'

# ensure all directories we'll write to here
for d in (DATA_PROCESSED,):
    d.mkdir(parents=True, exist_ok=True)
