import os
from typing import Dict, Any, List
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from app.llm.base import LLMInterface, ConversationContext
import re
import json
import ast

class HuggingFaceService(LLMInterface):
    def __init__(self):
        # Using TinyLlama-1.1B-Chat which is open source and instruction-tuned
        self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"  # Automatically handle device placement
        )
        
        # Improved prompt with clearer instructions and examples
        self.criteria_prompt = """<|system|>
You are a financial assistant that converts stock screening requests into Python dictionaries.
IMPORTANT: Output ONLY the dictionary, no explanations or code examples.

CRITICAL INSTRUCTIONS:
1. DO NOT generate any Python code
2. DO NOT provide explanations
3. DO NOT show examples
4. ONLY output the dictionary in the exact format shown

Rules:
1. Output ONLY a valid Python dictionary
2. Use these exact field names: market_cap, pe_ratio, sector, dividend_yield, debt_to_equity, rsi
3. For comparisons use tuples: (">", value) or ("<", value) 
4. For sectors use exact string: "Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"
5. Market cap values should be in actual dollar amounts (e.g., 1000000000 for $1B)

Example Input/Output pairs:
Input: "Find technology stocks with P/E under 15"
Output: {{"sector": "Technology", "pe_ratio": ("<", 15)}}

Input: "Large cap healthcare companies with dividend over 3%"
Output: {{"market_cap": (">", 10000000000), "sector": "Healthcare", "dividend_yield": (">", 0.03)}}

Input: "Low debt companies in finance sector"
Output: {{"sector": "Finance", "debt_to_equity": ("<", 0.5)}}

Input: "Oversold tech stocks"
Output: {{"sector": "Technology", "rsi": ("<", 30)}}

FINAL REMINDER: Output ONLY the dictionary, nothing else. No code, no explanations, no examples.
</|system|>

<|user|>
{query}
</|user|>

<|assistant|>
"""

    def _generate_response(self, prompt: str, max_new_tokens: int = 300) -> str:
        try:
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.3,  # Lower temperature for more focused output
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=2,
                    top_p=0.9,  # Add top_p sampling
                    top_k=50    # Add top_k sampling
                )
            
            # Decode and clean up the response
            raw_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"\nModel response: {raw_response}")
            
            # Remove the prompt from the response
            if prompt in raw_response:
                response = raw_response.replace(prompt, "").strip()
            else:
                response = raw_response
            
            # Extract only the part after <|assistant|>
            if "<|assistant|>" in response:
                response = response.split("<|assistant|>")[-1].strip()
            
            print(f"Cleaned response: {response}")
            return response
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return ""

    def _extract_dict_from_response(self, content: str) -> Dict[str, Any]:
        """Extract dictionary from model response"""
        if not content:
            return {}
        
        print(f"Attempting to extract dictionary from: {content}")
        
        # Look for Python dictionary and try to parse safely
        dict_match = re.search(r'\{[^{}]*\}', content)
        if dict_match:
            dict_str = dict_match.group(0)
            print(f"Found potential dictionary: {dict_str}")
            try:
                # Try to use ast.literal_eval for safer parsing
                result = ast.literal_eval(dict_str)
                if self._validate_criteria(result):
                    print(f"Successfully parsed dictionary: {result}")
                    return result
            except Exception as e:
                print(f"Parse error: {e}")
                # If literal_eval fails, try json.loads
                try:
                    result = json.loads(dict_str)
                    if self._validate_criteria(result):
                        print(f"Successfully parsed dictionary with json: {result}")
                        return result
                except Exception as e:
                    print(f"JSON parse error: {e}")
                    pass
        
        return {}

    def _validate_criteria(self, criteria: Dict[str, Any]) -> bool:
        """Validate the criteria format"""
        if not isinstance(criteria, dict) or not criteria:
            return False
        
        valid_fields = {'market_cap', 'pe_ratio', 'sector', 'dividend_yield', 'debt_to_equity', 'rsi'}
        valid_operators = {'>', '<', '>=', '<=', '=='}
        
        for key, value in criteria.items():
            if key not in valid_fields:
                continue
                
            if key == 'sector':
                if not isinstance(value, str):
                    return False
            else:
                # Should be a tuple with (operator, value)
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    operator, val = value
                    if operator not in valid_operators:
                        return False
                    if not isinstance(val, (int, float)):
                        return False
                else:
                    return False
        return True

    def process_query(self, query: str, context: ConversationContext) -> Dict[str, Any]:
        """Process a user's natural language query and convert it to structured data"""
        try:
            # Add the query to conversation history
            context.history.append({"role": "user", "content": query})
     
            try:
              
                
                # Generate response using the model
                prompt = self.criteria_prompt.format(query=query)
                content = self._generate_response(prompt, max_new_tokens=300)
                print("\nGenerated content:")
                print(content)
                
                # Parse the LLM criteria
                criteria = self._extract_dict_from_response(content)
                print("\nExtracted criteria:")
                print(criteria)
                
                if criteria and self._validate_criteria(criteria):
                    confidence = 0.8
                    needs_clarification = False
                    explanation = f"Found {len(criteria)} screening criteria from your request."
                else:
                    criteria = {}
                    confidence = 0.2
                    needs_clarification = True
                    explanation = "I couldn't understand your screening criteria. Could you be more specific?"
                
                context.history.append({"role": "assistant", "content": str(criteria)})
                
            except Exception as llm_error:
                print(f"\nLLM processing failed with error: {str(llm_error)}")
                print(f"Error type: {type(llm_error)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                criteria = {}
                confidence = 0.0
                needs_clarification = True
                explanation = "An error occurred while processing your request. Please try rephrasing."
                context.history.append({"role": "assistant", "content": str(criteria)})
            
            return {
                "criteria": criteria,
                "explanation": explanation,
                "confidence": confidence,
                "needs_clarification": needs_clarification
            }
            
        except Exception as e:
            import traceback
            print(f"Failed to process query: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "criteria": {},
                "explanation": "An error occurred. Please try rephrasing your query.",
                "confidence": 0.0,
                "needs_clarification": True
            }

    def generate_explanation(self, results: List[Dict[str, Any]], 
                           criteria: Dict[str, Any],
                           context: ConversationContext) -> str:
        """Generate a natural language explanation of the screening results"""
        try:
            if not results:
                return "No stocks matched your screening criteria. You may want to broaden your requirements."
            
            explanation_parts = []
            
            # Add criteria summary
            criteria_text = []
            for key, value in criteria.items():
                if key == 'sector':
                    criteria_text.append(f"in the {value} sector")
                elif isinstance(value, tuple) and len(value) == 2:
                    op, val = value
                    if key == 'market_cap':
                        if op == '>':
                            cap_text = "large-cap" if val >= 10000000000 else "mid-cap"
                        else:
                            cap_text = "small-cap"
                        criteria_text.append(f"{cap_text} companies")
                    elif key == 'pe_ratio':
                        criteria_text.append(f"P/E ratio {op} {val}")
                    elif key == 'dividend_yield':
                        criteria_text.append(f"dividend yield {op} {val*100:.1f}%")
                    elif key == 'debt_to_equity':
                        criteria_text.append(f"debt-to-equity {op} {val}")
                    elif key == 'rsi':
                        if val < 30:
                            criteria_text.append("potentially oversold (RSI < 30)")
                        elif val > 70:
                            criteria_text.append("potentially overbought (RSI > 70)")
                        else:
                            criteria_text.append(f"RSI {op} {val}")
            
            if criteria_text:
                explanation_parts.append(f"Found {len(results)} stocks matching your criteria: {', '.join(criteria_text)}.")
            
            # Add sample results
            if len(results) <= 3:
                stocks_text = ", ".join([f"{r['symbol']}" for r in results])
                explanation_parts.append(f"The stocks are: {stocks_text}.")
            else:
                top_stocks = ", ".join([f"{r['symbol']}" for r in results[:3]])
                explanation_parts.append(f"Top results include: {top_stocks}, and {len(results)-3} others.")
            
            return " ".join(explanation_parts)
            
        except Exception as e:
            return f"Successfully found {len(results)} stocks matching your criteria. Consider reviewing the fundamentals and recent performance of these companies before making investment decisions."

    def handle_clarification(self, query: str, context: ConversationContext) -> Dict[str, Any]:
        """Handle a user's response to a clarification request"""
        try:
            # Add the clarification to conversation history
            context.history.append({"role": "user", "content": query})
            
            # Process the clarification as a new query
            return self.process_query(query, context)
            
        except Exception as e:
            raise Exception(f"Failed to handle clarification: {str(e)}")