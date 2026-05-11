import os
import pandas as pd
from config import DATA_DIR, APPS_CSV, REVIEWS_CSV, RECOMMENDATIONS_CSV


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(APPS_CSV):
        pd.DataFrame(columns=[
            "rank",
            "app_id",
            "app_name",
            "developer",
            "developer_link",
            "category",
            "category_link"
        ]).to_csv(APPS_CSV, index=False)

    if not os.path.exists(REVIEWS_CSV):
        pd.DataFrame(columns=[
            "app_id",
            "app_name",
            "user_name",
            "content",
            "score",
            "review_date",
            "sentiment_label",
            "sentiment_score",
            "word_count",
        ]).to_csv(REVIEWS_CSV, index=False)

    if not os.path.exists(RECOMMENDATIONS_CSV):
        pd.DataFrame(columns=[
            "app_id",
            "generated_date",
            "recommendation",
        ]).to_csv(RECOMMENDATIONS_CSV, index=False)


def read_csv(path: str) -> pd.DataFrame:
    ensure_data_files()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def save_csv(df: pd.DataFrame, path: str):
    ensure_data_files()
    df.to_csv(path, index=False)


def append_csv(new_df: pd.DataFrame, path: str):
    ensure_data_files()

    if os.path.exists(path):
        old_df = pd.read_csv(path)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    combined_df.to_csv(path, index=False)
