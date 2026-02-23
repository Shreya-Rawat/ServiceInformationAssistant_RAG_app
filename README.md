# ServiceInformationAssistant_RAG_app
A RAG based LLM application to let users upload docs related to company services and solutions and query information on those docs.

## 📘 Service Information Assistant

A Retrieval-Augmented Generation (RAG) Based AI Assistant

## 1️⃣ Overview

This project implements a Service Information Assistant for a technology services company using a Retrieval-Augmented Generation (RAG) architecture with basic agentic behavior.

The assistant:

Ingests company service documents (PDF/DOCX)

Creates vector embeddings using HuggingFace models

Stores embeddings in a FAISS vector database

Retrieves relevant context for user queries

Uses an LLM (via Ollama) to generate grounded responses

Detects and handles cost estimation queries using a specialized agent workflow

Provides source citations for transparency

Exposes a FastAPI backend and Streamlit UI

## 2️⃣ Problem Statement

The assistant simulates a Service Information AI for a tech services company. It can answer questions such as:

“What AI services do you offer?”

“Do you have experience with fintech projects?”

“What’s the estimated cost for a 3-month digital marketing campaign?”

The system retrieves relevant document sections and generates context-aware responses grounded strictly in uploaded documents.

## 3️⃣ Core Requirements Implementation
### 3.1 Data Preparation & Document Ingestion

✔ Supports:

PDF documents

DOCX documents

✔ Processing Steps:

File upload via /upload endpoint

Text extraction using:

PyMuPDF (fitz) for PDFs

python-docx for DOCX

Semantic chunking using:

RecursiveCharacterTextSplitter

Chunk size: 800

Overlap: 150

Metadata attached:

source (filename)

chunk_id

✔ Scalable architecture — can handle real production documents.

### 3.2 RAG Pipeline Implementation

The system implements a complete RAG pipeline:

🔹 Embeddings

Model: sentence-transformers/all-MiniLM-L6-v2

Library: HuggingFaceEmbeddings

Converts chunks into dense vector embeddings

🔹 Vector Storage

Database: FAISS

Stored locally using:

vector_store.save_local("faiss_index")

🔹 Retrieval

Semantic similarity search

Top-k retrieval (k=3)

Metadata extraction for citation generation

🔹 Generation

LLM: llama3.2:1b (via Ollama)
** (Use qwen2.5:7b if possible for better response)

Strict grounding prompt:  ( No hallucinations, Answer only from retrieved context, Preserve original terminology )

🔹 Source Citations

Each answer includes:

Source: <filename>
Para: <retrieved content>


Ensuring transparency and trust.

### 3.3 Agentic Behaviour (Tool Integration)

This implementation includes:

#### 🧠 Pricing Estimation Agent

The assistant autonomously detects cost-related queries.

Step 1 — Intent Classification Agent

An LLM-based classifier determines whether the query is a:

Cost estimation request → TRUE

General query → FALSE

Output format:

{
  "is_cost_estimation": bool,
  "confidence_score": float,
  "reasoning": "..."
}

Step 2 — Financial Analyst Agent (if TRUE)

If cost-related:

Extracts pricing info strictly from context

Performs calculations if required

Provides:

Estimated cost

Breakdown

Confidence notes

If pricing info is missing:

Cost information not found in document.


This demonstrates agentic orchestration logic.

### 3.4 User Interface
✅ Option A — REST API (FastAPI)
/upload

Upload a PDF or DOCX document.

Response:

{
  "status": "Successfully ingested data.",
  "message": "Ingested X chunks."
}

/query

Submit a question.

Request:

{
  "query": "What AI services do you offer?"
}


Response:

{
  "answer": "...",
  "citation": "Source: services_overview.pdf"
}

✅ Option B — Streamlit Interface

A simple UI:

Upload document

Ask questions

View:

Answer

Source citation

Run with:

streamlit run app.py

## 4️⃣ Technical Architecture
🔹 Architecture Flow:

User → Streamlit UI → FastAPI → Ingestion → Embeddings → FAISS
                                              ↓
User Query → LangGraph StateGraph → Retrieve → Generate → Response

🔹 Agent Workflow (LangGraph)

Nodes:  ( retrieve, generate )

Graph:

START → retrieve → generate → END

## 5️⃣ Tech Stack
Language:  ( Python 3.8+ )

Core Libraries:  

LangChain

LangGraph

FAISS

HuggingFace Embeddings

Ollama (LLM)

Backend

FastAPI

Uvicorn

Frontend

Streamlit

Document Processing :

PyMuPDF (fitz)

python-docx

## 6️⃣ Project Structure

├── agent.py           # RAG + agent orchestration logic

├── api.py             # FastAPI backend

├── app.py             # Streamlit frontend

├── config.py          # Model & API configuration

├── embeddings.py      # Embedding & FAISS logic

├── ingestion.py       # Document extraction logic

├── faiss_index/       # Persisted vector store

├── requirements.txt

└── README.md

## 7️⃣ Setup Instructions
### 1️⃣ Clone Repository
git clone <your-repo-url>
cd <repo-name>

### 2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Install & Run Ollama

Install Ollama from:
https://ollama.com

Pull the model:

ollama pull llama3.2:1b

*** (Use model qwen2.5:7b if possible for better response (also update the model name in the config.py))

### 5️⃣ Start FastAPI Server
uvicorn api:app --reload


Server runs at:

http://localhost:8000

### 6️⃣ Run Streamlit App
streamlit run app.py

### 7️⃣ Query the Assistant

Once both FastAPI and Streamlit are running:

🔹 Option A — Using Streamlit UI

The streamlit command will open your browser:

http://localhost:8501


Upload a PDF or DOCX file.

Enter your question.

Click Ask.

You will see:

✅ Generated Answer

📌 Source Citation

🧠 Cost Estimation Analysis (if applicable)

** The Response will also include an answer and reasoning about weather your query is related to any cost estimation.

### 8️⃣ Key Design Decisions

✔ Strict context grounding to prevent hallucinations
✔ LLM-based intent detection for agentic behavior
✔ Modular project structure
✔ Persistent FAISS index
✔ CORS enabled for frontend-backend integration
✔ Clear separation of ingestion, embedding, retrieval, generation

### 9️⃣ Error Handling & Validation

Validates empty document upload

Prevents query before ingestion

Handles unsupported file formats

Structured JSON parsing for intent classification

### 🔟 Future Improvements

Add multiple document ingestion

Persistent vector DB reload on startup

Add sentiment analysis tool

Add conversation memory (memory chain)

Authentication & production deployment

Docker containerization

Replace local LLM with production-grade hosted LLM

## 🎯 Conclusion

This project demonstrates:

End-to-end RAG pipeline implementation

Agentic AI behavior via tool invocation

Vector database usage (FAISS)

LLM orchestration with LangGraph

Transparent source citations

REST + Interactive UI


