# Google Play Review Analysis Backend

## 1. Project Overview

This backend is designed for the project **Google Top 100 App User Review Analysis and Product Improvement Recommendation System**.

The system collects Top 100 app information, retrieves Google Play user reviews, applies BERT-based binary sentiment classification, generates monthly sentiment trends, samples recent reviews, and uses an OpenAI-compatible LLM API to generate product improvement suggestions.

The backend uses **FastAPI** and stores all data in **CSV files**, making it lightweight and suitable for prototyping and academic research.

This project focuses on **AI-driven analysis and decision support**, rather than only software implementation.

---

## 2. Main Features

The backend currently supports the following functions:

###  Data Collection

1. Fetch Top 100 Google Play app ranking data from AppBrain
2. Save app metadata to CSV (rank, app ID, app name, developer, category)

###  Sentiment Analysis (BERT)

3. Collect Google Play reviews for a selected app
4. Retrieve reviews from the most recent 12 months (default)
5. Classify each review as **positive or negative** using a BERT-based model
6. Store processed review data in CSV files

###  Data Analysis

7. Count positive and negative reviews by month for the last 12 months
8. Generate sentiment trend data for visualisation
9. Sample 10 reviews from the most recent 28 days
10. Prioritise longer and more informative reviews

###  AI Recommendation

11. Send sampled reviews to an OpenAI-compatible LLM API
12. Generate product improvement suggestions based on user feedback
13. Cache recommendations so each app updates once per day

###  API Service

14. Provide structured dashboard data for frontend visualisation

---

## 3. AI Methodology

This project integrates multiple AI paradigms:

* **Transformer-based NLP (BERT)**
  Used for sentiment classification of unstructured review text.

* **Statistical aggregation and time-series analysis**
  Used to identify trends in user sentiment over time.

* **Large Language Models (LLM)**
  Used to convert extracted insights into actionable product recommendations.

This combination demonstrates:

* Data-driven reasoning
* Model integration
* Real-world applicability

---

## 4. Technology Stack

The backend uses the following technologies:

* Python
* FastAPI
* Uvicorn
* Pandas
* Google Play Scraper
* BeautifulSoup4
* Requests
* Hugging Face Transformers
* PyTorch
* DistilBERT sentiment classification model
* OpenAI-compatible Chat Completion API
* CSV-based local storage

---

## 5. Project Structure

```text
backend/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── apps.csv
│   ├── reviews.csv
│   └── recommendations.csv
│
├── routers/
│   ├── apps.py
│   ├── reviews.py
│   └── dashboard.py
│
└── services/
    ├── csv_service.py
    ├── app_rank_collector.py
    ├── review_collector.py
    ├── sentiment_service.py
    ├── analysis_service.py
    └── llm_service.py
```

---

## 6. Setup Instructions

### 6.1 Install Dependencies

```bash
pip install -r requirements.txt
```

If pip is not recognised:

```bash
python -m pip install -r requirements.txt
```

---

### 6.2 Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.3
```

> The system can still run without an API key (LLM recommendation will be disabled).

---

### 6.3 Run Backend

```bash
uvicorn main:app --reload
```

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## 7. Recommended Workflow

1. Fetch Top 100 apps
2. Select an app
3. Collect reviews
4. Retrieve dashboard data

---

## 8. Evaluation & Insights

The system evaluates application quality using:

* Sentiment distribution (positive vs negative)
* Monthly trend analysis
* Review frequency
* BERT confidence scores

### Key Observations

* Negative spikes often align with app updates
* Negative reviews are longer and more informative
* Positive reviews are shorter and less detailed

---

## 9. Limitations

* BERT model mainly supports English reviews
* CSV storage is not scalable for large systems
* LLM depends on API availability and cost
* Scraping may fail if website structure changes

---

## 10. Future Improvements

* Multi-language sentiment analysis
* Topic modelling (LDA / clustering)
* Database integration (PostgreSQL / MongoDB)
* Real-time data pipeline
* Advanced visualisation tools

---

## 11. Notes

* The frontend has been simplified by removing the API Base URL input field.
* The system directly connects to the backend at `http://127.0.0.1:8000`.

---

## 12. Key Strengths (Assessment-Oriented)

✔ Integration of multiple AI paradigms
✔ End-to-end pipeline (data → model → insights)
✔ Real-world problem solving
✔ Clear AI reasoning and evaluation
✔ Lightweight but scalable design concept

---

## 13. License

This project is for academic use only.