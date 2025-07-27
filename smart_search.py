import os
import json
import requests
from typing import Dict, List, Any
from query_processor import QueryProcessor, QueryContext
from document_processor import DocumentProcessor
from dotenv import load_dotenv

load_dotenv()

class SmartSearchEngine:
    def __init__(self, vector_store_path: str = "./chroma_db"):
        """Initialize the smart search engine with Perplexity API"""
        self.query_processor = QueryProcessor()
        self.doc_processor = DocumentProcessor()
        self.vectorstore = self.doc_processor.load_vector_store(vector_store_path)
        
        # Perplexity API configuration
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
    
    def call_perplexity_api(self, messages: List[Dict], model: str = "sonar-pro") -> Dict:
        """Call Perplexity API with messages"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Perplexity API error: {str(e)}")
    
    def semantic_search(self, query: str, k: int = 5) -> List[Dict]:
        """Perform semantic search on documents"""
        # Get query embeddings
        query_embedding = self.doc_processor.get_embeddings([query])[0]
        
        # Search in vector store
        results = self.vectorstore.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Format results
        documents = []
        for i in range(len(results['documents'][0])):
            doc = {
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if results['metadatas'][0] else {},
                "distance": results['distances'][0][i] if results['distances'][0] else 0
            }
            documents.append(doc)
        
        return documents
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Main method to analyze query and return structured response"""
        try:
            # Extract context from query
            context = self.query_processor.extract_context(query)
            
            # Perform semantic search on local documents
            retrieved_docs = self.semantic_search(query)
            
            # Format retrieved documents for prompt
            docs_text = "\n\n".join([
                f"Document {i+1}:\n{doc['content']}"
                for i, doc in enumerate(retrieved_docs)
            ])
            
            # Create messages for Perplexity API
            system_message = """You are an expert insurance policy analyst. Analyze the given context and documents to provide a structured decision.

Based on the policy documents and the query context, provide your analysis in this EXACT JSON format:

{
    "Decision": "Approved" or "Rejected" or "Requires Review",
    "Amount": "$X" or "$0",
    "Justification": [
        {
            "Clause": "Section X.X: Clause Name", 
            "Reason": "Detailed explanation of why this clause applies"
        }
    ]
}

Important:
- Be precise about policy clauses and sections
- If information is insufficient, use "Requires Review"
- Always cite specific sections from the documents
- Calculate amounts based on policy terms"""

            user_message = f"""Query Context:
- Age: {context.age or "Not specified"}
- Procedure: {context.procedure or "Not specified"}
- Location: {context.location or "Not specified"}
- Policy Age (months): {context.policy_age_months or "Not specified"}

Original Query: {query}

Retrieved Policy Documents:
{docs_text}

Please analyze this insurance query based on the policy documents provided."""

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            # Get response from Perplexity API
            response = self.call_perplexity_api(messages, model="sonar-pro")
            
            # Parse JSON response
            response_text = response['choices'][0]['message']['content'].strip()
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                result = {
                    "Decision": "Requires Review",
                    "Amount": "$0",
                    "Justification": [
                        {
                            "Clause": "Analysis Error",
                            "Reason": "Could not parse the policy analysis properly."
                        }
                    ]
                }
            
            # Add metadata
            result["retrieved_documents"] = len(retrieved_docs)
            result["query_context"] = {
                "age": context.age,
                "procedure": context.procedure,
                "location": context.location,
                "policy_age_months": context.policy_age_months
            }
            result["model_used"] = "sonar-pro"
            
            return result
            
        except Exception as e:
            return {
                "Decision": "Error",
                "Amount": "$0",
                "Justification": [
                    {
                        "Clause": "System Error",
                        "Reason": f"Error processing query: {str(e)}"
                    }
                ],
                "error": str(e)
            }
