"""
Wearable Vitals Dashboard
============================
Generates and visualizes simulated daily wearable data (heart rate,
step count) for one patient over a 2-week period - illustrating the
kind of remote patient monitoring data pipeline used in digital health
platforms (e.g. tracking patient vitals trends to flag deterioration
early).

NOTE ON DATA: all data is synthetically generated (np.random, seeded
for reproducibility), not real patient data.

USAGE
-----
    python wearable_dashboard.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RANDOM_SEED = 1
N_DAYS = 14
HEART_RATE_MEAN, HEART_RATE_SD = 72, 5
STEPS_MEAN, STEPS_SD = 6000, 1500


def generate_wearable_data(n_days: int = N_DAYS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Simulate n_days of daily heart rate and step count readings."""
    np.random.seed(seed)
    dates = pd.date_range(start="2026-08-01", periods=n_days, freq="D")

    heart_rate = np.random.normal(loc=HEART_RATE_MEAN, scale=HEART_RATE_SD, size=n_days).round(0)
    steps = np.random.normal(loc=STEPS_MEAN, scale=STEPS_SD, size=n_days).round(0).astype(int)

    return pd.DataFrame({"date": dates, "heart_rate": heart_rate, "steps": steps})


def flag_elevated_heart_rate(df: pd.DataFrame, threshold: int = 80, min_consecutive_days: int = 3) -> pd.DataFrame:
    """
    Flag any run of `min_consecutive_days` or more consecutive days where
    heart rate stayed at or above `threshold` - a simple deterioration-style
    alert, similar in spirit to remote patient monitoring alert logic.
    """
    df = df.copy()
    df["above_threshold"] = df["heart_rate"] >= threshold

    # Identify consecutive-day streaks
    streak_id = (df["above_threshold"] != df["above_threshold"].shift()).cumsum()
    streak_lengths = df.groupby(streak_id)["above_threshold"].transform("size")

    df["alert"] = df["above_threshold"] & (streak_lengths >= min_consecutive_days)
    return df


def plot_dashboard(df: pd.DataFrame) -> None:
    """Plot heart rate and steps over time, highlighting any alert days."""
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)

    axes[0].plot(df["date"], df["heart_rate"], marker="o", color="crimson", label="Heart rate")
    if "alert" in df.columns and df["alert"].any():
        alert_days = df[df["alert"]]
        axes[0].scatter(alert_days["date"], alert_days["heart_rate"],
                         color="black", zorder=5, label="Alert")
    axes[0].set_ylabel("Heart Rate (bpm)")
    axes[0].set_title("Patient Wearable Data - Last 14 Days")
    axes[0].legend()

    axes[1].plot(df["date"], df["steps"], marker="o", color="steelblue")
    axes[1].set_ylabel("Steps")
    axes[1].set_xlabel("Date")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    data = generate_wearable_data()
    data = flag_elevated_heart_rate(data)

    print(data)
    if data["alert"].any():
        print("\n⚠️ Sustained elevated heart rate detected on:")
        print(data.loc[data["alert"], ["date", "heart_rate"]])

    plot_dashboard(data)
