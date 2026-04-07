"""
HRPulse — Performance Forecasting Model
PyTorch LSTM for predicting next-quarter KPI scores.

Input: 6 quarters of KPI history per employee
Output: predicted KPI for next quarter
Architecture: LSTM, hidden_size=64, 2 layers, trained 50 epochs
"""

import json
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, Dataset, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from app.core.config import settings

# ── Paths ────────────────────────────────────
MODEL_PATH = settings.ML_MODELS_DIR / "performance_lstm.pt"
SCALER_PATH = settings.ML_MODELS_DIR / "performance_scaler.pkl"
DATA_PATH = settings.DATA_DIR / "performance_history.csv"

# ── Hyperparameters ──────────────────────────
INPUT_SIZE = 1      # Single feature (KPI score)
HIDDEN_SIZE = 64
NUM_LAYERS = 2
SEQ_LENGTH = 6      # Use 6 quarters to predict the 7th
EPOCHS = 50
LEARNING_RATE = 0.001
BATCH_SIZE = 16


# ── LSTM Model Definition ───────────────────
if TORCH_AVAILABLE:
    class PerformanceLSTM(nn.Module):
        """LSTM model for KPI time series forecasting."""

        def __init__(self, input_size=INPUT_SIZE, hidden_size=HIDDEN_SIZE, num_layers=NUM_LAYERS):
            super(PerformanceLSTM, self).__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers

            self.lstm = nn.LSTM(
                input_size=input_size,
                hidden_size=hidden_size,
                num_layers=num_layers,
                batch_first=True,
                dropout=0.2 if num_layers > 1 else 0,
            )
            self.fc1 = nn.Linear(hidden_size, 32)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(32, 1)

        def forward(self, x):
            # x shape: (batch, seq_len, input_size)
            h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
            c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)

            out, _ = self.lstm(x, (h0, c0))
            out = out[:, -1, :]  # Take last time step
            out = self.fc1(out)
            out = self.relu(out)
            out = self.fc2(out)
            return out


def prepare_sequences(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare training sequences from performance history.
    Groups by employee_id, creates sequences of SEQ_LENGTH quarters,
    target is the next quarter's KPI score.
    """
    sequences = []
    targets = []

    for emp_id, group in df.groupby("employee_id"):
        # Sort by quarter
        group = group.sort_values("quarter")
        kpi_scores = group["kpi_score"].values

        if len(kpi_scores) < SEQ_LENGTH + 1:
            continue

        # Create sliding window sequences
        for i in range(len(kpi_scores) - SEQ_LENGTH):
            seq = kpi_scores[i : i + SEQ_LENGTH]
            target = kpi_scores[i + SEQ_LENGTH]
            sequences.append(seq)
            targets.append(target)

    if not sequences:
        return np.array([]), np.array([])

    return np.array(sequences), np.array(targets)


def train_model() -> dict:
    """Train the LSTM performance forecasting model."""
    print("  [Performance] Loading data...")

    if not DATA_PATH.exists():
        print("  [Performance] No data file found — skipping")
        return {"status": "error", "message": "No performance data"}

    df = pd.read_csv(DATA_PATH)
    print(f"  [Performance] Loaded {len(df)} records for {df['employee_id'].nunique()} employees")

    if not TORCH_AVAILABLE:
        print("  [Performance] PyTorch not available — saving mock model")
        mock_data = {"type": "mock", "mean_kpi": float(df["kpi_score"].mean())}
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(mock_data, f)
        return {"status": "mock", "message": "PyTorch not installed"}

    # Prepare sequences
    X, y = prepare_sequences(df)

    if len(X) == 0:
        print("  [Performance] Not enough data for sequences — saving mock")
        mock_data = {"type": "mock", "mean_kpi": float(df["kpi_score"].mean())}
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(mock_data, f)
        return {"status": "mock", "message": "Not enough sequential data"}

    print(f"  [Performance] Created {len(X)} training sequences")

    # Normalize
    kpi_mean = float(X.mean())
    kpi_std = float(X.std()) + 1e-8
    X_norm = (X - kpi_mean) / kpi_std
    y_norm = (y - kpi_mean) / kpi_std

    # Save scaler
    scaler = {"mean": kpi_mean, "std": kpi_std}
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    # Convert to tensors
    X_tensor = torch.FloatTensor(X_norm).unsqueeze(-1)  # (batch, seq_len, 1)
    y_tensor = torch.FloatTensor(y_norm).unsqueeze(-1)  # (batch, 1)

    # Train/test split
    split_idx = int(len(X_tensor) * 0.8)
    X_train, X_test = X_tensor[:split_idx], X_tensor[split_idx:]
    y_train, y_test = y_tensor[:split_idx], y_tensor[split_idx:]

    # DataLoader
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Model, loss, optimizer
    model = PerformanceLSTM()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Training loop
    print(f"  [Performance] Training for {EPOCHS} epochs...")
    model.train()
    for epoch in range(EPOCHS):
        epoch_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            avg_loss = epoch_loss / len(train_loader)
            print(f"    Epoch {epoch+1}/{EPOCHS} — Loss: {avg_loss:.6f}")

    # Evaluate on test set
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test)
        test_loss = criterion(test_pred, y_test).item()

        # Denormalize for MAE
        pred_denorm = test_pred.numpy() * kpi_std + kpi_mean
        actual_denorm = y_test.numpy() * kpi_std + kpi_mean
        mae = float(np.mean(np.abs(pred_denorm - actual_denorm)))

    print(f"  [Performance] Test MSE: {test_loss:.6f}")
    print(f"  [Performance] Test MAE: {mae:.2f} KPI points")

    # Save model
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"  [Performance] Model saved to {MODEL_PATH}")

    return {
        "status": "trained",
        "test_mse": test_loss,
        "test_mae": mae,
        "n_sequences": len(X),
    }


def load_model():
    """Load the trained LSTM model."""
    if not MODEL_PATH.exists():
        return None

    if not TORCH_AVAILABLE:
        return None

    # Check for mock model
    try:
        with open(MODEL_PATH, "rb") as f:
            data = pickle.load(f)
            if isinstance(data, dict) and data.get("type") == "mock":
                return data
    except Exception:
        pass

    model = PerformanceLSTM()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu", weights_only=True))
    model.eval()
    return model


def load_scaler() -> dict:
    """Load the normalization scaler."""
    if not SCALER_PATH.exists():
        return {"mean": 60.0, "std": 15.0}
    with open(SCALER_PATH, "rb") as f:
        return pickle.load(f)


def predict_next_quarter(kpi_history: List[float]) -> Dict:
    """
    Predict next quarter's KPI score given historical scores.
    Input: list of KPI scores (at least SEQ_LENGTH values)
    Returns: {predicted_kpi: float, trend: str, confidence: float}
    """
    if len(kpi_history) < SEQ_LENGTH:
        # Pad with mean if not enough history
        mean_kpi = sum(kpi_history) / max(len(kpi_history), 1) if kpi_history else 60.0
        while len(kpi_history) < SEQ_LENGTH:
            kpi_history.insert(0, mean_kpi)

    # Use the last SEQ_LENGTH values
    recent = kpi_history[-SEQ_LENGTH:]
    scaler = load_scaler()

    model = load_model()

    if model is None or (isinstance(model, dict) and model.get("type") == "mock"):
        # Mock prediction: simple moving average with slight trend
        avg = sum(recent) / len(recent)
        trend_val = recent[-1] - recent[0]
        predicted = round(min(100, max(0, avg + trend_val * 0.1)), 1)
        return {
            "predicted_kpi": predicted,
            "trend": _get_trend(recent),
            "confidence": 0.6,
            "history": recent,
        }

    # Normalize
    X = np.array(recent)
    X_norm = (X - scaler["mean"]) / scaler["std"]
    X_tensor = torch.FloatTensor(X_norm).unsqueeze(0).unsqueeze(-1)

    # Predict
    with torch.no_grad():
        pred_norm = model(X_tensor).item()
        predicted = round(pred_norm * scaler["std"] + scaler["mean"], 1)
        predicted = max(0, min(100, predicted))

    return {
        "predicted_kpi": predicted,
        "trend": _get_trend(recent),
        "confidence": 0.85,
        "history": recent,
    }


def predict_batch(employee_histories: Dict[str, List[float]]) -> Dict[str, Dict]:
    """
    Predict next quarter KPI for multiple employees.
    Input: {employee_id: [kpi_scores]}
    Returns: {employee_id: prediction_result}
    """
    results = {}
    for emp_id, history in employee_histories.items():
        results[emp_id] = predict_next_quarter(history)
    return results


def _get_trend(scores: List[float]) -> str:
    """Determine performance trend from recent scores."""
    if len(scores) < 2:
        return "stable"

    recent_avg = sum(scores[-3:]) / min(3, len(scores))
    older_avg = sum(scores[:3]) / min(3, len(scores))

    diff = recent_avg - older_avg
    if diff > 5:
        return "improving"
    elif diff < -5:
        return "declining"
    else:
        return "stable"
