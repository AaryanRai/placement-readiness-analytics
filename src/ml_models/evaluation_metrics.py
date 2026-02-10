"""
Comprehensive evaluation metrics calculation for ML models
"""
import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score, confusion_matrix,
    mean_squared_error, mean_absolute_error, r2_score
)

def calculate_classification_metrics(y_true, y_pred, y_proba, classes):
    """
    Calculate comprehensive classification metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_proba: Prediction probabilities (n_samples, n_classes)
        classes: Class names
    
    Returns:
        Dictionary with all classification metrics
    """
    # Basic metrics
    accuracy = float(np.mean(y_true == y_pred))
    
    # Per-class metrics
    precision_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
    recall_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
    f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
    
    # Macro averages (unweighted mean across classes)
    precision_macro = float(precision_score(y_true, y_pred, average='macro', zero_division=0))
    recall_macro = float(recall_score(y_true, y_pred, average='macro', zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average='macro', zero_division=0))
    
    # Micro averages (calculated globally)
    precision_micro = float(precision_score(y_true, y_pred, average='micro', zero_division=0))
    recall_micro = float(recall_score(y_true, y_pred, average='micro', zero_division=0))
    f1_micro = float(f1_score(y_true, y_pred, average='micro', zero_division=0))
    
    # Weighted averages (weighted by class support)
    precision_weighted = float(precision_score(y_true, y_pred, average='weighted', zero_division=0))
    recall_weighted = float(recall_score(y_true, y_pred, average='weighted', zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    confusion_matrix_list = cm.tolist()
    
    # Per-class metrics as dictionary
    per_class_metrics = {}
    for i, class_name in enumerate(classes):
        per_class_metrics[class_name] = {
            'precision': float(precision_per_class[i]),
            'recall': float(recall_per_class[i]),
            'f1_score': float(f1_per_class[i]),
            'support': int(np.sum(y_true == i))
        }
    
    return {
        'accuracy': accuracy,
        'precision_macro': precision_macro,
        'recall_macro': recall_macro,
        'f1_macro': f1_macro,
        'precision_micro': precision_micro,
        'recall_micro': recall_micro,
        'f1_micro': f1_micro,
        'precision_weighted': precision_weighted,
        'recall_weighted': recall_weighted,
        'f1_weighted': f1_weighted,
        'per_class': per_class_metrics,
        'confusion_matrix': confusion_matrix_list,
        'classes': classes.tolist() if hasattr(classes, 'tolist') else list(classes)
    }

def calculate_regression_metrics(y_true, y_pred):
    """
    Calculate comprehensive regression metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Dictionary with all regression metrics
    """
    # Basic metrics
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    
    # Mean Absolute Percentage Error (MAPE)
    # Avoid division by zero
    mask = y_true != 0
    if np.any(mask):
        mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
    else:
        mape = 0.0
    
    # Additional metrics
    mean_error = float(np.mean(y_pred - y_true))
    median_absolute_error = float(np.median(np.abs(y_true - y_pred)))
    
    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2_score': r2,
        'mape': mape,
        'mean_error': mean_error,
        'median_absolute_error': median_absolute_error
    }

