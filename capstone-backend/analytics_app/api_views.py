# analytics_app/api_views.py
from django.http import JsonResponse
import tensorflow as tf
import joblib
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from evac_app.models import EvacuationCenter, EvacuationLog
from .services.congestion import compute_congestion_risk, CongestionParams

# Global variables to load model and scalers once
model = None
scaler_X = None
scaler_Y = None

# Constants from your script
SAVE_DIR = "./models_kaggle_only/"  # Adjust to your path
INPUT_HOURS = 168
OUTPUT_HOURS = 72
TARGET_COLUMNS = ["temperature_2m", "wind_speed_10m", "wind_direction_10m",
                  "precipitation", "relative_humidity_2m", "pressure_msl", "cloud_cover"]
rename_map = {
    "temperature_2m": "TAVG",
    "relative_humidity_2m": "RH",
    "wind_speed_10m": "WDSP",
    "wind_direction_10m": "wind_dir",
    "precipitation": "PRCP",
    "pressure_msl": "pressure",
    "cloud_cover": "cloud_cover"
}
lags = [1, 3, 6, 24, 48, 72]
candidate_features = [
    "TAVG_lag_1", "TAVG_lag_3", "TAVG_lag_6", "TAVG_24h_mean",
    "PRCP_lag_1", "PRCP_lag_24", "PRCP_24h_sum",
    "pressure_lag_24", "pressure_tendency_24h",
    "WDSP_lag_1", "RH_lag_1", "wind_u_lag_1", "wind_v_lag_1",
    "low_pressure_flag", "hour", "dayofyear", "month", "city_count"
]
target_cols = ["TAVG", "WDSP", "wind_u", "wind_v", "PRCP", "RH", "pressure", "cloud_cover", "dew_point"]

def load_model_and_scalers():
    global model, scaler_X, scaler_Y

    if model is None:
        model_path = Path(SAVE_DIR) / "seq2seq_kaggle_best.h5"

        # Fixes "Could not deserialize 'keras.metrics.mse'"
        model = tf.keras.models.load_model(
            model_path,
            compile=False,     # <-- IMPORTANT
            custom_objects={
                "mse": tf.keras.metrics.MeanSquaredError(),
                "mae": tf.keras.metrics.MeanAbsoluteError(),
                "MeanSquaredError": tf.keras.metrics.MeanSquaredError(),
                "MeanAbsoluteError": tf.keras.metrics.MeanAbsoluteError()
            }
        )

    if scaler_X is None:
        scaler_X = joblib.load(Path(SAVE_DIR) / "scaler_X.pkl")

    if scaler_Y is None:
        scaler_Y = joblib.load(Path(SAVE_DIR) / "scaler_Y.pkl")

def fetch_recent_weather():
    lat = 13.41
    lon = 121.18
    now = datetime.now()
    # Fetch past 8 days to ensure at least 168 hours
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&past_days=8&forecast_days=0&hourly={','.join(TARGET_COLUMNS)}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Failed to fetch weather data")
    data = response.json()['hourly']
    df = pd.DataFrame({
        'datetime': pd.to_datetime(data['time']),
        **{col: data[col] for col in TARGET_COLUMNS}
    })
    df = df[df['datetime'] < now].tail(INPUT_HOURS).copy()
    if len(df) < INPUT_HOURS:
        raise ValueError("Insufficient historical data")
    df['city_count'] = 1  # Single location
    return df

def prepare_input(df):
    df = df.rename(columns=rename_map)
    df = df.set_index('datetime')

    # Compute dew_point
    if "dew_point" not in df.columns and ("TAVG" in df.columns and "RH" in df.columns):
        T = df["TAVG"]
        RH = df["RH"].clip(0.01, 100)
        a, b = 17.625, 243.04
        gamma = np.log(RH / 100.0) + (a * T) / (b + T)
        df["dew_point"] = (b * gamma) / (a - gamma)

    # Wind u/v
    if "WDSP" in df.columns and "wind_dir" in df.columns:
        theta = np.deg2rad(df["wind_dir"].fillna(0))
        df["wind_u"] = -df["WDSP"] * np.sin(theta)
        df["wind_v"] = -df["WDSP"] * np.cos(theta)

    # Datetime features
    df["hour"] = df.index.hour
    df["dayofyear"] = df.index.dayofyear
    df["month"] = df.index.month

    # Lags and rolling
    for lag in lags:
        if "TAVG" in df.columns:
            df[f"TAVG_lag_{lag}"] = df["TAVG"].shift(lag)
        if "PRCP" in df.columns:
            df[f"PRCP_lag_{lag}"] = df["PRCP"].shift(lag)
        if "pressure" in df.columns:
            df[f"pressure_lag_{lag}"] = df["pressure"].shift(lag)
        if "WDSP" in df.columns:
            df[f"WDSP_lag_{lag}"] = df["WDSP"].shift(lag)
        if "RH" in df.columns:
            df[f"RH_lag_{lag}"] = df["RH"].shift(lag)
        if "wind_u" in df.columns:
            df[f"wind_u_lag_{lag}"] = df["wind_u"].shift(lag)
        if "wind_v" in df.columns:
            df[f"wind_v_lag_{lag}"] = df["wind_v"].shift(lag)

    if "TAVG" in df.columns:
        df["TAVG_24h_mean"] = df["TAVG"].rolling(window=24, min_periods=1).mean()
    if "PRCP" in df.columns:
        df["PRCP_24h_sum"] = df["PRCP"].rolling(window=24, min_periods=1).sum()
    if "pressure" in df.columns:
        df["pressure_tendency_24h"] = df["pressure"] - df["pressure"].shift(24)

    df["low_pressure_flag"] = (df["pressure"] < 1005).astype(int) if "pressure" in df.columns else 0

    # Since df has exactly INPUT_HOURS rows, lags will have NaNs at start, but model was trained after dropna, but to match, fill NaNs?
    # Better to fill similar to training: interpolate or ffill/bfill, but since small, ffill
    df = df.ffill().bfill()  # Simple fill

    feature_cols_local = [c for c in candidate_features if c in df.columns]
    X = df[feature_cols_local].values[None, ...]  # (1, 168, n_feats)
    return X, feature_cols_local

def predict_weather_view(request):
    try:
        load_model_and_scalers()
        recent_df = fetch_recent_weather()
        X_raw, feature_cols_local = prepare_input(recent_df)
        X_s = scaler_X.transform(X_raw.reshape(-1, X_raw.shape[-1])).reshape(X_raw.shape)
        Y_pred_s = model.predict(X_s)
        Y_pred = scaler_Y.inverse_transform(Y_pred_s.reshape(-1, len(target_cols))).reshape(OUTPUT_HOURS, len(target_cols))

        now = datetime.now()
        predictions = []
        for i in range(OUTPUT_HOURS):
            pred_dict = {'datetime': (now + timedelta(hours=i + 1)).isoformat()}
            for j, col in enumerate(target_cols):
                pred_dict[col] = float(Y_pred[i, j])
            predictions.append(pred_dict)

        return JsonResponse({'predictions': predictions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

    
class CenterCongestionRiskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, center_id: int):
        # Optional query params:
        # ?window=60&horizon=60
        try:
            window = int(request.query_params.get("window", 60))
            horizon = int(request.query_params.get("horizon", 60))
        except ValueError:
            return Response({"detail": "window and horizon must be integers."}, status=400)

        window = max(5, min(window, 24 * 60))     # clamp 5 min .. 24 hours
        horizon = max(5, min(horizon, 6 * 60))    # clamp 5 min .. 6 hours

        center = EvacuationCenter.objects.filter(id=center_id).first()
        if not center:
            return Response({"detail": "Center not found."}, status=404)

        result = compute_congestion_risk(
            center=center,
            EvacuationLogModel=EvacuationLog,
            params=CongestionParams(window_minutes=window, horizon_minutes=horizon),
        )

        status_code = 200 if "error" not in result else 400
        return Response(result, status=status_code)