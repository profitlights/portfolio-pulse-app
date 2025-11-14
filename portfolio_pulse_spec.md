# Portfolio Pulse — Technical Specification (v1)

## Objective
Portfolio Pulse is an investor education and analytics app that ranks and scores a user’s portfolio against leading model portfolios (All Weather, Swensen, Hybrid). It provides a Portfolio Pulse Score, model comparisons, and rebalancing suggestions. This is **not** financial advice — purely analytics and education.

---

## 1. Global Configuration

```json
{
  "starting_value": 100,
  "currency": "USD",
  "rebalance": { "type": "calendar", "frequency": "quarterly" },
  "fees": { "expense_ratio_bps": 15, "trade_cost_bp_per_rebalance": 1 },
  "data": { "source": "yahoo", "interval": "1d", "lookback_years": 15 }
}
```

---

## 2. Model Portfolios

### **All Weather (Ray Dalio)**
```
VTI: 30%
TLT: 40%
IEF: 15%
IAU: 7.5%
DBC: 7.5%
```

### **Swensen (Lazy Princeton Model)**
```
VTI: 30%
VXUS: 15%
VNQ: 20%
TLT: 15%
TIP: 15%
GOLD (IAU): 5%
```

### **Hybrid 50 (All Weather + Swensen Blend)**
```
50% All Weather weights  
50% Swensen weights  
Normalized to 100%
```

---

## 3. User Portfolio Input Format

Users can upload a simple JSON structure:

```json
{
  "portfolio": [
    { "ticker": "VTI", "amount": 5000 },
    { "ticker": "TLT", "amount": 2000 },
    { "ticker": "AAPL", "amount": 1000 }
  ]
}
```

Codex should:
1. Normalize weights  
2. Identify asset class exposures  
3. Compare against model portfolios  

---

## 4. Portfolio Pulse Score

Score range: **0–100**

Formula components:

- **Diversification (0–30 pts)**  
  Compares sector + asset class concentration.

- **Drawdown resilience (0–30 pts)**  
  Based on volatility + historical max drawdown vs model portfolios.

- **Return efficiency (0–20 pts)**  
  Rolling 5-year CAGR relative to models.

- **Risk balance (0–20 pts)**  
  Evaluates bond/equity/gold/commodity balance.

Total Score:  
```
Total = Diversification + Resilience + Return Efficiency + Risk Balance
```

Traffic lights (for UI):
- 80–100: 🟢 Excellent  
- 60–79: 🟡 Moderate  
- 0–59: 🔴 Needs work  

---

## 5. API Endpoints (Codex to generate)

### `POST /portfolio/upload`
Uploads user’s portfolio.

### `GET /portfolio/score`
Returns:
- Pulse Score  
- Breakdown of score components  
- Traffic light  
- Diversification chart  

### `GET /portfolio/model-comparison`
Returns:
- All Weather expected performance  
- Swensen expected performance  
- Hybrid expected performance  
- Historical backtest curves  

### `GET /portfolio/rebalance-suggestions`
Returns:
- Target weights  
- Difference from model portfolio  
- Suggested trade adjustments  

---

## 6. Authentication

Use **Supabase Auth** (email + password, or Google Login).

---

## 7. File Structure (Codex should scaffold)

```
/app
    main.py
    api/
        portfolio.py
        scoring.py
        models.py
    services/
        data_loader.py
        rebalance.py
    utils/
        math_ops.py

requirements.txt
README.md
portfolio_pulse_spec.md
```

---

## 8. Output Examples

### Example Score Output

```json
{
  "pulse_score": 74,
  "grade": "🟡",
  "breakdown": {
    "diversification": 22,
    "resilience": 25,
    "return_efficiency": 12,
    "risk_balance": 15
  },
  "top_suggestions": [
    "Reduce concentration in AAPL from 42% to under 20%",
    "Increase bonds to improve drawdown resilience",
    "Add gold/commodities to improve inflation hedge"
  ]
}
```

---

## 9. Notes For Codex

- Use Yahoo Finance API or yfinance for historical prices  
- Fetch last 10–15 years of data  
- Normalize weights automatically  
- Ensure models can be rebalanced quarterly  
- Keep code modular so we can add more models later (e.g., Buffett 90/10, S&P 500, World Index)

---

## 10. License & Safety

This is **educational, informational analytics**.  
Must include boilerplate:  
“This is not investment advice.”

---

End of spec.
