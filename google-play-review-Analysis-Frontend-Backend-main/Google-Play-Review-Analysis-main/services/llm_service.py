import pandas as pd
from datetime import date
from openai import OpenAI

from config import (
    RECOMMENDATIONS_CSV,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
)
from services.csv_service import read_csv, save_csv


def build_recommendation_prompt(app_name: str, sampled_reviews: list):
    review_text = ""

    for index, review in enumerate(sampled_reviews, start=1):
        review_text += (
            f"Review {index}\n"
            f"Sentiment: {review['sentiment_label']}\n"
            f"Score: {review['score']}\n"
            f"Date: {review['review_date']}\n"
            f"Content: {review['content']}\n\n"
        )

    prompt = f"""
You are a product analyst. Based on the following Google Play user reviews for the app "{app_name}", generate practical product improvement suggestions.

The reviews are sampled from the most recent 28 days. They include both positive and negative reviews based on the observed sentiment ratio.

Please provide:
1. Main user pain points
2. Product strengths mentioned by users
3. Recommended improvements for the next update
4. Priority level
5. Short explanation

Reviews:
{review_text}
"""

    return prompt


def request_llm_recommendation(app_name: str, sampled_reviews: list):
    if not sampled_reviews:
        return "No recent review samples are available, so no recommendation can be generated."

    if not OPENAI_API_KEY:
        return "LLM API key is not configured. Please set OPENAI_API_KEY in the .env file."

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )

    prompt = build_recommendation_prompt(app_name, sampled_reviews)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert product improvement analyst.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def get_or_update_daily_recommendation(app_id: str, app_name: str, sampled_reviews: list):
    """Generate recommendation at most once per app per day."""
    today = str(date.today())
    recommendation_df = read_csv(RECOMMENDATIONS_CSV)

    if not recommendation_df.empty:
        cached = recommendation_df[
            (recommendation_df["app_id"] == app_id)
            & (recommendation_df["generated_date"] == today)
        ]

        if not cached.empty:
            return {
                "generated_date": today,
                "recommendation": cached.iloc[-1]["recommendation"],
                "from_cache": True,
            }

    recommendation = request_llm_recommendation(app_name, sampled_reviews)

    new_row = pd.DataFrame([{
        "app_id": app_id,
        "generated_date": today,
        "recommendation": recommendation,
    }])

    recommendation_df = pd.concat([recommendation_df, new_row], ignore_index=True)
    save_csv(recommendation_df, RECOMMENDATIONS_CSV)

    return {
        "generated_date": today,
        "recommendation": recommendation,
        "from_cache": False,
    }
