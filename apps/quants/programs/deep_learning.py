"""
Deep Learning Models for Financial Price Prediction

Implements LSTM, GRU, Transformer-based attention mechanisms, CNN,
and multi-task learning architectures for time series forecasting.

Author: Financial Quants
Date: 2025
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from typing import Tuple, List, Optional
from torch.utils.data import DataLoader, TensorDataset


# ============================================================================
# 1. LSTM-based Price Prediction Model
# ============================================================================

class LSTMPricePredictor(nn.Module):
    """
    LSTM-based price prediction model.

    Captures long-term temporal dependencies in price sequences using
    LSTM cells with optional bidirectional processing.

    Args:
        input_size: Number of input features (e.g., OHLCV)
        hidden_size: Number of LSTM hidden units
        num_layers: Number of stacked LSTM layers
        output_size: Number of outputs (1 for price prediction)
        dropout: Dropout rate for regularization
        bidirectional: Whether to use bidirectional LSTM
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2,
        bidirectional: bool = False
    ):
        super(LSTMPricePredictor, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.bidirectional = bidirectional

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True
        )

        lstm_output_size = hidden_size * (2 if bidirectional else 1)

        # Dense layers for regression
        self.dense1 = nn.Linear(lstm_output_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.dense2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for LSTM price predictor.

        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)

        Returns:
            Price predictions of shape (batch_size, output_size)
        """
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)

        # Use last output from LSTM
        last_output = lstm_out[:, -1, :]

        # Dense layers
        x = self.dense1(last_output)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.dense2(x)

        return x


# ============================================================================
# 2. GRU Architecture for Sequential Price Modeling
# ============================================================================

class GRUPricePredictor(nn.Module):
    """
    GRU-based price prediction model.

    Gated Recurrent Units offer faster computation than LSTM while maintaining
    strong temporal dependency modeling capabilities. Ideal for price sequences.

    Args:
        input_size: Number of input features
        hidden_size: Number of GRU hidden units
        num_layers: Number of stacked GRU layers
        output_size: Number of outputs
        dropout: Dropout rate
        bidirectional: Whether to use bidirectional GRU
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2,
        bidirectional: bool = False
    ):
        super(GRUPricePredictor, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size

        # GRU layers
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True
        )

        gru_output_size = hidden_size * (2 if bidirectional else 1)

        # Dense layers
        self.dense1 = nn.Linear(gru_output_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.dense2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for GRU price predictor.

        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)

        Returns:
            Price predictions of shape (batch_size, output_size)
        """
        # GRU forward pass
        gru_out, hidden = self.gru(x)

        # Use last output
        last_output = gru_out[:, -1, :]

        # Dense layers
        x = self.dense1(last_output)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.dense2(x)

        return x


# ============================================================================
# 3. Temporal Attention Mechanism
# ============================================================================

class TemporalAttention(nn.Module):
    """
    Temporal Attention Mechanism for time series.

    Learns to dynamically weight past observations based on their relevance
    to predicting future values. Uses multi-head self-attention to capture
    different aspects of temporal relationships.

    Args:
        hidden_size: Dimension of attention vectors
        num_heads: Number of attention heads
        dropout: Dropout rate
    """

    def __init__(
        self,
        hidden_size: int = 64,
        num_heads: int = 4,
        dropout: float = 0.1
    ):
        super(TemporalAttention, self).__init__()

        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads

        assert hidden_size % num_heads == 0, \
            f"hidden_size ({hidden_size}) must be divisible by num_heads ({num_heads})"

        # Query, Key, Value projections
        self.query = nn.Linear(hidden_size, hidden_size)
        self.key = nn.Linear(hidden_size, hidden_size)
        self.value = nn.Linear(hidden_size, hidden_size)

        # Output projection
        self.fc_out = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass for temporal attention.

        Args:
            query: Query tensor (batch, seq_len, hidden_size)
            key: Key tensor (batch, seq_len, hidden_size)
            value: Value tensor (batch, seq_len, hidden_size)
            mask: Optional attention mask

        Returns:
            Tuple of (attention_output, attention_weights)
        """
        batch_size = query.shape[0]

        # Linear transformations
        Q = self.query(query)
        K = self.key(key)
        V = self.value(value)

        # Reshape for multi-head attention
        Q = Q.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)

        # Compute attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.head_dim)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        # Apply softmax
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention to values
        context = torch.matmul(attention_weights, V)

        # Reshape back
        context = context.transpose(1, 2).contiguous()
        context = context.view(batch_size, -1, self.hidden_size)

        # Output projection
        output = self.fc_out(context)

        return output, attention_weights


class AttentionLSTM(nn.Module):
    """
    LSTM with Temporal Attention Mechanism.

    Combines LSTM for sequence processing with attention mechanism
    to focus on most relevant time steps.

    Args:
        input_size: Number of input features
        hidden_size: LSTM hidden size
        output_size: Number of outputs
        num_heads: Number of attention heads
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        output_size: int = 1,
        num_heads: int = 4
    ):
        super(AttentionLSTM, self).__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=2,
            batch_first=True,
            dropout=0.2
        )

        self.attention = TemporalAttention(hidden_size=hidden_size, num_heads=num_heads)

        self.fc1 = nn.Linear(hidden_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with attention.

        Args:
            x: Input tensor (batch, seq_len, input_size)

        Returns:
            Price predictions (batch, output_size)
        """
        # LSTM encoding
        lstm_out, _ = self.lstm(x)

        # Apply attention
        attention_out, _ = self.attention(lstm_out, lstm_out, lstm_out)

        # Use attention-weighted output
        last_output = attention_out[:, -1, :]

        # Dense layers
        x = self.fc1(last_output)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)

        return x


# ============================================================================
# 4. CNN for Pattern Recognition in Price Data
# ============================================================================

class CNNPricePredictor(nn.Module):
    """
    Convolutional Neural Network for price pattern recognition.

    Uses 1D convolutions to identify local patterns in price sequences,
    effective for capturing short-term market microstructure patterns.

    Args:
        input_size: Number of input features
        num_filters: Number of convolutional filters
        kernel_sizes: List of kernel sizes for parallel convolutions
        output_size: Number of outputs
        dropout: Dropout rate
    """

    def __init__(
        self,
        input_size: int,
        num_filters: int = 32,
        kernel_sizes: List[int] = [3, 5, 7],
        output_size: int = 1,
        dropout: float = 0.2
    ):
        super(CNNPricePredictor, self).__init__()

        self.input_size = input_size
        self.num_filters = num_filters
        self.kernel_sizes = kernel_sizes

        # Parallel convolutional layers with different kernel sizes
        self.convs = nn.ModuleList([
            nn.Conv1d(
                in_channels=input_size,
                out_channels=num_filters,
                kernel_size=k,
                padding=k // 2
            )
            for k in kernel_sizes
        ])

        # Batch normalization
        self.bn_layers = nn.ModuleList([
            nn.BatchNorm1d(num_filters)
            for _ in kernel_sizes
        ])

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

        # Global average pooling output: num_filters * len(kernel_sizes)
        cnn_output_size = num_filters * len(kernel_sizes)

        # Dense layers
        self.fc1 = nn.Linear(cnn_output_size, 64)
        self.fc2 = nn.Linear(64, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for CNN price predictor.

        Args:
            x: Input tensor (batch, seq_len, input_size)

        Returns:
            Price predictions (batch, output_size)
        """
        # Transpose for Conv1d: (batch, seq_len, features) -> (batch, features, seq_len)
        x = x.transpose(1, 2)

        # Parallel convolutions
        conv_outputs = []
        for conv, bn in zip(self.convs, self.bn_layers):
            out = conv(x)
            out = bn(out)
            out = self.relu(out)
            out = F.adaptive_avg_pool1d(out, 1)
            conv_outputs.append(out)

        # Concatenate outputs
        x = torch.cat(conv_outputs, dim=1)
        x = x.view(x.size(0), -1)

        # Dense layers
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)

        return x


# ============================================================================
# 5. Multi-Task Learning for Simultaneous Price Prediction
# ============================================================================

class MultiTaskPriceLearner(nn.Module):
    """
    Multi-Task Learning model for simultaneous price prediction across assets.

    Shares a common feature extractor across multiple price prediction tasks,
    allowing the model to learn shared temporal patterns while maintaining
    task-specific prediction heads.

    Args:
        input_size: Number of input features
        hidden_size: Hidden layer size
        num_tasks: Number of prediction tasks (assets)
        num_layers: Number of LSTM layers
        output_size: Output size per task
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_tasks: int = 3,
        num_layers: int = 2,
        output_size: int = 1
    ):
        super(MultiTaskPriceLearner, self).__init__()

        self.num_tasks = num_tasks
        self.hidden_size = hidden_size

        # Shared feature extractor (LSTM)
        self.shared_lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        # Shared attention mechanism
        self.shared_attention = TemporalAttention(hidden_size=hidden_size, num_heads=4)

        # Task-specific heads
        self.task_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_size, hidden_size // 2),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_size // 2, output_size)
            )
            for _ in range(num_tasks)
        ])

    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        """
        Forward pass for multi-task learning.

        Args:
            x: Input tensor (batch, seq_len, input_size)

        Returns:
            List of predictions for each task
        """
        # Shared feature extraction
        lstm_out, _ = self.shared_lstm(x)

        # Shared attention
        attention_out, _ = self.shared_attention(lstm_out, lstm_out, lstm_out)

        # Take last output
        shared_features = attention_out[:, -1, :]

        # Task-specific predictions
        task_outputs = [head(shared_features) for head in self.task_heads]

        return task_outputs


# ============================================================================
# Training Utilities
# ============================================================================

class DeepLearningTrainer:
    """
    Training utility for deep learning price prediction models.

    Handles model training, validation, and evaluation.
    """

    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-5,
        device: str = 'cpu'
    ):
        self.model = model.to(device)
        self.device = device
        self.optimizer = optim.Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        self.criterion = nn.MSELoss()
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=10,
            verbose=True
        )

    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0

        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(self.device)
            batch_y = batch_y.to(self.device)

            # Forward pass
            predictions = self.model(batch_x)
            loss = self.criterion(predictions, batch_y)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(train_loader)

    def validate(self, val_loader: DataLoader) -> float:
        """Validate model."""
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)

                predictions = self.model(batch_x)
                loss = self.criterion(predictions, batch_y)
                total_loss += loss.item()

        return total_loss / len(val_loader)

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 100,
        early_stopping_patience: int = 20
    ) -> dict:
        """
        Fit model with early stopping.

        Returns:
            Dictionary with training history
        """
        history = {'train_loss': [], 'val_loss': []}
        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)

            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)

            self.scheduler.step(val_loss)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - "
                      f"Train Loss: {train_loss:.6f}, "
                      f"Val Loss: {val_loss:.6f}")

            if patience_counter >= early_stopping_patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

        return history

    def predict(self, data: torch.Tensor) -> np.ndarray:
        """Generate predictions."""
        self.model.eval()
        with torch.no_grad():
            data = data.to(self.device)
            predictions = self.model(data)
        return predictions.cpu().numpy()


# ============================================================================
# Data Preparation Utilities
# ============================================================================

def create_sequences(
    data: np.ndarray,
    sequence_length: int = 30,
    forecast_horizon: int = 1
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create sequences for time series prediction.

    Args:
        data: Input data array (num_samples, num_features)
        sequence_length: Length of input sequences
        forecast_horizon: Number of steps ahead to predict

    Returns:
        Tuple of (X, y) arrays
    """
    X, y = [], []

    for i in range(len(data) - sequence_length - forecast_horizon + 1):
        X.append(data[i:i + sequence_length])
        y.append(data[i + sequence_length + forecast_horizon - 1])

    return np.array(X), np.array(y)


def normalize_data(
    data: np.ndarray,
    mean: Optional[np.ndarray] = None,
    std: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalize data using z-score normalization.

    Args:
        data: Input data
        mean: Pre-computed mean (for test data)
        std: Pre-computed std (for test data)

    Returns:
        Tuple of (normalized_data, mean, std)
    """
    if mean is None:
        mean = np.mean(data, axis=0)
    if std is None:
        std = np.std(data, axis=0)
        std[std == 0] = 1  # Avoid division by zero

    normalized = (data - mean) / std
    return normalized, mean, std


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("Deep Learning Price Prediction Models")
    print("=" * 50)

    # Example: Create synthetic price data
    np.random.seed(42)
    num_samples = 1000
    num_features = 5  # OHLCV

    # Simulate price sequences with trend
    trend = np.linspace(100, 150, num_samples)
    noise = np.random.normal(0, 2, (num_samples, num_features))
    data = trend[:, np.newaxis] + noise

    # Normalize
    data_normalized, mean, std = normalize_data(data)

    # Create sequences
    X, y = create_sequences(data_normalized, sequence_length=30)

    # Split into train/val
    split_idx = int(0.8 * len(X))
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]

    # Convert to tensors
    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.FloatTensor(y_train)
    X_val_t = torch.FloatTensor(X_val)
    y_val_t = torch.FloatTensor(y_val)

    # Create data loaders
    train_dataset = TensorDataset(X_train_t, y_train_t)
    val_dataset = TensorDataset(X_val_t, y_val_t)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)

    # Example: Train LSTM model
    print("\nTraining LSTM Model...")
    lstm_model = LSTMPricePredictor(input_size=5, hidden_size=64)
    trainer = DeepLearningTrainer(lstm_model, learning_rate=0.001)

    history = trainer.fit(train_loader, val_loader, epochs=50, early_stopping_patience=10)
    print(f"Final validation loss: {history['val_loss'][-1]:.6f}")

    # Example: Train Attention LSTM
    print("\nTraining Attention LSTM Model...")
    attn_lstm = AttentionLSTM(input_size=5, hidden_size=64)
    trainer = DeepLearningTrainer(attn_lstm, learning_rate=0.001)

    history = trainer.fit(train_loader, val_loader, epochs=50, early_stopping_patience=10)
    print(f"Final validation loss: {history['val_loss'][-1]:.6f}")

    # Example: Train CNN model
    print("\nTraining CNN Model...")
    cnn_model = CNNPricePredictor(input_size=5, num_filters=32)
    trainer = DeepLearningTrainer(cnn_model, learning_rate=0.001)

    history = trainer.fit(train_loader, val_loader, epochs=50, early_stopping_patience=10)
    print(f"Final validation loss: {history['val_loss'][-1]:.6f}")

    print("\nAll models trained successfully!")
