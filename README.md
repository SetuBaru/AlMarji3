# Al-Marji3 (المرجع) | Islamic Knowledge RAG AI & REST API Platform

> **Al-Marji3 (المرجع - *The Reference*)** is a state-of-the-art, evidence-grounded Islamic research platform and REST API powered by Retrieval-Augmented Generation (RAG). It provides intelligent, vector-backed answers strictly derived from the **Holy Quran** (English translation with classical Tafseer commentary) and authentic **Hadith collections** (*Sahih al-Bukhari*, *Sahih Muslim*, *Jami` at-Tirmidhi*, *Sunan Abi Dawud*, *Sunan an-Nasa'i*, and *Sunan Ibn Majah*).

---

## 🌟 Key Features

- **📖 Complete Quran & Tafseer Integration**: Semantic vector search across all 114 Surahs (6,236 verses) paired with classical Tafseer commentary (*Tafsir al-Jalalayn*).
- **📜 Authentic Hadith Collections**: Indexed vector database covering over 30,000+ authentic Hadiths from canonical Sunni collections.
- **🛡️ Strict Grounding Policy**: Zero un-grounded fabrications. The AI engine synthesizes answers using *only* retrieved evidence from ChromaDB vector stores and clearly distinguishes divine Quranic verses, prophetic Hadith narrations, and Tafseer commentary.
- **⚡ Comprehensive REST API**: Exposes clean JSON endpoints for semantic RAG queries, keyword searches, Surah indexes, Hadith collection metadata, and interactive API documentation.
- **🎨 Executive Web Interface**:
  - **Modern Islamic Aesthetic**: Obsidian Midnight Teal & Royal Gold design system with glassmorphism and Arabic calligraphy styling (`Amiri` & `Scheherazade New`).
  - **Dual Theme Support**: Instant dark mode and warm parchment light mode toggle.
  - **Knowledge Scope Router**: Toggle search scope between *Quran Verses & Tafsir*, *Prophetic Hadiths*, or *Combined Islamic Knowledge*.
  - **Evidence Inspector Drawer**: Side drawer presenting vector distance scores, match percentages (%), Hadith numbers, Book/Chapter metadata, and Arabic script with Tashkeel.
  - **Interactive Modals**:
    - 🕋 **Quran Surahs Explorer**: Browse and search all 114 Surahs.
    - 📜 **Hadith Collections Index**: Explore individual Hadith canonical books.
    - 🔖 **Personal Bookmarks Library**: Save verses and Hadiths for offline study (`localStorage`).
    - 🎨 **Quote Card Exporter**: Generate shareable social media cards with Arabic text and exact citations.
    - 🔊 **Text-To-Speech (Speech Synthesis)**: Listen to English translations and Arabic quotes aloud.

---

## 📐 Architecture & Technology Stack

```mermaid
graph TD
    User([User / Client App]) -->|HTTP / REST API| FlaskServer[Flask API Server (app.py)]
    FlaskServer -->|Static Files| Frontend[HTML5 / Vanilla CSS3 / JavaScript ES6+]
    FlaskServer -->|RAG Query| IslamicRAG[IslamicRAG Engine (rag.py)]
    IslamicRAG -->|Vector Embeddings| OllamaEmbed[Ollama (mxbai-embed-large)]
    IslamicRAG -->|Vector Similarity Query| ChromaDB[(ChromaDB Persistent Store)]
    ChromaDB -->|Quran Collection| QuranData[Quran & Tafseer Dataset]
    ChromaDB -->|Hadith Collection| HadithData[Cleaned Hadith Dataset]
    IslamicRAG -->|LLM Synthesis| OllamaLLM[Ollama (qwen3.5:4b)]
    OllamaLLM -->|Grounded Response| User
```

- **Backend**: Python 3.11+, Flask 3.1, Flask-CORS, Pandas, TQDM.
- **Vector Database**: ChromaDB (Persistent local vector storage).
- **LLM & Embeddings**: Ollama (`qwen3.5:4b` LLM, `mxbai-embed-large` embedding model).
- **Frontend**: Vanilla HTML5, CSS3 (Custom design system with HSL variables), Modern JavaScript (ES6+), Web Speech API.

---

## 🚀 Quick Start Guide

### 1. Prerequisites

Make sure you have installed:
- [Python 3.10+](https://www.python.org/)
- [Ollama](https://ollama.ai/) running locally with the required models pulled:
  ```bash
  ollama pull mxbai-embed-large
  ollama pull qwen3.5:4b
  ```

### 2. Environment Setup

Clone or enter the project directory and create a Python virtual environment:

```bash
cd AlMarji3

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Database Ingestion (Optional)

If rebuilding or ingesting the vector database from CSV files:

```bash
python ingest.py
```

*Note: Pre-indexed ChromaDB vectors are preserved in the `chroma_db/` directory.*

### 4. Running the Server

Start the Al-Marji3 API & Web Application:

```bash
python app.py
```

The server will start on **`http://localhost:8000`**.

---

## ⚡ REST API Reference

Al-Marji3 exposes a complete REST API for developers to query Islamic sources programmatically.

### 1. Execute RAG Query

Submit a user question to receive a grounded answer along with retrieved Quran and Hadith sources.

- **Endpoint**: `POST /api/query`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "question": "What does the Quran and Hadith say about seeking knowledge?",
    "source": "all",
    "top_k": 5
  }
  ```
- **Example Response**:
  ```json
  {
    "success": true,
    "answer": "According to the authentic Islamic traditions...",
    "engine": "live_rag",
    "retrieved": [
      {
        "type": "quran",
        "text": "Say: Are those who know equal to those who do not know?",
        "metadata": {
          "surah_name": "Az-Zumar",
          "surah": 39,
          "ayah": 9,
          "tafseer": "Commentary on the elevated status of scholars..."
        },
        "distance": 0.1245
      },
      {
        "type": "hadith",
        "text": "He who treads a path in search of knowledge, Allah will make easy for him a path leading to Paradise.",
        "metadata": {
          "source": "Sahih Muslim",
          "hadith_no": "2699",
          "chapter": "Book of Knowledge",
          "grade": "Sahih (Authentic)"
        },
        "distance": 0.1412
      }
    ]
  }
  ```

### 2. Search Quran Verses

Keyword search across Quran verses and Tafseer commentary.

- **Endpoint**: `GET /api/quran/search?q={query}&limit={limit}`
- **Example**: `GET http://localhost:8000/api/quran/search?q=patience&limit=5`

### 3. List Quran Surahs

Retrieve metadata for all 114 Surahs.

- **Endpoint**: `GET /api/quran/surahs`

### 4. Get Surah Verses

Fetch all verses and Tafseer commentary for a specific Surah by its ID (1-114).

- **Endpoint**: `GET /api/quran/surah/{surah_id}`
- **Example**: `GET http://localhost:8000/api/quran/surah/1`

### 5. Search Hadiths

Keyword search across indexed Hadith collections.

- **Endpoint**: `GET /api/hadith/search?q={query}&collection={collection}`
- **Example**: `GET http://localhost:8000/api/hadith/search?q=intention`

### 6. Interactive API Documentation

Retrieve the API documentation JSON schema programmatically:

- **Endpoint**: `GET /api/docs`

### 7. System Health Check

Check vector database availability and service status.

- **Endpoint**: `GET /api/health`

---

## 💻 Code Integration Examples

### Python (`requests`)

```python
import requests

url = "http://localhost:8000/api/query"
payload = {
    "question": "What is the Hadith regarding intentions?",
    "source": "hadith",
    "top_k": 3
}

response = requests.post(url, json=payload)
data = response.json()

print("AI Answer:", data["answer"])
for item in data["retrieved"]:
    print(f"- {item['metadata'].get('source')}: {item['text']}")
```

### JavaScript (`fetch`)

```javascript
async function askAlMarji3(question) {
  const response = await fetch("http://localhost:8000/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: question,
      source: "all",
      top_k: 5
    })
  });
  
  const result = await response.json();
  console.log("Answer:", result.answer);
  console.log("Retrieved Evidence:", result.retrieved);
}

askAlMarji3("What does the Quran say about hardship and ease?");
```

---

## 🛡️ Grounding & Scholarly Disclaimer

- **Al-Marji3** is designed strictly as a research tool to assist students of knowledge and researchers in locating relevant Quranic verses and Hadiths.
- Answers are synthesized strictly from retrieved text entries stored in ChromaDB.
- **Not a Fatwa Issuer**: This software does not issue independent religious rulings (*fatwas*). Users seeking binding personal legal rulings should consult qualified Islamic scholars and jurisprudential councils.

---

## 📄 License

This repository is maintained for research and educational purposes. All Quran translations and Hadith datasets belong to their respective scholarly sources and publishers.
