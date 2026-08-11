# CFPB Complaint Insights Platform

An internal compliance analytics platform for analyzing CFPB complaints and internal customer feedback using AI/NLP.

## Features

- **Data Ingestion**: Rolling 6-month CFPB complaint ingestion via public API; CSV/XLSX file upload
- **AI/NLP Analysis**: Taxonomy classification (CFPB categories), 3-class sentiment analysis, keyword extraction, topic clustering
- **Trend Analytics**: Week-over-week and month-over-month deltas for complaint volume, category counts, sentiment
- **Interactive Dashboard**: React frontend with charts, filters, and drill-down
- **Reporting**: On-demand PDF and CSV export

## Project Structure

```
src/
  api/          # FastAPI REST endpoints
  models/       # SQLAlchemy models and DB session
  services/     # Trend analytics business logic
  nlp/          # Taxonomy classifier, sentiment, keyword extraction, topic clustering
  ingestion/    # CFPB API + file upload pipelines
  reporting/    # PDF (ReportLab) and CSV export
  utils/        # Auth helpers (JWT, bcrypt)
  worker.py     # Celery tasks + beat schedule
config/
  settings.py   # Pydantic settings (env-based)
frontend/
  src/          # React application (MUI + Recharts)
tests/          # Pytest test suite
alembic/        # Database migrations
```

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (for frontend)

## Backend Setup

### 1. Clone and install

```bash
git clone <repo>
cd CFPB-complaint-insights
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, REDIS_URL
```

### 3. Run database migrations

```bash
alembic upgrade head
```

### 4. Start the API

```bash
PYTHONPATH=. uvicorn src.api.main:app --reload
# API available at http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### 5. Start Celery worker and beat scheduler

```bash
PYTHONPATH=. celery -A src.worker worker --loglevel=info
PYTHONPATH=. celery -A src.worker beat --loglevel=info
```

## Frontend Setup

```bash
cd frontend
npm install
npm start
# Frontend available at http://localhost:3000
```

## Docker Compose (all services)

```bash
# Copy and edit .env first
cp .env.example .env
docker-compose up --build
```

Services started: PostgreSQL, Redis, API, Celery worker, Celery beat.

## Running Tests

```bash
PYTHONPATH=. pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/token` | Login (returns JWT) |
| GET | `/complaints/` | List complaints (filterable) |
| GET | `/complaints/{id}` | Get single complaint |
| POST | `/ingest/cfpb` | Trigger CFPB API ingestion |
| POST | `/ingest/upload` | Upload CSV/XLSX file |
| GET | `/analytics/wow` | Week-over-week delta |
| GET | `/analytics/mom` | Month-over-month delta |
| GET | `/analytics/categories` | Category distribution |
| GET | `/analytics/keywords` | Top keywords |
| GET | `/analytics/sentiment` | Sentiment summary |
| GET | `/analytics/low-confidence` | Low-confidence predictions queue |
| GET | `/reports/pdf` | Download PDF report |
| GET | `/reports/csv` | Download CSV data |
| GET | `/health` | Health check |

Full interactive docs available at `http://localhost:8000/docs`.

## Configuration

All settings are read from environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis URL for Celery |
| `SECRET_KEY` | — | JWT signing secret (change in production) |
| `CFPB_LOOKBACK_MONTHS` | `6` | Months of CFPB data to ingest |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | JWT expiry |

## Architecture

```
React Frontend
     │
     ▼
FastAPI (src/api/)
     │
     ├── Auth (JWT)
     ├── Complaints CRUD
     ├── Ingestion trigger
     ├── Analytics endpoints
     └── Report export
           │
           ▼
     SQLAlchemy → PostgreSQL
     NLP pipeline (classifier + sentiment + keywords + clustering)
     Celery → Redis (weekly/monthly scheduled jobs)
```

## NLP Model Details

- **Taxonomy Classifier**: TF-IDF + Logistic Regression trained on CFPB categories; falls back to keyword rules when model not trained. Confidence threshold: 50%.
- **Sentiment Analysis**: Lexicon-based 3-class (Positive / Neutral / Negative).
- **Keyword Extraction**: Document-frequency based term counting.
- **Topic Clustering**: KMeans on TF-IDF vectors.

All NLP outputs include confidence scores; low-confidence predictions are flagged and surfaced in a dedicated queue.
