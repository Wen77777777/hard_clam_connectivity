# Data Documentation

## Overview

This directory contains processed data and instructions for obtaining the full datasets used in our Hard clam connectivity analysis.

## Data Structure

### Required Data Types

1. **Ocean Model Output (ROMS)**
   - Format: NetCDF (.nc files)
   - Variables: Temperature, salinity, currents (u, v, w), sea surface height
   - Temporal resolution: Hourly
   - Spatial resolution: ~2 km horizontal, 20 vertical layers
   - Coverage: Bohai Sea (117°E-122°E, 37°N-41°N)

2. **Particle Tracking Results**
   - Format: NetCDF or CSV
   - Variables: Particle positions, temperature exposure, development stage
   - Time period: September of each year (2014-2022)

3. **MPA Boundaries**
   - Format: Shapefile (.shp)
   - Content: Polygon boundaries for 5 MPAs in Bohai Sea

## Data Availability

### Included in Repository

Due to GitHub size limitations, we provide:
- Processed connectivity matrices (CSV format)
- Summary statistics
- Example datasets for testing

### Full Dataset Access

The complete datasets are available through:

1. **Zenodo Archive**: [DOI will be added upon publication]
   - Complete ROMS output for 2014-2022
   - Full particle tracking results
   - Raw temperature data

2. **Direct Request**:
   - Contact: [corresponding.author@email.com]
   - Please include: Institution, intended use, publication plans

## File Formats

### Connectivity Matrices (`connectivity_matrix_*.csv`)

```csv
Origin,MNR-7,MNR-8-N,MNR-8-S,SMPA-2,SMPA-4,OUTSIDE,UNSETTLED
MNR-7,0.17,0.00,0.00,0.00,0.00,0.78,0.05
MNR-8-N,0.00,0.52,0.08,0.01,0.00,0.35,0.04
...
```

- **Rows**: Source MPAs
- **Columns**: Destination MPAs + outside areas
- **Values**: Proportion of particles (0-1)

### Particle Data (`particle_data_*.csv`)

```csv
particle_id,release_mpa,release_day,settle_mpa,distance_km,egg_temp,larva_temp,pld_hours
1,MNR-7,20170901,MNR-7,15.3,26.5,28.2,456
2,MNR-7,20170901,OUTSIDE,125.7,26.5,27.8,512
...
```

- **particle_id**: Unique identifier
- **release_mpa**: Source MPA
- **release_day**: Release date (YYYYMMDD)
- **settle_mpa**: Destination (MPA name or OUTSIDE/UNSETTLED)
- **distance_km**: Dispersal distance
- **egg_temp**: Mean temperature during egg stage
- **larva_temp**: Mean temperature during larval stage
- **pld_hours**: Pelagic larval duration

### Temperature Data (`temperature_*.csv`)

```csv
year,month,day,mpa,surface_temp,bottom_temp,mean_temp
2017,9,1,MNR-7,26.8,25.2,26.0
2017,9,1,MNR-8-N,27.1,25.5,26.3
...
```

## Data Processing Pipeline

1. **Raw ROMS Output** → NetCDF files
2. **Particle Tracking** → OpenDrift output
3. **Connectivity Analysis** → Connectivity matrices
4. **Statistical Summary** → Final datasets

## Quality Control

All data underwent quality control:
- Temperature range: 0-35°C
- Particle positions: Within model domain
- Mass balance: >95% particles accounted for
- Temporal continuity: No gaps in time series

## Usage Examples

### Loading Connectivity Matrix

```python
import pandas as pd

# Load normalized connectivity matrix
conn = pd.read_csv('data/processed/connectivity_matrix_2017.csv', index_col=0)
print(f"Connectivity shape: {conn.shape}")
print(f"Self-recruitment MNR-7: {conn.loc['MNR-7', 'MNR-7']:.2%}")
```

### Loading Particle Data

```python
# Load particle-level data
particles = pd.read_csv('data/processed/particle_data_2017.csv')

# Calculate mean dispersal distance
mean_dist = particles.groupby('release_mpa')['distance_km'].mean()
print(f"Mean dispersal distances:\n{mean_dist}")
```

### Temperature Analysis

```python
# Load temperature data
temp = pd.read_csv('data/processed/temperature_2017.csv')

# Calculate monthly means
monthly = temp.groupby(['year', 'month', 'mpa'])['mean_temp'].mean()
print(f"September temperatures:\n{monthly}")
```

## Data Citation

When using these datasets, please cite:

```
[Authors] (2024). Temperature-driven connectivity dynamics dataset for Hard clam
in the Bohai Sea (2014-2022). Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

## Metadata Standards

All datasets follow CF (Climate and Forecast) conventions where applicable:
- Time: Days since 1970-01-01
- Coordinates: WGS84 (EPSG:4326)
- Units: SI units (temperature in °C, distance in km)

## Contact

For questions about the data:
- Email: [data.contact@email.com]
- GitHub Issues: [repository issues page]