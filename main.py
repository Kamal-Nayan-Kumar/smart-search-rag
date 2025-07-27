import os
import streamlit as st
import json
from smart_search import SmartSearchEngine
from document_processor import DocumentProcessor

def setup_documents():
    """Setup documents if vector store doesn't exist"""
    if not os.path.exists("./chroma_db"):
        st.info("Setting up document database for first time...")
        
        # Create documents folder if it doesn't exist
        if not os.path.exists("./documents"):
            os.makedirs("./documents")
            st.warning("Please upload your PDF documents to the './documents' folder and restart the app.")
            return False
        
        # Process documents
        doc_processor = DocumentProcessor()
        documents = doc_processor.load_documents("./documents")
        
        if not documents:
            st.warning("No PDF documents found in './documents' folder.")
            return False
        
        chunks = doc_processor.split_documents(documents)
        doc_processor.create_vector_store(chunks)
        st.success(f"Processed {len(documents)} documents into {len(chunks)} chunks!")
    
    return True

def main():
    st.set_page_config(
        page_title="Smart Search - Insurance Policy Assistant",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Smart Search - Insurance Policy Assistant")
    st.markdown("Ask questions about insurance policies in plain English!")
    
    # Setup documents
    if not setup_documents():
        return
    
    # Initialize search engine
    if 'search_engine' not in st.session_state:
        try:
            st.session_state.search_engine = SmartSearchEngine()
            st.success("Search engine initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing search engine: {e}")
            return
    
    # Query interface
    st.subheader("Ask Your Question")
    
    # Example queries
    with st.expander("📝 Example Questions"):
        st.markdown("""
        - "Can a 46-year-old man in Pune get his knee surgery covered if his policy is 3 months old?"
        - "What is the waiting period for cardiac surgery for a 55-year-old woman?"
        - "Is dental treatment covered in Mumbai for new policyholders?"
        - "Maximum coverage amount for maternity benefits?"
        """)
    
    query = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="e.g., Can a 46-year-old man in Pune get his knee surgery covered if his policy is 3 months old?"
    )
    
    if st.button("🔍 Search", type="primary"):
        if query.strip():
            with st.spinner("Analyzing your query..."):
                try:
                    result = st.session_state.search_engine.analyze_query(query)
                    
                    # Display results
                    st.subheader("📋 Analysis Result")
                    
                    # Decision with color coding
                    decision = result.get("Decision", "Unknown")
                    if decision == "Approved":
                        st.success(f"**Decision:** {decision}")
                    elif decision == "Rejected":
                        st.error(f"**Decision:** {decision}")
                    else:
                        st.warning(f"**Decision:** {decision}")
                    
                    # Amount
                    amount = result.get("Amount", "$0")
                    st.info(f"**Coverage Amount:** {amount}")
                    
                    # Justification
                    st.subheader("📖 Justification")
                    justifications = result.get("Justification", [])
                    
                    for i, just in enumerate(justifications, 1):
                        with st.expander(f"Reason {i}: {just.get('Clause', 'Unknown Clause')}"):
                            st.write(just.get('Reason', 'No reason provided'))
                    
                    # Query context (for debugging)
                    with st.expander("🔍 Query Analysis Details"):
                        context = result.get("query_context", {})
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Extracted Information:**")
                            st.write(f"- Age: {context.get('age', 'Not found')}")
                            st.write(f"- Procedure: {context.get('procedure', 'Not found')}")
                        
                        with col2:
                            st.write(f"- Location: {context.get('location', 'Not found')}")
                            st.write(f"- Policy Age: {context.get('policy_age_months', 'Not found')} months")
                        
                        st.write(f"**Documents Retrieved:** {result.get('retrieved_documents', 0)}")
                    
                    # JSON output
                    with st.expander("📄 Raw JSON Response"):
                        st.json(result)
                
                except Exception as e:
                    st.error(f"Error processing query: {e}")
        else:
            st.warning("Please enter a question!")

if __name__ == "__main__":
    main()
