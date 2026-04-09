import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
DOCS_DIR = BASE_DIR / "docs"

REPO_ROOT = BASE_DIR.parents[2]

DISASTER_SOURCE = REPO_ROOT / "ai-ml" / "synthetic" / "synthetic_disaster_10k.csv"
MISINFO_SOURCE = REPO_ROOT / "ai-ml" / "synthetic" / "asad_social_media_misinformation" / "data" / "social_media_misinformation_sample_output.csv"
CYBER_SOURCE = REPO_ROOT / "ai-ml" / "synthetic" / "bharadwaj" / "data" / "data" / "sample_output.csv"


def load_settings() -> dict:
    with open(CONFIG_DIR / "scenario_settings.json", "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_severity(value: str) -> str:
    if pd.isna(value):
        return value
    value = str(value).strip().lower()
    mapping = {
        "moderate": "moderate",
        "severe": "severe",
        "extreme": "extreme",
        "high": "severe",
        "critical": "extreme",
        "minor": "minor",
    }
    return mapping.get(value, value)


def load_disaster_parent() -> pd.DataFrame:
    df = pd.read_csv(DISASTER_SOURCE)
    df = df.rename(columns={
        "event_type": "event_type",
        "severity_level": "severity_level",
        "risk_category": "risk_category",
        "start_time": "start_time",
    })
    df["severity_level"] = df["severity_level"].apply(normalize_severity)
    return df


def load_misinfo() -> pd.DataFrame:
    df = pd.read_csv(MISINFO_SOURCE)
    df["threat_stream"] = "misinformation"
    df["source_dataset"] = "social_misinformation_dataset"
    df["severity_level"] = None
    df["timestamp"] = None
    df["source_record_id"] = df["threat_id"]
    return df


def build_cyber_parent_mapping(disaster_df: pd.DataFrame, cyber_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cyber IDs do not match parent disaster IDs.
    So we map cyber rows to parent disaster events by disaster_type and severity_level.
    """
    disaster_pool = disaster_df.copy()

    grouped = {
        (dtype, sev): grp["hazard_event_id"].tolist()
        for (dtype, sev), grp in disaster_pool.groupby(["event_type", "severity_level"])
    }

    assignment_counters = {key: 0 for key in grouped.keys()}
    mapped_ids = []

    for _, row in cyber_df.iterrows():
        key = (row["event_type"], row["severity_level"])
        options = grouped.get(key, [])

        if not options:
            mapped_ids.append(None)
            continue

        idx = assignment_counters[key] % len(options)
        mapped_ids.append(options[idx])
        assignment_counters[key] += 1

    cyber_df["parent_hazard_event_id"] = mapped_ids
    return cyber_df


def load_cyber(disaster_df: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(CYBER_SOURCE)
    df = df.rename(columns={
        "disaster_type": "event_type",
        "severity": "severity_level"
    })
    df["severity_level"] = df["severity_level"].apply(normalize_severity)
    df["threat_stream"] = "cyber"
    df["source_dataset"] = "cyber_network_threat_dataset"
    df["source_record_id"] = df["hazard_event_id"]
    df = build_cyber_parent_mapping(disaster_df, df)
    return df


def merge_misinfo_with_parent(disaster_df: pd.DataFrame, misinfo_df: pd.DataFrame) -> pd.DataFrame:
    merged = misinfo_df.merge(
        disaster_df,
        on="hazard_event_id",
        how="left",
        suffixes=("", "_parent")
    )

    merged["timestamp"] = merged["start_time"]
    merged["threat_type"] = merged["threat_type"]
    merged["attack_vector"] = None
    merged["impersonation"] = None
    merged["target"] = None
    merged["outcome"] = None
    merged["success"] = None
    merged["confidence_score"] = None

    return merged


def merge_cyber_with_parent(disaster_df: pd.DataFrame, cyber_df: pd.DataFrame) -> pd.DataFrame:
    cyber_df = cyber_df.rename(columns={"hazard_event_id": "source_hazard_event_id"})
    merged = cyber_df.merge(
        disaster_df,
        left_on="parent_hazard_event_id",
        right_on="hazard_event_id",
        how="left",
        suffixes=("", "_parent")
    )

    merged["hazard_event_id"] = merged["parent_hazard_event_id"]
    return merged


def select_master_columns(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = [
        "hazard_event_id",
        "integration_id",
        "state",
        "region",
        "suburb",
        "event_type",
        "severity_score",
        "severity_level",
        "risk_category",
        "start_time",
        "duration_hours",
        "temperature_c",
        "rainfall_mm",
        "humidity_pct",
        "fatalities",
        "injuries",
        "economic_loss_million",
        "affected_population",
        "threat_stream",
        "source_dataset",
        "source_record_id",
        "timestamp",
        "threat_type",
        "attack_vector",
        "impersonation",
        "target",
        "outcome",
        "success",
        "confidence_score",
        "alert_level",
        "misinformation_level",
        "social_media_spike",
        "cyber_frequency_level",
        "risk_score",
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    return df[required_cols]


def export_clean_inputs(disaster_df: pd.DataFrame, misinfo_df: pd.DataFrame, cyber_df: pd.DataFrame) -> None:
    disaster_df.to_csv(DATA_DIR / "parent_disaster_dataset.csv", index=False)
    misinfo_df.to_csv(DATA_DIR / "social_misinformation_dataset.csv", index=False)
    cyber_df.to_csv(DATA_DIR / "cyber_network_threat_dataset.csv", index=False)


def write_validation_note(master_df: pd.DataFrame, cyber_df: pd.DataFrame) -> None:
    missing_parent_links = cyber_df["parent_hazard_event_id"].isna().sum()
    with open(DOCS_DIR / "validation_report.md", "w", encoding="utf-8") as f:
        f.write("# Validation Report\n\n")
        f.write(f"- Master row count: {len(master_df)}\n")
        f.write(f"- Unique hazard_event_id count: {master_df['hazard_event_id'].nunique()}\n")
        f.write(f"- Missing parent links in cyber rows: {missing_parent_links}\n")
        f.write(f"- Missing hazard_event_id in final master: {master_df['hazard_event_id'].isna().sum()}\n")
        f.write(f"- Missing threat_stream in final master: {master_df['threat_stream'].isna().sum()}\n")
        f.write(f"- Duplicate rows in final master: {master_df.duplicated().sum()}\n")


def main() -> None:
    load_settings()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    disaster_df = load_disaster_parent()
    misinfo_df = load_misinfo()
    cyber_df = load_cyber(disaster_df)

    export_clean_inputs(disaster_df, misinfo_df, cyber_df)

    misinfo_master = merge_misinfo_with_parent(disaster_df, misinfo_df)
    cyber_master = merge_cyber_with_parent(disaster_df, cyber_df)

    master_df = pd.concat([
        select_master_columns(misinfo_master),
        select_master_columns(cyber_master),
    ], ignore_index=True)

    master_df.to_csv(DATA_DIR / "master_ai005_dataset.csv", index=False)
    master_df.to_json(DATA_DIR / "master_ai005_dataset.json", orient="records", indent=2)

    write_validation_note(master_df, cyber_df)

    print("Master AI005 dataset generated successfully.")
    print(f"CSV: {DATA_DIR / 'master_ai005_dataset.csv'}")
    print(f"JSON: {DATA_DIR / 'master_ai005_dataset.json'}")


if __name__ == "__main__":
    main()