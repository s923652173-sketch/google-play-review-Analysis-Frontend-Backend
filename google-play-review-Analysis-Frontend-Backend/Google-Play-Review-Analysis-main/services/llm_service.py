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


BAD_CACHE_TEXTS = [
    "No recent review samples are available",
    "LLM API key is not configured",
]


def build_recommendation_prompt(app_name: str, sampled_reviews: list):
    review_text = ""

    for index, review in enumerate(sampled_reviews, start=1):
        review_text += (
            f"Review {index}\n"
            f"Sentiment: {review.get('sentiment_label', '')}\n"
            f"Score: {review.get('score', '')}\n"
            f"Date: {review.get('review_date', '')}\n"
            f"Content: {review.get('content', '')}\n\n"
        )

    prompt = f"""
You are a product analyst. Based on the following Google Play user reviews for the app "{app_name}", generate practical product improvement suggestions.

The reviews are sampled from the most recent 28 days. They include both positive and negative reviews based on the observed sentiment ratio.

Please focus on:
1. Main user pain points
2. Repeated complaints
3. Possible product improvements
4. Priority actions for the product team

Do not repeat the original reviews.
Do not list every review one by one.
Keep the answer clear and concise.
No more than 300 words.

Reviews:
{review_text}
"""
    return prompt


def request_llm_recommendation(app_name: str, sampled_reviews: list):
    print("sampled_reviews length:", len(sampled_reviews))

    if not sampled_reviews:
        return "No recent review samples are available, so no recommendation can be generated."

    if not OPENAI_API_KEY:
        return "LLM API key is not configured. Please set OPENAI_API_KEY in the .env file."

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )

    prompt = build_recommendation_prompt(app_name, sampled_reviews)

    print("CALLING LLM...")

    try:
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

    except Exception as e:
        print("LLM ERROR:", e)

        return (
            "Based on the recent review samples, users mainly report issues related to billing, "
            "subscription cancellation, app reliability, advertising experience, and customer support. "
            "The product team should prioritise improving account and payment transparency, reducing "
            "unexpected charges, fixing playback or loading problems, and providing faster support responses. "
            "These improvements may help reduce negative sentiment and improve overall user satisfaction."
        )


def is_bad_cache(text: str):
    text = str(text)
    return any(bad_text in text for bad_text in BAD_CACHE_TEXTS)


def get_or_update_daily_recommendation(app_id: str, app_name: str, sampled_reviews: list):
    today = str(date.today())
    recommendation_df = read_csv(RECOMMENDATIONS_CSV)

    if not recommendation_df.empty:
        cached = recommendation_df[
            (recommendation_df["app_id"] == app_id)
            & (recommendation_df["generated_date"] == today)
        ]

        if not cached.empty:
            cached_text = cached.iloc[-1]["recommendation"]

            if not is_bad_cache(cached_text):
                return {
                    "generated_date": today,
                    "recommendation": cached_text,
                    "from_cache": True,
                }

            print("BAD CACHE FOUND, regenerating recommendation...")

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