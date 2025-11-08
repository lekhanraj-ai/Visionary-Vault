import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib, os

# ===== Load Datasets =====
df = pd.read_csv("../data/Nordic_Region_CO2_Emissions_Dataset.csv")
factors = pd.read_csv("../data/energy_emission_factors.csv")
renewables = pd.read_csv("../data/nordic_renewable_share.csv")

# Merge emission factors
df = df.merge(factors, on="EnergyType", how="left")
df["CO2_Emissions_Calc"] = df["Usage_kWh"] * df["EmissionFactor_kgCO2_per_kWh"]

# Fill missing emission values
df["CO2_Emissions_kg"].fillna(df["CO2_Emissions_Calc"], inplace=True)

# Add renewable percentage by country
df = df.merge(renewables, on="Country", how="left")

# === Preprocessing ===
df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
df = df.sort_values(["Company", "Month"])
df["prev_Usage"] = df.groupby("Company")["Usage_kWh"].shift(1).fillna(df["Usage_kWh"].mean())
df["month"] = df["Month"].dt.month
df["is_winter"] = df["month"].isin([11, 12, 1, 2, 3]).astype(int)

# === Features and Target ===
X = df[["Usage_kWh", "month", "is_winter", "prev_Usage", "Renewable_Percentage"]]
y = df["CO2_Emissions_kg"]

# === Train/Test Split ===
split = int(0.8 * len(df))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# === Train Model ===
model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)

# === Evaluate ===
mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))
r2 = r2_score(y_test, pred)
print(f"📊 MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.2f}")

# === Save Model ===
os.makedirs("../models", exist_ok=True)
joblib.dump(model, "../models/carbon_model.pkl")
print("✅ Model saved to ../models/carbon_model.pkl")
