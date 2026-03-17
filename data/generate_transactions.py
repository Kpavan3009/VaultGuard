import random
import csv
from datetime import datetime, timedelta

import numpy as np

random.seed(42)
np.random.seed(42)

MERCHANT_CATEGORIES = [
    "grocery", "gas_station", "online_shopping", "restaurant",
    "electronics", "travel", "atm_withdrawal", "wire_transfer",
    "subscription", "gaming"
]

HIGH_RISK_CATEGORIES = ["wire_transfer", "atm_withdrawal", "gaming"]

NUM_TRANSACTIONS = 100000
NUM_USERS = 500
FRAUD_RATE = 0.005

US_LAT_RANGE = (25.0, 48.0)
US_LON_RANGE = (-125.0, -67.0)

start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_seconds = int((end_date - start_date).total_seconds())

user_ids = [f"USER_{str(i).zfill(3)}" for i in range(1, NUM_USERS + 1)]
merchant_ids = [f"MERCH_{str(i).zfill(4)}" for i in range(1, 201)]

user_home_lats = {uid: np.random.uniform(*US_LAT_RANGE) for uid in user_ids}
user_home_lons = {uid: np.random.uniform(*US_LON_RANGE) for uid in user_ids}

num_fraud = int(NUM_TRANSACTIONS * FRAUD_RATE)
num_normal = NUM_TRANSACTIONS - num_fraud

fraud_indices = set(random.sample(range(NUM_TRANSACTIONS), num_fraud))

rows = []

for i in range(NUM_TRANSACTIONS):
    is_fraud = i in fraud_indices
    user_id = random.choice(user_ids)

    if is_fraud:
        amount = round(random.uniform(500, 10000), 2)
        category = random.choice(HIGH_RISK_CATEGORIES + ["electronics", "online_shopping"])
        offset_lat = np.random.uniform(-20, 20)
        offset_lon = np.random.uniform(-20, 20)
        location_lat = round(user_home_lats[user_id] + offset_lat, 6)
        location_lon = round(user_home_lons[user_id] + offset_lon, 6)
        ts_offset = random.randint(0, date_range_seconds)
        timestamp = start_date + timedelta(seconds=ts_offset)
    else:
        amount = round(random.uniform(5, 500), 2)
        category = random.choice(MERCHANT_CATEGORIES)
        offset_lat = np.random.uniform(-2, 2)
        offset_lon = np.random.uniform(-2, 2)
        location_lat = round(user_home_lats[user_id] + offset_lat, 6)
        location_lon = round(user_home_lons[user_id] + offset_lon, 6)
        ts_offset = random.randint(0, date_range_seconds)
        timestamp = start_date + timedelta(seconds=ts_offset)

    merchant_id = random.choice(merchant_ids)
    transaction_id = f"TXN_{str(i).zfill(7)}"

    rows.append({
        "transaction_id": transaction_id,
        "user_id": user_id,
        "amount": amount,
        "merchant_id": merchant_id,
        "merchant_category": category,
        "location_lat": location_lat,
        "location_lon": location_lon,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "is_fraud": int(is_fraud),
    })

rows.sort(key=lambda x: x["timestamp"])

output_path = "data/transactions.csv"
fieldnames = [
    "transaction_id", "user_id", "amount", "merchant_id",
    "merchant_category", "location_lat", "location_lon",
    "timestamp", "is_fraud"
]

with open(output_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"generated {len(rows)} transactions")
print(f"fraud count: {sum(1 for r in rows if r['is_fraud'] == 1)}")
print(f"saved to {output_path}")
