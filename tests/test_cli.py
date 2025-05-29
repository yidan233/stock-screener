import unittest
import sys
import os
import subprocess
import json
import csv

# Add the parent directory to the Python path so that app/ is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (If you have a cli function, uncomment and replace with your actual import, e.g.:
# from app.cli import run_cli
# )

CLI_PATH = "app/cli.py"

def run_cli(args):
    """Helper to run the CLI and capture output."""
    result = subprocess.run(
        ["python", CLI_PATH] + args,
        capture_output=True,
        text=True
    )
    return result

def test_console_output():
    result = run_cli([
        "--index", "dow30",
        "--criteria", "market_cap>1000000000,pe_ratio<40",
        "--limit", "3",
        "--output", "console"
    ])
    assert "Found" in result.stdout
    assert "Symbol" in result.stdout
    assert result.returncode == 0

def test_json_output(tmp_path):
    out_file = tmp_path / "results.json"
    result = run_cli([
        "--index", "dow30",
        "--criteria", "market_cap>1000000000,pe_ratio<40",
        "--limit", "2",
        "--output", "json",
        "--output-file", str(out_file)
    ])
    assert out_file.exists()
    with open(out_file) as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) <= 2

def test_csv_output(tmp_path):
    out_file = tmp_path / "results.csv"
    result = run_cli([
        "--index", "dow30",
        "--criteria", "market_cap>1000000000,pe_ratio<40",
        "--limit", "2",
        "--output", "csv",
        "--output-file", str(out_file)
    ])
    assert out_file.exists()
    with open(out_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) <= 2
    assert "symbol" in rows[0] or "Symbol" in rows[0]

def test_default_criteria():
    result = run_cli([
        "--index", "dow30",
        "--limit", "1",
        "--output", "console"
    ])
    assert "Found" in result.stdout
    assert result.returncode == 0

def test_reload_flag():
    result = run_cli([
        "--index", "dow30",
        "--criteria", "market_cap>1000000000",
        "--limit", "1",
        "--reload"
    ])
    assert "Loading data" in result.stdout or "Fetched" in result.stdout
    assert result.returncode == 0

def test_invalid_criteria():
    result = run_cli([
        "--index", "dow30",
        "--criteria", "not_a_field>100",
        "--limit", "1",
        "--output", "console"
    ])
    # Should not crash, may return 0 results
    assert result.returncode == 0

def test_help():
    result = subprocess.run(
        ["python", CLI_PATH, "--help"],
        capture_output=True,
        text=True
    )
    assert "usage:" in result.stdout
    assert "--criteria" in result.stdout

if __name__ == '__main__':
    unittest.main()

