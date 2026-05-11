from datetime import datetime
from collections import defaultdict

from google_play_scraper import reviews, Sort


def get_month_key(review_date: datetime):
    """
    Convert review date to month key.
    Example: 2026-04-20 -> 2026-04
    """
    return review_date.strftime("%Y-%m")


def get_recent_month_keys(months_back: int = 12):
    """
    Generate recent month keys including current month.

    Example:
    If current month is 2026-05 and months_back=12,
    return:
    2026-05, 2026-04, ..., 2025-06
    """
    today = datetime.today()

    month_keys = []

    year = today.year
    month = today.month

    for _ in range(months_back):
        month_keys.append(f"{year:04d}-{month:02d}")

        month -= 1

        if month == 0:
            month = 12
            year -= 1

    return set(month_keys)


def get_oldest_allowed_month(months_back: int = 12):
    """
    Get the oldest month key allowed.
    This is used to stop fetching when reviews are older than target range.
    """
    recent_month_keys = sorted(get_recent_month_keys(months_back))
    return recent_month_keys[0]


def collect_reviews_from_google_play(
    app_package_name: str,
    months_back: int = 12,
    reviews_per_month: int = 100,
    batch_size: int = 200,
    max_batches: int = 80
):
    """
    Collect Google Play reviews by month.

    The function fetches reviews in newest-first order, then groups reviews by month.
    It keeps at most `reviews_per_month` reviews for each month in the most recent
    `months_back` months.

    Args:
        app_package_name: Google Play package name.
        months_back: Number of recent months to collect.
        reviews_per_month: Maximum reviews to keep for each month.
        batch_size: Number of reviews fetched per request.
        max_batches: Safety limit to avoid endless fetching.

    Returns:
        list[dict]: Collected reviews.
    """

    target_months = get_recent_month_keys(months_back)
    oldest_month = get_oldest_allowed_month(months_back)

    monthly_counts = defaultdict(int)
    collected_reviews = []
    all_fetched_reviews = []

    continuation_token = None
    batch_count = 0

    while batch_count < max_batches:
        batch_count += 1

        result, continuation_token = reviews(
            app_package_name,
            lang="en",
            country="au",
            sort=Sort.NEWEST,
            count=batch_size,
            continuation_token=continuation_token
        )

        print("APP:", app_package_name)
        print("BATCH:", batch_count)
        print("RESULT COUNT:", len(result))
        
        if not result:
            break

        should_stop = False

        for item in result:
            review_date = item.get("at")

            if not review_date:
               continue

            all_fetched_reviews.append({
               "user_name": item.get("userName"),
               "content": item.get("content"),
               "score": item.get("score"),
               "review_date": review_date
             })

            month_key = get_month_key(review_date)

            if not review_date:
                continue

            month_key = get_month_key(review_date)

            if month_key < oldest_month:
                should_stop = True
                continue

            if month_key not in target_months:
                continue

            if monthly_counts[month_key] >= reviews_per_month:
                continue

            collected_reviews.append({
                "user_name": item.get("userName"),
                "content": item.get("content"),
                "score": item.get("score"),
                "review_date": review_date
            })

            monthly_counts[month_key] += 1

        all_months_completed = all(
            monthly_counts[month_key] >= reviews_per_month
            for month_key in target_months
        )

        if all_months_completed:
            break

        if should_stop:
            break

        if continuation_token is None:
            break

    if collected_reviews:
        print("FINAL REVIEWS:", len(collected_reviews))    
        return collected_reviews

    return all_fetched_reviews[:months_back * reviews_per_month] 