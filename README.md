# Temperature-driven Connectivity Dynamics in Marine Protected Area Networks

## A Nine-Year Assessment Using Effective Accumulated Temperature Framework in the Bohai Sea

This repository contains the analysis code and visualization scripts for our research on Hard clam (*Meretrix meretrix*) connectivity patterns in the Bohai Sea Marine Protected Area (MPA) network.

### Overview

This study investigates how temperature variability influences larval connectivity patterns between MPAs in the Bohai Sea from 2014-2022. We developed an Individual-Based Model (IBM) incorporating stage-specific temperature responses to assess connectivity dynamics under different thermal regimes.

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
git clone https://github.com/yourusername/hard_clam_connectivity.git
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

### Key Findings

1. **Temperature-driven connectivity patterns**: Warm years show significantly different connectivity patterns compared to cold years
2. **Network resilience**: Self-recruitment rates vary by 2-3 fold between temperature regimes
3. **Critical corridors**: Certain MPA connections serve as temperature-sensitive bottlenecks
4. **Management implications**: Temperature variability should be incorporated into MPA network design


### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Contact

- **Corresponding Author**: [Your Name] (email@institution.edu)
- **Lab Website**: [Your Lab URL]
- **Issues**: Please report bugs and feature requests via [GitHub Issues](https://github.com/yourusername/hard_clam_connectivity/issues)

### Acknowledgments

- Ocean model data provided by [Institution/Collaborator]
- Funding support from [Grant Numbers]
- Computational resources provided by [HPC Center]

