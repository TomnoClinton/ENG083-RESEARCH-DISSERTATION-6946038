"""
PHASE 2 — LIFECYCLE COST AND EMISSIONS CALCULATOR
Dissertation: A Lifecycle Cost Optimisation Methodology to Evaluate
Appliance Efficiency in Off-Grid Solar Systems
Author: Tomno Kiprotich | MSc Sustainable Energy | University of Surrey
"""

from phase1_data import (
    appliances, system_costs, financial,
    solar, tariffs, battery_scenarios, emissions
)

def calculate_npc(appliance_type, efficiency, location, tariff_type,
                  battery_scenario='normal_usage', verbose=False):
    """
    Calculate 10-year Net Present Cost and lifecycle emissions for one scenario.

    Special handling for mill:
    - Uses fixed USD maintenance cost (not percentage)
    - Uses Agsol-confirmed 1.5-year battery replacement cycle
    - Adds consumables (sieves every 6 months, hammers every 18 months)
    """
    app   = appliances[appliance_type][efficiency]
    sol   = solar[location]
    tarif = tariffs[tariff_type]
    r     = financial['discount_rate']
    H     = financial['horizon']

    # Mill uses its own confirmed battery replacement cycle from Agsol
    # Other appliances use the sensitivity scenario
    if appliance_type == 'mill':
        batt_life = app['battery_replacement_yrs']  # 1.5 years — Agsol confirmed
    else:
        batt_life = battery_scenarios[battery_scenario]

    # ── LOCATION ADJUSTMENT ───────────────────────────────────────────────
    temp_correction  = 1 - (system_costs['pv_temp_coefficient'] *
                            max(0, sol['mean_temp_c'] - 25))
    ghi_factor       = sol['annual_mean_ghi'] / system_costs['reference_ghi']
    solar_factor     = ghi_factor * temp_correction

    pv_size_location      = app['pv_size_wp'] / solar_factor
    battery_size_location = (app['battery_kwh'] / min(solar_factor, 1.0)
                             if solar_factor < 1.0 else app['battery_kwh'])

    pv_cost_usd   = pv_size_location      * system_costs['pv_cost_per_wp']
    batt_cost_usd = battery_size_location * system_costs['battery_cost_per_kwh']

    # ── ANNUAL ENERGY COST ────────────────────────────────────────────────
    if tariff_type == 'flat':
        energy_cost_year = (app['daily_energy_kwh'] * 365 *
                            tarif['rate_usd_per_kwh'])
    else:
        energy_cost_year = (app['daily_energy_kwh'] * 365 *
                            (tarif['peak_share']     * tarif['peak_rate'] +
                             tarif['off_peak_share'] * tarif['off_peak_rate']))

    # ── MAINTENANCE COST ──────────────────────────────────────────────────
    # Mill: fixed USD amount from Agsol ($20/year consumables)
    # Fridge/pump: percentage of purchase price
    if appliance_type == 'mill':
        annual_maint = app['annual_maintenance_usd']  # $20/yr Agsol confirmed
        # Add consumable costs: sieves every 6 months ($5.25), hammers every 18 months ($15.45)
        sieve_cost_annual  = app['consumables']['sieve_cost_usd'] * 2    # 2×/year
        hammer_cost_annual = app['consumables']['hammer_cost_usd'] / 1.5  # every 18 months
        annual_maint += sieve_cost_annual + hammer_cost_annual
    else:
        annual_maint = app['purchase_cost_usd'] * app['annual_maintenance_pct']

    # ── YEAR 0 CAPEX ──────────────────────────────────────────────────────
    capex = (app['purchase_cost_usd'] + pv_cost_usd +
             batt_cost_usd + system_costs['inverter_cost_usd'])

    # ── YEAR-BY-YEAR NPC CALCULATION ──────────────────────────────────────
    total_discounted_opex  = 0
    total_replacement_cost = 0
    replacement_events     = []
    pv_size_current        = pv_size_location

    for t in range(1, H + 1):
        discount_factor  = 1 / (1 + r) ** t
        pv_size_current *= (1 - system_costs['pv_degradation_rate'])
        annual_cost      = annual_maint + energy_cost_year
        replacement_this_year = 0

        # Appliance replacement
        if t % app['lifetime_years'] == 0 and t < H:
            replacement_this_year += app['purchase_cost_usd']
            replacement_events.append({
                'year': t, 'type': 'appliance',
                'cost': app['purchase_cost_usd']
            })

        # Battery replacement
        # For mill: every 1.5 years (Agsol confirmed BMS failures)
        # Count replacements at each 1.5-year interval
        if appliance_type == 'mill':
            # Check if a 1.5-year interval falls in this year
            # Replacements at years: 1.5, 3.0, 4.5, 6.0, 7.5, 9.0
            replacements_this_year = 0
            for k in range(1, 20):
                rep_year = k * batt_life
                if abs(rep_year - t) < 0.5 and rep_year < H:
                    replacements_this_year += 1
            if replacements_this_year > 0:
                cost = replacements_this_year * batt_cost_usd
                replacement_this_year += cost
                replacement_events.append({
                    'year': t, 'type': 'battery',
                    'cost': cost,
                    'count': replacements_this_year
                })
        else:
            if t % int(batt_life) == 0 and t < H:
                replacement_this_year += batt_cost_usd
                replacement_events.append({
                    'year': t, 'type': 'battery',
                    'cost': batt_cost_usd
                })

        annual_cost            += replacement_this_year
        total_replacement_cost += replacement_this_year
        total_discounted_opex  += annual_cost * discount_factor

    # ── RESIDUAL VALUE ────────────────────────────────────────────────────
    years_since_last = H % app['lifetime_years']
    if years_since_last == 0:
        years_since_last = app['lifetime_years']
    remaining      = app['lifetime_years'] - years_since_last
    residual_value = (app['purchase_cost_usd'] *
                      (remaining / app['lifetime_years']) *
                      (1 / (1 + r) ** H))

    npc = capex + total_discounted_opex - residual_value

    # ── LIFECYCLE EMISSIONS ───────────────────────────────────────────────
    pv_kwh_lifetime   = (pv_size_location / 1000 *
                         sol['annual_mean_ghi'] * 365 * H)
    pv_co2            = pv_kwh_lifetime * (emissions['pv_manufacturing_gco2e_kwh'] / 1000)
    batt_co2          = battery_size_location * emissions['battery_manufacturing_kgco2e_kwh']
    appliance_co2     = emissions['appliance_manufacturing_kgco2e']
    manufacturing_co2 = pv_co2 + batt_co2 + appliance_co2

    replacement_co2 = 0
    for event in replacement_events:
        if event['type'] == 'appliance':
            replacement_co2 += emissions['appliance_manufacturing_kgco2e']
        elif event['type'] == 'battery':
            count = event.get('count', 1)
            replacement_co2 += (count * battery_size_location *
                                emissions['battery_manufacturing_kgco2e_kwh'])

    total_co2 = manufacturing_co2 + replacement_co2

    # Diesel baseline
    diesel_daily_litres = (app['daily_energy_kwh'] /
                           emissions['diesel_energy_content_kwh_litre'])
    diesel_co2_10yr     = (diesel_daily_litres * 365 * H *
                           emissions['diesel_per_litre_kgco2e'])

    return {
        'scenario_id':            f"{appliance_type}_{efficiency}_{location}_{tariff_type}_{battery_scenario}",
        'appliance':               appliance_type,
        'efficiency':              efficiency,
        'location':                location,
        'tariff':                  tariff_type,
        'battery_scenario':        battery_scenario,
        'capex_usd':               round(capex, 2),
        'npc_usd':                 round(npc, 2),
        'total_co2e_kg':           round(total_co2, 1),
        'diesel_co2e_kg':          round(diesel_co2_10yr, 1),
        'co2e_saving_vs_diesel':   round(diesel_co2_10yr - total_co2, 1),
        'n_replacements':          len(replacement_events),
        'total_replacement_cost':  round(total_replacement_cost, 2),
        'residual_value':          round(residual_value, 2),
        'pv_size_wp':              round(pv_size_location, 0),
        'battery_kwh':             round(battery_size_location, 2),
        'solar_factor':            round(solar_factor, 4),
        'annual_maint_usd':        round(annual_maint, 2),
        'manufacturing_co2e':      round(manufacturing_co2, 1),
        'replacement_co2e':        round(replacement_co2, 1),
    }
