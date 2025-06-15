import requests
import json
from datetime import datetime

def test_stock_endpoint():
    base_url = "http://localhost:5000"
    
    # Test cases
    test_symbols = ["AAPL", "MSFT", "GOOGL", "INVALID"]
    
    for symbol in test_symbols:
        print(f"\nTesting symbol: {symbol}")
        print("=" * 50)
        
        try:
            # Make the request
            response = requests.get(f"{base_url}/api/v1/stock/{symbol}")
            
            # Print status code
            print(f"Status Code: {response.status_code}")
            
            # Try to parse JSON response
            try:
                data = response.json()
                
                if response.status_code == 200:
                    # Print basic info
                    print("\nBasic Information:")
                    print(f"Symbol: {data['symbol']}")
                    print(f"Name: {data['info'].get('shortName', 'N/A')}")
                    print(f"Sector: {data['info'].get('sector', 'N/A')}")
                    print(f"Current Price: ${data['info'].get('currentPrice', 'N/A')}")
                    
                    # Print historical data summary
                    if data['historical']:
                        print("\nHistorical Data Summary:")
                        print(f"Number of days: {len(data['historical']['dates'])}")
                        print(f"Latest date: {data['historical']['dates'][-1]}")
                        print(f"Latest close: ${data['historical']['close'][-1]}")
                else:
                    # Print error message
                    print(f"Error: {data.get('error', 'Unknown error')}")
                    
            except json.JSONDecodeError:
                print("Error: Could not parse JSON response")
                print("Response content:", response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")

if __name__ == "__main__":
    test_stock_endpoint() 