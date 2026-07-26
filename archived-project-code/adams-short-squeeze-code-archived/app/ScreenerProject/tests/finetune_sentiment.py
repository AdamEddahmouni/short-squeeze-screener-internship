import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

from core.sentiment import FINBERT_MODEL, FINETUNED_MODEL_DIR

LABELED_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "labeled_data.csv")

# Must match FinBERT's own id2label ({0: positive, 1: negative, 2: neutral}) so fine-tuning
# continues training the existing classification head instead of a randomly reinitialized one.
MOVEMENT_TO_ID = {1: 0, -1: 1, 0: 2}

# More epochs than the original 4 - safe to extend since best-validation-accuracy checkpointing
# already guards against overfitting picking the wrong epoch; more epochs just means more chances
# to find a better peak, and CPU training here is fast enough (~seconds/epoch on ~1000 headlines)
# that the extra compute cost is negligible.
EPOCHS = 8
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
WARMUP_RATIO = 0.1


class HeadlineDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def _make_loader(tokenizer, headlines, labels, batch_size, shuffle):
    encodings = tokenizer(list(headlines), truncation=True, padding=True, return_tensors="pt")
    dataset = HeadlineDataset(encodings, list(labels))
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def _evaluate(model, loader, device, loss_fn):
    model.eval()
    correct, total, total_loss = 0, 0, 0.0
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            labels = batch.pop("labels")
            outputs = model(**batch)
            loss = loss_fn(outputs.logits, labels)
            total_loss += loss.item() * len(labels)
            predictions = outputs.logits.argmax(dim=-1)
            correct += (predictions == labels).sum().item()
            total += len(labels)
    return total_loss / total, correct / total


def main():
    # Same split as tests/test_sentiment_finbert.py (test_size=0.3, random_state=42) so the
    # 247-headline held-out test set is never seen during fine-tuning - it stays a fair,
    # uncontaminated benchmark comparable across the old, zero-shot, and fine-tuned rows already
    # logged in data/sentiment_eval_log.csv.
    df = pd.read_csv(LABELED_DATA_PATH, encoding="utf-8")
    train_df, test_df = train_test_split(df, test_size=0.3, random_state=42)

    # Held out from *within* the training portion only, purely to monitor overfitting during
    # training - the real held-out test set (test_df) is evaluated separately by
    # test_sentiment_finbert.py after this script finishes.
    fit_df, val_df = train_test_split(train_df, test_size=0.1, random_state=42)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Fine-tuning on {len(fit_df)} headlines, validating on {len(val_df)}, "
          f"holding out {len(test_df)} untouched for final comparison.\n")

    tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(FINBERT_MODEL).to(device)

    train_loader = _make_loader(
        tokenizer, fit_df["headline"], fit_df["price_movement"].map(MOVEMENT_TO_ID),
        BATCH_SIZE, shuffle=True
    )
    val_loader = _make_loader(
        tokenizer, val_df["headline"], val_df["price_movement"].map(MOVEMENT_TO_ID),
        BATCH_SIZE, shuffle=False
    )

    # Class-weighted loss: labeled_data.csv is only roughly balanced (positive is still the
    # plurality class even after the §8e/§8f expansion), and inverse-frequency weighting keeps
    # the model from just leaning on the majority class to minimize loss - directly targets the
    # kind of per-class recall gap (e.g. old model's 0.00 neutral recall) this whole upgrade
    # started by fixing.
    fit_label_ids = fit_df["price_movement"].map(MOVEMENT_TO_ID).to_numpy()
    class_weights = compute_class_weight(
        class_weight="balanced", classes=np.array([0, 1, 2]), y=fit_label_ids
    )
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor(class_weights, dtype=torch.float32, device=device))
    print(f"Class weights (positive/negative/neutral): {np.round(class_weights, 3)}\n")

    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(total_steps * WARMUP_RATIO), num_training_steps=total_steps
    )

    best_val_accuracy = -1
    for epoch in range(1, EPOCHS + 1):
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            labels = batch.pop("labels")
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = loss_fn(outputs.logits, labels)
            loss.backward()
            optimizer.step()
            scheduler.step()
            train_loss += loss.item() * len(labels)
        train_loss /= len(fit_df)

        val_loss, val_accuracy = _evaluate(model, val_loader, device, loss_fn)
        print(f"Epoch {epoch}/{EPOCHS} - train_loss={train_loss:.4f} "
              f"val_loss={val_loss:.4f} val_accuracy={val_accuracy:.4f}")

        # Keep only the checkpoint that generalized best to the validation split, not
        # necessarily the last epoch - guards against overfitting on only ~520 training examples.
        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            os.makedirs(FINETUNED_MODEL_DIR, exist_ok=True)
            model.save_pretrained(FINETUNED_MODEL_DIR)
            tokenizer.save_pretrained(FINETUNED_MODEL_DIR)
            print(f"  -> new best (val_accuracy={val_accuracy:.4f}), saved to {FINETUNED_MODEL_DIR}")

    print(f"\nDone. Best val_accuracy={best_val_accuracy:.4f}. "
          f"Run tests/test_sentiment_finbert.py next to score the held-out test set and log it.")


if __name__ == "__main__":
    main()
