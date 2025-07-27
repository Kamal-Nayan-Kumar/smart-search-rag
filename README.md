# 📘 Smart Search RAG System for Insurance Policies

An AI-powered document search system that makes it easy to understand insurance policies using natural language. It uses RAG (Retrieval-Augmented Generation) and the Perplexity API to provide accurate answers to your questions. Built with Streamlit for an intuitive web experience.

---

## 🌟 Key Features

### 🧠 AI-Powered Search

- Ask questions in plain English
- Understands meaning, not just keywords
- Returns structured answers with reasons
- Analyzes real-time data using Perplexity API

### 📄 Document Intelligence

- Upload PDFs, Word docs, or text files
- Extracts medical procedures, user age, policy duration, and locations
- Calculates waiting periods, policy maturity

### 🖥️ Web Interface

- Clean and simple Streamlit dashboard
- Live feedback while processing
- Built-in test questions for demo
- Debug mode for developers

---

## 🚀 Quick Start Guide

### ✅ Requirements

- Python 3.8+
- Perplexity API key (get from [Perplexity](https://www.perplexity.ai))

### 🔧 Setup Instructions

1. **Clone repository:**
```bash
git clone https://github.com/Kamal-Nayan-Kumar/smart-search-rag.git

cd smart-search-rag
```
Recommended: Create virtual env

2. **Install required packages:**

```bash
pip install -r requirements.txt
```

3. **Set up environment file:**

```bash
echo "PERPLEXITY_API_KEY=your_key_here" > .env
```

4. **Add insurance documents:**

```bash
mkdir documents
cp /path/to/your/files.pdf ./documents/
```

5. **Run setup script:**

```bash
python setup.py
```

6. **Start the app:**

```bash
streamlit run main.py
```

---

## 📁 Folder Structure

```bash
smart-search-rag/
├── .env                    # API key here
├── README.md
├── requirements.txt       # Python dependencies
├── main.py                # Web interface (Streamlit)
├── setup.py               # Runs initial setup
├── smart_search.py        # Core engine logic
├── document_processor.py  # Document parsing
├── query_processor.py     # Extracts query data
├── documents/             # Store your PDF/DOC files
└── chroma_db/             # Local vector database
```

---

## 📦 Dependencies

Install with:

```bash
pip install -r requirements.txt
```

---

## 💬 Example Questions

- "Can a 46-year-old in Pune get his knee surgery covered if policy is 3 months old?"
- "Waiting period for cardiac surgery for 55-year-old woman?"
- "Is dental treatment covered in Mumbai?"
- "How much maternity benefit is offered?"

### Output Format:

```json
{
  "Decision": "Rejected",
  "Amount": "$0",
  "Justification": [
    {
      "Clause": "Section 4.2: Waiting Period",
      "Reason": "The policy has a 12-month waiting period. Only 3 months have passed."
    }
  ],
  "query_context": {
    "age": 46,
    "procedure": "knee surgery",
    "location": "Pune",
    "policy_age_months": 3
  },
  "retrieved_documents": 5,
  "model_used": "sonar-pro"
}
```

---

## ⚙️ Config & Customization

### .env Variables

```env
PERPLEXITY_API_KEY=your_key_here
```

---

## 🙌 Acknowledgments

- LangChain: Document parsing and RAG framework
- ChromaDB: Vector store
- Perplexity: Language model API
- Streamlit: Web UI
- SentenceTransformers: Embedding generation
