# Portfolio Pulse Backend

Portfolio Pulse is an educational analytics API that benchmarks a user's portfolio against well-known model allocations like All Weather, Swensen, and a Hybrid blend. The backend is written in **Python + FastAPI** and integrates **Supabase Auth** for protecting user data.

> **Disclaimer:** This application is for informational and educational purposes only. It is **not** investment advice.

## Repository Layout

```
app/
  main.py                  # FastAPI app entrypoint
  api/
    portfolio.py           # Portfolio upload + analytics endpoints
    models.py              # Shared Pydantic schemas
    scoring.py             # Pulse score logic and helpers
  services/
    data_loader.py         # yfinance-powered price utilities
    rebalance.py           # Rebalancing + model selection helpers
  utils/
    auth.py                # Supabase auth dependency
    math_ops.py            # Weight normalization + helpers
README.md
portfolio_pulse_spec.md
requirements.txt
```

## Prerequisites

- Python 3.11+
- Supabase project (URL + anon key) for authentication
- (Optional) `ALLOW_ANON=true` for local testing without Supabase credentials

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="public-anon-key"
# Optional: allow anonymous requests for local testing
export ALLOW_ANON=true
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Authentication

All portfolio endpoints expect a Supabase JWT bearer token in the `Authorization` header (`Bearer <token>`). When `ALLOW_ANON=true` is set, the API will fall back to an in-memory demo user for easier development.

## Key Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `POST` | `/portfolio/upload` | Upload tickers with amounts or weights. Normalizes and stores per user. |
| `GET`  | `/portfolio/score` | Calculates the Portfolio Pulse Score + component breakdown. |
| `GET`  | `/portfolio/model-comparison` | Compares the user portfolio to All Weather, Swensen, and Hybrid portfolios. |
| `GET`  | `/portfolio/rebalance-suggestions` | Generates target weights + suggested trades to align with the closest model. |
| `GET`  | `/health` | Basic readiness probe. |

All numeric outputs are reported as decimals (e.g., weights sum to 1.0). Historical price analytics rely on Yahoo Finance data via `yfinance`. If price downloads fail, conservative fallback assumptions are applied so responses remain stable offline.

## Example Upload Payload

```json
{
  "portfolio": [
    { "ticker": "VTI", "amount": 5000 },
    { "ticker": "TLT", "amount": 2000 },
    { "ticker": "AAPL", "amount": 1000 }
  ]
}
```

After uploading, call `/portfolio/score` to retrieve the score breakdown:

```json
{
  "pulse_score": 74.5,
  "grade": "🟡",
  "breakdown": {
    "diversification": 22.0,
    "resilience": 25.0,
    "return_efficiency": 12.0,
    "risk_balance": 15.5
  },
  "diversification_chart": [
    { "label": "Equities", "weight": 0.52 },
    { "label": "Long Bonds", "weight": 0.28 }
  ],
  "top_suggestions": [
    "Reduce concentration in VTI to below 30%.",
    "Add more bonds to improve drawdown resilience."
  ]
}
```

## Testing Tips

- Use tools like [httpie](https://httpie.io/) or [Bruno](https://www.usebruno.com/) to call the API.
- Mock Supabase locally by setting `ALLOW_ANON=true`.
- Re-run `/portfolio/upload` whenever you want to replace the in-memory holdings.

Enjoy building on top of Portfolio Pulse! 🎯
