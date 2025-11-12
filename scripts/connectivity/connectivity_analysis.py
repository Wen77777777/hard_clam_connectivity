#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hard clam MPA connectivity analysis
Temperature-driven connectivity patterns in the Bohai Sea

This script analyzes connectivity patterns between Marine Protected Areas (MPAs)
based on particle tracking simulations and temperature conditions.

Main components:
- Connectivity matrix calculation
- Temperature classification (warm/cold/neutral years)
- Statistical analysis and bootstrapping
- Network metrics (source strength, sink strength, leakage rate)
"""

import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
from scipy import stats

warnings.filterwarnings('ignore')

# ----------------- Configuration -----------------
# Marine Protected Areas
MPA_ORDER = ["MNR-7", "MNR-8-N", "MNR-8-S", "SMPA-2", "SMPA-4"]
DEST_OUTSIDE = "OUTSIDE"
DEST_UNSETTLED = "UNSETTLED"
NA_ORIGIN = "NA_ORIGIN"

# Temperature-based year classification (based on egg-stage temperature)
WARM_YEARS = [2017, 2018, 2022]    # Egg temperature > 75th percentile
COLD_YEARS = [2014, 2015, 2020]    # Egg temperature < 25th percentile
NEUTRAL_YEARS = [2016, 2019, 2021]  # 25th ≤ egg temperature ≤ 75th percentile

# Statistical parameters
N_BOOTSTRAP = 2000
CONFIDENCE_LEVEL = 0.95
INCLUDE_UNSETTLED_IN_LEAKAGE = False
EXCLUDE_SELF_IN_SS = True

# Visualization colors
COLOR_COLD = "#3B4CC0"   # Blue for cold years
COLOR_WARM = "#B40426"   # Red for warm years
COLOR_NEUTRAL = "#888888" # Gray for neutral years


class ConnectivityAnalyzer:
    """Analyze connectivity patterns from particle tracking results."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.years = list(range(2014, 2023))

    def load_connectivity_matrix(self, year: int, normalized: bool = True) -> pd.DataFrame:
        """
        Load connectivity matrix for a specific year.

        Parameters:
            year: Year to load
            normalized: If True, load row-normalized (probability) matrix

        Returns:
            Connectivity matrix as DataFrame
        """
        if normalized:
            filename = "connectivity_matrix_normalized_v10.csv"
        else:
            filename = "connectivity_matrix_v10.csv"

        file_path = self.data_dir / f"output_dir_{year}" / "analysis_outputs_v10" / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Connectivity matrix not found: {file_path}")

        df = pd.read_csv(file_path, index_col=0, encoding="utf-8-sig")

        # Clean and reorder
        if NA_ORIGIN in df.index:
            df = df.drop(index=[NA_ORIGIN])

        rows = [r for r in MPA_ORDER if r in df.index]
        cols = [c for c in MPA_ORDER if c in df.columns]

        # Include outside destinations if present
        for extra in [DEST_UNSETTLED, DEST_OUTSIDE]:
            if extra in df.columns:
                cols.append(extra)

        df = df.reindex(index=rows, columns=cols).fillna(0.0)
        return df

    def load_particle_data(self, year: int) -> pd.DataFrame:
        """Load particle-level data including temperature and distance metrics."""
        file_path = self.data_dir / f"output_dir_{year}" / "analysis_outputs_v10" / "particle_data.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Particle data not found: {file_path}")

        return pd.read_csv(file_path, encoding="utf-8-sig")

    def calculate_network_metrics(self, conn_matrix: pd.DataFrame) -> dict:
        """
        Calculate network-level connectivity metrics.

        Parameters:
            conn_matrix: Normalized connectivity matrix

        Returns:
            Dictionary of metrics
        """
        metrics = {}

        # Source strength (outgoing connectivity)
        source_strength = {}
        for origin in MPA_ORDER:
            if origin not in conn_matrix.index:
                continue
            row = conn_matrix.loc[origin]
            # Sum connections to other MPAs (exclude self and outside)
            other_mpas = [c for c in MPA_ORDER if c != origin and c in row.index]
            source_strength[origin] = row[other_mpas].sum()

        # Sink strength (incoming connectivity)
        sink_strength = {}
        for dest in MPA_ORDER:
            if dest not in conn_matrix.columns:
                continue
            # Sum connections from other MPAs
            other_mpas = [r for r in MPA_ORDER if r != dest and r in conn_matrix.index]
            sink_strength[dest] = conn_matrix.loc[other_mpas, dest].sum()

        # Leakage rate (particles leaving MPA network)
        leakage = {}
        for origin in MPA_ORDER:
            if origin not in conn_matrix.index:
                continue
            row = conn_matrix.loc[origin]
            outside = 0.0
            if DEST_OUTSIDE in row.index:
                outside += row[DEST_OUTSIDE]
            if INCLUDE_UNSETTLED_IN_LEAKAGE and DEST_UNSETTLED in row.index:
                outside += row[DEST_UNSETTLED]
            leakage[origin] = outside

        # Self-recruitment rate
        self_recruitment = {}
        for mpa in MPA_ORDER:
            if mpa in conn_matrix.index and mpa in conn_matrix.columns:
                self_recruitment[mpa] = conn_matrix.loc[mpa, mpa]

        metrics['source_strength'] = source_strength
        metrics['sink_strength'] = sink_strength
        metrics['leakage'] = leakage
        metrics['self_recruitment'] = self_recruitment

        return metrics

    def bootstrap_connectivity(self, years: list, n_bootstrap: int = 1000) -> dict:
        """
        Bootstrap connectivity metrics across years.

        Parameters:
            years: List of years to include
            n_bootstrap: Number of bootstrap iterations

        Returns:
            Dictionary with bootstrapped statistics
        """
        # Load all connectivity matrices
        matrices = []
        for year in years:
            try:
                conn = self.load_connectivity_matrix(year, normalized=True)
                matrices.append(conn)
            except FileNotFoundError:
                print(f"Warning: No data for year {year}")
                continue

        if not matrices:
            raise ValueError("No valid connectivity matrices found")

        # Bootstrap sampling
        bootstrap_results = []
        for _ in range(n_bootstrap):
            # Sample with replacement
            sampled_matrices = np.random.choice(matrices, size=len(matrices), replace=True)
            # Average the sampled matrices
            avg_matrix = pd.concat(sampled_matrices).groupby(level=0).mean()
            # Calculate metrics
            metrics = self.calculate_network_metrics(avg_matrix)
            bootstrap_results.append(metrics)

        # Aggregate bootstrap results
        aggregated = {
            'source_strength': {},
            'sink_strength': {},
            'leakage': {},
            'self_recruitment': {}
        }

        for metric_type in aggregated.keys():
            for mpa in MPA_ORDER:
                values = [r[metric_type].get(mpa, 0) for r in bootstrap_results]
                if values:
                    aggregated[metric_type][mpa] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'ci_low': np.percentile(values, 2.5),
                        'ci_high': np.percentile(values, 97.5)
                    }

        return aggregated

    def compare_temperature_regimes(self):
        """Compare connectivity patterns between warm and cold years."""
        # Load data for each temperature regime
        warm_metrics = self.bootstrap_connectivity(WARM_YEARS, N_BOOTSTRAP)
        cold_metrics = self.bootstrap_connectivity(COLD_YEARS, N_BOOTSTRAP)

        # Statistical comparison
        comparisons = {}
        for metric_type in ['source_strength', 'sink_strength', 'leakage', 'self_recruitment']:
            comparisons[metric_type] = {}
            for mpa in MPA_ORDER:
                if mpa in warm_metrics[metric_type] and mpa in cold_metrics[metric_type]:
                    warm_val = warm_metrics[metric_type][mpa]['mean']
                    cold_val = cold_metrics[metric_type][mpa]['mean']
                    diff = warm_val - cold_val
                    comparisons[metric_type][mpa] = {
                        'warm': warm_val,
                        'cold': cold_val,
                        'difference': diff,
                        'relative_change': diff / cold_val if cold_val > 0 else 0
                    }

        return comparisons


def plot_connectivity_comparison(analyzer: ConnectivityAnalyzer):
    """Create comprehensive connectivity comparison figure."""

    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, hspace=0.3, wspace=0.25)

    # Load connectivity matrices
    warm_matrices = [analyzer.load_connectivity_matrix(y) for y in WARM_YEARS]
    cold_matrices = [analyzer.load_connectivity_matrix(y) for y in COLD_YEARS]

    warm_avg = pd.concat(warm_matrices).groupby(level=0).mean()
    cold_avg = pd.concat(cold_matrices).groupby(level=0).mean()

    # Panel A: Warm years connectivity matrix
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(warm_avg.loc[MPA_ORDER, MPA_ORDER].values,
                     cmap='Reds', vmin=0, vmax=0.5, aspect='auto')
    ax1.set_xticks(range(len(MPA_ORDER)))
    ax1.set_yticks(range(len(MPA_ORDER)))
    ax1.set_xticklabels(MPA_ORDER, rotation=45, ha='right')
    ax1.set_yticklabels(MPA_ORDER)
    ax1.set_xlabel("Destination")
    ax1.set_ylabel("Origin")
    ax1.set_title("Warm years connectivity", fontsize=12, fontweight='bold')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    # Add values to cells
    for i in range(len(MPA_ORDER)):
        for j in range(len(MPA_ORDER)):
            val = warm_avg.iloc[i, j]
            if val > 0.01:
                text = ax1.text(j, i, f'{val:.2f}' if val < 0.1 else f'{val:.1%}',
                              ha="center", va="center", color="white" if val > 0.3 else "black")

    # Panel B: Cold years connectivity matrix
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = ax2.imshow(cold_avg.loc[MPA_ORDER, MPA_ORDER].values,
                     cmap='Blues', vmin=0, vmax=0.5, aspect='auto')
    ax2.set_xticks(range(len(MPA_ORDER)))
    ax2.set_yticks(range(len(MPA_ORDER)))
    ax2.set_xticklabels(MPA_ORDER, rotation=45, ha='right')
    ax2.set_yticklabels(MPA_ORDER)
    ax2.set_xlabel("Destination")
    ax2.set_ylabel("Origin")
    ax2.set_title("Cold years connectivity", fontsize=12, fontweight='bold')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    # Add values to cells
    for i in range(len(MPA_ORDER)):
        for j in range(len(MPA_ORDER)):
            val = cold_avg.iloc[i, j]
            if val > 0.01:
                text = ax2.text(j, i, f'{val:.2f}' if val < 0.1 else f'{val:.1%}',
                              ha="center", va="center", color="white" if val > 0.3 else "black")

    # Panel C: Difference matrix
    ax3 = fig.add_subplot(gs[0, 2])
    diff = warm_avg.loc[MPA_ORDER, MPA_ORDER] - cold_avg.loc[MPA_ORDER, MPA_ORDER]
    im3 = ax3.imshow(diff.values, cmap='RdBu_r', vmin=-0.1, vmax=0.1, aspect='auto')
    ax3.set_xticks(range(len(MPA_ORDER)))
    ax3.set_yticks(range(len(MPA_ORDER)))
    ax3.set_xticklabels(MPA_ORDER, rotation=45, ha='right')
    ax3.set_yticklabels(MPA_ORDER)
    ax3.set_xlabel("Destination")
    ax3.set_ylabel("Origin")
    ax3.set_title("Connectivity difference (Warm - Cold)", fontsize=12, fontweight='bold')
    plt.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)

    # Panel D-F: Network metrics
    comparisons = analyzer.compare_temperature_regimes()

    # Source strength
    ax4 = fig.add_subplot(gs[1, 0])
    x = np.arange(len(MPA_ORDER))
    width = 0.35
    warm_vals = [comparisons['source_strength'][mpa]['warm'] for mpa in MPA_ORDER]
    cold_vals = [comparisons['source_strength'][mpa]['cold'] for mpa in MPA_ORDER]
    ax4.bar(x - width/2, warm_vals, width, label='Warm', color=COLOR_WARM)
    ax4.bar(x + width/2, cold_vals, width, label='Cold', color=COLOR_COLD)
    ax4.set_xlabel("MPA")
    ax4.set_ylabel("Source strength")
    ax4.set_title("Source strength comparison")
    ax4.set_xticks(x)
    ax4.set_xticklabels(MPA_ORDER, rotation=45)
    ax4.legend()

    # Sink strength
    ax5 = fig.add_subplot(gs[1, 1])
    warm_vals = [comparisons['sink_strength'][mpa]['warm'] for mpa in MPA_ORDER]
    cold_vals = [comparisons['sink_strength'][mpa]['cold'] for mpa in MPA_ORDER]
    ax5.bar(x - width/2, warm_vals, width, label='Warm', color=COLOR_WARM)
    ax5.bar(x + width/2, cold_vals, width, label='Cold', color=COLOR_COLD)
    ax5.set_xlabel("MPA")
    ax5.set_ylabel("Sink strength")
    ax5.set_title("Sink strength comparison")
    ax5.set_xticks(x)
    ax5.set_xticklabels(MPA_ORDER, rotation=45)
    ax5.legend()

    # Leakage rate
    ax6 = fig.add_subplot(gs[1, 2])
    warm_vals = [comparisons['leakage'][mpa]['warm'] for mpa in MPA_ORDER]
    cold_vals = [comparisons['leakage'][mpa]['cold'] for mpa in MPA_ORDER]
    ax6.bar(x - width/2, warm_vals, width, label='Warm', color=COLOR_WARM)
    ax6.bar(x + width/2, cold_vals, width, label='Cold', color=COLOR_COLD)
    ax6.set_xlabel("MPA")
    ax6.set_ylabel("Leakage rate")
    ax6.set_title("Leakage rate comparison")
    ax6.set_xticks(x)
    ax6.set_xticklabels(MPA_ORDER, rotation=45)
    ax6.legend()

    # Self-recruitment
    ax7 = fig.add_subplot(gs[2, 0:2])
    warm_vals = [comparisons['self_recruitment'][mpa]['warm'] for mpa in MPA_ORDER]
    cold_vals = [comparisons['self_recruitment'][mpa]['cold'] for mpa in MPA_ORDER]
    ax7.bar(x - width/2, warm_vals, width, label='Warm', color=COLOR_WARM)
    ax7.bar(x + width/2, cold_vals, width, label='Cold', color=COLOR_COLD)
    ax7.set_xlabel("MPA")
    ax7.set_ylabel("Self-recruitment rate")
    ax7.set_title("Self-recruitment comparison")
    ax7.set_xticks(x)
    ax7.set_xticklabels(MPA_ORDER, rotation=45)
    ax7.legend()

    plt.suptitle("Temperature-driven connectivity patterns in Bohai Sea MPAs",
                 fontsize=14, fontweight='bold', y=0.98)

    return fig


if __name__ == "__main__":
    # Example usage
    data_dir = Path("./data")  # Update with actual data path
    analyzer = ConnectivityAnalyzer(data_dir)

    # Generate comparison figure
    fig = plot_connectivity_comparison(analyzer)
    fig.savefig("connectivity_comparison.png", dpi=300, bbox_inches='tight')

    # Export comparison statistics
    comparisons = analyzer.compare_temperature_regimes()

    # Save to CSV
    for metric_type in comparisons:
        df = pd.DataFrame(comparisons[metric_type]).T
        df.to_csv(f"connectivity_{metric_type}_comparison.csv")

    print("Analysis complete. Results saved.")