#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Statistical utilities for Hard clam connectivity analysis
Provides common statistical methods used across analyses

Functions:
- Bootstrap confidence intervals
- Block bootstrap for time series
- Permutation tests
- FDR correction
- Robust regression methods
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import spearmanr, pearsonr, theilslopes
from typing import Tuple, Optional, Union, List


def bootstrap_ci(data: np.ndarray,
                 statistic_func=np.mean,
                 n_bootstrap: int = 2000,
                 confidence: float = 0.95,
                 seed: int = 42) -> Tuple[float, float, float]:
    """
    Calculate bootstrap confidence interval for a statistic.

    Parameters:
        data: Input data array
        statistic_func: Function to calculate statistic (default: mean)
        n_bootstrap: Number of bootstrap iterations
        confidence: Confidence level (e.g., 0.95 for 95% CI)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (statistic, ci_lower, ci_upper)
    """
    rng = np.random.default_rng(seed)

    # Calculate observed statistic
    obs_stat = statistic_func(data)

    # Bootstrap sampling
    bootstrap_stats = []
    n = len(data)

    for _ in range(n_bootstrap):
        sample = rng.choice(data, size=n, replace=True)
        bootstrap_stats.append(statistic_func(sample))

    bootstrap_stats = np.array(bootstrap_stats)

    # Calculate confidence interval
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_stats, 100 * alpha/2)
    ci_upper = np.percentile(bootstrap_stats, 100 * (1 - alpha/2))

    return obs_stat, ci_lower, ci_upper


def block_bootstrap_ci(time_series: np.ndarray,
                       block_length: int = 5,
                       statistic_func=np.mean,
                       n_bootstrap: int = 2000,
                       confidence: float = 0.95,
                       seed: int = 42) -> Tuple[float, float, float]:
    """
    Block bootstrap for time series with temporal correlation.

    Parameters:
        time_series: Time series data
        block_length: Length of blocks to preserve correlation
        statistic_func: Function to calculate statistic
        n_bootstrap: Number of bootstrap iterations
        confidence: Confidence level
        seed: Random seed

    Returns:
        Tuple of (statistic, ci_lower, ci_upper)
    """
    rng = np.random.default_rng(seed)

    # Remove NaN values
    clean_data = time_series[~np.isnan(time_series)]
    if len(clean_data) == 0:
        return np.nan, np.nan, np.nan

    n = len(clean_data)
    obs_stat = statistic_func(clean_data)

    # Block bootstrap
    bootstrap_stats = []

    for _ in range(n_bootstrap):
        # Create blocks
        indices = []
        while len(indices) < n:
            start_idx = rng.integers(0, n)
            block_indices = [(start_idx + i) % n for i in range(block_length)]
            indices.extend(block_indices)

        # Trim to exact length
        indices = indices[:n]
        sample = clean_data[indices]
        bootstrap_stats.append(statistic_func(sample))

    bootstrap_stats = np.array(bootstrap_stats)

    # Calculate confidence interval
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_stats, 100 * alpha/2)
    ci_upper = np.percentile(bootstrap_stats, 100 * (1 - alpha/2))

    return obs_stat, ci_lower, ci_upper


def permutation_test(x: np.ndarray,
                    y: np.ndarray,
                    statistic: str = 'correlation',
                    n_permutations: int = 5000,
                    seed: int = 42) -> float:
    """
    Permutation test for significance of relationship between x and y.

    Parameters:
        x, y: Data arrays
        statistic: Type of statistic ('correlation', 'difference', 'slope')
        n_permutations: Number of permutations
        seed: Random seed

    Returns:
        p-value from permutation test
    """
    rng = np.random.default_rng(seed)

    # Remove paired NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 3:
        return np.nan

    # Calculate observed statistic
    if statistic == 'correlation':
        obs_stat = spearmanr(x_clean, y_clean)[0]
    elif statistic == 'difference':
        obs_stat = np.mean(x_clean) - np.mean(y_clean)
    elif statistic == 'slope':
        obs_stat = stats.linregress(x_clean, y_clean).slope
    else:
        raise ValueError(f"Unknown statistic: {statistic}")

    # Permutation distribution
    perm_stats = []

    for _ in range(n_permutations):
        y_perm = rng.permutation(y_clean)

        if statistic == 'correlation':
            perm_stat = spearmanr(x_clean, y_perm)[0]
        elif statistic == 'difference':
            perm_stat = np.mean(x_clean) - np.mean(y_perm)
        elif statistic == 'slope':
            perm_stat = stats.linregress(x_clean, y_perm).slope

        perm_stats.append(perm_stat)

    perm_stats = np.array(perm_stats)

    # Two-tailed p-value
    p_value = np.mean(np.abs(perm_stats) >= np.abs(obs_stat))

    return p_value


def fdr_correction(p_values: Union[list, np.ndarray],
                  alpha: float = 0.05,
                  method: str = 'benjamini-hochberg') -> Tuple[np.ndarray, np.ndarray]:
    """
    False Discovery Rate correction for multiple comparisons.

    Parameters:
        p_values: Array of p-values
        alpha: Significance level
        method: 'benjamini-hochberg' or 'bonferroni'

    Returns:
        Tuple of (adjusted_p_values, reject_null)
    """
    p_values = np.asarray(p_values)
    n = len(p_values)

    if n == 0:
        return np.array([]), np.array([])

    if method == 'bonferroni':
        # Bonferroni correction
        adjusted = p_values * n
        adjusted = np.minimum(adjusted, 1.0)
        reject = adjusted < alpha

    elif method == 'benjamini-hochberg':
        # Sort p-values
        sorted_idx = np.argsort(p_values)
        sorted_p = p_values[sorted_idx]

        # Calculate adjusted p-values
        adjusted = np.zeros(n)
        for i in range(n):
            adjusted[i] = sorted_p[i] * n / (i + 1)

        # Ensure monotonicity
        for i in range(n-2, -1, -1):
            adjusted[i] = min(adjusted[i], adjusted[i+1])

        # Cap at 1
        adjusted = np.minimum(adjusted, 1.0)

        # Restore original order
        result = np.zeros(n)
        result[sorted_idx] = adjusted
        adjusted = result

        # Determine rejection
        reject = adjusted < alpha

    else:
        raise ValueError(f"Unknown method: {method}")

    return adjusted, reject


def robust_regression(x: np.ndarray,
                     y: np.ndarray,
                     method: str = 'theil-sen',
                     confidence: float = 0.95) -> dict:
    """
    Perform robust regression analysis.

    Parameters:
        x, y: Data arrays
        method: 'theil-sen' or 'huber'
        confidence: Confidence level for intervals

    Returns:
        Dictionary with regression results
    """
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 3:
        return {'slope': np.nan, 'intercept': np.nan,
                'ci_slope': (np.nan, np.nan), 'r_squared': np.nan}

    results = {}

    if method == 'theil-sen':
        # Theil-Sen estimator
        slope, intercept, ci_low, ci_high = theilslopes(y_clean, x_clean,
                                                        alpha=1-confidence)
        results['slope'] = slope
        results['intercept'] = intercept
        results['ci_slope'] = (ci_low, ci_high)

    elif method == 'huber':
        # Huber regression (requires sklearn)
        try:
            from sklearn.linear_model import HuberRegressor

            huber = HuberRegressor()
            X = x_clean.reshape(-1, 1)
            huber.fit(X, y_clean)

            results['slope'] = huber.coef_[0]
            results['intercept'] = huber.intercept_

            # Bootstrap confidence interval
            slopes = []
            rng = np.random.default_rng(42)
            for _ in range(1000):
                idx = rng.choice(len(x_clean), size=len(x_clean), replace=True)
                X_boot = x_clean[idx].reshape(-1, 1)
                y_boot = y_clean[idx]
                huber_boot = HuberRegressor()
                huber_boot.fit(X_boot, y_boot)
                slopes.append(huber_boot.coef_[0])

            alpha = 1 - confidence
            results['ci_slope'] = (np.percentile(slopes, 100*alpha/2),
                                  np.percentile(slopes, 100*(1-alpha/2)))

        except ImportError:
            raise ImportError("Huber regression requires scikit-learn")

    else:
        raise ValueError(f"Unknown method: {method}")

    # Calculate R-squared
    y_pred = results['slope'] * x_clean + results['intercept']
    ss_res = np.sum((y_clean - y_pred)**2)
    ss_tot = np.sum((y_clean - np.mean(y_clean))**2)
    results['r_squared'] = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    return results


def calculate_effect_size(group1: np.ndarray,
                         group2: np.ndarray,
                         method: str = 'cohen_d') -> float:
    """
    Calculate effect size between two groups.

    Parameters:
        group1, group2: Data arrays for two groups
        method: 'cohen_d', 'hedges_g', or 'glass_delta'

    Returns:
        Effect size value
    """
    # Remove NaN values
    g1 = group1[~np.isnan(group1)]
    g2 = group2[~np.isnan(group2)]

    if len(g1) == 0 or len(g2) == 0:
        return np.nan

    mean1, mean2 = np.mean(g1), np.mean(g2)
    std1, std2 = np.std(g1, ddof=1), np.std(g2, ddof=1)
    n1, n2 = len(g1), len(g2)

    if method == 'cohen_d':
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))
        if pooled_std == 0:
            return np.nan
        effect_size = (mean1 - mean2) / pooled_std

    elif method == 'hedges_g':
        # Hedges' g (corrected Cohen's d)
        pooled_std = np.sqrt(((n1-1)*std1**2 + (n2-1)*std2**2) / (n1+n2-2))
        if pooled_std == 0:
            return np.nan
        cohen_d = (mean1 - mean2) / pooled_std
        # Correction factor
        correction = 1 - (3 / (4*(n1+n2) - 9))
        effect_size = cohen_d * correction

    elif method == 'glass_delta':
        # Glass's delta (uses control group SD)
        if std2 == 0:
            return np.nan
        effect_size = (mean1 - mean2) / std2

    else:
        raise ValueError(f"Unknown method: {method}")

    return effect_size


def moving_block_bootstrap_forecast(time_series: np.ndarray,
                                   forecast_horizon: int = 1,
                                   block_length: int = 5,
                                   n_bootstrap: int = 1000,
                                   confidence: float = 0.95,
                                   seed: int = 42) -> Tuple[float, float, float]:
    """
    Bootstrap forecast for time series using moving blocks.

    Parameters:
        time_series: Historical time series data
        forecast_horizon: Number of steps ahead to forecast
        block_length: Length of blocks
        n_bootstrap: Number of bootstrap iterations
        confidence: Confidence level
        seed: Random seed

    Returns:
        Tuple of (forecast, ci_lower, ci_upper)
    """
    rng = np.random.default_rng(seed)

    # Clean data
    clean_data = time_series[~np.isnan(time_series)]
    if len(clean_data) < block_length:
        return np.nan, np.nan, np.nan

    n = len(clean_data)
    forecasts = []

    for _ in range(n_bootstrap):
        # Generate bootstrap sample
        indices = []
        while len(indices) < n + forecast_horizon:
            start_idx = rng.integers(0, n - block_length + 1)
            block_indices = list(range(start_idx, start_idx + block_length))
            indices.extend(block_indices)

        # Take the forecast horizon values
        forecast_values = [clean_data[idx % n] for idx in indices[n:n+forecast_horizon]]
        forecasts.append(np.mean(forecast_values))

    forecasts = np.array(forecasts)

    # Calculate statistics
    forecast = np.mean(forecasts)
    alpha = 1 - confidence
    ci_lower = np.percentile(forecasts, 100 * alpha/2)
    ci_upper = np.percentile(forecasts, 100 * (1 - alpha/2))

    return forecast, ci_lower, ci_upper


def significance_stars(p_value: float) -> str:
    """
    Convert p-value to significance stars.

    Parameters:
        p_value: P-value

    Returns:
        String with stars indicating significance level
    """
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return 'ns'


def calculate_cv(data: np.ndarray) -> float:
    """
    Calculate coefficient of variation.

    Parameters:
        data: Data array

    Returns:
        Coefficient of variation (CV)
    """
    clean_data = data[~np.isnan(data)]
    if len(clean_data) == 0:
        return np.nan

    mean_val = np.mean(clean_data)
    if mean_val == 0:
        return np.nan

    return np.std(clean_data, ddof=1) / mean_val


def calculate_autocorrelation(time_series: np.ndarray,
                            max_lag: int = 10) -> np.ndarray:
    """
    Calculate autocorrelation function for time series.

    Parameters:
        time_series: Time series data
        max_lag: Maximum lag to calculate

    Returns:
        Array of autocorrelation values for lags 0 to max_lag
    """
    clean_data = time_series[~np.isnan(time_series)]
    if len(clean_data) < max_lag + 1:
        return np.full(max_lag + 1, np.nan)

    # Demean the series
    data_centered = clean_data - np.mean(clean_data)

    # Calculate autocorrelation
    acf = []
    c0 = np.dot(data_centered, data_centered) / len(data_centered)

    for lag in range(max_lag + 1):
        if lag == 0:
            acf.append(1.0)
        else:
            c_lag = np.dot(data_centered[:-lag], data_centered[lag:]) / len(data_centered)
            acf.append(c_lag / c0 if c0 > 0 else np.nan)

    return np.array(acf)


# Example usage and testing
if __name__ == "__main__":
    # Generate example data
    np.random.seed(42)
    x = np.random.normal(25, 2, 100)  # Temperature
    y = 50 + 2*x + np.random.normal(0, 5, 100)  # Distance

    # Test bootstrap CI
    mean_val, ci_low, ci_high = bootstrap_ci(y)
    print(f"Bootstrap CI for mean: {mean_val:.2f} [{ci_low:.2f}, {ci_high:.2f}]")

    # Test permutation test
    p_val = permutation_test(x, y, statistic='correlation')
    print(f"Permutation test p-value: {p_val:.4f}")

    # Test robust regression
    reg_results = robust_regression(x, y)
    print(f"Theil-Sen regression: slope={reg_results['slope']:.3f}, "
          f"CI=[{reg_results['ci_slope'][0]:.3f}, {reg_results['ci_slope'][1]:.3f}]")

    # Test FDR correction
    p_values = [0.001, 0.01, 0.03, 0.05, 0.20]
    adjusted, reject = fdr_correction(p_values)
    print(f"FDR adjusted p-values: {adjusted}")
    print(f"Reject null: {reject}")

    # Test effect size
    group1 = np.random.normal(100, 15, 50)
    group2 = np.random.normal(110, 15, 50)
    d = calculate_effect_size(group1, group2)
    print(f"Cohen's d effect size: {d:.3f}")