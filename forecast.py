# forecast.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib, os

MODEL_FILE = "enershift_rf_models.joblib"

def _make_features(df):
    d = df.copy()
    d['hour'] = d['timestamp'].dt.hour
    d['minute'] = d['timestamp'].dt.minute
    d['dow'] = d['timestamp'].dt.dayofweek
    d['month'] = d['timestamp'].dt.month
    d['lag1'] = d.groupby('village')['demand'].shift(1).fillna(method='bfill')
    d['solar_lag1'] = d.groupby('village')['solar'].shift(1).fillna(0)
    return d

def train_or_load_models(df, force_retrain=False):
    if (not force_retrain) and os.path.exists(MODEL_FILE):
        try:
            return joblib.load(MODEL_FILE)
        except Exception:
            pass
    models = {}
    # train per village
    for vid, grp in df.groupby('village'):
        g = grp.sort_values('timestamp').reset_index(drop=True)
        g = _make_features(g)
        feats = ['hour','minute','dow','month','lag1','solar_lag1']
        X = g[feats].fillna(0)
        y = g['demand'].values
        if len(g) < 50:
            models[vid] = {'demand': None, 'mean_demand': float(g['demand'].mean()), 'mean_solar': float(g['solar'].mean())}
            continue
        rf = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        # solar predictor (optional)
        rf_s = None
        if 'solar' in g.columns and g['solar'].notna().sum() >= 50:
            rf_s = RandomForestRegressor(n_estimators=80, random_state=42, n_jobs=-1)
            rf_s.fit(X, g['solar'].values)
        models[vid] = {'demand': rf, 'solar': rf_s, 'mean_demand': float(g['demand'].mean()), 'mean_solar': float(g['solar'].mean())}
    joblib.dump(models, MODEL_FILE)
    return models

def forecast_horizon(df, models, villages, horizon_hours=24, res_minutes=60):
    freq = f"{res_minutes}T"
    last = df['timestamp'].max()
    periods = int(horizon_hours * 60 / res_minutes)
    future_idx = pd.date_range(last + pd.Timedelta(minutes=res_minutes), periods=periods, freq=freq)
    results = {}
    for vid in villages:
        tmpl = pd.DataFrame({'timestamp': future_idx})
        tmpl['village'] = vid
        tmpl_feat = _make_features(tmpl.assign(demand=0, solar=0))
        feats = ['hour','minute','dow','month','lag1','solar_lag1']
        Xp = tmpl_feat[feats].fillna(0)
        m = models.get(vid)
        if (m is None) or (m.get('demand') is None):
            tmpl['demand'] = m['mean_demand'] if m else df['demand'].mean()
        else:
            tmpl['demand'] = m['demand'].predict(Xp).clip(min=0)
        if (m is None) or (m.get('solar') is None):
            tmpl['solar'] = m['mean_solar'] if m else df['solar'].mean()
        else:
            tmpl['solar'] = m['solar'].predict(Xp).clip(min=0)
        results[vid] = tmpl[['timestamp','village','demand','solar']].reset_index(drop=True)
    return results
