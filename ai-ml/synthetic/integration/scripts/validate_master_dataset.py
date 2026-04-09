from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def main() -> None:
    df = pd.read_csv(DATA_DIR / "master_ai005_dataset.csv")

    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Unique hazard_event_id:", df["hazard_event_id"].nunique())
    print("Missing hazard_event_id:", df["hazard_event_id"].isna().sum())
    print("Missing threat_stream:", df["threat_stream"].isna().sum())
    print("Duplicates:", df.duplicated().sum())
    print("\nNull counts:\n")
    print(df.isna().sum())


if __name__ == "__main__":
    main()