# Stock Screener

A flexible stock screener for fundamental and technical analysis, with CLI and REST API support.

---

## Features

- Screen stocks by fundamental and technical criteria
- Supports S&P 500, NASDAQ 100, and Dow 30
- Command-line interface (CLI) for quick screening and output (console, JSON, CSV)
- REST API (Flask) for programmatic access
- Easily extensible for new indicators and data sources

---

## Getting Started

### 1. **Clone the Repository**

```sh
git clone https://github.com/yourusername/stock-screener.git
cd stock-screener
```

### 2. **Set Up Python Environment**

It’s recommended to use a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. **Install Dependencies**

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Usage

### **Command-Line Interface (CLI)**

Screen stocks from your terminal:

```sh
python cli.py --index sp500 --criteria "market_cap>1000000000,pe_ratio<40" --limit 5 --output console
```

**Other examples:**

- Output to JSON:
  ```sh
  python cli.py --index nasdaq100 --criteria "market_cap>5000000000" --output json --output-file results.json
  ```
- Output to CSV:
  ```sh
  python cli.py --index dow30 --criteria "sector=Technology" --output csv --output-file results.csv
  ```
- Force reload data:
  ```sh
  python cli.py --index sp500 --criteria "market_cap>1000000000" --reload
  ```

### **REST API**

Start the API server:

```sh
python api.py
```

Example API requests (use `curl` or Postman):

- List indexes:
  ```sh
  curl http://localhost:5000/api/v1/indexes
  ```
- Screen by fundamentals:
  ```sh
  curl -X POST -H "Content-Type: application/json" \
    -d '{"index":"sp500","criteria":{"market_cap":[">",1000000000]}}' \
    http://localhost:5000/api/v1/screen
  ```

---

## Development & Testing

- Run all tests:
  ```sh
  pytest
  ```

---

## Project Structure

```
.
├── cli.py
├── api.py
├── screener.py
├── indicators.py
├── data_fetcher.py
├── requirements.txt
├── .gitignore
├── data/
├── test/
└── ...
```

---

## Notes

- Always quote your criteria if using `<` or `>` in the shell.
- Data and cache files are ignored by git (see `.gitignore`).
- For PostgreSQL or other DB integration, see `database.py` and project plan.

---

## License

MIT License (or your chosen license)
