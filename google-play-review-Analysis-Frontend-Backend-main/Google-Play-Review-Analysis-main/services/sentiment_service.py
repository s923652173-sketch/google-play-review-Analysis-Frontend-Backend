import torch
from transformers import pipeline

# Use GPU when available. If CUDA is not available, the model will run on CPU.
device = 0 if torch.cuda.is_available() else -1

sentiment_pipeline = pipeline(
    task="sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    tokenizer="distilbert-base-uncased-finetuned-sst-2-english",
    device=device,
)


def analyse_sentiment(text: str):
    """
    Classify review sentiment into positive or negative using a BERT-family model.

    Returns:
        sentiment_label: "positive" or "negative"
        sentiment_score: confidence score of the predicted class
    """
    if text is None or str(text).strip() == "":
        return "negative", 0.0

    text = str(text)

    result = sentiment_pipeline(
        text[:512],
        truncation=True,
    )[0]

    label = result["label"].lower()
    score = float(result["score"])

    if label == "positive":
        return "positive", score
    return "negative", score
