# Temperature-driven Connectivity Dynamics in Marine Protected Area Networks

## A Nine-Year Assessment Using Effective Accumulated Temperature Framework in the Bohai Sea

This repository contains the analysis code and visualization scripts for our research on hard clam (*Meretrix petechialis*) connectivity patterns in the Bohai Sea Marine Protected Area (MPA) network.

### Overview

This study quantifies how interannual thermal variability influences larval connectivity patterns in the Bohai Sea MPA network from 2014-2022. We developed a temperature-explicit biophysical model incorporating accumulated thermal units to assess connectivity dynamics under different thermal regimes. Our analysis reveals that in weak-current environments like the Bohai Sea, dispersal distances show reduced sensitivity to temperature-driven pelagic larval duration (PLD) changes, with important implications for MPA network design under climate change.

### Key Features

- **Individual-Based Model (IBM)** with stage-specific temperature parameters
- **Connectivity analysis** across nine years (2014-2022)
- **Temperature classification** (warm/cold/neutral years based on egg-stage temperature)
- **Network metrics** calculation (source strength, sink strength, leakage rate, self-recruitment)
- **Statistical analysis** with bootstrapping for robust confidence intervals

### Repository Structure

```
hard_clam_connectivity/
├── README.md                           # This file
├── LICENSE                             # MIT License
├── requirements.txt                    # Python dependencies
├── data/
│   └── README.md                      # Data acquisition instructions
├── scripts/
│   ├── model/                         # Core IBM implementation
│   │   └── hard_clam_drift.py      # Individual-based model
│   ├── connectivity/                  # Connectivity analysis
│   │   ├── connectivity_analysis.py  # Main connectivity analysis
│   │   └── network_metrics.py        # Network metric calculations
│   ├── thermal/                       # Temperature analysis
│   │   ├── thermal_analysis.py       # Temperature effect analysis
│   │   └── year_classification.py    # Year temperature classification
│   └── visualization/                 # Plotting scripts
│       ├── connectivity_plots.py     # Connectivity visualizations
│       └── temperature_plots.py      # Temperature response plots
├── analysis/                          # Additional analyses
│   ├── sensitivity_analysis.py       # Parameter sensitivity
│   └── robustness_check.py          # Statistical robustness tests
├── docs/                              # Documentation
│   ├── methods.md                    # Detailed methodology
│   └── parameters.md                 # Model parameters
└── figures/                           # Example output figures
    ├── connectivity_matrices.png     # Connectivity comparison
    └── temperature_response.png      # Temperature effects
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Wen77777777/hard_clam_connectivity.git
cd hard_clam_connectivity
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Data Requirements

Due to size constraints, the original ROMS ocean model output files and particle tracking results are not included in this repository.

#### Data Availability
- **ROMS model data**: Available upon request (contact corresponding author)
- **Particle tracking outputs**: Processed connectivity matrices are provided in `data/processed/`
- **Example data**: Sample datasets for testing are included in `data/examples/`

See `data/README.md` for detailed instructions on data structure and format requirements.

### Usage

#### 1. Running the Individual-Based Model

```python
from scripts.model.hard_clam_drift import HardClamDrift

# Initialize model
model = HardClamDrift()

# Set biological parameters
model.T0_egg = 12.9      # Egg development threshold (°C)
model.K_egg = 259.0      # Egg development requirement (degree-hours)
model.T0_larva = 19.0    # Larval development threshold (°C)
model.K_larva = 840.0    # Larval development requirement (degree-hours)

# Stage-specific optimal temperatures
model.Topt_low_egg = 25.0    # Egg optimal range: 25-27°C
model.Topt_high_egg = 27.0
model.Topt_low_larva = 27.0  # Larval optimal range: 27-29°C
model.Topt_high_larva = 29.0

# Run simulation (requires ROMS data)
# model.run()
```

#### 2. Analyzing Connectivity Patterns

```python
from scripts.connectivity.connectivity_analysis import ConnectivityAnalyzer
from pathlib import Path

# Initialize analyzer
analyzer = ConnectivityAnalyzer(data_dir=Path("./data"))

# Compare warm vs. cold years
comparisons = analyzer.compare_temperature_regimes()

# Generate visualization
fig = plot_connectivity_comparison(analyzer)
fig.savefig("connectivity_comparison.png")
```

#### 3. Temperature Effect Analysis

```python
from scripts.thermal.thermal_analysis import TemperatureAnalyzer

# Analyze temperature impacts on connectivity
temp_analyzer = TemperatureAnalyzer()
results = temp_analyzer.analyze_temperature_effects(year=2018)
```

### Model Parameters

#### Biological Parameters
- **Egg stage**:
  - Development threshold (T₀): 12.9°C
  - Development requirement (K): 259 degree-hours
  - Optimal temperature: 25-27°C

- **Larval stage**:
  - Development threshold (T₀): 19.0°C
  - Development requirement (K): 840 degree-hours
  - Optimal temperature: 27-29°C

- **Critical thresholds**:
  - Sublethal temperature: 30°C
  - Lethal temperature: 33°C

#### Physical Parameters
- Horizontal diffusivity: 5.0 m²/s
- Vertical advection: Enabled
- Simulation period: September (peak spawning season)
- Particle release: 10,000 particles/day per MPA

#### Temperature Variability (2014-2022)
- Annual mean egg temperature range: 25.72–26.71°C (0.99°C variation)
- Cold vs. warm year difference: 0.64°C
- Extreme exposure (≥30°C): 0.35–8.60% (25-fold variation between years)

### Key Findings

1. **Non-linear dispersal response**: Between cold and warm years (0.64°C difference), pelagic larval duration decreased by 10.2% (0.60 days), yet mean dispersal distance decreased by only 5.1% (0.56 km). This disproportionate response reflects the weak-current environment of the Bohai Sea, where low flow velocities create a baseline constraint on dispersal.

2. **Network-level connectivity shifts**: Absolute self-recruitment increased from 0.221 to 0.238, while leakage to unprotected areas decreased from 0.686 to 0.658 between cold and warm years.

3. **Heterogeneous site responses**: Individual reserves showed variable responses—the most isolated site maintained only 17% self-recruitment with <1% external MPA input, while historically sink-dominated areas gained up to 2.8 percentage points in self-recruitment under warming.

4. **Extreme temperature exposure**: Exposure to sublethal temperatures (≥30°C) varied 25-fold between years (0.35–8.60%), potentially triggering threshold mortality effects beyond mean temperature impacts.

5. **Management implications**: In marginal seas with weak circulation, spatial network optimization may provide greater conservation benefits than strategies relying on temperature-driven connectivity responses for maintaining MPA connectivity under climate change.


### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contact

- **Corresponding Author**: Binduo Xu (bdxu@ouc.edu.cn)
- **Laboratory**: Laboratory of Fisheries Ecosystem Monitoring and Assessment, Ocean University of China
- **Issues**: Please report bugs and feature requests via [GitHub Issues](https://github.com/Wen77777777/hard_clam_connectivity/issues)

### Acknowledgments

We acknowledge the support and resources that made this research possible. Detailed acknowledgments will be included in the published manuscript.

