"""
Download annual financial statements for every company in data/companies.csv.

For each ticker we download three ANNUAL statements from Yahoo Finance:
- Balance sheet:    what the company owns (assets) and owes (liabilities),
                    plus shareholders' equity, at each fiscal year end.
- Income statement: revenue, costs and profit earned over each fiscal year.
- Cash flow:        cash actually received and paid out over each fiscal year.

Why all three: the Altman Z'', Piotroski F and Beneish M scores each combine
items from more than one statement (e.g. profit from the income statement
divided by total assets from the balance sheet), and most items are compared
year-on-year, so we need several years of each.

Each statement is saved unchanged as a CSV in data/raw/ (raw data is never
edited). A log of what worked is saved to data/processed/fetch_log.csv.

Run from the project root:
    python src/fetch_financials.py
"""

import os
import time
from datetime import date

import pandas as pd
import yfinance as yf

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# Ticker list built in Step 1 by src/prepare_companies.py.
COMPANIES_FILE = "data/companies.csv"

# Where the downloaded statements go (gitignored; re-created by this script).
RAW_DIR = "data/raw"

# One row per ticker per statement, saying whether the download worked.
LOG_FILE = "data/processed/fetch_log.csv"

# Seconds to wait between tickers so we don't send Yahoo too many requests
# in a short time (which can get us temporarily blocked).
PAUSE_SECONDS = 1.5

# Our file-name label -> the yfinance attribute that returns that statement.
# These attributes return ANNUAL figures. The quarterly versions have
# different names (e.g. quarterly_balance_sheet), which we do not use.
STATEMENTS = {
    "balance_sheet": "balance_sheet",
    "income_statement": "income_stmt",
    "cash_flow": "cashflow",
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def load_tickers():
    """Read companies.csv and return the tickers as a list, e.g. ['ABBOTINDIA.NS', ...]."""
    companies = pd.read_csv(COMPANIES_FILE)
    return companies["ticker"].tolist()


def ticker_to_filename_prefix(ticker):
    """
    Turn a Yahoo ticker into a safe file-name prefix.

    "CIPLA.NS" -> "CIPLA_NS"
    (A dot in the middle of a file name can be confused with the extension.)
    """
    return ticker.replace(".", "_")


def make_log_row(ticker, label, status, n_years, n_line_items):
    """Build one row of the fetch log as a dictionary."""
    return {
        "ticker": ticker,
        "statement": label,
        "status": status,
        "n_years": n_years,
        "n_line_items": n_line_items,
        "download_date": date.today().isoformat(),
    }


def years_with_data(table):
    """
    Return the fiscal year-end dates (as 'YYYY-MM-DD' text) whose column
    has at least one non-blank value.

    Yahoo sometimes adds an extra, older year column that is almost or
    entirely blank. We don't count a fully blank column as a real year.
    Indian companies mostly use a 31 March year end, so expect dates
    like 2025-03-31 (= fiscal year FY2024-25).
    """
    years = []
    for column in table.columns:
        # notna() marks each cell True if it holds a value; any() asks
        # "is at least one cell in this column filled in?"
        if table[column].notna().any():
            years.append(pd.Timestamp(column).strftime("%Y-%m-%d"))
    # Oldest first, which is easier to read in the progress output.
    years.sort()
    return years


# ---------------------------------------------------------------------------
# Downloading
# ---------------------------------------------------------------------------

def fetch_statement(stock, ticker, label, attribute):
    """
    Download one annual statement for one company and save it to data/raw/.

    Status meanings:
      OK     - table downloaded and saved
      EMPTY  - no error, but Yahoo returned an empty table (nothing saved)
      FAILED - an error happened while downloading or saving

    Returns one log row (a dictionary).
    """
    try:
        # getattr(stock, "balance_sheet") is the same as stock.balance_sheet,
        # but lets us choose the attribute name from a variable.
        # The result is a table: rows = line items (e.g. "Total Assets"),
        # columns = fiscal year-end dates.
        table = getattr(stock, attribute)

        if table is None or table.empty:
            print(f"    EMPTY   {label:<17} Yahoo returned no data")
            return make_log_row(ticker, label, "EMPTY", 0, 0)

        # Save the table exactly as downloaded. The line-item names are the
        # row index, so we label that first column "line_item".
        file_name = ticker_to_filename_prefix(ticker) + "_" + label + ".csv"
        file_path = os.path.join(RAW_DIR, file_name)
        table.to_csv(file_path, index_label="line_item")

        years = years_with_data(table)
        n_line_items = len(table)
        print(f"    OK      {label:<17} {len(years)} years: {', '.join(years)}"
              f"  | {n_line_items} line items")
        return make_log_row(ticker, label, "OK", len(years), n_line_items)

    except Exception as error:
        # Network problems, Yahoo changes or disk errors end up here.
        # We log the failure and carry on with the next statement.
        print(f"    FAILED  {label:<17} {error}")
        return make_log_row(ticker, label, "FAILED", 0, 0)


def fetch_company(ticker):
    """
    Download all three annual statements for one ticker.

    Returns a list of three log rows (one per statement).
    """
    rows = []
    try:
        # One Ticker object per company. The statements themselves are
        # only downloaded when we ask for each attribute below.
        stock = yf.Ticker(ticker)
        for label, attribute in STATEMENTS.items():
            row = fetch_statement(stock, ticker, label, attribute)
            rows.append(row)
    except Exception as error:
        # Safety net: if something unexpected breaks for this ticker,
        # mark any statements we didn't reach as FAILED and move on.
        print(f"    FAILED  unexpected error for {ticker}: {error}")
        done_labels = [row["statement"] for row in rows]
        for label in STATEMENTS:
            if label not in done_labels:
                rows.append(make_log_row(ticker, label, "FAILED", 0, 0))
    return rows


# ---------------------------------------------------------------------------
# Log and summary
# ---------------------------------------------------------------------------

def save_log(rows):
    """Save the list of log rows to LOG_FILE (overwritten each run) and return it as a table."""
    log = pd.DataFrame(rows)
    log.to_csv(LOG_FILE, index=False)
    print(f"Saved fetch log ({len(log)} rows) to {LOG_FILE}")
    return log


def print_summary(log):
    """Print counts of OK / EMPTY / FAILED and list anything that did not work."""
    n_ok = (log["status"] == "OK").sum()
    n_empty = (log["status"] == "EMPTY").sum()
    n_failed = (log["status"] == "FAILED").sum()

    # A company is "complete" if all three of its statements are OK.
    complete_tickers = []
    for ticker in log["ticker"].unique():
        company_rows = log[log["ticker"] == ticker]
        if (company_rows["status"] == "OK").all():
            complete_tickers.append(ticker)

    print()
    print(f"Tickers processed:          {log['ticker'].nunique()}")
    print(f"Tickers with all 3 OK:      {len(complete_tickers)}")
    print(f"Statements OK:              {n_ok}")
    print(f"Statements EMPTY:           {n_empty}")
    print(f"Statements FAILED:          {n_failed}")

    problems = log[log["status"] != "OK"]
    if len(problems) > 0:
        print()
        print("Not OK:")
        for index, row in problems.iterrows():
            print(f"  {row['status']:<7} {row['ticker']:<16} {row['statement']}")


# ---------------------------------------------------------------------------
# Main: runs only when the file is executed directly, not when imported
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Make sure the output folders exist (data/raw is gitignored, so a fresh
    # clone of the repo won't have it).
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    tickers = load_tickers()
    all_rows = []

    for number, ticker in enumerate(tickers, start=1):
        print(f"[{number}/{len(tickers)}] {ticker}")
        company_rows = fetch_company(ticker)
        all_rows.extend(company_rows)

        # Pause between tickers (not after the last one).
        if number < len(tickers):
            time.sleep(PAUSE_SECONDS)

    print()
    fetch_log = save_log(all_rows)
    print_summary(fetch_log)
