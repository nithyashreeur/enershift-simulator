# simulator.py
import pandas as pd
import numpy as np
from optimizer import optimize_storage

def simulate_multi_village(forecasts, battery_kwh=100, battery_pmax_kw=50, min_soc_frac=0.2,
                           critical_fraction=0.25, dt_hours=1.0):
    villages = list(forecasts.keys())
    # first per-village optimization
    local = {}
    for v in villages:
        local[v] = optimize_storage(forecasts[v], battery_kwh=battery_kwh,
                                    battery_pmax_kw=battery_pmax_kw,
                                    min_soc_frac=min_soc_frac,
                                    dt_hours=dt_hours,
                                    critical_fraction=critical_fraction)
    # sharing loop (per timestep)
    timestamps = forecasts[villages[0]]['timestamp'].tolist()
    final = {v: [] for v in villages}
    for i, ts in enumerate(timestamps):
        pool_surplus = 0.0
        pool_deficit = 0.0
        snapshot = {}
        for v in villages:
            row = local[v].iloc[i].to_dict()
            # define surplus: positive leftover generation after local charge and demand
            surplus = max(0.0, row.get('solar',0) - row.get('demand',0))
            if row.get('battery_soc',0) >= 0.95:
                pool_surplus += surplus
            deficit = max(0.0, row.get('net_import_kw',0))
            pool_deficit += deficit
            snapshot[v] = row
            snapshot[v]['surplus'] = surplus
            snapshot[v]['deficit'] = deficit

        # distribute pool_surplus proportionally to deficits
        if pool_surplus > 0 and pool_deficit > 0:
            for v in villages:
                need = snapshot[v]['deficit']
                if need <= 0:
                    snapshot[v]['received_from_pool'] = 0.0
                    snapshot[v]['net_import_after_share'] = snapshot[v]['net_import_kw']
                else:
                    receive = min(need, pool_surplus * (need / pool_deficit))
                    snapshot[v]['received_from_pool'] = receive
                    snapshot[v]['net_import_after_share'] = max(0.0, snapshot[v]['net_import_kw'] - receive)
                    pool_surplus -= receive
        else:
            for v in villages:
                snapshot[v]['received_from_pool'] = 0.0
                snapshot[v]['net_import_after_share'] = snapshot[v]['net_import_kw']

        for v in villages:
            final[v].append(snapshot[v])

    # convert to DataFrames
    final_dfs = {v: pd.DataFrame(final[v]) for v in villages}
    return final_dfs
