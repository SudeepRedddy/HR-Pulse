"""
HRPulse — Policy Q&A Agent (RAG)
Uses LlamaIndex + FAISS + Ollama for policy document Q&A.
Falls back to mock responses if Ollama is not running.

Pipeline: Load hr_policies.txt → chunk → embed → FAISS → retrieve → LLM answer
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import settings

# ── Paths ────────────────────────────────────
POLICY_PATH = settings.DATA_DIR / "hr_policies.txt"
FAISS_INDEX_PATH = settings.ML_MODELS_DIR / "faiss_policy_index"

# ── RAG Pipeline State ───────────────────────
_index = None
_chunks = []


def _load_policy_text() -> str:
    """Load the HR policy document."""
    if not POLICY_PATH.exists():
        return ""
    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []

    chunks = []
    sentences = text.replace("\n\n", "\n").split("\n")
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap
            words = current_chunk.split()
            overlap_words = words[-overlap // 5:] if len(words) > overlap // 5 else words
            current_chunk = " ".join(overlap_words) + " " + sentence
        else:
            current_chunk += " " + sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _build_index():
    """Build the FAISS index from policy document."""
    global _index, _chunks

    text = _load_policy_text()
    if not text:
        print("  [PolicyAgent] No policy document found")
        return

    _chunks = _chunk_text(text)
    print(f"  [PolicyAgent] Created {len(_chunks)} chunks from policy document")

    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np

        # Embed chunks
        print("  [PolicyAgent] Loading embedding model (all-MiniLM-L6-v2)...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(_chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        # Build FAISS index
        dimension = embeddings.shape[1]
        _index = faiss.IndexFlatL2(dimension)
        _index.add(embeddings)

        print(f"  [PolicyAgent] FAISS index built with {_index.ntotal} vectors")

    except ImportError as e:
        print(f"  [PolicyAgent] FAISS/sentence-transformers not available: {e}")
        print("  [PolicyAgent] Will use keyword-based fallback")
        _index = None
    except Exception as e:
        print(f"  [PolicyAgent] Index building failed: {e}")
        _index = None


def _retrieve_chunks(query: str, top_k: int = 3) -> List[str]:
    """Retrieve the most relevant chunks for a query."""
    global _index, _chunks

    if not _chunks:
        _build_index()

    if not _chunks:
        return []

    if _index is not None:
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np

            model = SentenceTransformer("all-MiniLM-L6-v2")
            query_embedding = model.encode([query]).astype("float32")
            distances, indices = _index.search(query_embedding, top_k)

            return [_chunks[i] for i in indices[0] if i < len(_chunks)]
        except Exception:
            pass

    # Keyword fallback
    query_words = set(query.lower().split())
    scored_chunks = []
    for chunk in _chunks:
        chunk_words = set(chunk.lower().split())
        overlap = len(query_words & chunk_words)
        scored_chunks.append((overlap, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored_chunks[:top_k]]


def _query_llm(question: str, context: str) -> str:
    """Query the LLM with context and question."""
    try:
        from langchain_community.chat_models import ChatOllama

        llm = ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.3,
        )

        prompt = f"""You are an HR policy expert assistant. Answer the question based ONLY on the provided policy context.
If the answer is not found in the context, say "I could not find this information in the current HR policies."

Context:
{context}

Question: {question}

Answer concisely and accurately, citing specific policy sections when possible."""

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        # Ollama not available — use mock response
        return _mock_answer(question, context)


def _mock_answer(question: str, context: str) -> str:
    """Generate a mock answer based on keyword matching with the context."""
    question_lower = question.lower()

    if "leave" in question_lower or "vacation" in question_lower or "time off" in question_lower:
        return ("According to HR policy, all full-time employees receive 20 paid vacation days per year, "
                "accrued monthly at 1.67 days per month. Unused leave may be carried forward up to 5 days. "
                "Sick leave is 12 days per year, and parental leave offers 16 weeks for primary caregivers. "
                "Leave requests must be submitted at least 5 business days in advance.")

    elif "remote" in question_lower or "work from home" in question_lower or "hybrid" in question_lower:
        return ("HRPulse supports a hybrid work model. Employees may work remotely up to 3 days per week "
                "with manager approval. Core business hours are 10:00 AM to 4:00 PM. A $500 home office "
                "stipend is provided, and employees must visit the office at least once per month.")

    elif "performance" in question_lower or "review" in question_lower or "rating" in question_lower:
        return ("Performance reviews are conducted quarterly. The rating scale is 1-4: (1) Needs Improvement, "
                "(2) Meets Expectations, (3) Exceeds Expectations, (4) Outstanding. Employees rated 1 for "
                "two consecutive quarters are placed on a 60-day Performance Improvement Plan (PIP). "
                "Compensation adjustments are made during the Q4 annual review.")

    elif "grievance" in question_lower or "complaint" in question_lower or "issue" in question_lower:
        return ("The grievance procedure has 5 steps: (1) Informal resolution within 5 business days, "
                "(2) Formal written complaint to HR, acknowledged within 2 business days, (3) HR investigation "
                "within 10 business days, (4) Written resolution within 5 business days, (5) Appeal to Chief "
                "People Officer within 10 business days. All grievances are confidential.")

    elif "conduct" in question_lower or "behavior" in question_lower or "harassment" in question_lower:
        return ("The Code of Conduct requires respect, inclusion, and professional behavior. Discrimination, "
                "harassment, and bullying are strictly prohibited and result in immediate disciplinary action. "
                "Employees must protect confidential information and disclose conflicts of interest to the "
                "Ethics Committee within 5 business days.")

    else:
        return (f"Based on the HR policy document, here is relevant information: {context[:300]}... "
                "For more specific details, please refer to the complete HR policy document or contact "
                "the HR department at hr@hrpulse.com.")


async def ask_question(question: str) -> Dict:
    """
    Main entry point: answer an HR policy question using RAG.
    Returns: {answer: str, source_snippets: list, confidence: float}
    """
    # Retrieve relevant chunks
    relevant_chunks = _retrieve_chunks(question, top_k=3)

    if not relevant_chunks:
        return {
            "answer": "I could not find relevant information in the HR policies. Please contact HR directly.",
            "source_snippets": [],
            "confidence": 0.0,
        }

    # Combine context
    context = "\n\n".join(relevant_chunks)

    # Query LLM
    answer = _query_llm(question, context)

    return {
        "answer": answer,
        "source_snippets": relevant_chunks,
        "confidence": 0.85 if _index is not None else 0.6,
    }
