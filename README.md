# THE LIFE-CYCLE COST OF EFFICIENCY:  A TECHNO-ECONOMIC ANALYSIS OF PRODUCTIVE-USE SOLAR APPLIANCES IN KENYA     


**MSc Sustainable Energy | University of Surrey | ENGM083**
**Author:** Tomno Kiprotich
**Supervisor:** Prof Michael Short (University of Surrey) | Hannah Mottram (Energy Saving Trust)
**Submission:** September 2026

---

## Overview

This repository contains all Python code and results data for the dissertation:

> *A Lifecycle Cost Optimisation Methodology to Evaluate Appliance Efficiency in Off-Grid Solar Systems: A Case Study for Sub-Saharan Africa*

The model uses Mixed Integer Linear Programming (Pyomo) to calculate the ten-year Net Present Cost (NPC) and lifecycle emissions of three productive-use solar appliances in Kenya — a solar refrigerator, a solar water pump, and a micro grain mill — comparing standard and high-efficiency variants across two solar locations and two tariff structures.



---

## Data Sources

| Source | Data Type | Used For |
|--------|-----------|----------|
| NASA POWER (2014–2024) | Monthly GHI, temperature | Turkana and Kisumu solar resource |
| VeraSol Database (2026) | Appliance performance benchmarks | 131 fridges, 58 pumps |
| Koolboks (personal comm., May 2026) | IoT monitoring data | 8,289 records, 4 units |
| Pump field parameters | Lifetime, maintenance, battery |
| Mill manufacturer data | Power, throughput, BMS failure rate |
| IRENA 2023 | System cost benchmarks | PV $0.30/Wp, battery $273/kWh |
| Mepsy v1.15.3 Kenya 2024 | National baselines | Mill energy proxy |
| IPCC / NREL / Le Varlet et al. 2020 | Emission factors | CO₂e calculations |

---

## Model Architecture

### Objective Function

Minimise NPC = CAPEX₀ + Σ[(Mₜ + Rₜ) / (1+r)ᵗ] − SV₁₀


Where:
- **CAPEX₀** = Appliance + PV array + Battery + Inverter
- **Mₜ** = Annual maintenance (percentage of purchase price or fixed USD)
- **Rₜ** = Replacement cost when appliance or battery reaches end of life
- **r** = 10% discount rate (World Bank sub-Saharan Africa benchmark)
- **SV₁₀** = Residual value at year 10

### Scenario Matrix

24 primary scenarios: 3 appliances × 2 efficiency levels × 2 locations × 2 tariffs

---

## Key Results

| Appliance | NPC Saving (Efficient vs Standard) | Monte Carlo Wins |
|-----------|-------------------------------------|-----------------|
| Solar Refrigerator | **$653 saving (−26.7%)** | 100% of 1,000 runs |
| Solar Water Pump | **$988 saving (−31.2%)** | 100% of 1,000 runs |
| Micro Grain Mill | **$776 premium (standard wins)** | 0% of 1,000 runs |

The mill result reveals that the efficiency label referred to power supply configuration rather than motor efficiency. Both variants use the same 1,000W motor at 65 kg/kWh throughput. With no energy demand reduction and a confirmed 1.5-year BMS battery failure cycle (Agsol, 2026), the USD 772 purchase premium of the solar version is not recovered within the ten-year model horizon.

---

## Installation

```bash
pip install pyomo pandas numpy matplotlib scipy
```

GLPK solver required for Pyomo:

```bash
# Ubuntu/Debian
sudo apt-get install glpk-utils

# macOS
brew install glpk
```

---

## Usage

```bash
# Run all 24 scenarios, sensitivity analysis, and Monte Carlo
python Phase4fullrun.py

# Generate all dissertation figures
python Dissertationfigures.py
```

Results CSVs are saved to the `results/` folder. Figures are saved to the working directory.

---

## Monte Carlo Design

Five uncertain parameters sampled per iteration across 1,000 runs:

| Parameter | Distribution | Range | Empirical Basis |
|-----------|-------------|-------|-----------------|
| Battery lifetime | Triangular | Min=3yr, Mode=5yr, Max=7yr | Koolboks IoT Nodes 1–4 |
| Maintenance cost | Uniform | Baseline ±30% | GOGLA market literature |
| Annual mean GHI | Uniform | Baseline ±5% | NASA POWER inter-annual variability |
| Purchase cost | Uniform | Baseline ±10% | GOGLA market reports |
| Appliance lifetime | Discrete uniform | Baseline ±1yr | Murray (2026); CLASP RI (2026) |

Mill battery cycle fixed at 1.5 years — Agsol confirmed BMS hardware failure rate invariant to usage.

---

## Note on Phase Numbering

Phase 3 was planned as an intermediate validation step but was incorporated directly into Phase 4 during model development. The three model files — Phase 1, Phase 2, and Phase 4 — constitute the complete model pipeline.

---

## Citation

> Kiprotich, T. (2026). *A Lifecycle Cost Optimisation Methodology to Evaluate Appliance Efficiency in Off-Grid Solar Systems: A Case Study for Sub-Saharan Africa*. MSc Dissertation, University of Surrey, ENGM083.

---

## Collaborators and Data Partners

- **Energy Saving Trust** — Hannah Mottram (research collaboration)
- **CLASP** — Mike Ofuya, Tarus Kiplabat Brian (methodology validation)
- **Koolboks** — IoT monitoring data (Research Collaboration Agreement, May 2026)

---

## Appendix D Reference

This repository constitutes Appendix D of the dissertation: *Model Code and Results Data*.

Full dissertation available upon request from the University of Surrey library.
