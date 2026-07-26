"""SHAP-like attribution calculator for the Random Forest risk model."""

from __future__ import annotations

import math
from typing import Any, List, Dict
import numpy as np
from ..analytics.risk import get_trained_model_and_features

# Feature baselines (from training data or global medians)
BASELINES = [3.0, 0.30, 0.55, 0.30, 0.40]


def calculate_exact_shap(values: List[float]) -> Dict[str, float]:
    """Calculate exact Shapley values for a 5-feature input vector using the Random Forest model."""
    model, _, _, feature_names = get_trained_model_and_features()
    
    num_features = len(feature_names)
    shap_values = np.zeros(num_features)
    
    # Pre-calculate factorials
    def weight(s_size: int, n: int) -> float:
        return math.factorial(s_size) * math.factorial(n - s_size - 1) / math.factorial(n)
        
    # Iterate over every feature
    for i in range(num_features):
        # Find all subsets of features excluding feature i
        other_features = [j for j in range(num_features) if j != i]
        
        # Total combinations is 2^(n-1) = 16
        for mask in range(1 << (num_features - 1)):
            # Form subset S
            S = []
            for bit in range(num_features - 1):
                if (mask & (1 << bit)) > 0:
                    S.append(other_features[bit])
                    
            # Compute v(S)
            vector_s = np.array(BASELINES, dtype=float)
            for feat_idx in S:
                vector_s[feat_idx] = values[feat_idx]
                
            # Compute v(S U {i})
            vector_s_i = np.copy(vector_s)
            vector_s_i[i] = values[i]
            
            # Predict probabilities
            v_s = float(model.predict_proba([vector_s])[0][1])
            v_s_i = float(model.predict_proba([vector_s_i])[0][1])
            
            # Weight contribution
            w = weight(len(S), num_features)
            shap_values[i] += w * (v_s_i - v_s)
            
    return {name: float(val) for name, val in zip(feature_names, shap_values)}
