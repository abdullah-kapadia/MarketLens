import pandas as pd
import re

INPUT_FILE = "raw_ogdc.csv"
OUTPUT_FILE = "OGDC.csv"

def parse_number(value):
    if value is None:
        return None

    value = str(value).replace(",", "").strip()

    if value == "":
        return None

    multiplier = 1

    if value.endswith("K"):
        multiplier = 1_000
        value = value[:-1]
    elif value.endswith("M"):
        multiplier = 1_000_000
        value = value[:-1]
    elif value.endswith("B"):
        multiplier = 1_000_000_000
        value = value[:-1]

    try:
        return float(value) * multiplier
    except ValueError:
        return None

# Read CSV
df = pd.read_csv(INPUT_FILE)

# Rename columns cleanly
df.columns = [col.strip() for col in df.columns if col.strip() != ""]

# Convert Date
df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

# Clean numeric columns
for col in ["Open", "High", "Low", "Close", "Volume"]:
    df[col] = df[col].apply(parse_number)

# Sort by date (ascending)
df = df.sort_values("Date")

# Save cleaned CSV
df.to_csv(OUTPUT_FILE, index=False)

print("✅ CSV cleaned successfully:", OUTPUT_FILE)
