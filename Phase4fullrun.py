"""
PHASE 4 — FULL SCENARIO RUN + SENSITIVITY + MONTE CARLO
Dissertation: A Lifecycle Cost Optimisation Methodology to Evaluate
Appliance Efficiency in Off-Grid Solar Systems
Author: Tomno Kiprotich | MSc Sustainable Energy | University of Surrey

Produces:
  1. results_24_scenarios.csv       — all 24 primary scenarios
  2. results_sensitivity_72.csv     — 24 × 3 battery scenarios
  3. results_monte_carlo.csv        — 1000 Monte Carlo runs
  4. results_summary_table.csv      — clean comparison table
"""

import pandas as pd
import numpy as np
import os
from phase1_data import appliances, solar, tariffs, battery_scenarios, emissions, system_costs, financial
from phase2_model import calculate_npc

os.makedirs('/home/claude/results', exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# PART 1 — ALL 24 PRIMARY SCENARIOS (normal usage baseline)
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 65)
print("RUNNING 24 PRIMARY SCENARIOS")
print("=" * 65)

appliance_types  = ['fridge', 'pump', 'mill']
efficiency_types = ['standard', 'efficient']
locations        = ['turkana', 'kisumu']
tariff_types     = ['flat', 'time_of_use']

results_24 = []

for app in appliance_types:
    for eff in efficiency_types:
        for loc in locations:
            for tar in tariff_types:
                r = calculate_npc(app, eff, loc, tar,
                                  battery_scenario='normal_usage')
                results_24.append(r)
                print(f"  {app:6} | {eff:9} | {loc:7} | {tar:12} | "
                      f"NPC=${r['npc_usd']:,.0f} | CO2e={r['total_co2e_kg']:,.0f}kg")

df24 = pd.DataFrame(results_24)
df24.to_csv('/home/claude/results/results_24_scenarios.csv', index=False)
print(f"\n✅ 24 scenarios saved — {len(df24)} rows\n")

# ══════════════════════════════════════════════════════════════════════════════
# PART 2 — SENSITIVITY ANALYSIS (72 scenarios: 24 × 3 battery scenarios)
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 65)
print("RUNNING 72 SENSITIVITY SCENARIOS (24 × 3 battery scenarios)")
print("=" * 65)

results_72 = []

for bscen in ['good_usage', 'normal_usage', 'poor_usage']:
    for app in appliance_types:
        for eff in efficiency_types:
            for loc in locations:
                for tar in tariff_types:
                    r = calculate_npc(app, eff, loc, tar,
                                      battery_scenario=bscen)
                    results_72.append(r)

df72 = pd.DataFrame(results_72)
df72.to_csv('/home/claude/results/results_sensitivity_72.csv', index=False)
print(f"✅ 72 sensitivity scenarios saved — {len(df72)} rows\n")

# Print sensitivity summary
print("SENSITIVITY SUMMARY — NPC by battery usage scenario:")
print(f"{'Appliance':8} {'Efficiency':10} {'Battery scenario':18} {'Mean NPC':>10} {'Min NPC':>10} {'Max NPC':>10}")
print("-" * 70)
for app in appliance_types:
    for eff in efficiency_types:
        subset = df72[(df72['appliance'] == app) & (df72['efficiency'] == eff)]
        for bscen in ['good_usage', 'normal_usage', 'poor_usage']:
            s = subset[subset['battery_scenario'] == bscen]['npc_usd']
            print(f"  {app:8} {eff:10} {bscen:18} "
                  f"${s.mean():>8,.0f} ${s.min():>8,.0f} ${s.max():>8,.0f}")
    print()

# ══════════════════════════════════════════════════════════════════════════════
# PART 3 — MONTE CARLO ANALYSIS (1000 runs)
# ══════════════════════════════════════════════════════════════════════════════

print("=" * 65)
print("RUNNING MONTE CARLO SIMULATION — 1000 RUNS")
print("=" * 65)

np.random.seed(42)
N_RUNS = 1000

# Parameter distributions — grounded in empirical ranges
# Battery lifetime: triangular distribution across poor/normal/good range
# Maintenance cost: ±30% around baseline (literature uncertainty)
# Solar GHI: ±5% around annual mean (inter-annual variability from NASA POWER)
# Purchase cost: ±10% around baseline (market price variation)

def run_monte_carlo(appliance_type, efficiency, location, tariff_type,
                    n_runs=1000):
    """
    Run Monte Carlo simulation for one appliance/location/tariff combination.
    Samples uncertain parameters from empirically grounded distributions.
    """
    app   = appliances[appliance_type][efficiency]
    sol   = solar[location]
    tarif = tariffs[tariff_type]
    r_d   = financial['discount_rate']
    H     = financial['horizon']

    npc_results   = []
    co2_results   = []
    saving_results = []

    for _ in range(n_runs):

        # Sample battery lifetime from triangular distribution
        # Min=3 (poor usage Node1), Mode=5 (normal), Max=7 (good usage Node3)
        # Mill uses confirmed 1.5yr cycle; others use triangular distribution
        if appliance_type == 'mill':
            batt_life_sample = 1.5  # Agsol confirmed BMS failure rate
        else:
            batt_life_sample = int(np.random.triangular(left=3, mode=5, right=7))
            batt_life_sample = max(2, batt_life_sample)

        # Sample maintenance cost ±30% around baseline
        # Handle both fixed USD and percentage maintenance
        if app["annual_maintenance_pct"] is not None:
            maint_pct = app["annual_maintenance_pct"] * np.random.uniform(0.70, 1.30)
            maint_fixed = None
        else:
            maint_pct = None
            maint_fixed = app["annual_maintenance_usd"] * np.random.uniform(0.70, 1.30)

        # Sample GHI ±5% around annual mean (inter-annual variability)
        ghi_sample = sol['annual_mean_ghi'] * np.random.uniform(0.95, 1.05)

        # Sample purchase cost ±10% (market price variation)
        purchase_cost = app['purchase_cost_usd'] * np.random.uniform(0.90, 1.10)

        # Sample appliance lifetime ±1 year (field vs spec variation)
        lifetime = max(2, app['lifetime_years'] + np.random.randint(-1, 2))

        # ── COMPUTE NPC FOR THIS SAMPLE ────────────────────────────────
        temp_corr   = 1 - (system_costs['pv_temp_coefficient'] *
                           max(0, sol['mean_temp_c'] - 25))
        ghi_factor  = ghi_sample / system_costs['reference_ghi']
        sf          = ghi_factor * temp_corr

        pv_size     = app['pv_size_wp'] / sf
        batt_size   = (app['battery_kwh'] / min(sf, 1.0)
                       if sf < 1.0 else app['battery_kwh'])

        pv_cost     = pv_size * system_costs['pv_cost_per_wp']
        batt_cost   = batt_size * system_costs['battery_cost_per_kwh']

        if tariff_type == 'flat':
            energy_yr = app['daily_energy_kwh'] * 365 * tarif['rate_usd_per_kwh']
        else:
            energy_yr = (app['daily_energy_kwh'] * 365 *
                         (tarif['peak_share'] * tarif['peak_rate'] +
                          tarif['off_peak_share'] * tarif['off_peak_rate']))

        # Compute maintenance amount
        if maint_pct is not None:
            annual_m = purchase_cost * maint_pct
        else:
            # Mill: fixed consumables + random variation
            sieve_annual = app["consumables"]["sieve_cost_usd"] * 2
            hammer_annual = app["consumables"]["hammer_cost_usd"] / 1.5
            annual_m = maint_fixed + sieve_annual + hammer_annual
        capex    = (purchase_cost + pv_cost + batt_cost +
                    system_costs['inverter_cost_usd'])

        total_opex = 0
        repl_events = []

        for t in range(1, H + 1):
            df = 1 / (1 + r_d) ** t
            ac = annual_m + energy_yr

            if t % lifetime == 0 and t < H:
                ac += purchase_cost
                repl_events.append({'type': 'appliance', 'cost': purchase_cost})

            if t % batt_life_sample == 0 and t < H:
                ac += batt_cost
                repl_events.append({'type': 'battery', 'cost': batt_cost})

            total_opex += ac * df

        ysl = H % lifetime
        if ysl == 0: ysl = lifetime
        rem = lifetime - ysl
        rv  = purchase_cost * (rem / lifetime) * (1 / (1 + r_d) ** H)

        npc = capex + total_opex - rv

        # Emissions
        pv_kwh = (pv_size / 1000) * ghi_sample * 365 * H
        mfg_co2 = (pv_kwh * emissions['pv_manufacturing_gco2e_kwh'] / 1000 +
                   batt_size * emissions['battery_manufacturing_kgco2e_kwh'] +
                   emissions['appliance_manufacturing_kgco2e'])
        rep_co2 = sum(
            emissions['appliance_manufacturing_kgco2e'] if e['type'] == 'appliance'
            else batt_size * emissions['battery_manufacturing_kgco2e_kwh']
            for e in repl_events
        )
        total_co2 = mfg_co2 + rep_co2

        npc_results.append(npc)
        co2_results.append(total_co2)

    return np.array(npc_results), np.array(co2_results)


mc_results = []
print(f"\n{'Appliance':8} {'Eff':9} {'Location':8} {'Tariff':12} "
      f"{'Mean NPC':>10} {'Std NPC':>9} {'P5':>8} {'P95':>8} {'Eff wins%':>10}")
print("-" * 85)

# Run for each appliance × location × tariff (standard vs efficient paired)
for app in appliance_types:
    for loc in locations:
        for tar in tariff_types:
            npc_std, co2_std = run_monte_carlo(app, 'standard', loc, tar, N_RUNS)
            npc_eff, co2_eff = run_monte_carlo(app, 'efficient', loc, tar, N_RUNS)

            # Efficient wins when its NPC is lower
            eff_wins_pct = 100 * np.mean(npc_eff < npc_std)
            mean_saving  = np.mean(npc_std - npc_eff)

            for eff, npc_arr, co2_arr in [('standard', npc_std, co2_std),
                                           ('efficient', npc_eff, co2_eff)]:
                mc_results.append({
                    'appliance':         app,
                    'efficiency':        eff,
                    'location':          loc,
                    'tariff':            tar,
                    'mc_runs':           N_RUNS,
                    'npc_mean':          round(np.mean(npc_arr), 2),
                    'npc_std':           round(np.std(npc_arr), 2),
                    'npc_p5':            round(np.percentile(npc_arr, 5), 2),
                    'npc_p25':           round(np.percentile(npc_arr, 25), 2),
                    'npc_p50':           round(np.percentile(npc_arr, 50), 2),
                    'npc_p75':           round(np.percentile(npc_arr, 75), 2),
                    'npc_p95':           round(np.percentile(npc_arr, 95), 2),
                    'co2_mean':          round(np.mean(co2_arr), 1),
                    'co2_std':           round(np.std(co2_arr), 1),
                    'eff_wins_pct':      round(eff_wins_pct, 1),
                    'mean_npc_saving':   round(mean_saving, 2),
                })

            print(f"  {app:8} {'std':9} {loc:8} {tar:12} "
                  f"${np.mean(npc_std):>8,.0f} ${np.std(npc_std):>7,.0f} "
                  f"${np.percentile(npc_std,5):>6,.0f} ${np.percentile(npc_std,95):>6,.0f} "
                  f"{'':>10}")
            print(f"  {app:8} {'eff':9} {loc:8} {tar:12} "
                  f"${np.mean(npc_eff):>8,.0f} ${np.std(npc_eff):>7,.0f} "
                  f"${np.percentile(npc_eff,5):>6,.0f} ${np.percentile(npc_eff,95):>6,.0f} "
                  f"  {eff_wins_pct:>7.1f}%")
            print()

df_mc = pd.DataFrame(mc_results)
df_mc.to_csv('/home/claude/results/results_monte_carlo.csv', index=False)
print(f"\n✅ Monte Carlo results saved — {len(df_mc)} rows ({N_RUNS} runs each)")

# ══════════════════════════════════════════════════════════════════════════════
# PART 4 — CLEAN SUMMARY TABLE
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 65)
print("SUMMARY TABLE — EFFICIENT vs STANDARD (Normal Usage Baseline)")
print("=" * 65)

rows = []
for app in appliance_types:
    for loc in locations:
        for tar in tariff_types:
            std = df24[(df24['appliance']==app) & (df24['efficiency']=='standard') &
                       (df24['location']==loc) & (df24['tariff']==tar)].iloc[0]
            eff = df24[(df24['appliance']==app) & (df24['efficiency']=='efficient') &
                       (df24['location']==loc) & (df24['tariff']==tar)].iloc[0]

            mc_row = df_mc[(df_mc['appliance']==app) & (df_mc['efficiency']=='efficient') &
                           (df_mc['location']==loc) & (df_mc['tariff']==tar)].iloc[0]

            saving    = std['npc_usd'] - eff['npc_usd']
            co2_save  = std['total_co2e_kg'] - eff['total_co2e_kg']
            extra_cap = eff['capex_usd'] - std['capex_usd']
            winner    = 'Efficient' if saving > 0 else 'Standard'

            rows.append({
                'Appliance':          app.capitalize(),
                'Location':           loc.capitalize(),
                'Tariff':             tar.replace('_', ' ').capitalize(),
                'Std CAPEX (USD)':    f"${std['capex_usd']:,.0f}",
                'Eff CAPEX (USD)':    f"${eff['capex_usd']:,.0f}",
                'Extra upfront':      f"${extra_cap:,.0f}",
                'Std NPC (USD)':      f"${std['npc_usd']:,.0f}",
                'Eff NPC (USD)':      f"${eff['npc_usd']:,.0f}",
                'NPC saving (USD)':   f"${saving:,.0f}",
                'Std CO2e (kg)':      f"{std['total_co2e_kg']:,.0f}",
                'Eff CO2e (kg)':      f"{eff['total_co2e_kg']:,.0f}",
                'CO2e saving (kg)':   f"{co2_save:,.0f}",
                'Eff wins MC (%)':    f"{mc_row['eff_wins_pct']:.1f}%",
                'Winner':             winner,
            })

            print(f"  {app.upper()} | {loc} | {tar}")
            print(f"    NPC:  Std=${std['npc_usd']:,.0f}  Eff=${eff['npc_usd']:,.0f}  "
                  f"Saving=${saving:,.0f}  Winner={winner}")
            print(f"    CO2e: Std={std['total_co2e_kg']:,.0f}kg  Eff={eff['total_co2e_kg']:,.0f}kg  "
                  f"CO2e save={co2_save:,.0f}kg")
            print(f"    MC:   Efficient wins in {mc_row['eff_wins_pct']:.1f}% of {N_RUNS} simulations")
            print()

df_summary = pd.DataFrame(rows)
df_summary.to_csv('/home/claude/results/results_summary_table.csv', index=False)
print(f"\n✅ Summary table saved\n")
print("ALL RUNS COMPLETE")
print(f"  results/results_24_scenarios.csv")
print(f"  results/results_sensitivity_72.csv")
print(f"  results/results_monte_carlo.csv")
print(f"  results/results_summary_table.csv")
