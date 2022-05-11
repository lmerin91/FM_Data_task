"""Misc utils."""
import logging
from pathlib import Path
from typing import List

from rich.logging import RichHandler


def setup_logger(log_dir: str):
    """Create log directory and logger."""
    Path(log_dir).mkdir(exist_ok=True, parents=True)
    log_path = str(Path(log_dir) / "log.txt")
    handlers = [logging.FileHandler(log_path), RichHandler(rich_tracebacks=True)]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(module)s] [%(levelname)s] %(message)s",
        handlers=handlers,
    )


def compute_metrics(preds: List, golds: List):
    """Compute metrics."""
    mets = {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "crc": 0, "total": 0}
    for pred, label in zip(preds, golds):
        label = label.strip().lower()
        pred = pred.strip().lower()
        mets["total"] += 1
        # Measure startswith accuracy for generation
        if pred.startswith(label):
            mets["crc"] += 1
        if label == "yes":
            if pred.startswith(label):
                mets["tp"] += 1
            else:
                mets["fn"] += 1
        elif label == "no":
            if pred.startswith(label):
                mets["tn"] += 1
            else:
                mets["fp"] += 1

    prec = mets["tp"] / max(1, (mets["tp"] + mets["fp"]))
    rec = mets["tp"] / max(1, (mets["tp"] + mets["fn"]))
    acc = mets["crc"] / mets["total"]
    f1 = 2 * prec * rec / max(1, (prec + rec))
    return prec, rec, acc, f1
