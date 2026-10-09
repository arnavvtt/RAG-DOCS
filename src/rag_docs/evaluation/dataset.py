import json
from pathlib import Path
from typing import List, Dict


def load_eval_dataset(path: str = "data/eval/qa_pairs.json") -> List[Dict]:
    """Load the evaluation Q&A pairs from JSON."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Eval dataset not found: {path}")
    return json.loads(p.read_text(encoding="utf-8"))