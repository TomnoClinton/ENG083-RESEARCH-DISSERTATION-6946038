"""
PHASE 1 — DATA DICTIONARY
Dissertation: A Lifecycle Cost Optimisation Methodology to Evaluate
Appliance Efficiency in Off-Grid Solar Systems: A Case Study for Sub-Saharan Africa
Author: Tomno Kiprotich | MSc Sustainable Energy | University of Surrey

All values sourced and cited. See dissertation Chapter 3 for full methodology.
"""

# ══════════════════════════════════════════════════════════════════════════════
# APPLIANCE DATA
# Sources: VeraSol (2026), Koolboks personal communication May 2026,
#          SunCulture personal communication June 2026 (Odhiambo K.),
#          Agsol personal communication July 2026,
#          Mepsy v1.15.3 Kenya 2024
# ══════════════════════════════════════════════════════════════════════════════

appliances = {

    'fridge': {
        'standard': {
            'purchase_cost_usd':        350,
            'lifetime_years':             4,
            'daily_energy_kwh':         1.20,
            'annual_maintenance_pct':   0.045,
            'annual_maintenance_usd':   None,   # percentage-based
            'pv_size_wp':               320,
            'battery_kwh':              2.0,
            'battery_replacement_yrs':    5,    # Koolboks normal usage baseline
            'warranty_months':           36,
            'source': 'VeraSol (2026); Koolboks personal comm. May 2026'
        },
        'efficient': {
            'purchase_cost_usd':        650,
            'lifetime_years':             8,
            'daily_energy_kwh':         0.558,
            'annual_maintenance_pct':   0.030,
            'annual_maintenance_usd':   None,
            'pv_size_wp':               140,
            'battery_kwh':              1.0,
            'battery_replacement_yrs':    5,
            'warranty_months':           36,
            'iot_mean_load_w':         76.74,
            'iot_daily_kwh':            1.84,
            'iot_mean_temp_c':         37.0,
            'iot_max_temp_c':          45.83,
            'iot_deep_discharges': {
                'node_1': 312, 'node_2': 90,
                'node_3':  27, 'node_4': 111
            },
            'source': 'VeraSol (2026); Koolboks IoT data May 2026'
        }
    },

    'pump': {
        'standard': {
            'purchase_cost_usd':        300,
            'lifetime_years':             5,
            'daily_energy_kwh':         2.50,
            'wire_to_water_pct':        20.5,
            'annual_maintenance_pct':   0.020,
            'annual_maintenance_usd':   None,
            'pv_size_wp':               639,
            'battery_kwh':              2.8,
            'battery_replacement_yrs':    5,
            'warranty_months':           12,
            'source': 'VeraSol (2026); SunCulture personal comm. June 2026'
        },
        'efficient': {
            'purchase_cost_usd':        600,
            'lifetime_years':            10,
            'daily_energy_kwh':         1.20,
            'wire_to_water_pct':        40.7,
            'annual_maintenance_pct':   0.020,
            'annual_maintenance_usd':   None,
            'pv_size_wp':               544,
            'battery_kwh':              1.5,
            'battery_replacement_yrs':    7,
            'warranty_months':           12,
            'source': 'VeraSol (2026); SunCulture personal comm. June 2026 (Odhiambo K.)'
        }
    },

    'mill': {
        # Standard = AC package with AC/DC converter (grid/generator powered)
        # Source: Agsol personal communication, July 2026
        'standard': {
            'purchase_cost_usd':        618,    # AC package with AC/DC converter
            'lifetime_years':             8,    # 8-10 years confirmed Agsol
            'daily_energy_kwh':         4.0,    # 1000W rated × 4 hrs/day operation
            'rated_power_w':           1000,    # Agsol confirmed
            'kwh_per_kg_milled':       0.0154,  # 1/65 kg/kWh confirmed Agsol
            'throughput_kg_per_kwh':     65,    # Agsol confirmed
            'annual_maintenance_pct':   None,   # fixed amount used instead
            'annual_maintenance_usd':   20.0,   # $20/yr confirmed Agsol (sieves $5.25, hammers $15.45)
            'pv_size_wp':               750,    # Recommended 2×350W confirmed Agsol
            'battery_kwh':              0.9,    # 900Wh confirmed Agsol
            'battery_replacement_yrs':  1.5,    # ~1 replacement per 1.5 years — BMS failures Agsol
            'warranty_months':           12,    # Agsol confirmed
            'consumables': {
                'sieve_replacement_months':  6,
                'hammer_replacement_months': 18,  # 1.5-2 years
                'sieve_cost_usd':          5.25,
                'hammer_cost_usd':        15.45,
            },
            'source': 'Agsol personal communication, July 2026'
        },
        # Efficient = purpose-built solar DC version
        'efficient': {
            'purchase_cost_usd':       1390,    # Solar version confirmed Agsol
            'lifetime_years':             9,    # Mid-point of 8-10 year range
            'daily_energy_kwh':         4.0,    # Same rated power — efficiency gain in throughput
            'rated_power_w':           1000,    # Same motor — solar optimised controller
            'kwh_per_kg_milled':       0.0154,  # Same efficiency metric — DC drive more stable
            'throughput_kg_per_kwh':     65,    # Same throughput
            'annual_maintenance_pct':   None,
            'annual_maintenance_usd':   20.0,   # Same consumables cost Agsol
            'pv_size_wp':               750,    # Minimum 600W, recommended 750W confirmed Agsol
            'battery_kwh':              0.9,    # 900Wh confirmed Agsol
            'battery_replacement_yrs':  1.5,    # Same BMS failure rate confirmed Agsol
            'warranty_months':           12,    # Agsol confirmed
            'consumables': {
                'sieve_replacement_months':  6,
                'hammer_replacement_months': 18,
                'sieve_cost_usd':          5.25,
                'hammer_cost_usd':        15.45,
            },
            'source': 'Agsol personal communication, July 2026'
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# SOLAR RESOURCE DATA
# Source: NASA POWER Data Access Viewer — monthly mean 2014-2024
# Turkana: 3.12N 35.60E | Kisumu: -0.11N 34.77E
# ══════════════════════════════════════════════════════════════════════════════

solar = {
    'turkana': {
        'annual_mean_ghi':   6.23,
        'annual_min_ghi':    5.77,
        'mean_temp_c':      29.8,
        'clearness_index':   0.625,
        'scenario_type':    'high_sun',
        'location':         'Turkana, Kenya',
        'coordinates':      '3.12N, 35.60E',
        'source':           'NASA POWER 2014-2024'
    },
    'kisumu': {
        'annual_mean_ghi':   5.96,
        'annual_min_ghi':    5.41,
        'mean_temp_c':      20.4,
        'clearness_index':   0.597,
        'scenario_type':    'variable_solar',
        'location':         'Kisumu, Kenya',
        'coordinates':      '-0.11N, 34.77E',
        'source':           'NASA POWER 2014-2024'
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM COSTS — IRENA Renewable Power Generation Costs 2023
# ══════════════════════════════════════════════════════════════════════════════

system_costs = {
    'pv_cost_per_wp':         0.30,
    'battery_cost_per_kwh': 273.0,
    'inverter_cost_usd':    200.0,
    'pv_degradation_rate':  0.005,
    'pv_temp_coefficient':  0.004,
    'reference_ghi':        5.5,
    'inverter_efficiency':  0.85,
    'source': 'IRENA (2024); NREL'
}

# ══════════════════════════════════════════════════════════════════════════════
# FINANCIAL PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

financial = {
    'discount_rate':  0.10,
    'horizon':          10,
    'source': 'World Bank (2024)'
}

# ══════════════════════════════════════════════════════════════════════════════
# TARIFF STRUCTURES
# ══════════════════════════════════════════════════════════════════════════════

tariffs = {
    'flat': {
        'rate_usd_per_kwh':  0.20,
        'description':       'Flat rate',
        'source':            'Mini-grid literature average sub-Saharan Africa'
    },
    'time_of_use': {
        'peak_rate':         0.28,
        'off_peak_rate':     0.12,
        'peak_share':        0.30,
        'off_peak_share':    0.70,
        'description':       'Time-of-use',
        'source':            'Mini-grid ToU literature'
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# BATTERY REPLACEMENT SCENARIOS
# Grounded in Koolboks IoT data May 2026 (Nodes 1-4)
# Note: Mill battery replacement is handled separately in the model
#       using Agsol's confirmed 1.5-year replacement cycle
# ══════════════════════════════════════════════════════════════════════════════

battery_scenarios = {
    'good_usage':   7,   # Node 3: 27 deep discharges
    'normal_usage': 5,   # Literature baseline
    'poor_usage':   3,   # Node 1: 312 deep discharges
}

# ══════════════════════════════════════════════════════════════════════════════
# EMISSION FACTORS
# ══════════════════════════════════════════════════════════════════════════════

emissions = {
    'diesel_per_litre_kgco2e':           2.68,
    'diesel_energy_content_kwh_litre':   3.5,
    'battery_manufacturing_kgco2e_kwh': 200.0,
    'pv_manufacturing_gco2e_kwh':        35.0,
    'appliance_manufacturing_kgco2e':    10.0,
    'source': 'IPCC; NREL (2012); Le Varlet et al. (2020)'
}

# ══════════════════════════════════════════════════════════════════════════════
# KOOLBOKS IoT SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

koolboks_iot = {
    'total_records':       8289,
    'units_monitored':        4,
    'mean_load_w':        76.74,
    'daily_energy_kwh':    1.84,
    'mean_temp_c':        37.0,
    'max_temp_c':         45.83,
    'system_downtime_pct': 7.0,
    'deep_discharges': {
        'node_1': 312, 'node_2': 90,
        'node_3':  27, 'node_4': 111
    },
    'source': 'Koolboks personal communication, May 2026'
}

# ══════════════════════════════════════════════════════════════════════════════
# AGSOL MILL DATA SUMMARY
# Source: Agsol personal communication, July 2026
# ══════════════════════════════════════════════════════════════════════════════

agsol_data = {
    'rated_power_w':              1000,
    'throughput_kg_per_kwh':        65,
    'kwh_per_kg_milled':        0.0154,
    'price_ac_package_usd':        618,
    'price_solar_version_usd':    1390,
    'pv_minimum_wp':               600,
    'pv_recommended_wp':           750,
    'battery_wh':                  900,
    'lifetime_years_range':   '8-10',
    'annual_maintenance_usd':       20,
    'sieve_cost_usd':             5.25,
    'sieve_replacement_months':      6,
    'hammer_cost_usd':           15.45,
    'hammer_replacement_months':    18,
    'battery_replacement_yrs':     1.5,
    'battery_failure_cause':   'BMS failure',
    'pv_replacements_to_date':       0,
    'warranty_months':              12,
    'spare_parts':             'Available at all distributor shops in East Africa',
    'source': 'Agsol personal communication, July 2026'
}
