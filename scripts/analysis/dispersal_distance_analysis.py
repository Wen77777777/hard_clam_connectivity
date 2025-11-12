#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dispersal distance analysis for Hard clam connectivity
Particle-level analysis of temperature-distance relationships

This script analyzes the relationship between egg-stage temperature and dispersal
distance using particle-level data (~1.7 million particles).

Key outputs:
- Temperature vs dispersal distance scatter plots
- Statistical correlations by year type
- Linear and non-linear regression models
"""

import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
from scipy import stats
from scipy.optimize import curve_fit

warnings.filterwarnings('ignore')

# ----------------- Configuration -----------------
YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]

# Temperature-based year classification (egg stage)
WARM_YEARS = [2017, 2018, 2022]    # Egg temperature > 75th percentile
COLD_YEARS = [2014, 2015, 2020]    # Egg temperature < 25th percentile
NEUTRAL_YEARS = [2016, 2019, 2021] # Between 25th-75th percentile

# MPA zones
MPA_ORDER = ["MNR-7", "MNR-8-N", "MNR-8-S", "SMPA-2", "SMPA-4"]

# Colors consistent with other analyses
COLOR_COLD = "#3B4CC0"   # Blue
COLOR_WARM = "#B40426"   # Red
COLOR_NEUTRAL = "#888888" # Gray

# Statistical parameters
N_BOOTSTRAP = 2000
ALPHA = 0.05
RANDOM_SEED = 42

# Plot settings
plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 1.0,
    "axes.edgecolor": "#333333",
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "svg.fonttype": 'none'
})


class DispersalAnalyzer:
    """Analyze dispersal distance patterns in relation to temperature."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.particle_data = {}

    def load_particle_data(self, year: int) -> pd.DataFrame:
        """
        Load per-particle summary data.

        Parameters:
            year: Year to load

        Returns:
            DataFrame with particle data
        """
        file_path = (self.data_dir / f"output_dir_{year}" /
                    "analysis_outputs_v10" / "per_particle_summary_rel_v10.csv")

        if not file_path.exists():
            print(f"Warning: No data for {year}")
            return pd.DataFrame()

        df = pd.read_csv(file_path, encoding="utf-8-sig", low_memory=False)

        # Process columns
        if "zone_release" in df.columns:
            df = df[df["zone_release"].isin(MPA_ORDER)]

        # Calculate dispersal distance if not present
        if "distance_km" not in df.columns and all(col in df.columns for col in
                                                   ["settle_lon", "settle_lat",
                                                    "release_lon", "release_lat"]):
            df["distance_km"] = self._haversine_distance(
                df["release_lon"], df["release_lat"],
                df["settle_lon"], df["settle_lat"]
            )

        # Get egg temperature
        if "temp_mean_egg" not in df.columns and "temp_mean" in df.columns:
            df["temp_mean_egg"] = df["temp_mean"]

        # Filter valid data
        df = df[df["distance_km"].notna() & df["temp_mean_egg"].notna()]
        df = df[df["distance_km"] >= 0]  # Remove invalid distances

        # Add year info
        df["year"] = year
        df["year_type"] = self._classify_year(year)

        return df

    def _haversine_distance(self, lon1, lat1, lon2, lat2):
        """Calculate great-circle distance in km."""
        R = 6371.0  # Earth radius in km

        lon1_rad = np.radians(lon1)
        lat1_rad = np.radians(lat1)
        lon2_rad = np.radians(lon2)
        lat2_rad = np.radians(lat2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return R * c

    def _classify_year(self, year: int) -> str:
        """Classify year as warm/cold/neutral."""
        if year in WARM_YEARS:
            return "warm"
        elif year in COLD_YEARS:
            return "cold"
        else:
            return "neutral"

    def load_all_years(self):
        """Load data for all years."""
        for year in YEARS:
            df = self.load_particle_data(year)
            if not df.empty:
                self.particle_data[year] = df
                print(f"Loaded {year}: {len(df)} particles")

    def calculate_correlations(self) -> pd.DataFrame:
        """
        Calculate temperature-distance correlations.

        Returns:
            DataFrame with correlation statistics
        """
        results = []

        # Overall correlation
        all_data = pd.concat(self.particle_data.values(), ignore_index=True)
        if not all_data.empty:
            r, p = stats.spearmanr(all_data["temp_mean_egg"],
                                   all_data["distance_km"])
            results.append({
                "Group": "All years",
                "N": len(all_data),
                "Spearman_r": r,
                "p_value": p
            })

        # By year type
        for year_type in ["warm", "cold", "neutral"]:
            data = all_data[all_data["year_type"] == year_type]
            if len(data) > 10:
                r, p = stats.spearmanr(data["temp_mean_egg"],
                                       data["distance_km"])
                results.append({
                    "Group": f"{year_type.capitalize()} years",
                    "N": len(data),
                    "Spearman_r": r,
                    "p_value": p
                })

        # By individual year
        for year in sorted(self.particle_data.keys()):
            data = self.particle_data[year]
            if len(data) > 10:
                r, p = stats.spearmanr(data["temp_mean_egg"],
                                       data["distance_km"])
                results.append({
                    "Group": str(year),
                    "N": len(data),
                    "Spearman_r": r,
                    "p_value": p
                })

        return pd.DataFrame(results)

    def fit_regression_models(self, data: pd.DataFrame) -> dict:
        """
        Fit various regression models to temperature-distance data.

        Parameters:
            data: DataFrame with temp_mean_egg and distance_km columns

        Returns:
            Dictionary of fitted models and parameters
        """
        x = data["temp_mean_egg"].values
        y = data["distance_km"].values

        models = {}

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        models["linear"] = {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "predict": lambda t: slope * t + intercept
        }

        # Polynomial regression (quadratic)
        poly_coef = np.polyfit(x, y, 2)
        poly_func = np.poly1d(poly_coef)
        y_pred = poly_func(x)
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)
        models["quadratic"] = {
            "coefficients": poly_coef,
            "r_squared": r_squared,
            "predict": poly_func
        }

        # Exponential model: y = a * exp(b * x)
        try:
            def exp_func(x, a, b):
                return a * np.exp(b * x)

            popt, pcov = curve_fit(exp_func, x, y, p0=[100, 0.01], maxfev=5000)
            y_pred = exp_func(x, *popt)
            ss_res = np.sum((y - y_pred)**2)
            ss_tot = np.sum((y - np.mean(y))**2)
            r_squared = 1 - (ss_res / ss_tot)

            models["exponential"] = {
                "a": popt[0],
                "b": popt[1],
                "r_squared": r_squared,
                "predict": lambda t: exp_func(t, *popt)
            }
        except:
            models["exponential"] = None

        return models

    def plot_temperature_distance_relationship(self, output_path: Path = None):
        """
        Create comprehensive temperature-distance relationship figure.

        Parameters:
            output_path: Path to save figure
        """
        # Load all data if not already loaded
        if not self.particle_data:
            self.load_all_years()

        # Combine all data
        all_data = pd.concat(self.particle_data.values(), ignore_index=True)

        # Create figure with multiple panels
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(2, 2, hspace=0.3, wspace=0.25)

        # Panel A: Overall relationship
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_scatter(ax1, all_data, "All years (2014-2022)")

        # Panel B: Warm years
        ax2 = fig.add_subplot(gs[0, 1])
        warm_data = all_data[all_data["year_type"] == "warm"]
        self._plot_scatter(ax2, warm_data, "Warm years", COLOR_WARM)

        # Panel C: Cold years
        ax3 = fig.add_subplot(gs[1, 0])
        cold_data = all_data[all_data["year_type"] == "cold"]
        self._plot_scatter(ax3, cold_data, "Cold years", COLOR_COLD)

        # Panel D: Comparison
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_comparison(ax4, all_data)

        plt.suptitle("Temperature-dispersal distance relationships",
                    fontsize=14, fontweight='bold')

        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {output_path}")

        return fig

    def _plot_scatter(self, ax, data, title, color="#4169E1", alpha=0.3):
        """Plot scatter with regression line."""
        if data.empty:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes,
                   ha='center', va='center')
            ax.set_title(title)
            return

        x = data["temp_mean_egg"]
        y = data["distance_km"]

        # Scatter plot
        ax.scatter(x, y, alpha=alpha, s=1, color=color, rasterized=True)

        # Fit and plot regression line
        models = self.fit_regression_models(data)

        # Plot linear regression
        x_range = np.linspace(x.min(), x.max(), 100)
        y_pred = models["linear"]["predict"](x_range)
        ax.plot(x_range, y_pred, 'r-', linewidth=2,
               label=f'Linear (R²={models["linear"]["r_squared"]:.3f})')

        # Add statistics
        r, p = stats.spearmanr(x, y)
        ax.text(0.05, 0.95, f'n = {len(data):,}\nr = {r:.3f}\np = {p:.3e}',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax.set_xlabel('Egg-stage temperature (°C)')
        ax.set_ylabel('Dispersal distance (km)')
        ax.set_title(title, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

    def _plot_comparison(self, ax, all_data):
        """Plot comparison of warm vs cold years."""
        warm_data = all_data[all_data["year_type"] == "warm"]
        cold_data = all_data[all_data["year_type"] == "cold"]
        neutral_data = all_data[all_data["year_type"] == "neutral"]

        # Calculate mean distances by temperature bins
        temp_bins = np.arange(20, 31, 0.5)

        for data, color, label in [(warm_data, COLOR_WARM, "Warm years"),
                                   (cold_data, COLOR_COLD, "Cold years"),
                                   (neutral_data, COLOR_NEUTRAL, "Neutral years")]:
            if not data.empty:
                means = []
                stds = []
                for i in range(len(temp_bins) - 1):
                    mask = (data["temp_mean_egg"] >= temp_bins[i]) & \
                           (data["temp_mean_egg"] < temp_bins[i+1])
                    bin_data = data[mask]["distance_km"]
                    if len(bin_data) > 10:
                        means.append(bin_data.mean())
                        stds.append(bin_data.std() / np.sqrt(len(bin_data)))
                    else:
                        means.append(np.nan)
                        stds.append(np.nan)

                bin_centers = (temp_bins[:-1] + temp_bins[1:]) / 2
                valid = ~np.isnan(means)

                ax.errorbar(bin_centers[valid], np.array(means)[valid],
                          yerr=np.array(stds)[valid],
                          marker='o', label=label, color=color,
                          linewidth=2, markersize=6, capsize=3)

        ax.set_xlabel('Egg-stage temperature (°C)')
        ax.set_ylabel('Mean dispersal distance (km)')
        ax.set_title('Temperature regime comparison', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

    def generate_statistics_table(self, output_path: Path = None):
        """
        Generate statistical summary table.

        Parameters:
            output_path: Path to save CSV file
        """
        # Calculate correlations
        corr_df = self.calculate_correlations()

        # Add significance markers
        corr_df["Significance"] = corr_df["p_value"].apply(
            lambda p: "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        )

        if output_path:
            corr_df.to_csv(output_path, index=False)
            print(f"Statistics saved to {output_path}")

        return corr_df


def main():
    """Main analysis workflow."""
    # Set up paths
    data_dir = Path("./data")  # Update with actual path
    output_dir = Path("./figures")
    output_dir.mkdir(exist_ok=True)

    # Initialize analyzer
    analyzer = DispersalAnalyzer(data_dir)

    # Load all data
    print("Loading particle data...")
    analyzer.load_all_years()

    # Generate main figure
    print("Generating temperature-distance figure...")
    fig = analyzer.plot_temperature_distance_relationship(
        output_dir / "temperature_dispersal_distance.png"
    )

    # Generate statistics
    print("Calculating statistics...")
    stats_df = analyzer.generate_statistics_table(
        output_dir / "dispersal_statistics.csv"
    )

    print("\nCorrelation summary:")
    print(stats_df.to_string(index=False))

    # Summary statistics
    all_data = pd.concat(analyzer.particle_data.values(), ignore_index=True)
    print(f"\nTotal particles analyzed: {len(all_data):,}")
    print(f"Mean dispersal distance: {all_data['distance_km'].mean():.2f} ± "
          f"{all_data['distance_km'].std():.2f} km")
    print(f"Temperature range: {all_data['temp_mean_egg'].min():.1f} - "
          f"{all_data['temp_mean_egg'].max():.1f}°C")


if __name__ == "__main__":
    main()