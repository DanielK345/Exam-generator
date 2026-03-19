# Phase 1: Exam Generator Web App (MVP) – Implementation Instructions

## 🎯 Objective
Build a working demo web application that:
1. Accepts PDF and PPTX uploads
2. Extracts and processes text
3. Generates an exam based on user-defined format
4. Displays an interactive exam interface with timer and grading

⚠️ CRITICAL REQUIREMENT:
The system MUST minimize hallucination and produce HIGH-QUALITY, RELEVANT questions grounded strictly in the uploaded documents.

---

## 🧱 Tech Stack (MANDATORY)

### Backend
- Python
- FastAPI
- LangChain (or minimal custom RAG pipeline)
- Embeddings: OpenAI or BGE
- Vector DB: FAISS or Chroma

### Frontend
- React (simple UI)

### File Processing
- PDF: PyMuPDF or pdfplumber
- PPTX: python-pptx

---

## 📁 Project Structure

```
backend/
  app.py
  routes/
    upload.py
    generate.py
  services/
    parser.py
    chunker.py
    embedder.py
    retriever.py
    generator.py
    validator.py
  models/
    schema.py

frontend/
  src/
    pages/
      UploadPage.jsx
      ConfigPage.jsx
      ExamPage.jsx
    components/
      Timer.jsx
      Question.jsx
```

---

## 🔄 End-to-End Workflow

### Step 1: Upload + Parsing

- Accept PDF and PPTX files
- Extract raw text:
  - PDF → page-level
  - PPTX → slide-level

Output format:
```
{
  "source": "slide_3",
  "content": "text here"
}
```

---

### Step 2: Chunking (VERY IMPORTANT)

- Chunk size: 300–500 tokens
- Overlap: 50 tokens
- Each chunk MUST include:
  - source reference
  - clean text (remove noise)

Example:
```
{
  "chunk_id": "doc1_chunk_5",
  "source": "slide_3",
  "content": "..."
}
```

---

### Step 3: Embedding + Storage

- Convert chunks → embeddings
- Store in FAISS/Chroma

---

### Step 4: Exam Configuration Input

Example:
```
{
  "time_limit": 30,
  "mcq": 10,
  "true_false": 5,
  "short_answer": 3,
  "difficulty": "medium",
  "focus": "chapter 2 and 3"
}
```

---

### Step 5: Retrieval (ANTI-HALLUCINATION CORE)

⚠️ DO NOT generate questions from the LLM without retrieval.

- Query vector DB using:
  - user focus
  - OR generic queries like "key concepts"

- Retrieve TOP-K chunks (K = 10–20)

- Combine into a CONTEXT BLOCK:
```
CONTEXT:
[Chunk 1]
[Chunk 2]
...
```

---

## 🧠 Step 6: Question Generation (CRITICAL SECTION)

This is the MOST IMPORTANT part of the system.

### 🔴 STRICT RULES

1. The LLM MUST ONLY use the provided CONTEXT
2. If answer is not in context → DO NOT CREATE QUESTION
3. Every question MUST:
   - be answerable from context
   - include a source reference
4. NO vague or opinion-based questions

---

## 🧾 Prompt Template (USE EXACTLY)

```
You are an exam generator.

Your task is to generate HIGH-QUALITY exam questions strictly based on the provided CONTEXT.

RULES:
- ONLY use information from the CONTEXT
- DO NOT use outside knowledge
- DO NOT hallucinate
- If information is insufficient, SKIP the question
- Each question must be clear, unambiguous, and test understanding
- Avoid trivial or overly obvious questions
- Avoid repeating the same concept

QUESTION QUALITY REQUIREMENTS:
- Must test understanding, not just copying text
- Must be specific and precise
- Must have exactly ONE correct answer
- Distractors (wrong options) must be plausible

OUTPUT FORMAT (STRICT JSON):
{
  "questions": [
    {
      "type": "mcq",
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A",
      "explanation": "...",
      "source": "slide_3"
    }
  ]
}

CONTEXT:
{context}

Generate:
- {mcq} MCQ
- {true_false} True/False
- {short_answer} Short Answer

Difficulty: {difficulty}
```

---

## 🛡️ Step 7: Validation Layer (MANDATORY)

After generation, VALIDATE each question.

### Reject question if:
- Answer not found in context
- अस्पष्ट / ambiguous wording
- Duplicate question
- Multiple correct answers

### Basic validation logic:
- Check if answer string appears in retrieved chunks
- Check length and clarity

---

## 🔁 Step 8: Regeneration Strategy

If validation fails:
- Retry generation with:
  - lower temperature (0.3–0.5)
  - different chunk subset

MAX retries: 2

---

## 🖥️ Step 9: Exam Interface

### Features
- Timer countdown
- Question navigation
- Submit button
- Auto grading:
  - MCQ
  - True/False

---

## 📊 Step 10: Output

Display:
- Score
- Correct answers
- Explanations

---

## ⚙️ API Design

### POST /upload
- Input: file
- Output: document_id

### POST /generate
- Input: document_id + config
- Output: questions JSON

### GET /exam
- Returns generated exam

---

## 🔥 Key Anti-Hallucination Strategies (NON-NEGOTIABLE)

1. Retrieval-first (RAG mandatory)
2. Strict prompt constraints
3. JSON structured output
4. Validation layer
5. Regeneration on failure

---

## 🚀 Minimum Demo Success Criteria

The system is considered COMPLETE if:

- Upload PDF/PPTX works
- Questions are generated
- Questions are grounded in document
- Exam UI works with timer
- No obvious hallucinated questions

---

## 🧠 Notes for Coding Agent

- Prioritize correctness over complexity
- Keep UI minimal
- Focus MOST effort on prompt + validation
- Do NOT over-engineer

---

## ✅ Final Deliverable

A working web app where:
1. User uploads lecture slides
2. Configures exam
3. Clicks "Generate"
4. Takes exam in browser
5. Gets score immediately

---

---

## 🧠 Short Answer Grading Strategy (MANDATORY)

### 🎯 Goal
Efficiently and accurately grade short-answer responses while minimizing cost, latency, and hallucination.

---

## ❗ DO NOT use a single approach

- ❌ Only LLM → slow, expensive, inconsistent
- ❌ Only similarity → shallow, inaccurate

✅ MUST implement a HYBRID grading pipeline

---

## 🔄 Two-Stage Grading Pipeline

### Stage 1: Semantic Similarity (FAST FILTER)

- Embed:
  - student answer
  - reference answer

- Compute cosine similarity

Thresholds:
```
similarity > 0.85 → correct (score = 1)
similarity < 0.5 → incorrect (score = 0)
otherwise → send to LLM
```

Recommended model:
- BGE (bge-small-en)

---

### Stage 2: LLM Grading (FALLBACK ONLY)

Use LLM ONLY when similarity is inconclusive.

---

## 🧾 LLM Grading Prompt (USE EXACTLY)

```
You are a strict exam grader.

QUESTION:
{question}

REFERENCE ANSWER:
{reference}

STUDENT ANSWER:
{student}

GRADING RULES:
- Grade based ONLY on correctness relative to reference
- Accept paraphrasing if meaning is equivalent
- Do NOT give credit for partially correct answers unless specified
- Be strict and objective

OUTPUT FORMAT:
{
  "score": 0 or 1,
  "reason": "short explanation"
}
```

---

## ⚙️ Implementation Logic

```
def grade_answer(student, reference):
    sim = cosine_similarity(embed(student), embed(reference))

    if sim > 0.85:
        return {"score": 1, "reason": "High semantic similarity"}

    if sim < 0.5:
        return {"score": 0, "reason": "Low semantic similarity"}

    return llm_grade(student, reference)
```

---

## 🔥 Optional Upgrade (RECOMMENDED)

### Keyword Coverage Check

- Extract key concepts from reference answer
- Check if student answer covers them

Example:

Reference:
"Photosynthesis converts light energy into chemical energy using chlorophyll"

Key points:
- light energy
- chemical energy
- chlorophyll

Rule:
- If ≥ 2 key points present → likely correct

---

## 📊 Output Format

Return:
```
{
  "score": 0 or 1,
  "feedback": "short explanation"
}
```

---

## 🚀 Requirements

- MUST use hybrid grading
- MUST avoid unnecessary LLM calls
- MUST keep grading deterministic where possible

---

END OF INSTRUCTIONS

