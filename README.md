# GREC — Game Recommendation Engine

GREC lets you search for a Steam game and get a ranked list of similar titles. Recommendations are driven by **content-based filtering** (tags, genres, and descriptions) combined with a Wilson score quality boost. Collaborative filtering is not supported yet.

## How it works

1. **Pipeline** — downloads the [Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset) from Kaggle, cleans the data, builds a composite feature vector per game, and stores everything in PostgreSQL via `pgvector`.
2. **Backend** — a FastAPI app that serves game search, detail, and recommendation endpoints.
3. **Frontend** — a React + Vite app where users search for a game and explore similar titles.

The `/notebooks` directory contains experimentation and analysis covering the data cleaning and feature engineering decisions.

## Running locally

(coming soon)


## Running tests

```bash
pytest
```

## Tech stack

- **Feature store** — PostgreSQL + pgvector
- **Embeddings** — `sentence-transformers`
- **Backend** — FastAPI + SQLModel
- **Frontend** — React + Vite + TanStack Query
- **CI** — GitHub Actions