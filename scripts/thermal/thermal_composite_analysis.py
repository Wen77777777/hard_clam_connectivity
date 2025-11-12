#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thermal composite analysis for Hard clam egg stage
Temperature-driven connectivity analysis - Figure 1 (Results)

Analyzes temperature conditions during the critical egg development stage
Uses literature-validated 25-27°C optimal range (Kim et al., 2011)

Three-panel layout:
- Panel A: Hot-cold degree-days (thermal deviation)
- Panel B: Interannual temperature variation (time series)
- Panel C: High-temperature exposure patterns

FOCUS: EGG STAGE TEMPERATURE ANALYSIS
- Analyzes temperature during critical egg development
- 30°C threshold represents sublethal stress (development success drops)
- Scientifically justified approach with literature validation
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec
from scipy import stats

# ----------------- Configuration -----------------
YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]

# Thermal settings (EGG STAGE)
TOPT_LOW = 25.0       # Egg stage optimal lower bound (Kim et al., 2011)
TOPT_HIGH = 27.0      # Egg stage optimal upper bound (80.3% success at 27°C)
HTHRESH = 30.0        # Sublethal threshold (success drops to 58.2% at 30°C)
RUN_MIN = 6           # Minimum hours for continuity analysis
BLOCK_LENGTH = 5      # Days for block bootstrap
N_BOOTSTRAP = 2000

# Publication-quality color scheme
COLOR_COLD = "#3B4CC0"     # Deep blue
COLOR_WARM = "#B40426"     # Deep red
COLOR_NEUTRAL = "#888888"  # Gray
COLOR_OPT_BAND = "#90EE90" # Light green for optimal range

# Set publication-level plot parameters
plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
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


class ThermalAnalyzer:
    """Analyze thermal conditions during egg development stage."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.years = YEARS

    def load_particle_data(self, year: int) -> pd.DataFrame:
        """Load per-particle summary data for a specific year."""
        file_path = (self.data_dir / f"output_dir_{year}" /
                    "analysis_outputs_v10" / "per_particle_summary_rel_v10.csv")

        if not file_path.exists():
            raise FileNotFoundError(f"Particle data not found: {file_path}")

        df = pd.read_csv(file_path, encoding="utf-8-sig", low_memory=False)

        # Process release day
        if "release_day" in df.columns:
            df["release_day"] = pd.to_numeric(df["release_day"],
                                             errors="coerce").astype("Int64")
        elif "release_date" in df.columns:
            df["release_day"] = pd.to_datetime(df["release_date"],
                                               errors="coerce").dt.dayofyear

        return df

    def block_bootstrap_mean(self, day_values: np.ndarray,
                            block_len: int = BLOCK_LENGTH,
                            n_boot: int = N_BOOTSTRAP) -> tuple:
        """
        Calculate block-bootstrap mean and 95% confidence interval.

        Parameters:
            day_values: Daily time series values
            block_len: Length of blocks for resampling
            n_boot: Number of bootstrap iterations

        Returns:
            Tuple of (mean, confidence_interval_low, confidence_interval_high)
        """
        x = np.asarray(day_values, dtype=float)
        x = x[np.isfinite(x)]
        n = x.size

        if n == 0:
            return np.nan, np.nan, np.nan

        rng = np.random.default_rng(42)
        means = []

        for _ in range(n_boot):
            idx = []
            while len(idx) < n:
                start = rng.integers(0, n)
                blk = [(start + k) % n for k in range(block_len)]
                idx.extend(blk)
            idx = np.array(idx[:n], dtype=int)
            means.append(np.nanmean(x[idx]))

        means = np.asarray(means)
        m = float(np.nanmean(means))
        lo, hi = np.nanpercentile(means, [2.5, 97.5])

        return m, float(lo), float(hi)

    def calculate_hot_degree_days(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate hot degree-days (temperature excess above optimal).

        Hot degree-days = mean(max(0, T - T_opt_high)) per day
        """
        temp_col = self._find_column(df, "temp_mean_egg", ["temp_mean_larva"])

        if temp_col:
            def calc_hot(temps):
                return np.clip(temps - TOPT_HIGH, 0, None).mean()
            return df.groupby("release_day")[temp_col].apply(calc_hot)

        return pd.Series(dtype=float)

    def calculate_cold_degree_days(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate cold degree-days (temperature deficit below optimal).

        Cold degree-days = mean(max(0, T_opt_low - T)) per day
        """
        temp_col = self._find_column(df, "temp_mean_egg", ["temp_mean_larva"])

        if temp_col:
            def calc_cold(temps):
                return np.clip(TOPT_LOW - temps, 0, None).mean()
            return df.groupby("release_day")[temp_col].apply(calc_cold)

        return pd.Series(dtype=float)

    def calculate_heat_exposure(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate fraction of time experiencing high temperature (>=30°C).
        """
        col = self._find_column(df, "frac_egg_hours_hot", ["frac_larva_hours_hot"])

        if col:
            return df.groupby("release_day")[col].mean()

        # Fallback calculation
        temp_col = self._find_column(df, "temp_mean_egg", ["temp_mean_larva"])
        if temp_col:
            def calc_frac(temps):
                return (temps >= HTHRESH).mean()
            return df.groupby("release_day")[temp_col].apply(calc_frac)

        return pd.Series(dtype=float)

    def classify_temperature_regime(self, year: int,
                                    egg_temps: dict) -> str:
        """
        Classify year as warm/cold/neutral based on egg temperature.

        Parameters:
            year: Year to classify
            egg_temps: Dictionary of {year: mean_egg_temperature}

        Returns:
            'warm', 'cold', or 'neutral'
        """
        all_temps = list(egg_temps.values())
        p25 = np.percentile(all_temps, 25)
        p75 = np.percentile(all_temps, 75)

        temp = egg_temps.get(year, np.nan)

        if temp > p75:
            return 'warm'
        elif temp < p25:
            return 'cold'
        else:
            return 'neutral'

    def _find_column(self, df: pd.DataFrame,
                    prefer: str, fallback: list = None) -> str:
        """Find column in dataframe with preference order."""
        for c in ([prefer] + (fallback or [])):
            if c in df.columns:
                return c
        return None

    def generate_composite_figure(self, output_path: Path = None):
        """
        Generate three-panel thermal composite figure.

        Panel A: Hot-cold degree-days
        Panel B: Interannual temperature variation
        Panel C: High-temperature exposure patterns
        """
        # Load data for all years
        year_data = {}
        for year in self.years:
            try:
                df = self.load_particle_data(year)
                year_data[year] = df
            except FileNotFoundError:
                print(f"Warning: No data for {year}")
                continue

        # Calculate metrics for each year
        metrics = {}
        for year, df in year_data.items():
            metrics[year] = {
                'hot_dd': self.calculate_hot_degree_days(df),
                'cold_dd': self.calculate_cold_degree_days(df),
                'heat_exp': self.calculate_heat_exposure(df),
                'mean_temp': df.groupby("release_day")["temp_mean_egg"].mean()
                            if "temp_mean_egg" in df.columns else None
            }

        # Create figure
        fig = plt.figure(figsize=(14, 12))
        gs = gridspec.GridSpec(3, 1, hspace=0.3)

        # Panel A: Degree-days
        ax1 = fig.add_subplot(gs[0])
        self._plot_degree_days(ax1, metrics)
        ax1.set_title("(A) Thermal deviation from optimal range",
                     fontweight='bold', loc='left')

        # Panel B: Temperature time series
        ax2 = fig.add_subplot(gs[1])
        self._plot_temperature_series(ax2, metrics)
        ax2.set_title("(B) Interannual temperature variation",
                     fontweight='bold', loc='left')

        # Panel C: Heat exposure
        ax3 = fig.add_subplot(gs[2])
        self._plot_heat_exposure(ax3, metrics)
        ax3.set_title("(C) High-temperature exposure patterns",
                     fontweight='bold', loc='left')

        plt.suptitle("Temperature conditions during egg development stage",
                    fontsize=14, fontweight='bold', y=0.98)

        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {output_path}")

        return fig

    def _plot_degree_days(self, ax, metrics):
        """Plot hot and cold degree-days comparison."""
        years = sorted(metrics.keys())

        hot_means = []
        cold_means = []

        for year in years:
            hot_dd = metrics[year]['hot_dd']
            cold_dd = metrics[year]['cold_dd']

            hot_mean, _, _ = self.block_bootstrap_mean(hot_dd.values)
            cold_mean, _, _ = self.block_bootstrap_mean(cold_dd.values)

            hot_means.append(hot_mean)
            cold_means.append(cold_mean)

        x = np.arange(len(years))
        width = 0.35

        ax.bar(x - width/2, hot_means, width, label='Above optimal',
               color=COLOR_WARM, alpha=0.7)
        ax.bar(x + width/2, [-c for c in cold_means], width,
               label='Below optimal', color=COLOR_COLD, alpha=0.7)

        ax.set_xlabel('Year')
        ax.set_ylabel('Degree-days (°C·day)')
        ax.set_xticks(x)
        ax.set_xticklabels(years, rotation=45)
        ax.legend()
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    def _plot_temperature_series(self, ax, metrics):
        """Plot temperature time series for all years."""
        for year in sorted(metrics.keys()):
            if metrics[year]['mean_temp'] is not None:
                temp_series = metrics[year]['mean_temp']
                ax.plot(temp_series.index, temp_series.values,
                       label=str(year), alpha=0.7)

        # Add optimal range band
        ax.axhspan(TOPT_LOW, TOPT_HIGH, alpha=0.2, color=COLOR_OPT_BAND,
                  label=f'Optimal range ({TOPT_LOW}-{TOPT_HIGH}°C)')
        ax.axhline(y=HTHRESH, color=COLOR_WARM, linestyle='--',
                  linewidth=1, label=f'Sublethal threshold ({HTHRESH}°C)')

        ax.set_xlabel('Day of year')
        ax.set_ylabel('Temperature (°C)')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)

    def _plot_heat_exposure(self, ax, metrics):
        """Plot high-temperature exposure patterns."""
        years = sorted(metrics.keys())

        exposure_means = []
        exposure_ci = []

        for year in years:
            heat_exp = metrics[year]['heat_exp']
            mean, lo, hi = self.block_bootstrap_mean(heat_exp.values)
            exposure_means.append(mean * 100)  # Convert to percentage
            exposure_ci.append((mean - lo) * 100, (hi - mean) * 100)

        x = np.arange(len(years))
        colors = [COLOR_WARM if m > 10 else COLOR_COLD for m in exposure_means]

        ax.bar(x, exposure_means, color=colors, alpha=0.7)
        ax.errorbar(x, exposure_means,
                   yerr=np.array(exposure_ci).T,
                   fmt='none', color='black', capsize=3)

        ax.set_xlabel('Year')
        ax.set_ylabel(f'Time with T ≥ {HTHRESH}°C (%)')
        ax.set_xticks(x)
        ax.set_xticklabels(years, rotation=45)
        ax.axhline(y=10, color='gray', linestyle='--', linewidth=0.5)


if __name__ == "__main__":
    # Example usage
    data_dir = Path("./data")  # Update with actual path
    analyzer = ThermalAnalyzer(data_dir)

    # Generate composite figure
    output_file = Path("./figures/thermal_composite_egg_stage.png")
    fig = analyzer.generate_composite_figure(output_file)

    print("Thermal analysis complete.")
