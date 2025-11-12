#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exposure-response analysis for Hard clam connectivity
Temperature effects on connectivity metrics

This script analyzes the relationship between temperature exposure (Ty, EAT)
and connectivity response metrics (self-recruitment, source strength, etc.)

Key analyses:
- Ty (mean egg temperature) vs connectivity metrics
- EAT (Effective Accumulated Temperature) calculations
- Spearman correlations with FDR correction
- Robust regression (Theil-Sen) with confidence intervals
"""

import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from scipy.stats import spearmanr, theilslopes
from scipy import stats
import seaborn as sns

warnings.filterwarnings('ignore')

# ----------------- Configuration -----------------
YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
MPA_ORDER = ["MNR-7", "MNR-8-N", "MNR-8-S", "SMPA-2", "SMPA-4"]

# Temperature-based year classification (egg stage)
WARM_YEARS = {2017, 2018, 2022}    # Ty > P75 based on egg stage
COLD_YEARS = {2014, 2015, 2020}    # Ty < P25 based on egg stage
NEUTRAL_YEARS = {2016, 2019, 2021} # P25 ≤ Ty ≤ P75 based on egg stage

# Statistical parameters
N_BOOTSTRAP = 1000
N_PERMUTATION = 5000
ALPHA = 0.05
RANDOM_SEED = 42

# Color scheme (colorblind-friendly)
COLOR_COLD = "#3B4CC0"   # Blue
COLOR_NEUTRAL = "#888888" # Gray
COLOR_WARM = "#B40426"   # Red

# Marker styles for year types
MARKER_COLD = 'o'    # Circle
MARKER_NEUTRAL = 's'  # Square
MARKER_WARM = '^'     # Triangle

# Plot settings
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 12,
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.2,
    'patch.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'pdf.fonttype': 42,
    'svg.fonttype': 'none'
})


class ExposureResponseAnalyzer:
    """Analyze exposure-response relationships in Hard clam connectivity."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.year_metrics = {}
        self.connectivity_metrics = {}

    def load_particle_data(self, year: int) -> pd.DataFrame:
        """Load per-particle summary data for a year."""
        file_path = (self.data_dir / f"output_dir_{year}" /
                    "analysis_outputs_v10" / "per_particle_summary_rel_v10.csv")

        if not file_path.exists():
            print(f"Warning: No particle data for {year}")
            return pd.DataFrame()

        df = pd.read_csv(file_path, encoding="utf-8-sig", low_memory=False)

        # Ensure required columns
        if "temp_mean_egg" not in df.columns and "temp_mean" in df.columns:
            df["temp_mean_egg"] = df["temp_mean"]

        return df

    def load_connectivity_matrix(self, year: int) -> pd.DataFrame:
        """Load normalized connectivity matrix for a year."""
        file_path = (self.data_dir / f"output_dir_{year}" /
                    "analysis_outputs_v10" / "connectivity_matrix_normalized_v10.csv")

        if not file_path.exists():
            print(f"Warning: No connectivity matrix for {year}")
            return pd.DataFrame()

        df = pd.read_csv(file_path, index_col=0, encoding="utf-8-sig")

        # Filter to MPA zones
        rows = [r for r in MPA_ORDER if r in df.index]
        cols = [c for c in MPA_ORDER if c in df.columns]
        df = df.reindex(index=rows, columns=cols).fillna(0.0)

        return df

    def calculate_ty(self, particle_df: pd.DataFrame) -> float:
        """
        Calculate Ty (mean egg-stage temperature).

        Parameters:
            particle_df: DataFrame with particle data

        Returns:
            Mean egg temperature (°C)
        """
        if "temp_mean_egg" in particle_df.columns:
            return particle_df["temp_mean_egg"].mean()
        return np.nan

    def calculate_eat(self, particle_df: pd.DataFrame) -> float:
        """
        Calculate EAT (Effective Accumulated Temperature).

        EAT = mean(hot_degree_hours - cold_degree_hours) across particles

        Parameters:
            particle_df: DataFrame with particle data

        Returns:
            EAT value (degree-hours)
        """
        if "hot_deg_h_egg" in particle_df.columns and "cold_deg_h_egg" in particle_df.columns:
            eat = particle_df["hot_deg_h_egg"] - particle_df["cold_deg_h_egg"]
            return eat.mean()

        # Fallback calculation
        if "temp_mean_egg" in particle_df.columns:
            temp = particle_df["temp_mean_egg"]
            hot = np.maximum(0, temp - 27.0)  # Above optimal high
            cold = np.maximum(0, 25.0 - temp)  # Below optimal low
            return (hot - cold).mean()

        return np.nan

    def calculate_connectivity_metrics(self, conn_matrix: pd.DataFrame) -> dict:
        """
        Calculate connectivity metrics from matrix.

        Parameters:
            conn_matrix: Normalized connectivity matrix

        Returns:
            Dictionary of metrics
        """
        metrics = {}

        if conn_matrix.empty:
            return metrics

        # Self-recruitment (mean of diagonal)
        diagonal = np.diag(conn_matrix.values)
        metrics['self_recruitment'] = np.mean(diagonal)

        # Source strength (mean outgoing to other MPAs)
        source_strength = []
        for origin in conn_matrix.index:
            row = conn_matrix.loc[origin]
            others = [c for c in conn_matrix.columns if c != origin]
            if others:
                source_strength.append(row[others].sum())
        metrics['source_strength'] = np.mean(source_strength) if source_strength else 0

        # Sink strength (mean incoming from other MPAs)
        sink_strength = []
        for dest in conn_matrix.columns:
            col = conn_matrix[dest]
            others = [r for r in conn_matrix.index if r != dest]
            if others:
                sink_strength.append(col[others].sum())
        metrics['sink_strength'] = np.mean(sink_strength) if sink_strength else 0

        # Network connectivity (mean of all connections)
        metrics['network_connectivity'] = conn_matrix.values.mean()

        # Local retention (self + neighboring MPAs)
        # Define neighbors (simplified - you can customize)
        neighbors = {
            "MNR-7": ["MNR-8-N", "MNR-8-S"],
            "MNR-8-N": ["MNR-7", "MNR-8-S"],
            "MNR-8-S": ["MNR-7", "MNR-8-N"],
            "SMPA-2": ["SMPA-4"],
            "SMPA-4": ["SMPA-2"]
        }

        local_retention = []
        for mpa in conn_matrix.index:
            if mpa in neighbors:
                local = conn_matrix.loc[mpa, mpa]  # Self
                for neighbor in neighbors[mpa]:
                    if neighbor in conn_matrix.columns:
                        local += conn_matrix.loc[mpa, neighbor]
                local_retention.append(local)

        metrics['local_retention'] = np.mean(local_retention) if local_retention else 0

        return metrics

    def compile_year_metrics(self):
        """Compile metrics for all years."""
        for year in YEARS:
            print(f"Processing {year}...")

            # Load data
            particle_df = self.load_particle_data(year)
            conn_matrix = self.load_connectivity_matrix(year)

            if particle_df.empty or conn_matrix.empty:
                continue

            # Calculate exposure metrics
            ty = self.calculate_ty(particle_df)
            eat = self.calculate_eat(particle_df)

            # Calculate connectivity metrics
            conn_metrics = self.calculate_connectivity_metrics(conn_matrix)

            # Determine year type
            if year in WARM_YEARS:
                year_type = "warm"
            elif year in COLD_YEARS:
                year_type = "cold"
            else:
                year_type = "neutral"

            # Store results
            self.year_metrics[year] = {
                'year': year,
                'year_type': year_type,
                'Ty': ty,
                'EAT': eat,
                **conn_metrics
            }

    def calculate_correlations(self) -> pd.DataFrame:
        """
        Calculate correlations between exposure and response variables.

        Returns:
            DataFrame with correlation statistics
        """
        if not self.year_metrics:
            self.compile_year_metrics()

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(self.year_metrics, orient='index')

        # Response variables
        response_vars = ['self_recruitment', 'source_strength',
                        'sink_strength', 'network_connectivity', 'local_retention']

        # Exposure variables
        exposure_vars = ['Ty', 'EAT']

        results = []

        for exposure in exposure_vars:
            for response in response_vars:
                if exposure in df.columns and response in df.columns:
                    # Remove NaN values
                    valid = df[[exposure, response]].dropna()

                    if len(valid) >= 3:  # Need at least 3 points
                        # Spearman correlation
                        r_spear, p_spear = spearmanr(valid[exposure], valid[response])

                        # Pearson correlation
                        r_pear, p_pear = stats.pearsonr(valid[exposure], valid[response])

                        # Theil-Sen regression
                        slope, intercept, lo_slope, hi_slope = theilslopes(
                            valid[response], valid[exposure], alpha=0.95
                        )

                        results.append({
                            'Exposure': exposure,
                            'Response': response,
                            'N': len(valid),
                            'Spearman_r': r_spear,
                            'Spearman_p': p_spear,
                            'Pearson_r': r_pear,
                            'Pearson_p': p_pear,
                            'TheilSen_slope': slope,
                            'TheilSen_CI_low': lo_slope,
                            'TheilSen_CI_high': hi_slope
                        })

        corr_df = pd.DataFrame(results)

        # Apply FDR correction
        if len(corr_df) > 0:
            corr_df['Spearman_p_adj'] = self._fdr_correction(corr_df['Spearman_p'])
            corr_df['Pearson_p_adj'] = self._fdr_correction(corr_df['Pearson_p'])

        return corr_df

    def _fdr_correction(self, p_values):
        """
        Apply Benjamini-Hochberg FDR correction.

        Parameters:
            p_values: Array of p-values

        Returns:
            Adjusted p-values
        """
        n = len(p_values)
        sorted_idx = np.argsort(p_values)
        sorted_p = np.array(p_values)[sorted_idx]

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

        return result

    def plot_exposure_response_curves(self, output_path: Path = None):
        """
        Create 2×2 panel figure of exposure-response relationships.

        Parameters:
            output_path: Path to save figure
        """
        if not self.year_metrics:
            self.compile_year_metrics()

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(self.year_metrics, orient='index')

        # Select key metrics for 2×2 layout
        metrics_to_plot = [
            ('Ty', 'self_recruitment', 'Self-recruitment vs Temperature'),
            ('Ty', 'source_strength', 'Source strength vs Temperature'),
            ('EAT', 'network_connectivity', 'Network connectivity vs EAT'),
            ('EAT', 'local_retention', 'Local retention vs EAT')
        ]

        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        for idx, (x_var, y_var, title) in enumerate(metrics_to_plot):
            ax = axes[idx]

            # Plot by year type
            for year_type, color, marker, label in [
                ('cold', COLOR_COLD, MARKER_COLD, 'Cold years'),
                ('neutral', COLOR_NEUTRAL, MARKER_NEUTRAL, 'Neutral years'),
                ('warm', COLOR_WARM, MARKER_WARM, 'Warm years')
            ]:
                subset = df[df['year_type'] == year_type]
                ax.scatter(subset[x_var], subset[y_var],
                          color=color, marker=marker, s=100,
                          alpha=0.7, label=label, edgecolors='black', linewidth=1)

            # Add year labels
            for _, row in df.iterrows():
                ax.annotate(str(row['year'])[-2:],  # Last 2 digits of year
                          (row[x_var], row[y_var]),
                          fontsize=8, ha='center', va='center')

            # Fit regression line (all data)
            valid = df[[x_var, y_var]].dropna()
            if len(valid) >= 3:
                # Theil-Sen regression
                slope, intercept, lo_slope, hi_slope = theilslopes(
                    valid[y_var], valid[x_var], alpha=0.95
                )

                # Plot regression line
                x_range = np.linspace(valid[x_var].min(), valid[x_var].max(), 100)
                y_pred = slope * x_range + intercept
                ax.plot(x_range, y_pred, 'k-', linewidth=2, alpha=0.5)

                # Add confidence band
                y_lower = lo_slope * x_range + intercept
                y_upper = hi_slope * x_range + intercept
                ax.fill_between(x_range, y_lower, y_upper, alpha=0.2, color='gray')

                # Calculate correlation
                r, p = spearmanr(valid[x_var], valid[y_var])

                # Add statistics
                stats_text = f'r = {r:.3f}'
                if p < 0.001:
                    stats_text += '***'
                elif p < 0.01:
                    stats_text += '**'
                elif p < 0.05:
                    stats_text += '*'
                else:
                    stats_text += ' (ns)'

                ax.text(0.05, 0.95, stats_text,
                       transform=ax.transAxes, fontsize=9,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            # Labels and formatting
            if x_var == 'Ty':
                ax.set_xlabel('Mean egg temperature, Ty (°C)')
            else:
                ax.set_xlabel('Effective Accumulated Temperature, EAT (°C·h)')

            ax.set_ylabel(y_var.replace('_', ' ').capitalize())
            ax.set_title(f'({chr(65+idx)}) {title}', fontweight='bold', loc='left')
            ax.grid(True, alpha=0.3)

            # Legend only on first panel
            if idx == 0:
                ax.legend(loc='lower right', framealpha=0.9)

        plt.suptitle('Temperature exposure-connectivity response relationships',
                    fontsize=14, fontweight='bold', y=1.02)

        plt.tight_layout()

        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {output_path}")

        return fig

    def permutation_test(self, x, y, n_permutations=5000):
        """
        Perform permutation test for correlation significance.

        Parameters:
            x, y: Data arrays
            n_permutations: Number of permutations

        Returns:
            p-value from permutation test
        """
        # Observed correlation
        obs_r, _ = spearmanr(x, y)

        # Permutation correlations
        perm_r = []
        rng = np.random.default_rng(RANDOM_SEED)

        for _ in range(n_permutations):
            y_perm = rng.permutation(y)
            r_perm, _ = spearmanr(x, y_perm)
            perm_r.append(r_perm)

        perm_r = np.array(perm_r)

        # Two-tailed p-value
        p_value = np.mean(np.abs(perm_r) >= np.abs(obs_r))

        return p_value

    def generate_summary_table(self, output_path: Path = None):
        """
        Generate summary table of exposure-response relationships.

        Parameters:
            output_path: Path to save CSV
        """
        # Calculate correlations
        corr_df = self.calculate_correlations()

        # Add significance markers
        def sig_marker(p):
            if p < 0.001:
                return '***'
            elif p < 0.01:
                return '**'
            elif p < 0.05:
                return '*'
            else:
                return 'ns'

        corr_df['Significance'] = corr_df['Spearman_p_adj'].apply(sig_marker)

        # Format for publication
        summary = corr_df[['Exposure', 'Response', 'N',
                          'Spearman_r', 'Spearman_p_adj', 'Significance',
                          'TheilSen_slope', 'TheilSen_CI_low', 'TheilSen_CI_high']]

        summary.columns = ['Exposure', 'Response', 'N',
                          'Spearman r', 'Adjusted p', 'Sig',
                          'Slope', 'CI_low', 'CI_high']

        if output_path:
            summary.to_csv(output_path, index=False)
            print(f"Summary table saved to {output_path}")

        return summary


def main():
    """Main analysis workflow."""
    # Set up paths
    data_dir = Path("./data")  # Update with actual path
    output_dir = Path("./figures")
    output_dir.mkdir(exist_ok=True)

    # Initialize analyzer
    analyzer = ExposureResponseAnalyzer(data_dir)

    # Compile metrics
    print("Compiling year metrics...")
    analyzer.compile_year_metrics()

    # Generate exposure-response figure
    print("Generating exposure-response curves...")
    fig = analyzer.plot_exposure_response_curves(
        output_dir / "exposure_response_curves.png"
    )

    # Generate summary table
    print("Generating summary statistics...")
    summary = analyzer.generate_summary_table(
        output_dir / "exposure_response_statistics.csv"
    )

    print("\nExposure-Response Summary:")
    print(summary.to_string(index=False))

    # Print year metrics
    print("\nYear-by-year metrics:")
    year_df = pd.DataFrame.from_dict(analyzer.year_metrics, orient='index')
    print(year_df[['year', 'year_type', 'Ty', 'EAT',
                   'self_recruitment', 'network_connectivity']].round(3))


if __name__ == "__main__":
    main()