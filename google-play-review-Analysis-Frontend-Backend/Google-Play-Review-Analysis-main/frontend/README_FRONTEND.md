# Frontend Running Guide

## 1. Start backend
Create `.env` in backend root:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.4-mini
```

Install and run backend:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## 2. Start frontend
Open a second terminal in the project root:

```bash
cd frontend
python -m http.server 5173
```

Then open:

```text
http://127.0.0.1:5173
```

## 3. Recommended demo flow
1. Click **Fetch Top 100**.
2. Select an app.
3. Set months/reviews smaller first, for example `2` and `20`.
4. Click **Collect Reviews**.
5. View trend chart, review samples, and AI recommendation.
