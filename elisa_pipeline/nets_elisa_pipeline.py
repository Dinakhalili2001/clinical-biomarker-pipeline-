"""
NETs/cfDNA ELISA Analysis Pipeline
=====================================
Processes raw ELISA optical density (OD) readings into blank-corrected,
dilution-adjusted biomarker concentrations, and compares pre- vs.
post-treatment levels per patient.

Built to reflect real ELISA-based immunoassay workflows used in clinical
plasma biomarker research (e.g. quantifying Neutrophil Extracellular
Traps and cell-free DNA across patient cohorts).

NOTE ON DATA: the CSV files in /sample_data are anonymized, illustrative
values used to demonstrate the pipeline - not identifiable patient data.

KEY DESIGN DECISIONS
---------------------
- Each plate gets its OWN blank correction and its OWN fitted standard
  curve. Data from different plates/days is never mixed when fitting
  a curve, since assay conditions can shift day to day.
- Dilution factor is applied AFTER concentration is calculated, not
  before - matching correct immunoassay calculation order.
- Any reading falling outside the standard curve's calibrated range is
  automatically flagged rather than silently reported, since such
  values are extrapolated and less reliable.

USAGE
-----
    python nets_elisa_pipeline.py

Expects two CSV files in ../sample_data/:
    standards_data.csv : plate_id, standard, concentration, raw_OD
    samples_data.csv   : plate_id, patient_id, timepoint, raw_OD
"""

import pandas as pd
from scipy import stats

DILUTION_FACTOR = 200  # all samples diluted 1:200 in this dataset
STANDARDS_PATH = "../sample_data/standards_data.csv"
SAMPLES_PATH = "../sample_data/samples_data.csv"


def fit_plate_curve(plate_standards: pd.DataFrame) -> dict:
    """Fit a standard curve for ONE plate, using that plate's own blank (Standard A)."""
    blank_od = plate_standards.loc[plate_standards["standard"] == "A", "raw_OD"].values[0]
    plate_standards = plate_standards.copy()
    plate_standards["blank_corrected_OD"] = plate_standards["raw_OD"] - blank_od

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        plate_standards["blank_corrected_OD"], plate_standards["concentration"]
    )

    return {
        "blank_od": blank_od,
        "slope": slope,
        "r_squared": r_value ** 2,
        "max_od": plate_standards["blank_corrected_OD"].max(),
    }


def process_plate(plate_samples: pd.DataFrame, curve_info: dict) -> pd.DataFrame:
    """Apply one plate's blank correction, standard curve, and dilution factor."""
    df = plate_samples.copy()
    df["OD_blank_corrected"] = df["raw_OD"] - curve_info["blank_od"]
    df["concentration_in_well"] = df["OD_blank_corrected"] * curve_info["slope"]
    df["final_concentration"] = df["concentration_in_well"] * DILUTION_FACTOR
    df["in_range"] = df["OD_blank_corrected"] <= curve_info["max_od"]
    df["flag"] = df["in_range"].apply(
        lambda ok: "OK" if ok else "ABOVE RANGE - re-dilute & repeat"
    )
    return df


def run_pipeline(standards_path: str, samples_path: str) -> pd.DataFrame:
    """Run the full pipeline across all plates found in the input files."""
    standards_data = pd.read_csv(standards_path)
    samples_data = pd.read_csv(samples_path)

    all_results = []
    for plate_id, plate_standards in standards_data.groupby("plate_id"):
        curve_info = fit_plate_curve(plate_standards)
        print(f"Plate {plate_id}: slope={curve_info['slope']:.2f}, "
              f"R²={curve_info['r_squared']:.4f}, blank={curve_info['blank_od']}")

        plate_samples = samples_data[samples_data["plate_id"] == plate_id]
        all_results.append(process_plate(plate_samples, curve_info))

    return pd.concat(all_results, ignore_index=True)


def summarize_pre_post(results: pd.DataFrame) -> pd.DataFrame:
    """Pivot to one row per patient, with % change from Pre to Post treatment."""
    comparison = results.pivot_table(
        index="patient_id", columns="timepoint", values="final_concentration"
    )
    comparison["percent_change"] = (
        (comparison["Post"] - comparison["Pre"]) / comparison["Pre"]
    ) * 100
    comparison["result"] = comparison["percent_change"].apply(
        lambda x: "INCREASED" if x > 0 else "Reduced"
    )
    return comparison


if __name__ == "__main__":
    results = run_pipeline(STANDARDS_PATH, SAMPLES_PATH)

    print("\nAll processed readings:")
    print(results[["plate_id", "patient_id", "timepoint", "final_concentration", "flag"]])

    print("\nPre vs Post comparison per patient:")
    print(summarize_pre_post(results))
