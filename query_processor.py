import re
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class QueryContext:
    """Structure to hold extracted query context"""
    age: int = None
    procedure: str = None
    location: str = None
    policy_age_months: int = None
    raw_query: str = ""
    
class QueryProcessor:
    def __init__(self):
        """Initialize query processor with pattern matching"""
        self.patterns = {
            'age': r'(\d+)[-\s]?year[-\s]?old',
            'procedure': r'(?:surgery|treatment|procedure|operation)\s*(?:for\s+)?([^?.!,]+)',
            'location': r'(?:in|at|from)\s+([A-Za-z\s]+?)(?:\s|,|$)',
            'policy_age': r'policy\s+(?:is\s+)?(\d+)\s+months?\s+old'
        }
    
    def extract_context(self, query: str) -> QueryContext:
        """Extract structured information from natural language query"""
        context = QueryContext(raw_query=query)
        
        # Extract age
        age_match = re.search(self.patterns['age'], query, re.IGNORECASE)
        if age_match:
            context.age = int(age_match.group(1))
        
        # Extract procedure
        procedure_match = re.search(self.patterns['procedure'], query, re.IGNORECASE)
        if procedure_match:
            context.procedure = procedure_match.group(1).strip()
        
        # Extract location
        location_match = re.search(self.patterns['location'], query, re.IGNORECASE)
        if location_match:
            context.location = location_match.group(1).strip()
        
        # Extract policy age
        policy_match = re.search(self.patterns['policy_age'], query, re.IGNORECASE)
        if policy_match:
            context.policy_age_months = int(policy_match.group(1))
        
        return context
    
    def create_search_queries(self, context: QueryContext) -> List[str]:
        """Create semantic search queries based on extracted context"""
        queries = [context.raw_query]  # Always include original query
        
        if context.procedure:
            queries.append(f"waiting period {context.procedure}")
            queries.append(f"coverage {context.procedure}")
        
        if context.age:
            queries.append(f"age limit {context.age} years coverage")
        
        if context.location:
            queries.append(f"geographic coverage {context.location}")
        
        return queries
