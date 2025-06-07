import unittest
from app.llm.service import HuggingFaceService
from app.llm.base import ConversationContext
from app.screener.screener import StockScreener

class TestInteractiveLLM(unittest.TestCase):
    def test_natural_language_query(self):
        """Test the LLM service with natural language queries"""
        service = HuggingFaceService()
        context = ConversationContext()
        screener = StockScreener()
        
        # Load test data before running queries
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'JNJ', 'PFE', 'MRK', 'JNJ', 'BAC', 'WFC']
        print("\nLoading test data...")
        screener.load_data(test_symbols)
        
        # Test queries
        test_queries = [
            "Find me large technology companies with P/E ratios under 20",
        ]
        
        print("\nTesting LLM Service with sample queries:")
        print("=" * 80)
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 40)
            
            try:
                # Process the query
                result = service.process_query(query, context)
                
                print("\nDebug Information:")
                print(f"Raw result: {result}")
                
                # Extract criteria
                criteria = result.get('criteria', {})
                explanation = result.get('explanation', '')
                confidence = result.get('confidence', 0.0)
                needs_clarification = result.get('needs_clarification', True)
                
                print(f"Criteria: {criteria}")
                print(f"Explanation: {explanation}")
                print(f"Confidence: {confidence}")
                print(f"Needs clarification: {needs_clarification}")
                
                # Convert criteria to string format for display
                criteria_str = ", ".join([f"{k}: {v}" for k, v in criteria.items()])
                print(f"\nConverted Criteria: {criteria_str}")
                
                # Screen stocks with the criteria
                if criteria:
                    print("\nScreening stocks...")
                    stocks = screener.screen_stocks(criteria)
                    
                    # Generate explanation
                    explanation = service.generate_explanation(stocks, criteria, context)
                    
                    print(f"\nFound {len(stocks)} matching stocks")
                    print("\nExplanation:")
                    print(explanation)
                    
                    # Print first few results
                    print("\nTop Results:")
                    for stock in stocks[:5]:
                        print(f"- {stock['symbol']}: {stock['name']} (Market Cap: ${stock['market_cap']:,.0f})")
                
            except Exception as e:
                print(f"Error processing query: {str(e)}")
            
            print("=" * 80)

    def test_llm_response(self):
        """Test that the LLM service returns a response"""
        service = HuggingFaceService()
        context = ConversationContext()
        
        # Simple test query
        query = "Find technology stocks with P/E under 15"
        
        print("\nTesting LLM Response:")
        print("=" * 80)
        print(f"Query: {query}")
        print("-" * 40)
        
        try:
            # Process the query
            result = service.process_query(query, context)
            
            print("\nDebug Information:")
            print(f"Raw result: {result}")
            
            # Basic assertions
            self.assertIsNotNone(result, "Result should not be None")
            self.assertIsInstance(result, dict, "Result should be a dictionary")
            
            # Check that we got a response from the model
            self.assertIn('criteria', result, "Result should contain 'criteria'")
            self.assertIn('explanation', result, "Result should contain 'explanation'")
            self.assertIn('confidence', result, "Result should contain 'confidence'")
            self.assertIn('needs_clarification', result, "Result should contain 'needs_clarification'")
            
            # Print the model's response
            print("\nModel Response:")
            print(f"Criteria: {result['criteria']}")
            print(f"Explanation: {result['explanation']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Needs clarification: {result['needs_clarification']}")
            
        except Exception as e:
            self.fail(f"Test failed with error: {str(e)}")
        
        print("=" * 80)

if __name__ == "__main__":
    unittest.main() 