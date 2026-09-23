# Project: Financial Red-Flag Screener

## Goal
Screen 15-20 listed Indian companies in ONE sector (Pharma) for financial distress
and earnings-manipulation risk using Altman Z'' score, Piotroski F-score and
Beneish M-score, plus custom red flags. Final outputs: a ranked Excel watchlist
and a written sector note.

## About me
I'm a master's in analytics student building this for my CV. I must understand
and explain every line in interviews. So:
- Explain your reasoning before and after writing code.
- Keep code simple and readable. No clever one-liners.
- Add comments explaining the finance logic, not just the Python.

## Environment
- Windows, PowerShell, VS Code. Python 3.14 in a virtual env at .venv.
- Libraries: pandas, numpy, yfinance, openpyxl, matplotlib, jupyter, pytest.

## Folder structure
- data/raw: untouched downloads (never edit these)
- data/processed: cleaned tables, ratios, scores
- src: reusable Python functions
- notebooks: exploration and charts
- tests: pytest tests for calculations
- outputs: Excel watchlist, chart images
- reports: sector note, manual Excel check

## Rules
- Never invent or hardcode financial data. If a field is missing, use NaN and log it.
- Every formula function needs a docstring with the formula written out.
- Ask me before making design decisions (thresholds, definitions, dropping companies).
- Do only the step I ask for. Don't jump ahead.