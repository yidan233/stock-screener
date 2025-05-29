# created a flask based REST API for the stock screener 

from ast import arg
from flask import Flask, request, jsonify
import logging
import traceback
from datetime import datetime
from screener import StockScreener
from flask import Flask, request, jsonify, render_template_string

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize stock screener
screener = StockScreener()

@app.route('/api/v1/indexes', methods=['GET'])
def get_indexes():
    return jsonify({
        'indexes': ['sp500', 'nasdaq100', 'dow30']
    })

@app.route('/api/v1/symbols/<index>', methods=['GET'])

# return stock symbols for a given index
def get_symbols(index):
    try:
        symbols = screener.data_fetcher.get_stock_symbols(index=index)
        return jsonify({
            'index': index,
            'count': len(symbols),
            'symbols': symbols
        })
    except Exception as e:
        logger.error(f"Error getting symbols for {index}: {e}")
        return jsonify({
            'error': str(e)
        }), 400

# get info for a specific stock symbol
@app.route('/api/v1/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    try:
        # hasattr to check if screnner has stock_data attribute
        if not hasattr(screener, 'stock_data') or not screener.stock_data:
            screener.load_data([symbol])
        elif symbol not in screener.stock_data:
            data = screener.data_fetcher.fetch_yfinance_data([symbol])
            if data:
                screener.stock_data[symbol] = data[symbol]
        
        if symbol not in screener.stock_data:
            return jsonify({
                'error': f"Could not find data for symbol: {symbol}"
            }), 404
        
        # Get the data
        stock_data = screener.stock_data[symbol]
        info = stock_data.get('info', {})
        # only respond these field 
        key_info_fields = [
            'symbol', 'shortName', 'longName', 'sector', 'industry',
            'marketCap', 'currentPrice', 'trailingPE', 'forwardPE',
            'dividendYield', 'beta', 'fiftyTwoWeekHigh', 'fiftyTwoWeekLow'
        ]
        
        filtered_info = {field: info.get(field) for field in key_info_fields if field in info}
        
        historical = {}
        if 'historical' in stock_data and not stock_data['historical'].empty:
            hist = stock_data['historical']
            historical = {
                'dates': hist.index.strftime('%Y-%m-%d').tolist(),
                'open': hist['Open'].tolist(),
                'high': hist['High'].tolist(),
                'low': hist['Low'].tolist(),
                'close': hist['Close'].tolist(),
                'volume': hist['Volume'].tolist()
            }
        
        response = {
            'symbol': symbol,
            'info': filtered_info,
            'historical': historical
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error getting data for {symbol}: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 400

@app.route('/api/v1/screen', methods=['POST'])
def screen_stocks():
    try:
        # reads the json body from the request 
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        # get parameters
        index = data.get('index', 'sp500')
        criteria = data.get('criteria', {})
        limit = data.get('limit', 50)
        reload = data.get('reload', False)
        
        # Validate criteria
        if not criteria:
            return jsonify({
                'error': 'No screening criteria provided'
            }), 400
        
       
        symbols = screener.data_fetcher.get_stock_symbols(index=index)
        screener.load_data(symbols, reload=reload)
        results = screener.screen_stocks(criteria, limit=limit)
        
        return jsonify({
            'count': len(results),
            'stocks': results
        })
    
    except Exception as e:
        logger.error(f"Error screening stocks: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 400

@app.route('/api/v1/technical', methods=['POST'])
def technical_screen():
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        

        index = data.get('index', 'sp500')
        criteria = data.get('criteria', {})
        limit = data.get('limit', 50)
        reload = data.get('reload', False)

        if not criteria:
            return jsonify({
                'error': 'No screening criteria provided'
            }), 400

        symbols = screener.data_fetcher.get_stock_symbols(index=arg.index)
        screener.load_data(symbols, reload=reload)
        results = screener.screen_by_technical(criteria)

        if limit and len(results) > limit:
            results = results[:limit]
        
        return jsonify({
            'count': len(results),
            'stocks': results
        })
    
    except Exception as e:
        logger.error(f"Error in technical screening: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 400

@app.route('/api/v1/combined', methods=['POST'])
def combined_screen():
    try:
 
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
      
        index = data.get('index', 'sp500')
        fundamental = data.get('fundamental', {})
        technical = data.get('technical', {})
        limit = data.get('limit', 50)
        reload = data.get('reload', False)
        

        if not fundamental and not technical:
            return jsonify({
                'error': 'No screening criteria provided'
            }), 400
        
        symbols = screener.data_fetcher.get_stock_symbols(index=index)
        screener.load_data(symbols, reload=reload)
        results = screener.create_combined_screen(fundamental, technical, limit=limit)
        
        return jsonify({
            'count': len(results),
            'stocks': results
        })
    
    except Exception as e:
        logger.error(f"Error in combined screening: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 400

if __name__ == '__main__':
    try:
        logger.info("Preloading some stock data...")
        symbols = screener.data_fetcher.get_stock_symbols(index='dow30')  # Just the Dow 30 for quick startup
        screener.load_data(symbols)
        logger.info(f"Preloaded data for {len(symbols)} stocks")
    except Exception as e:
        logger.error(f"Error preloading data: {e}")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)

API_DOCS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Screener API</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        code {
            font-family: monospace;
            background-color: #f1f1f1;
            padding: 2px 4px;
            border-radius: 3px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <h1>Stock Screener API</h1>
    <p>Welcome to the Stock Screener API. Below you'll find documentation for all available endpoints.</p>
    
    <h2>Available Endpoints</h2>
    
    <h3>1. Get Available Stock Indexes</h3>
    <p><code>GET /api/v1/indexes</code></p>
    <p>Returns a list of available stock indexes that can be used for screening.</p>
    <pre>curl http://localhost:5000/api/v1/indexes</pre>
    
    <h3>2. Get Symbols for an Index</h3>
    <p><code>GET /api/v1/symbols/{index}</code></p>
    <p>Returns a list of stock symbols for the specified index.</p>
    <pre>curl http://localhost:5000/api/v1/symbols/dow30</pre>
    
    <h3>3. Get Data for a Specific Stock</h3>
    <p><code>GET /api/v1/stock/{symbol}</code></p>
    <p>Returns detailed information for a specific stock, including fundamental data and historical prices.</p>
    <pre>curl http://localhost:5000/api/v1/stock/AAPL</pre>
    
    <h3>4. Screen Stocks Based on Fundamental Criteria</h3>
    <p><code>POST /api/v1/screen</code></p>
    <p>Screens stocks based on fundamental criteria.</p>
    <pre>curl -X POST \\
  -H "Content-Type: application/json" \\
  -d '{
    "index": "sp500",
    "criteria": {
      "market_cap": [">", 100000000000],
      "pe_ratio": ["<", 20],
      "dividend_yield": [">", 0.02],
      "sector": "Technology"
    },
    "limit": 10
  }' \\
  http://localhost:5000/api/v1/screen</pre>
    
    <h3>5. Screen Stocks Based on Technical Criteria</h3>
    <p><code>POST /api/v1/technical</code></p>
    <p>Screens stocks based on technical indicators.</p>
    <pre>curl -X POST \\
  -H "Content-Type: application/json" \\
  -d '{
    "index": "sp500",
    "criteria": {
      "rsi": ["<", 30],
      "sma_50_200": [">", 1.0],
      "volume_avg": [">", 1000000]
    },
    "limit": 10
  }' \\
  http://localhost:5000/api/v1/technical</pre>
    
    <h3>6. Combined Screening (Fundamental + Technical)</h3>
    <p><code>POST /api/v1/combined</code></p>
    <p>Screens stocks based on both fundamental and technical criteria.</p>
    <pre>curl -X POST \\
  -H "Content-Type: application/json" \\
  -d '{
    "index": "sp500",
    "fundamental": {
      "market_cap": [">", 10000000000],
      "pe_ratio": ["<", 25],
      "sector": "Technology"
    },
    "technical": {
      "price_to_sma_200": [">", 1.0],
      "rsi": [">", 50]
    },
    "limit": 5
  }' \\
  http://localhost:5000/api/v1/combined</pre>
    
    <h2>Available Fields for Screening</h2>
    
    <h3>Fundamental Fields</h3>
    <table>
        <tr>
            <th>Field</th>
            <th>Description</th>
        </tr>
        <tr>
            <td>market_cap</td>
            <td>Market capitalization in USD</td>
        </tr>
        <tr>
            <td>pe_ratio</td>
            <td>Trailing price-to-earnings ratio</td>
        </tr>
        <tr>
            <td>forward_pe</td>
            <td>Forward price-to-earnings ratio</td>
        </tr>
        <tr>
            <td>price_to_book</td>
            <td>Price-to-book ratio</td>
        </tr>
        <tr>
            <td>price_to_sales</td>
            <td>Price-to-sales ratio</td>
        </tr>
        <tr>
            <td>dividend_yield</td>
            <td>Dividend yield (e.g., 0.02 for 2%)</td>
        </tr>
        <tr>
            <td>return_on_equity</td>
            <td>Return on equity</td>
        </tr>
        <tr>
            <td>beta</td>
            <td>Beta (market volatility)</td>
        </tr>
        <tr>
            <td>sector</td>
            <td>Industry sector (exact match)</td>
        </tr>
        <tr>
            <td>industry</td>
            <td>Specific industry (exact match)</td>
        </tr>
    </table>
    
    <h3>Technical Fields</h3>
    <table>
        <tr>
            <th>Field</th>
            <th>Description</th>
        </tr>
        <tr>
            <td>rsi</td>
            <td>Relative Strength Index (0-100)</td>
        </tr>
        <tr>
            <td>sma_50_200</td>
            <td>Ratio of 50-day SMA to 200-day SMA</td>
        </tr>
        <tr>
            <td>volume_avg</td>
            <td>Average trading volume</td>
        </tr>
        <tr>
            <td>price_to_sma_200</td>
            <td>Ratio of current price to 200-day SMA</td>
        </tr>
    </table>
    
    <h2>Comparison Operators</h2>
    <p>For numerical fields, you can use the following operators:</p>
    <table>
        <tr>
            <th>Operator</th>
            <th>Description</th>
        </tr>
        <tr>
            <td>&gt;</td>
            <td>Greater than</td>
        </tr>
        <tr>
            <td>&lt;</td>
            <td>Less than</td>
        </tr>
        <tr>
            <td>&gt;=</td>
            <td>Greater than or equal to</td>
        </tr>
        <tr>
            <td>&lt;=</td>
            <td>Less than or equal to</td>
        </tr>
        <tr>
            <td>==</td>
            <td>Equal to</td>
        </tr>
        <tr>
            <td>!=</td>
            <td>Not equal to</td>
        </tr>
    </table>
</body>
</html>
"""

# Add a root endpoint to display API documentation
@app.route('/')
def index():
    """Display API documentation."""
    return render_template_string(API_DOCS_HTML)