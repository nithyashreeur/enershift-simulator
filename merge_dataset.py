import pandas as pd

# Load datasets
gen = pd.read_csv("Plant_1_Generation_Data.csv")
weather = pd.read_csv("Plant_1_Weather_Sensor_Data.csv")

# Convert timestamp to datetime
gen['DATE_TIME'] = pd.to_datetime(gen['DATE_TIME'])
weather['DATE_TIME'] = pd.to_datetime(weather['DATE_TIME'])

# Merge on timestamp
merged = pd.merge_asof(
    gen.sort_values('DATE_TIME'),
    weather.sort_values('DATE_TIME'),
    on="DATE_TIME",
    direction="nearest"
)

# Create simplified dataset
final = pd.DataFrame()
final["Timestamp"] = merged["DATE_TIME"]
final["Solar (kW)"] = merged["AC_POWER"]

# Approximate Wind power (scale wind speed)
final["Wind (kW)"] = merged["WIND_SPEED"] * 2.5  

# Simulate demand (solar + wind influence + base load)
final["Demand (kW)"] = (final["Solar (kW)"] * 0.6 +
                        final["Wind (kW)"] * 0.8 + 50).round(2)

# Save
final.to_csv("enershift_real.csv", index=False)
print("enershift_real.csv created successfully!")
