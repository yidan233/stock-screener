from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
# base define the interface that llm servic need to follow, like a blue print 
class ConversationContext:
    def __init__(self):
        self.history: List[Dict[str, str]] = []  
        self.current_criteria: Optional[Dict[str, Any]] = None  
        self.last_results: Optional[List[Dict[str, Any]]] = None  

class LLMInterface(ABC):

    @abstractmethod
    def process_query(self, query: str, context: ConversationContext) -> Dict[str, Any]:
        """
        Process a user's natural language query and convert it to structured data
        
        Args:
            query: The user's natural language input
            context: The current conversation context
            
        Returns:
            Dictionary containing:
            - criteria: The structured screening criteria
            - explanation: Natural language explanation of the criteria
            - confidence: Confidence score (0-1) of the conversion
            - needs_clarification: Boolean indicating if more information is needed
        """
        pass
    
    @abstractmethod
    def generate_explanation(self, results: List[Dict[str, Any]], 
                           criteria: Dict[str, Any],
                           context: ConversationContext) -> str:
        """
        Generate a natural language explanation of the screening results
        
        Args:
            results: List of stock results
            criteria: Criteria used for screening
            context: The current conversation context
            
        Returns:
            Natural language explanation of the results
        """
        pass
    
    @abstractmethod
    def handle_clarification(self, query: str, context: ConversationContext) -> Dict[str, Any]:
        """
        Handle a user's response to a clarification request
        
        Args:
            query: The user's clarification response
            context: The current conversation context
            
        Returns:
            Updated criteria and explanation
        """
        pass
