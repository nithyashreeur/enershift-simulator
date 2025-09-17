# ai_suggestions.py
def make_recommendations(schedule_df, forecast_df, village_name="1"):
    recs = []
    # key stats
    final_soc = float(schedule_df['battery_soc'].iloc[-1])
    avg_import = float(schedule_df['net_import_kw'].mean())
    peak_demand = float(forecast_df['demand'].max())
    solar_peak = float(forecast_df['solar'].max())
    # 1) Immediate alerts
    if final_soc < 0.25:
        recs.append(f"Village {village_name}: ALERT — battery SOC may drop to {final_soc*100:.0f}%. Prioritize critical loads (hospital, water pumps).")
    if avg_import > 0.5:
        recs.append(f"Village {village_name}: Expected average import {avg_import:.2f} kW — consider adding storage or reducing non-critical demand windows.")
    # 2) Charging window suggestion
    # find hours where solar > demand (surplus)
    merged = forecast_df.copy().reset_index(drop=True)
    surplus = (merged['solar'] - merged['demand'])
    surplus_windows = merged[surplus > 0]
    if len(surplus_windows) > 0:
        start = surplus_windows['timestamp'].iloc[0]
        end = surplus_windows['timestamp'].iloc[-1]
        recs.append(f"Village {village_name}: Charge recommendation — schedule battery charging between {start.strftime('%Y-%m-%d %H:%M')} and {end.strftime('%Y-%m-%d %H:%M')} when solar surplus exists.")
    else:
        # if no surplus, recommend nighttime charging if grid available or reduce loads
        recs.append(f"Village {village_name}: No daytime solar surplus expected — avoid deep discharge; schedule non-critical tasks when predicted solar rises (≈midday).")
    # 3) Discharge recommendation
    high_deficit = merged[merged['demand'] > (merged['solar'] * 1.2)]
    if len(high_deficit) > 0:
        t = high_deficit['timestamp'].iloc[0]
        recs.append(f"Village {village_name}: Discharge when deficit begins (around {t.strftime('%Y-%m-%d %H:%M')}) to protect critical services; avoid discharging below 20% SOC.")
    # 4) Sharing / ops
    if schedule_df.get('received_from_pool', None) is not None and schedule_df['received_from_pool'].sum() > 0:
        recs.append(f"Village {village_name}: This village will receive shared energy from neighbors during some timesteps — coordinate transfers and notify operators.")
    # 5) Short tactical suggestions
    recs.append("Operational tips: (1) Shift high-energy deferrable loads (pumps, EV charging) to daytime solar peak. (2) Keep battery SOC >= 30% overnight if possible. (3) Log any outages and re-run forecast.")
    return recs
