import pandas as pd


def get_monthly_sentiment_trend(reviews_df: pd.DataFrame, app_id: str):
    """Return positive and negative review counts for the latest 12 months."""
    if reviews_df.empty:
        return []

    df = reviews_df[reviews_df["app_id"] == app_id].copy()

    if df.empty:
        return []

    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df = df.dropna(subset=["review_date"])

    if df.empty:
        return []

    today = pd.Timestamp.today()
    start_month = today.to_period("M") - 11

    df["month"] = df["review_date"].dt.to_period("M")

    monthly = (
        df.groupby(["month", "sentiment_label"])
        .size()
        .reset_index(name="count")
    )

    result = []

    for period in pd.period_range(start=start_month, periods=12, freq="M"):
        month_data = monthly[monthly["month"] == period]

        positive_count = int(
            month_data[month_data["sentiment_label"] == "positive"]["count"].sum()
        )
        negative_count = int(
            month_data[month_data["sentiment_label"] == "negative"]["count"].sum()
        )

        result.append({
            "month": str(period),
            "positive_count": positive_count,
            "negative_count": negative_count,
        })

    return result


def sample_recent_reviews(reviews_df: pd.DataFrame, app_id: str, sample_size: int = 10):
    """
    Sample reviews from the latest 28 days.

    Sampling rule:
    1. Preserve the positive-negative ratio in the recent 28-day review set.
    2. Select 10 reviews in total.
    3. Within each sentiment class, select reviews by descending word count.
    4. Return the final sampled reviews sorted by descending word count.
    """
    if reviews_df.empty:
        return []

    df = reviews_df[reviews_df["app_id"] == app_id].copy()

    if df.empty:
        return []

    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df = df.dropna(subset=["review_date"])

    if df.empty:
        return []

    today = pd.Timestamp.today()
    start_date = today - pd.Timedelta(days=28)

    recent_df = df[df["review_date"] >= start_date].copy()

    if recent_df.empty:
        return []

    recent_df["word_count"] = recent_df["content"].fillna("").apply(
        lambda x: len(str(x).split())
    )

    total_count = len(recent_df)
    positive_df = recent_df[recent_df["sentiment_label"] == "positive"].copy()
    negative_df = recent_df[recent_df["sentiment_label"] == "negative"].copy()

    positive_ratio = len(positive_df) / total_count
    positive_sample_count = round(sample_size * positive_ratio)
    negative_sample_count = sample_size - positive_sample_count

    if len(positive_df) == 0:
        positive_sample_count = 0
        negative_sample_count = sample_size

    if len(negative_df) == 0:
        negative_sample_count = 0
        positive_sample_count = sample_size

    positive_sample_count = min(positive_sample_count, len(positive_df))
    negative_sample_count = min(negative_sample_count, len(negative_df))

    positive_samples = (
        positive_df.sort_values(by="word_count", ascending=False)
        .head(positive_sample_count)
    )

    negative_samples = (
        negative_df.sort_values(by="word_count", ascending=False)
        .head(negative_sample_count)
    )

    sampled_df = pd.concat([positive_samples, negative_samples], ignore_index=False)

    if len(sampled_df) < min(sample_size, len(recent_df)):
        remaining_df = recent_df.drop(sampled_df.index, errors="ignore")
        remaining_df = remaining_df.sort_values(by="word_count", ascending=False)
        extra_needed = min(sample_size, len(recent_df)) - len(sampled_df)
        sampled_df = pd.concat([sampled_df, remaining_df.head(extra_needed)], ignore_index=False)

    sampled_df = sampled_df.sort_values(by="word_count", ascending=False).head(sample_size)

    result = []

    for _, row in sampled_df.iterrows():
        result.append({
            "content": str(row["content"]),
            "score": int(row["score"]),
            "review_date": str(pd.to_datetime(row["review_date"]).date()),
            "sentiment_label": row["sentiment_label"],
            "sentiment_score": float(row["sentiment_score"]),
            "word_count": int(row["word_count"]),
        })

    return result
