import unittest
import sys
import os
import subprocess
import json
import csv
import logging
from io import StringIO

# Add the parent directory to the Python path so that app/ is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set logging to ERROR level for all tests
logging.basicConfig(level=logging.ERROR)

CLI_PATH = "app/cli.py"

def run_cli(args):
    """Helper to run the CLI and capture output."""
    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cli_path = os.path.join(project_root, CLI_PATH)
    
    # Run the CLI script with PYTHONPATH set to include the project root
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{project_root}:{env.get('PYTHONPATH', '')}"
    
    try:
        result = subprocess.run(
            ["python", cli_path] + args,
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        return result
    except subprocess.TimeoutExpired:
        raise
    except Exception as e:
        raise

class TestCLI(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cli_path = os.path.join(self.project_root, "app/cli.py")
        
        # Set up environment variables
        self.env = os.environ.copy()
        self.env['PYTHONPATH'] = f"{self.project_root}:{self.env.get('PYTHONPATH', '')}"

    def run_cli(self, args, timeout=60):
        """Helper to run the CLI and capture output"""
        try:
            result = subprocess.run(
                ["python", self.cli_path] + args,
                capture_output=True,
                text=True,
                env=self.env,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"CLI command timed out after {timeout} seconds")
        except Exception as e:
            self.fail(f"Error running CLI: {str(e)}")

    def test_basic_screening(self):
        """Test basic screening with default settings"""
        result = self.run_cli([
            "--index", "dow30",
            "--criteria", "market_cap>1000000000",
            "--limit", "2",
            "--output", "console"
        ])
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Found", result.stdout)
        self.assertIn("Symbol", result.stdout)

    def test_json_output(self):
        """Test JSON output format"""
        result = self.run_cli([
            "--index", "dow30",
            "--criteria", "market_cap>1000000000",
            "--limit", "2",
            "--output", "json"
        ])
        
        self.assertEqual(result.returncode, 0)
        try:
            data = json.loads(result.stdout)
            self.assertIsInstance(data, list)
            self.assertLessEqual(len(data), 2)
            if len(data) > 0:
                self.assertIn('symbol', data[0])
                self.assertIn('name', data[0])
                self.assertIn('price', data[0])
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_csv_output(self):
        """Test CSV output format"""
        result = self.run_cli([
            "--index", "dow30",
            "--criteria", "market_cap>1000000000",
            "--limit", "2",
            "--output", "csv"
        ])
        
        self.assertEqual(result.returncode, 0)
        try:
            # Parse CSV output
            csv_data = list(csv.DictReader(StringIO(result.stdout)))
            self.assertLessEqual(len(csv_data), 2)
            if len(csv_data) > 0:
                # Check for lowercase column names
                self.assertIn('symbol', csv_data[0])
                self.assertIn('name', csv_data[0])
                self.assertIn('price', csv_data[0])
        except Exception as e:
            self.fail(f"Error parsing CSV output: {str(e)}")

    def test_technical_screening(self):
        """Test technical screening criteria"""
        result = self.run_cli([
            "--index", "dow30",
            "--criteria", "rsi>40,ma>100",
            "--limit", "2",
            "--output", "console"
        ])
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Found", result.stdout)

    def test_invalid_criteria(self):
        """Test handling of invalid criteria"""
        result = self.run_cli([
            "--index", "dow30",
            "--criteria", "invalid>1000",
            "--output", "console"
        ])
        
        self.assertEqual(result.returncode, 0)  # Should handle gracefully
        self.assertIn("Found", result.stdout)

    def test_single_index(self):
        """Test a single stock index"""
        result = self.run_cli([
            "--index", "dow30",
            "--criteria", "market_cap>1000000000",
            "--limit", "1",
            "--output", "console"
        ])
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Found", result.stdout)

if __name__ == '__main__':
    unittest.main()