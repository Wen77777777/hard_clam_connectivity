#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract particle tracking data from NetCDF output files
Processes OpenDrift output to generate per-particle summaries

This script:
1. Reads NetCDF trajectory files from OpenDrift
2. Extracts particle trajectories and environmental data
3. Calculates biological and thermal metrics
4. Generates CSV summaries for further analysis
"""

import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# ----------------- Configuration -----------------
# MPA zone definitions
MPA_ZONES = {
    "MNR-7": {"lat": [38.8, 39.1], "lon": [118.0, 118.3]},
    "MNR-8-N": {"lat": [39.2, 39.5], "lon": [119.0, 119.3]},
    "MNR-8-S": {"lat": [38.9, 39.2], "lon": [119.0, 119.3]},
    "SMPA-2": {"lat": [38.5, 38.8], "lon": [120.0, 120.3]},
    "SMPA-4": {"lat": [38.2, 38.5], "lon": [120.5, 120.8]}
}

# Temperature thresholds (based on literature)
TOPT_LOW_EGG = 25.0    # Egg optimal lower bound
TOPT_HIGH_EGG = 27.0   # Egg optimal upper bound
TOPT_LOW_LARVA = 27.0  # Larva optimal lower bound
TOPT_HIGH_LARVA = 29.0 # Larva optimal upper bound
T_SUBLETHAL = 30.0     # Sublethal threshold
T_LETHAL = 33.0        # Lethal threshold

# Development thresholds
T0_EGG = 12.9          # Egg development threshold (°C)
T0_LARVA = 19.0        # Larval development threshold (°C)


class ParticleDataExtractor:
    """Extract and process particle tracking data from NetCDF files."""

    def __init__(self, nc_path: Path):
        """
        Initialize extractor with NetCDF file.

        Parameters:
            nc_path: Path to NetCDF trajectory file
        """
        self.nc_path = nc_path
        self.ds = None
        self.particle_df = None

    def load_netcdf(self):
        """Load NetCDF dataset."""
        self.ds = xr.open_dataset(self.nc_path)
        print(f"Loaded {self.nc_path.name}")
        print(f"  Particles: {self.ds.dims['trajectory']}")
        print(f"  Time steps: {self.ds.dims['time']}")

    def extract_trajectories(self) -> pd.DataFrame:
        """
        Extract particle trajectories and properties.

        Returns:
            DataFrame with particle data
        """
        # Get dimensions
        n_particles = self.ds.dims['trajectory']
        n_times = self.ds.dims['time']

        # Initialize lists to store particle data
        particle_data = []

        # Process each particle
        for i in range(n_particles):
            # Get trajectory data
            lon = self.ds['lon'].values[i, :]
            lat = self.ds['lat'].values[i, :]
            z = self.ds['z'].values[i, :] if 'z' in self.ds else np.zeros(n_times)
            status = self.ds['status'].values[i, :]

            # Get biological variables
            stage = self.ds['stage'].values[i, :] if 'stage' in self.ds else None
            age_h = self.ds['age_h'].values[i, :] if 'age_h' in self.ds else None
            progress = self.ds['progress'].values[i, :] if 'progress' in self.ds else None

            # Get temperature data
            temp = self.ds['sea_water_temperature'].values[i, :] if \
                   'sea_water_temperature' in self.ds else None

            # Get release info
            release_id = self.ds['release_id'].values[i] if 'release_id' in self.ds else i
            release_day = self.ds['release_day'].values[i] if 'release_day' in self.ds else 0

            # Find key events
            release_idx = 0
            settle_idx = self._find_settlement(status)
            hatch_idx = self._find_hatching(stage) if stage is not None else None

            # Calculate metrics
            particle_dict = {
                'particle_id': i,
                'release_id': release_id,
                'release_day': release_day,
                'release_lon': lon[release_idx],
                'release_lat': lat[release_idx],
                'release_zone': self._identify_zone(lon[release_idx], lat[release_idx])
            }

            # Settlement info
            if settle_idx is not None:
                particle_dict.update({
                    'settled': True,
                    'settle_time_h': settle_idx,  # Convert to hours based on output frequency
                    'settle_lon': lon[settle_idx],
                    'settle_lat': lat[settle_idx],
                    'settle_zone': self._identify_zone(lon[settle_idx], lat[settle_idx]),
                    'distance_km': self._haversine_distance(
                        lon[release_idx], lat[release_idx],
                        lon[settle_idx], lat[settle_idx]
                    )
                })
            else:
                particle_dict.update({
                    'settled': False,
                    'settle_time_h': np.nan,
                    'settle_lon': np.nan,
                    'settle_lat': np.nan,
                    'settle_zone': 'UNSETTLED',
                    'distance_km': np.nan
                })

            # Temperature metrics
            if temp is not None:
                particle_dict.update(self._calculate_temperature_metrics(
                    temp, stage, settle_idx
                ))

            # Development metrics
            if stage is not None and progress is not None:
                particle_dict.update(self._calculate_development_metrics(
                    stage, progress, age_h, settle_idx
                ))

            particle_data.append(particle_dict)

        return pd.DataFrame(particle_data)

    def _find_settlement(self, status: np.ndarray) -> int:
        """Find index where particle settled."""
        # Status codes: 0=active, 2=stranded/settled, 3=deactivated
        settled_mask = (status == 2) | (status == 3)
        if np.any(settled_mask):
            return np.argmax(settled_mask)
        return None

    def _find_hatching(self, stage: np.ndarray) -> int:
        """Find index where particle hatched (stage 0->1)."""
        if stage is None:
            return None
        hatch_mask = stage == 1
        if np.any(hatch_mask):
            return np.argmax(hatch_mask)
        return None

    def _identify_zone(self, lon: float, lat: float) -> str:
        """Identify which MPA zone a point belongs to."""
        for zone_name, bounds in MPA_ZONES.items():
            if (bounds['lat'][0] <= lat <= bounds['lat'][1] and
                bounds['lon'][0] <= lon <= bounds['lon'][1]):
                return zone_name
        return 'OUTSIDE'

    def _haversine_distance(self, lon1, lat1, lon2, lat2):
        """Calculate great-circle distance in km."""
        R = 6371.0
        lon1_rad = np.radians(lon1)
        lat1_rad = np.radians(lat1)
        lon2_rad = np.radians(lon2)
        lat2_rad = np.radians(lat2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return R * c

    def _calculate_temperature_metrics(self, temp: np.ndarray,
                                      stage: np.ndarray = None,
                                      settle_idx: int = None) -> dict:
        """
        Calculate temperature exposure metrics.

        Returns:
            Dictionary with temperature statistics
        """
        metrics = {}

        # Define valid period (until settlement or end)
        end_idx = settle_idx if settle_idx is not None else len(temp)
        valid_temp = temp[:end_idx]

        # Overall statistics
        metrics['temp_mean'] = np.nanmean(valid_temp)
        metrics['temp_std'] = np.nanstd(valid_temp)
        metrics['temp_min'] = np.nanmin(valid_temp)
        metrics['temp_max'] = np.nanmax(valid_temp)

        # Stage-specific statistics
        if stage is not None:
            # Egg stage
            egg_mask = stage[:end_idx] == 0
            if np.any(egg_mask):
                egg_temp = valid_temp[egg_mask]
                metrics['temp_mean_egg'] = np.nanmean(egg_temp)
                metrics['temp_std_egg'] = np.nanstd(egg_temp)

                # Optimal temperature exposure (egg)
                opt_egg = np.sum((egg_temp >= TOPT_LOW_EGG) &
                                (egg_temp <= TOPT_HIGH_EGG))
                metrics['frac_egg_hours_optimal'] = opt_egg / len(egg_temp)

                # High temperature exposure (egg)
                hot_egg = np.sum(egg_temp >= T_SUBLETHAL)
                metrics['frac_egg_hours_hot'] = hot_egg / len(egg_temp)

                # Degree-day deviations (egg)
                metrics['hot_deg_h_egg'] = np.sum(np.maximum(0, egg_temp - TOPT_HIGH_EGG))
                metrics['cold_deg_h_egg'] = np.sum(np.maximum(0, TOPT_LOW_EGG - egg_temp))

            # Larval stage
            larva_mask = stage[:end_idx] == 1
            if np.any(larva_mask):
                larva_temp = valid_temp[larva_mask]
                metrics['temp_mean_larva'] = np.nanmean(larva_temp)
                metrics['temp_std_larva'] = np.nanstd(larva_temp)

                # Optimal temperature exposure (larva)
                opt_larva = np.sum((larva_temp >= TOPT_LOW_LARVA) &
                                  (larva_temp <= TOPT_HIGH_LARVA))
                metrics['frac_larva_hours_optimal'] = opt_larva / len(larva_temp)

                # High temperature exposure (larva)
                hot_larva = np.sum(larva_temp >= T_SUBLETHAL)
                metrics['frac_larva_hours_hot'] = hot_larva / len(larva_temp)

                # Degree-day deviations (larva)
                metrics['hot_deg_h_larva'] = np.sum(np.maximum(0, larva_temp - TOPT_HIGH_LARVA))
                metrics['cold_deg_h_larva'] = np.sum(np.maximum(0, TOPT_LOW_LARVA - larva_temp))

        # Extreme temperature events
        metrics['hours_above_30'] = np.sum(valid_temp >= T_SUBLETHAL)
        metrics['hours_above_33'] = np.sum(valid_temp >= T_LETHAL)

        # Consecutive high temperature
        above_30 = valid_temp >= T_SUBLETHAL
        metrics['max_consecutive_hot'] = self._max_consecutive_true(above_30)

        return metrics

    def _calculate_development_metrics(self, stage: np.ndarray,
                                      progress: np.ndarray,
                                      age_h: np.ndarray = None,
                                      settle_idx: int = None) -> dict:
        """
        Calculate development metrics.

        Returns:
            Dictionary with development statistics
        """
        metrics = {}

        end_idx = settle_idx if settle_idx is not None else len(stage)

        # Egg duration
        egg_mask = stage[:end_idx] == 0
        if np.any(egg_mask):
            metrics['egg_duration_h'] = np.sum(egg_mask)
        else:
            metrics['egg_duration_h'] = 0

        # Larval duration
        larva_mask = stage[:end_idx] == 1
        if np.any(larva_mask):
            metrics['larva_duration_h'] = np.sum(larva_mask)
        else:
            metrics['larva_duration_h'] = 0

        # Total pelagic larval duration
        metrics['pld_h'] = metrics['egg_duration_h'] + metrics['larva_duration_h']

        # Development progress at settlement
        if settle_idx is not None:
            metrics['progress_at_settlement'] = progress[settle_idx]
        else:
            metrics['progress_at_settlement'] = progress[-1]

        # Age if available
        if age_h is not None:
            metrics['age_at_settlement_h'] = age_h[settle_idx] if settle_idx else age_h[-1]

        return metrics

    def _max_consecutive_true(self, arr: np.ndarray) -> int:
        """Find maximum consecutive True values."""
        if not np.any(arr):
            return 0

        max_count = 0
        current_count = 0

        for val in arr:
            if val:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0

        return max_count

    def generate_connectivity_matrix(self, particle_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate connectivity matrix from particle data.

        Parameters:
            particle_df: DataFrame with particle data

        Returns:
            Connectivity matrix as DataFrame
        """
        # Filter settled particles
        settled = particle_df[particle_df['settled']].copy()

        # Create connectivity matrix
        zones = list(MPA_ZONES.keys()) + ['OUTSIDE']
        matrix = pd.DataFrame(0, index=zones, columns=zones)

        # Count connections
        for _, particle in settled.iterrows():
            source = particle['release_zone']
            dest = particle['settle_zone']
            if source in matrix.index and dest in matrix.columns:
                matrix.loc[source, dest] += 1

        # Add unsettled column
        unsettled = particle_df[~particle_df['settled']]
        for _, particle in unsettled.iterrows():
            source = particle['release_zone']
            if source in matrix.index:
                if 'UNSETTLED' not in matrix.columns:
                    matrix['UNSETTLED'] = 0
                matrix.loc[source, 'UNSETTLED'] += 1

        return matrix

    def save_results(self, output_dir: Path):
        """
        Save extracted data to CSV files.

        Parameters:
            output_dir: Directory to save outputs
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save particle data
        if self.particle_df is not None:
            particle_file = output_dir / "per_particle_summary.csv"
            self.particle_df.to_csv(particle_file, index=False)
            print(f"Saved particle data to {particle_file}")

            # Save connectivity matrix
            conn_matrix = self.generate_connectivity_matrix(self.particle_df)
            conn_file = output_dir / "connectivity_matrix.csv"
            conn_matrix.to_csv(conn_file)
            print(f"Saved connectivity matrix to {conn_file}")

            # Save normalized connectivity matrix
            conn_norm = conn_matrix.div(conn_matrix.sum(axis=1), axis=0)
            conn_norm_file = output_dir / "connectivity_matrix_normalized.csv"
            conn_norm.to_csv(conn_norm_file)
            print(f"Saved normalized connectivity to {conn_norm_file}")

            # Summary statistics
            self._save_summary_statistics(output_dir)

    def _save_summary_statistics(self, output_dir: Path):
        """Save summary statistics."""
        stats = {
            'total_particles': len(self.particle_df),
            'settled_particles': self.particle_df['settled'].sum(),
            'settlement_rate': self.particle_df['settled'].mean(),
            'mean_distance_km': self.particle_df['distance_km'].mean(),
            'std_distance_km': self.particle_df['distance_km'].std(),
            'mean_pld_h': self.particle_df['pld_h'].mean(),
            'std_pld_h': self.particle_df['pld_h'].std()
        }

        # Temperature statistics
        if 'temp_mean_egg' in self.particle_df.columns:
            stats.update({
                'mean_egg_temp': self.particle_df['temp_mean_egg'].mean(),
                'std_egg_temp': self.particle_df['temp_mean_egg'].std()
            })

        stats_df = pd.DataFrame([stats])
        stats_file = output_dir / "summary_statistics.csv"
        stats_df.to_csv(stats_file, index=False)
        print(f"Saved summary statistics to {stats_file}")


def main():
    """Main processing workflow."""
    # Example usage
    nc_file = Path("tracks_v3_2017_20170901_20170930.nc")  # Update with actual file
    output_dir = Path("./analysis_outputs")

    if not nc_file.exists():
        print(f"Error: NetCDF file not found: {nc_file}")
        return

    # Initialize extractor
    extractor = ParticleDataExtractor(nc_file)

    # Load and process data
    print("Loading NetCDF file...")
    extractor.load_netcdf()

    print("Extracting particle trajectories...")
    extractor.particle_df = extractor.extract_trajectories()

    print(f"Processed {len(extractor.particle_df)} particles")

    # Save results
    print("Saving results...")
    extractor.save_results(output_dir)

    # Print summary
    settled = extractor.particle_df['settled'].sum()
    total = len(extractor.particle_df)
    print(f"\nSummary:")
    print(f"  Total particles: {total}")
    print(f"  Settled: {settled} ({100*settled/total:.1f}%)")
    print(f"  Mean distance: {extractor.particle_df['distance_km'].mean():.1f} km")


if __name__ == "__main__":
    main()