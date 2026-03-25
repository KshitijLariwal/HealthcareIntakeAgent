# Healthcare Intake Agent: RAG-Powered Clinical Assistant

An intelligent, strictly guardrailed healthcare intake API designed to empathetically gather patient symptoms without offering medical diagnoses. Built with FastAPI, LangGraph, and a Qdrant Vector Database, this project demonstrates a production-ready Retrieval-Augmented Generation (RAG) architecture.

## 🗺️ Architecture Diagram

```text
[Patient / Client UI]
         │
         ▼ (POST /api/chat)
┌────────────────────────────────────────────────────────┐
│                    FastAPI Backend                     │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │             LangGraph Orchestrator               │  │
│  │  (State Machine for Strict Medical Boundaries)   │  │
│  └─────────┬───────────────────────────────┬────────┘  │
│            │                               │           │
│      1. Retrieve Context             2. Generate       │
│            ▼                               ▼           │
│  ┌───────────────────┐           ┌──────────────────┐  │
│  │ Qdrant Vector DB  │           │   LLM Engine     │  │
│  │ (RAG Guidelines)  │           │ (Gemini/Llama 3) │  │
│  └───────────────────┘           └──────────────────┘  │
└────────────────────────────────────────────────────────┘
```

## 🧠 Design Choices & Trade-offs

### 1. The Agent Framework: LangGraph
* **Choice:** LangGraph over standard LangChain sequential chains.
* **Why:** Medical intake is a cyclical process (ask, listen, retrieve, evaluate, ask again), not a simple prompt-to-response pipeline. LangGraph provides a state machine architecture.
* **Trade-off:** Introduces a steeper learning curve and slightly more complex code overhead compared to standard conversational chains, but it guarantees the strict, predictable routing required for medical safety.

### 2. The LLM Engine: Dual-Model Architecture
* **Choice:** A custom fine-tuned **Llama 3 (8B)** for production, with **Google Gemini 2.5 Flash** as a local development proxy.
* **Why:** Standard LLMs naturally attempt to diagnose patients, which is a liability. Llama 3 was fine-tuned via LoRA specifically for clinical empathy and strict boundary adherence (see `finetune_intake_agent.ipynb`). 
* **Trade-off:** Maintaining a proxy model (Gemini) for local testing creates a slight parity gap between development and production. However, it enables rapid, lightweight containerized development on standard CPUs (like GitHub Codespaces) without requiring 16GB+ of dedicated GPU VRAM just to test API routing.

### 3. The Vector Database: Qdrant
* **Choice:** Qdrant (Dockerized).
* **Why:** Qdrant is built in Rust, highly performant, and easily runs as a local Docker container alongside the API, making network orchestration seamless.
* **Trade-off:** Requires spinning up and managing an additional container compared to lightweight, in-memory options like ChromaDB. However, it provides true production-ready scalability and persistent storage.

## 🚀 Core Technologies
* **Orchestration:** LangGraph & LangChain
* **API Framework:** FastAPI & Uvicorn
* **Vector Database:** Qdrant (Dockerized)
* **Embeddings:** Google Generative AI Embeddings
* **Containerization:** Docker & Docker Compose

## 📁 Project Structure
```text
HealthcareIntakeAgent/
├── app/
│   ├── core/
│   │   └── agent.py          # LangGraph routing and LLM initialization
│   ├── rag/
│   │   └── ingest.py         # Document chunking and Qdrant population
│   ├── main.py               # FastAPI application and endpoints
│   └── requirements.txt      # Python dependencies
├── data/
│   └── sample_guidelines.txt # Knowledge base for RAG
├── docker-compose.yml        # Multi-container orchestration
├── Dockerfile                # API container image definition
└── finetune_intake_agent.ipynb # Llama 3 fine-tuning pipeline
```

## 🛠️ Setup Instructions

This project is fully containerized. You can spin up the entire backend network (API + Database) with a single command.

**1. Clone the repository and set your environment variables:**
Create a `.env` file in the root directory:
```text
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

**2. Start the services:**
```bash
docker-compose up --build -d
```

**3. Populate the Vector Database:**
Once the containers are running, execute the ingestion script to load the medical guidelines into Qdrant:
```bash
docker exec -it <api_container_name> python /workspace/app/rag/ingest.py
```

**4. Access the API:**
* **Health Check:** `http://localhost:8000/health`
* **Interactive Docs (Swagger UI):** `http://localhost:8000/docs`

## 💬 API Usage

**Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "message": "I've been having a sharp pain in my side since this morning.",
  "thread_id": "patient_session_123"
}
```

**Expected Response:**
```json
{
  "reply": "I understand you are experiencing sharp pain. To help me gather the right information for the doctor, could you tell me if the pain is localized to a specific side, and if you are experiencing any other symptoms like fever or nausea?"
}
```