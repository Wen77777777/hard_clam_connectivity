# Analysis Workflow

## Overview

This document describes the complete analysis workflow for generating the results presented in the manuscript.

## Data Processing Pipeline

```
ROMS Model Output → Particle Tracking → Connectivity Analysis → Statistical Testing → Visualization
```

## Key Analysis Scripts

### 1. Particle Tracking Model

**Script**: `scripts/model/hard_clam_drift.py`

**Purpose**: Individual-based model simulating Hard clam larval dispersal

**Key Features**:
- Two-stage development (egg → larva)
- Stage-specific temperature responses
- Accumulated temperature (degree-hours) tracking
- Sublethal and lethal temperature exposure recording

**Output**: NetCDF files with particle trajectories and biological states

---

### 2. Connectivity Matrix Calculation

**Script**: `scripts/connectivity/connectivity_analysis.py`

**Purpose**: Calculate connectivity matrices between MPAs

**Key Metrics**:
- Source strength (outgoing connectivity)
- Sink strength (incoming connectivity)
- Self-recruitment rate
- Leakage rate (particles leaving MPA network)

**Output**: CSV connectivity matrices (normalized and count-based)

---

### 3. Temperature Classification

**Script**: `scripts/thermal/thermal_composite_analysis.py`

**Purpose**: Classify years by egg-stage temperature conditions

**Classification Criteria**:
- **Warm years**: Egg temperature > 75th percentile
  - Years: 2017, 2018, 2022
- **Cold years**: Egg temperature < 25th percentile
  - Years: 2014, 2015, 2020
- **Neutral years**: Between 25th-75th percentile
  - Years: 2016, 2019, 2021

**Figures Generated**:
- Figure 1: Thermal composite (3 panels)
  - Panel A: Hot-cold degree-days
  - Panel B: Interannual temperature variation
  - Panel C: High-temperature exposure patterns

---

### 4. Connectivity Comparison

**Script**: `scripts/visualization/connectivity_plots.py`

**Purpose**: Compare connectivity patterns between temperature regimes

**Statistical Methods**:
- Block bootstrap for confidence intervals
- Permutation tests for significance
- False Discovery Rate (FDR) correction

**Figures Generated**:
- Figure 2: Connectivity matrices (warm vs cold vs difference)
  - Panel A: Warm years connectivity
  - Panel B: Cold years connectivity
  - Panel C: Connectivity difference (warm - cold)
  - Panel D: Network metrics comparison

---

### 5. Dispersal Distance Analysis

**Script**: `scripts/analysis/dispersal_distance.py`

**Purpose**: Analyze relationship between temperature and dispersal distance

**Particle-Level Analysis**:
- Uses ~1.7 million particle records
- Statistical power >> year-level aggregation
- Linear mixed-effects models

**Figures Generated**:
- Figure 3: Temperature-distance relationships
  - Scatter plots by year type
  - Regression lines with confidence bands

---

### 6. Exposure-Response Analysis

**Script**: `scripts/analysis/exposure_response.py`

**Purpose**: Quantify temperature effects on connectivity metrics

**Key Variables**:
- **Ty**: Mean egg-stage temperature (°C)
- **EAT**: Effective Accumulated Temperature
  - EAT = Hot degree-hours - Cold degree-hours
- **Connectivity metrics**: Self-recruitment, source strength, etc.

**Statistical Approaches**:
- Spearman correlation (non-parametric)
- Theil-Sen regression (robust to outliers)
- Permutation-based significance testing
- FDR correction for multiple comparisons

**Figures Generated**:
- Figure 4: Exposure-response curves (2×2 panel layout)
  - Each panel: One connectivity metric vs temperature
  - Color-coded by year type (warm/cold/neutral)
  - Regression lines with 95% CI

---

## Reproducibility Checklist

### Required Data Files

For each year (2014-2022):
```
output_dir_{year}/
├── analysis_outputs_v10/
│   ├── connectivity_matrix_v10.csv
│   ├── connectivity_matrix_normalized_v10.csv
│   ├── per_particle_summary_rel_v10.csv
│   └── thermal_metrics_{year}.csv
└── tracks_v3_{year}_YYYYMMDD_YYYYMMDD.nc
```

### Software Requirements

See `requirements.txt` for complete list. Key dependencies:
- Python >= 3.8
- NumPy, Pandas, SciPy
- Matplotlib, Seaborn
- OpenDrift >= 1.14
- statsmodels (for advanced statistics)

### Running the Complete Analysis

```bash
# 1. Classify years by temperature
python scripts/thermal/thermal_composite_analysis.py

# 2. Calculate connectivity matrices
python scripts/connectivity/connectivity_analysis.py

# 3. Generate all figures
python scripts/visualization/generate_all_figures.py

# 4. Run statistical tests
python scripts/analysis/exposure_response.py
```

---

## Figure Correspondence

| Figure | Script | Output File |
|--------|--------|-------------|
| Figure 1 | `thermal_composite_analysis.py` | `thermal_composite_egg_stage.png` |
| Figure 2 | `connectivity_analysis.py` | `connectivity_comparison.png` |
| Figure 3 | `dispersal_distance.py` | `temperature_distance_relationship.png` |
| Figure 4 | `exposure_response.py` | `exposure_response_curves.png` |

---

## Statistical Considerations

### Bootstrap Procedures

**Block Bootstrap**:
- Used for time series data (daily temperature)
- Block length: 5 days (accounts for temporal autocorrelation)
- Number of iterations: 2000
- Confidence level: 95%

**Standard Bootstrap**:
- Used for independent samples
- Number of iterations: 2000

### Multiple Testing Correction

When testing multiple hypotheses (e.g., correlations for multiple MPAs):
- **Method**: Benjamini-Hochberg FDR correction
- **α level**: 0.05
- **Adjusted p-values** reported in tables

### Robustness Checks

1. **Sensitivity to year classification**: Re-run with ±1 year shifts
2. **Subsample analysis**: Use 50% and 80% of particles
3. **Alternative metrics**: Test with different connectivity definitions
4. **Threshold sensitivity**: Vary optimal temperature bounds (±1°C)

---

## Data Quality Control

### Inclusion Criteria

Particles included in analysis must:
1. Have complete temperature history (no missing data)
2. Settle within 45 days of release
3. Have valid origin and destination assignments
4. Pass quality checks (e.g., within model domain)

### Exclusion Criteria

Particles excluded if:
1. Missing temperature data >10% of pelagic duration
2. Trajectory exits model boundaries
3. Development progress anomalies (progress < 0 or > 1.5)

### Expected Sample Sizes

- Total particles per year: ~180,000
- Settled particles per year: ~90,000-110,000
- Self-recruiting particles per year: ~15,000-25,000

---

## Troubleshooting

### Common Issues

1. **Missing data files**: Check file paths in configuration
2. **Memory errors**: Reduce bootstrap iterations or use chunked processing
3. **Plot rendering**: Ensure matplotlib backend is correctly configured
4. **Statistical warnings**: Normal for small samples; check documentation

### Performance Optimization

- Use `low_memory=False` when reading large CSVs
- Consider parallel processing for bootstrap procedures
- Cache intermediate results to avoid recomputation

---

## Contact

For questions about the analysis workflow:
- Email: [your.email@institution.edu]
- GitHub Issues: [link to repository issues]

## Version History

- v1.0 (2024): Initial release
- Scripts correspond to manuscript submitted [Date]