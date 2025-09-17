# optimizer.py
import pandas as pd
import numpy as np

def optimize_storage(forecast_df, battery_kwh=100, battery_pmax_kw=50, min_soc_frac=0.2,
                     dt_hours=1.0, critical_fraction=0.25):
    df = forecast_df.copy().reset_index(drop=True)
    cap = float(battery_kwh)
    pmax = float(battery_pmax_kw)
    soc = 0.6  # start SOC fraction
    min_soc = min_soc_frac
    records = []
    for _, row in df.iterrows():
        demand = float(row['demand'])
        solar = float(row.get('solar',0))
        # split critical vs flexible
        critical = demand * critical_fraction
        flexible = demand - critical
        # use solar to supply demand first
        used_solar = min(solar, demand)
        remaining = demand - used_solar
        # battery discharge to cover remaining (respect pmax and SOC)
        max_discharge_kwh = max(0.0, (soc - min_soc) * cap)
        max_discharge_kw = min(pmax, max_discharge_kwh / dt_hours)
        discharge_kw = min(max_discharge_kw, remaining)
        discharge_kwh = discharge_kw * dt_hours
        soc -= (discharge_kwh / cap) if cap>0 else 0
        remaining_after_batt = remaining - discharge_kw
        net_import = max(0.0, remaining_after_batt)
        # leftover solar can charge battery
        leftover_solar = max(0.0, solar - used_solar)
        max_charge_kwh = (1.0 - soc) * cap
        max_charge_kw = min(pmax, max_charge_kwh / dt_hours)
        charge_kw = min(max_charge_kw, leftover_solar)
        charge_kwh = charge_kw * dt_hours
        soc += (charge_kwh / cap) if cap>0 else 0
        soc = max(0.0, min(1.0, soc))
        served_critical = min(critical, used_solar + discharge_kw)
        served_noncritical = demand - served_critical - net_import
        records.append({
            'timestamp': row['timestamp'],
            'demand': demand,
            'solar': solar,
            'battery_soc': round(soc,4),
            'charge_kw': round(charge_kw,3),
            'discharge_kw': round(discharge_kw,3),
            'net_import_kw': round(net_import,3),
            'served_critical_kw': round(served_critical,3),
            'served_noncritical_kw': round(max(0.0, served_noncritical),3)
        })
    return pd.DataFrame(records)
