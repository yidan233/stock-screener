from flask import Blueprint, request, jsonify
from app.screener import StockScreener, screen_stocks, screen_by_technical, create_combined_screen
from app.data import get_stock_symbols
from app.cli import parse_criteria
import logging


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



screener = StockScreener()
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# screen with fundamental criteria 
@api_bp.route('/screen/fundamental', methods=['POST'])
def screen_fundamental():
    try:
        data = request.get_json() or {}
        
        index = data.get('index', 'sp500')
        criteria_str = data.get('criteria', '')
        limit = data.get('limit', 50)
        reload = data.get('reload', False)
        period = data.get('period', '1y')
        interval = data.get('interval', '1d')
        
        criteria = parse_criteria(criteria_str)
        if not criteria:
            return jsonify({'error': 'Technical criteria required'}), 400
        

        symbols = get_stock_symbols(index=index)
        screener.load_data(symbols=symbols, reload=reload, period=period, interval=interval)
        results = screen_stocks(screener.stock_data, criteria, limit=limit)
        
        return jsonify({
            'count': len(results),
            'criteria': criteria,
            'index': index,
            'stocks': results
        })
    
    except Exception as e:
        logger.error(f"Error in fundamental screening: {e}")
        return jsonify({'error': str(e)}), 500


# screen with technical criteria 
@api_bp.route('/screen/technical', methods=['POST'])
def screen_technical():
    try:
        data = request.get_json() or {}
        
        index = data.get('index', 'sp500')
        criteria_str = data.get('criteria', '')
        limit = data.get('limit', 50)
        reload = data.get('reload', False)
        period = data.get('period', '1y')
        interval = data.get('interval', '1d')
        
    
        criteria = parse_criteria(criteria_str)
        if not criteria:
            return jsonify({'error': 'Technical criteria required'}), 400
        
      
        symbols = get_stock_symbols(index=index)
        screener.load_data(symbols=symbols, reload=reload, period=period, interval=interval)
        results = screen_by_technical(screener.stock_data, screener.indicators, criteria)
        
        # Apply limit
        if limit and results:
            results = results[:limit]
        
        return jsonify({
            'count': len(results),
            'criteria': criteria,
            'index': index,
            'stocks': results
        })
    except Exception as e:
        logger.error(f"Error in technical screening: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/screen/combined', methods=['POST'])
def screen_combined():
    try:
        data = request.get_json() or {}
        
        index = data.get('index', 'sp500')
        fundamental_criteria_str = data.get('fundamental_criteria', '')
        technical_criteria_str = data.get('technical_criteria', '')
        limit = data.get('limit', 50)
        reload = data.get('reload', False)
        period = data.get('period', '1y')
        interval = data.get('interval', '1d')
        
        fundamental_criteria = parse_criteria(fundamental_criteria_str)
        technical_criteria = parse_criteria(technical_criteria_str)
        
        if not fundamental_criteria or not technical_criteria:
            return jsonify({'error': 'Both fundamental and technical criteria required'}), 400
        

        symbols = get_stock_symbols(index=index)
        screener.load_data(symbols=symbols, reload=reload, period=period, interval=interval)
        
        results = create_combined_screen(screener, fundamental_criteria, technical_criteria, limit=limit)
        
        return jsonify({
            'count': len(results),
            'fundamental_criteria': fundamental_criteria,
            'technical_criteria': technical_criteria,
            'index': index,
            'stocks': results
        })
    except Exception as e:
        logger.error(f"Error in combined screening: {e}")
        return jsonify({'error': str(e)}), 500

# ===== SUPPORTING ROUTES =====

@api_bp.route('/indexes', methods=['GET'])
def get_indexes():
    """Get available stock indexes"""
    return jsonify({
        'indexes': ['sp500', 'nasdaq100', 'dow30'],
        'count': 3
    })

@api_bp.route('/symbols/<index>', methods=['GET'])
def get_symbols(index):
    """Get stock symbols for a given index"""
    try:
        symbols = get_stock_symbols(index=index)
        return jsonify({
            'index': index,
            'symbols': symbols,
            'count': len(symbols)
        })
    except Exception as e:
        logger.error(f"Error getting symbols for {index}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/indicators', methods=['GET'])
def get_available_indicators():
    """Get list of available technical indicators and fundamental fields"""
    return jsonify({
        'technical_indicators': [
            'rsi', 'ma', 'ema', 'macd_hist', 'boll_upper', 'boll_lower',
            'atr', 'obv', 'stoch_k', 'stoch_d', 'roc'
        ],
        'fundamental_fields': [
            'market_cap', 'pe_ratio', 'forward_pe', 'price_to_book', 'price_to_sales',
            'dividend_yield', 'payout_ratio', 'return_on_equity', 'return_on_assets',
            'profit_margin', 'operating_margin', 'revenue_growth', 'earnings_growth',
            'beta', 'current_ratio', 'debt_to_equity', 'enterprise_to_revenue',
            'enterprise_to_ebitda', 'price', 'sector', 'industry', 'country'
        ],
        'operators': ['>', '<', '>=', '<=', '==', '!=']
    })

@api_bp.route('/', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        'name': 'Stock Screener API',
        'version': '1.0.0',
        'description': 'REST API for stock screening using fundamental and technical analysis',
        'endpoints': {
            'POST /api/v1/screen/fundamental': 'Screen stocks by fundamental criteria',
            'POST /api/v1/screen/technical': 'Screen stocks by technical criteria', 
            'POST /api/v1/screen/combined': 'Screen stocks by both criteria',
            'GET /api/v1/indexes': 'Get available stock indexes',
            'GET /api/v1/symbols/<index>': 'Get stock symbols for an index',
            'GET /api/v1/indicators': 'Get available indicators and fields'
        },
        'examples': {
            'fundamental_screening': {
                'url': '/api/v1/screen/fundamental',
                'method': 'POST',
                'body': {
                    'index': 'sp500',
                    'criteria': 'market_cap>1000000000,pe_ratio<20',
                    'limit': 10
                }
            },
            'technical_screening': {
                'url': '/api/v1/screen/technical',
                'method': 'POST',
                'body': {
                    'index': 'sp500',
                    'criteria': 'rsi<30,ma>100',
                    'limit': 10
                }
            },
            'combined_screening': {
                'url': '/api/v1/screen/combined',
                'method': 'POST',
                'body': {
                    'index': 'sp500',
                    'fundamental_criteria': 'sector=Technology',
                    'technical_criteria': 'rsi>40',
                    'limit': 10
                }
            }
        }
    })

def register_routes(app):
    """Register all API routes with the Flask app"""
    app.register_blueprint(api_bp)