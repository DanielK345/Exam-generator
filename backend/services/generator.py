import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_TEMPLATE = """You are an exam generator.

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
{{
  "questions": [
    {{
      "type": "mcq",
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "explanation": "...",
      "source": "slide_3"
    }},
    {{
      "type": "true_false",
      "question": "...",
      "options": ["True", "False"],
      "answer": "True",
      "explanation": "...",
      "source": "page_2"
    }},
    {{
      "type": "short_answer",
      "question": "...",
      "options": null,
      "answer": "...",
      "explanation": "...",
      "source": "page_1"
    }}
  ]
}}

CONTEXT:
{context}

Generate:
- {mcq} MCQ questions
- {true_false} True/False questions
- {short_answer} Short Answer questions

Difficulty: {difficulty}
"""


def build_context_block(chunks: list[dict]) -> str:
    """Build a context string from retrieved chunks."""
    parts = []
    for chunk in chunks:
        parts.append(f"[Source: {chunk['source']}]\n{chunk['content']}")
    return "\n\n".join(parts)


def generate_questions(
    chunks: list[dict],
    mcq: int,
    true_false: int,
    short_answer: int,
    difficulty: str,
    temperature: float = 0.7,
) -> list[dict]:
    """Generate exam questions using Gemini with RAG context."""
    context = build_context_block(chunks)

    prompt = PROMPT_TEMPLATE.format(
        context=context,
        mcq=mcq,
        true_false=true_false,
        short_answer=short_answer,
        difficulty=difficulty,
    )

    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Parse JSON response
    parsed = json.loads(text)
    questions = parsed.get("questions", [])

    return questions
