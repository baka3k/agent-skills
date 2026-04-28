# Estimation Formulas

1. Base WBS effort:

`wbs_pm = sum(module_base_pm * complexity_multiplier)`

2. Risk-adjusted base effort:

`base_pm = wbs_pm * (1 + min(risk_buffer_sum, 0.30))`

3. Effort range:

- `best_pm = 0.85 * base_pm`
- `worst_pm = 1.30 * base_pm`

4. Cost:

- `fixed_price_base_cost = base_pm * blended_monthly_rate * 1.15`
- `tm_base_cost = sum(role_pm * role_rate)`
