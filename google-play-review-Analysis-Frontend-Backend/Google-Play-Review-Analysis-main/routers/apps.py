from fastapi import APIRouter
import pandas as pd

from config import APPS_CSV
from services.csv_service import read_csv, save_csv, append_csv
from services.app_rank_collector import fetch_top_100_apps

router = APIRouter(
    prefix="/apps",
    tags=["Apps"]
)


@router.post("/")
def add_app(app_id: str, app_name: str, category: str = "", developer: str = ""):
    apps_df = read_csv(APPS_CSV)

    if not apps_df[apps_df["app_id"] == app_id].empty:
        return {
            "message": "App already exists",
            "app_id": app_id
        }

    new_app = pd.DataFrame([{
        "rank": "",
        "app_id": app_id,
        "app_name": app_name,
        "developer": developer,
        "developer_link": "",
        "category": category,
        "category_link": ""
    }])

    append_csv(new_app, APPS_CSV)

    return {
        "message": "App added successfully",
        "app_id": app_id,
        "app_name": app_name,
        "developer": developer,
        "category": category
    }


@router.get("/")
def get_apps():
    apps_df = read_csv(APPS_CSV)
    return apps_df.fillna("").to_dict(orient="records")


@router.post("/fetch-top100")
def fetch_and_save_top_100_apps():
    app_list = fetch_top_100_apps()

    if not app_list:
        return {
            "error": "Failed to fetch Top 100 apps from AppBrain."
        }

    new_apps_df = pd.DataFrame(app_list)

    old_apps_df = read_csv(APPS_CSV)

    combined_df = pd.concat(
        [old_apps_df, new_apps_df],
        ignore_index=True
    )

    combined_df = combined_df.drop_duplicates(
        subset=["app_id"],
        keep="last"
    )

    combined_df = combined_df.sort_values(
        by="rank",
        ascending=True
    )

    save_csv(combined_df, APPS_CSV)

    return {
        "message": "Top 100 apps fetched and saved successfully",
        "saved_count": len(new_apps_df),
        "total_apps": len(combined_df)
    }