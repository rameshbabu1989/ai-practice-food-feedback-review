# Customer Feedback Analyzer

A small application that analyzes customer reviews with Google Gemini. Enter multiple reviews in the Streamlit interface, one review per line, and view each analysis in a table. Results can be saved to and loaded from a local SQLite database.

## Features

- Analyzes each review independently through a FastAPI endpoint.
- Reports sentiment (`positive`, `negative`, or `neutral`), a score from 1 to 5, and a one-word theme.
- Shows an error for an individual review if its API request fails, without stopping the remaining reviews.
- Saves successful analyses to SQLite and loads saved history into the results table.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- A Google Gemini API key

## Setup

From the project directory, install the dependencies:

```powershell
uv sync
```

Configure the Gemini API key before starting the API. One option is to create a `.env` file in the project directory:

```text
GEMINI_API_KEY=your-gemini-api-key
```

The API loads this file at startup. Do not commit `.env` or share your API key. Alternatively, set the key in PowerShell before starting the API:

```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
```

## Run the application

Start the API in one terminal:

```powershell
uv run fastapi dev api.py
```

By default, the API is available at `http://127.0.0.1:8000`.

Start Streamlit in a second terminal:

```powershell
uv run streamlit run app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`. Keep both services running while using the app.

The Streamlit app calls `http://127.0.0.1:8000/analyze` by default. To use a different API address, set `ANALYSIS_API_URL` in the terminal where Streamlit will run. For example:

```powershell
$env:ANALYSIS_API_URL = "http://127.0.0.1:8001/analyze"
uv run streamlit run app.py
```

## Use the app

1. Enter one customer review per line.
2. Select **Analyze reviews**. The app sends one request per review.
3. Review the label, score, theme, and any per-review error in the results table.
4. Select **Save results** to store successful analyses.
5. Select **Load history** to display all saved analyses.

The SQLite database is named `feedback.db` and is created automatically in the current working directory when the app starts. Run Streamlit from the project directory so the database stays there.

## API

The FastAPI service exposes `POST /analyze`. It accepts a JSON body containing one review:

```json
{
	"text": "The delivery was quick and the packaging was great."
}
```

It returns an analysis in this format:

```json
{
	"label": "positive",
	"score": 5,
	"theme": "delivery"
}
```
<img width="829" height="843" alt="image" src="https://github.com/user-attachments/assets/e7533f0a-7508-4812-beb5-10693dacbf22" />
