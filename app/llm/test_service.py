import unittest
from app.llm.service import HuggingFaceService
from app.llm.base import ConversationContext

class TestHuggingFaceService(unittest.TestCase):
    def setUp(self):
        self.service = HuggingFaceService()
        self.context = ConversationContext()

    def test_process_query(self):
        # Test a simple query
        query = "Find me large technology companies with low P/E ratios"
        result = self.service.process_query(query, self.context)
        
        # Check the structure of the response
        self.assertIn('criteria', result)
        self.assertIn('explanation', result)
        self.assertIn('confidence', result)
        self.assertIn('needs_clarification', result)
        
        # Check that criteria contains expected fields
        criteria = result['criteria']
        self.assertIn('market_cap', criteria)
        self.assertIn('pe_ratio', criteria)
        self.assertIn('sector', criteria)
        
        # Check that the query was added to history
        self.assertEqual(len(self.context.history), 2)  # User query + Assistant response

    def test_generate_explanation(self):
        # Test data
        results = [
            {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'market_cap': 2000000000000,
                'pe_ratio': 25
            }
        ]
        criteria = {
            'market_cap': ('>', 1000000000),
            'pe_ratio': ('<', 30),
            'sector': 'Technology'
        }
        
        # Generate explanation
        explanation = self.service.generate_explanation(results, criteria, self.context)
        
        # Check that we got a non-empty explanation
        self.assertTrue(len(explanation) > 0)

    def test_handle_clarification(self):
        # First query
        initial_query = "Find me technology stocks"
        initial_result = self.service.process_query(initial_query, self.context)
        
        # Clarification
        clarification = "I want companies with market cap over 100 billion"
        clarification_result = self.service.handle_clarification(clarification, self.context)
        
        # Check that the clarification was processed
        self.assertIn('criteria', clarification_result)
        self.assertIn('market_cap', clarification_result['criteria'])

if __name__ == '__main__':
    unittest.main() 