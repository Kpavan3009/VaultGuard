import json
import os

import numpy as np
import pandas as pd


CATEGORY_MAP = {
    "atm_withdrawal": 0,
    "dining": 1,
    "gaming": 2,
    "grocery": 3,
    "online_shopping": 4,
    "retail": 5,
    "subscription": 6,
    "travel": 7,
    "utilities": 8,
    "wire_transfer": 9,
}


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def load_feature_columns(model_path="models/"):
    path = os.path.join(model_path, "feature_columns.json")
    with open(path) as f:
        return json.load(f)


def compute_features(transaction_df):
    df = transaction_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    user_stats = df.groupby("user_id")["amount"].agg(["mean", "std"]).reset_index()
    user_stats.columns = ["user_id", "user_amount_mean", "user_amount_std"]
    df = df.merge(user_stats, on="user_id", how="left")
    df["user_amount_std"] = df["user_amount_std"].fillna(1.0)
    df["amount_zscore"] = (df["amount"] - df["user_amount_mean"]) / df["user_amount_std"].clip(lower=0.01)

    df["amount_to_avg_ratio"] = df["amount"] / df["user_amount_mean"].clip(lower=0.01)

    df["prev_timestamp"] = df.groupby("user_id")["timestamp"].shift(1)
    df["time_since_last_txn"] = (df["timestamp"] - df["prev_timestamp"]).dt.total_seconds()
    df["time_since_last_txn"] = df["time_since_last_txn"].fillna(-1)

    df["prev_lat"] = df.groupby("user_id")["location_lat"].shift(1)
    df["prev_lon"] = df.groupby("user_id")["location_lon"].shift(1)

    valid_geo = df["prev_lat"].notna() & df["location_lat"].notna()
    df["geo_distance_from_last"] = 0.0
    if valid_geo.any():
        df.loc[valid_geo, "geo_distance_from_last"] = haversine(
            df.loc[valid_geo, "prev_lat"].values,
            df.loc[valid_geo, "prev_lon"].values,
            df.loc[valid_geo, "location_lat"].values,
            df.loc[valid_geo, "location_lon"].values,
        )

    df["merchant_category_encoded"] = df["merchant_category"].map(CATEGORY_MAP).fillna(-1).astype(int)

    user_cat_first = df.groupby(["user_id", "merchant_category"]).cumcount()
    df["is_new_merchant"] = (user_cat_first == 0).astype(int)

    df["is_round_amount"] = df["amount"].apply(
        lambda x: int(x % 100 == 0 and x >= 100)
    )

    high_risk = {"wire_transfer", "atm_withdrawal", "gaming"}
    df["is_high_risk_category"] = df["merchant_category"].isin(high_risk).astype(int)

    df["timestamp_unix"] = df["timestamp"].astype(np.int64) // 10 ** 9

    txn_count_1h = []
    txn_count_24h = []
    amount_sum_1h = []
    amount_sum_24h = []

    for user_id in df["user_id"].unique():
        user_mask = df["user_id"] == user_id
        user_df = df.loc[user_mask].copy()
        ts = user_df["timestamp_unix"].values
        amounts = user_df["amount"].values

        counts_1h = []
        counts_24h = []
        sums_1h = []
        sums_24h = []

        for j in range(len(ts)):
            mask_1h = (ts[:j] >= ts[j] - 3600) & (ts[:j] < ts[j])
            mask_24h = (ts[:j] >= ts[j] - 86400) & (ts[:j] < ts[j])

            counts_1h.append(int(mask_1h.sum()))
            counts_24h.append(int(mask_24h.sum()))
            sums_1h.append(float(amounts[:j][mask_1h].sum()))
            sums_24h.append(float(amounts[:j][mask_24h].sum()))

        txn_count_1h.extend(counts_1h)
        txn_count_24h.extend(counts_24h)
        amount_sum_1h.extend(sums_1h)
        amount_sum_24h.extend(sums_24h)

    df["txn_count_1h"] = txn_count_1h
    df["txn_count_24h"] = txn_count_24h
    df["amount_sum_1h"] = amount_sum_1h
    df["amount_sum_24h"] = amount_sum_24h

    df["velocity_1h"] = df["amount_sum_1h"] / df["txn_count_1h"].clip(lower=1)

    feature_columns = [
        "amount", "amount_zscore", "amount_to_avg_ratio",
        "hour_of_day", "day_of_week", "is_weekend",
        "time_since_last_txn", "geo_distance_from_last",
        "merchant_category_encoded", "is_new_merchant",
        "is_round_amount", "is_high_risk_category",
        "txn_count_1h", "txn_count_24h",
        "amount_sum_1h", "amount_sum_24h",
        "velocity_1h",
    ]

    drop_cols = [
        "user_amount_mean", "user_amount_std", "prev_timestamp",
        "prev_lat", "prev_lon", "timestamp_unix",
    ]
    df = df.drop(columns=drop_cols, errors="ignore")

    return df, feature_columns


def compute_single_transaction_features(txn_dict, user_history=None):
    feature_columns = load_feature_columns()

    ts = pd.to_datetime(txn_dict["timestamp"])
    amount = float(txn_dict["amount"])
    category = txn_dict.get("merchant_category", "")

    if user_history and len(user_history) > 0:
        amounts = [h["amount"] for h in user_history]
        user_mean = np.mean(amounts)
        user_std = max(np.std(amounts), 0.01)
        last_ts = pd.to_datetime(user_history[-1]["timestamp"])
        time_since_last = (ts - last_ts).total_seconds()
        last_lat = user_history[-1].get("location_lat")
        last_lon = user_history[-1].get("location_lon")
        categories_seen = {h.get("merchant_category") for h in user_history}

        now_unix = int(ts.timestamp())
        recent_1h = [h for h in user_history if now_unix - int(pd.to_datetime(h["timestamp"]).timestamp()) <= 3600]
        recent_24h = [h for h in user_history if now_unix - int(pd.to_datetime(h["timestamp"]).timestamp()) <= 86400]
        txn_count_1h = len(recent_1h)
        txn_count_24h = len(recent_24h)
        amount_sum_1h = sum(h["amount"] for h in recent_1h)
        amount_sum_24h = sum(h["amount"] for h in recent_24h)
    else:
        user_mean = amount
        user_std = 1.0
        time_since_last = -1
        last_lat = None
        last_lon = None
        categories_seen = set()
        txn_count_1h = 0
        txn_count_24h = 0
        amount_sum_1h = 0.0
        amount_sum_24h = 0.0

    amount_zscore = (amount - user_mean) / max(user_std, 0.01)
    amount_to_avg_ratio = amount / max(user_mean, 0.01)

    geo_dist = 0.0
    cur_lat = txn_dict.get("location_lat")
    cur_lon = txn_dict.get("location_lon")
    if last_lat is not None and cur_lat is not None:
        geo_dist = float(haversine(last_lat, last_lon, cur_lat, cur_lon))

    cat_encoded = CATEGORY_MAP.get(category, -1)
    is_new = int(category not in categories_seen)
    is_round = int(amount % 100 == 0 and amount >= 100)
    high_risk = {"wire_transfer", "atm_withdrawal", "gaming"}
    is_high_risk = int(category in high_risk)
    velocity_1h = amount_sum_1h / max(txn_count_1h, 1)

    features = {
        "amount": amount,
        "amount_zscore": amount_zscore,
        "amount_to_avg_ratio": amount_to_avg_ratio,
        "hour_of_day": ts.hour,
        "day_of_week": ts.dayofweek,
        "is_weekend": int(ts.dayofweek >= 5),
        "time_since_last_txn": time_since_last,
        "geo_distance_from_last": geo_dist,
        "merchant_category_encoded": cat_encoded,
        "is_new_merchant": is_new,
        "is_round_amount": is_round,
        "is_high_risk_category": is_high_risk,
        "txn_count_1h": txn_count_1h,
        "txn_count_24h": txn_count_24h,
        "amount_sum_1h": amount_sum_1h,
        "amount_sum_24h": amount_sum_24h,
        "velocity_1h": velocity_1h,
    }

    aligned = np.array([[features.get(col, 0.0) for col in feature_columns]])
    return aligned, feature_columns
