"""
Test whether the embedding-based cosine similarity (Stage 1 of the grader)
can correctly distinguish correct vs incorrect short answers on its own.

Requires GEMINI_API_KEY env variable to be set.
Run:
    cd backend && python -m pytest ../tests/test_grader.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from services.grader import _cosine_similarity, SIM_CORRECT_THRESHOLD, SIM_INCORRECT_THRESHOLD
from services.embedder import embed_query


@pytest.fixture(scope="module")
def api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set")
    return key


# Each case: (question, correct_answer, student_answer)
# Correct answers — student says the same thing in different words
CORRECT_PAIRS = [
    (
        "What is the powerhouse of the cell?",
        "The mitochondria",
        "Mitochondria generates energy for the cell",
    ),
    (
        "What is the chemical formula for water?",
        "H2O",
        "Water is H2O, two hydrogen atoms and one oxygen",
    ),
    (
        "Who wrote Romeo and Juliet?",
        "William Shakespeare",
        "Shakespeare authored Romeo and Juliet",
    ),
    (
        "What does CPU stand for?",
        "Central Processing Unit",
        "CPU means Central Processing Unit",
    ),
    (
        "What is the boiling point of water at sea level?",
        "100 degrees Celsius",
        "Water boils at 100°C under standard atmospheric pressure",
    ),
    (
        "What planet is known as the Red Planet?",
        "Mars",
        "Mars is called the Red Planet",
    ),
    (
        "What is Newton's second law of motion?",
        "Force equals mass times acceleration (F=ma)",
        "F = ma, the net force on an object equals its mass multiplied by acceleration",
    ),
    (
        "What is the process by which plants make food from sunlight?",
        "Photosynthesis",
        "Plants use photosynthesis to convert sunlight into glucose",
    ),
    (
        "What is the largest organ in the human body?",
        "The skin",
        "Skin is the body's largest organ",
    ),
    (
        "What carries genetic information in living organisms?",
        "DNA (deoxyribonucleic acid)",
        "Deoxyribonucleic acid, or DNA, stores the genetic code",
    ),
]

# Incorrect answers — student gives a wrong or unrelated answer
INCORRECT_PAIRS = [
    (
        "What is the powerhouse of the cell?",
        "The mitochondria",
        "The nucleus is the brain of the cell",
    ),
    (
        "What is the chemical formula for water?",
        "H2O",
        "NaCl is the formula for table salt",
    ),
    (
        "Who wrote Romeo and Juliet?",
        "William Shakespeare",
        "Charles Dickens wrote Oliver Twist",
    ),
    (
        "What does CPU stand for?",
        "Central Processing Unit",
        "GPU stands for Graphics Processing Unit",
    ),
    (
        "What is the boiling point of water at sea level?",
        "100 degrees Celsius",
        "Water freezes at zero degrees",
    ),
    (
        "What planet is known as the Red Planet?",
        "Mars",
        "Jupiter is the largest planet in our solar system",
    ),
    (
        "What is Newton's second law of motion?",
        "Force equals mass times acceleration (F=ma)",
        "Every action has an equal and opposite reaction",
    ),
    (
        "What is the process by which plants make food from sunlight?",
        "Photosynthesis",
        "Cellular respiration breaks down glucose for energy",
    ),
    (
        "What is the largest organ in the human body?",
        "The skin",
        "The liver is responsible for detoxification",
    ),
    (
        "What carries genetic information in living organisms?",
        "DNA (deoxyribonucleic acid)",
        "Red blood cells carry oxygen through the body",
    ),
]


def _embed_and_score(reference: str, student: str) -> float:
    """Embed both answers and return cosine similarity."""
    ref_emb = embed_query(reference)
    stu_emb = embed_query(student)
    return _cosine_similarity(ref_emb, stu_emb)


# ---------------------------------------------------------------------------
# Tests: correct answers should have HIGH similarity
# ---------------------------------------------------------------------------

class TestCorrectAnswerSimilarity:
    """Correct student answers should score above the INCORRECT threshold,
    ideally above the CORRECT threshold so Stage 1 alone marks them right."""

    @pytest.mark.parametrize(
        "question,correct,student", CORRECT_PAIRS,
        ids=[f"correct_{i}" for i in range(len(CORRECT_PAIRS))],
    )
    def test_similarity_above_incorrect_threshold(self, api_key, question, correct, student):
        sim = _embed_and_score(correct, student)
        assert sim > SIM_INCORRECT_THRESHOLD, (
            f"sim={sim:.3f} fell below INCORRECT threshold ({SIM_INCORRECT_THRESHOLD}) "
            f"for a correct answer.\n"
            f"  Q: {question}\n  Expected: {correct}\n  Student: {student}"
        )

    @pytest.mark.parametrize(
        "question,correct,student", CORRECT_PAIRS,
        ids=[f"correct_high_{i}" for i in range(len(CORRECT_PAIRS))],
    )
    def test_similarity_above_correct_threshold(self, api_key, question, correct, student):
        """Ideally the embedder gives > 0.85 so Stage 1 alone handles it."""
        sim = _embed_and_score(correct, student)
        # Log the score even if it passes — helpful for tuning thresholds
        print(f"  sim={sim:.3f}  Q: {question[:50]}  A: {student[:50]}")
        assert sim > SIM_CORRECT_THRESHOLD, (
            f"sim={sim:.3f} below CORRECT threshold ({SIM_CORRECT_THRESHOLD}). "
            f"This answer would fall to LLM fallback.\n"
            f"  Q: {question}\n  Expected: {correct}\n  Student: {student}"
        )


# ---------------------------------------------------------------------------
# Tests: wrong answers should have LOW similarity
# ---------------------------------------------------------------------------

class TestIncorrectAnswerSimilarity:
    """Wrong student answers should score below the CORRECT threshold,
    ideally below the INCORRECT threshold so Stage 1 alone rejects them."""

    @pytest.mark.parametrize(
        "question,correct,student", INCORRECT_PAIRS,
        ids=[f"wrong_{i}" for i in range(len(INCORRECT_PAIRS))],
    )
    def test_similarity_below_correct_threshold(self, api_key, question, correct, student):
        sim = _embed_and_score(correct, student)
        assert sim < SIM_CORRECT_THRESHOLD, (
            f"sim={sim:.3f} exceeded CORRECT threshold ({SIM_CORRECT_THRESHOLD}) "
            f"for a wrong answer!\n"
            f"  Q: {question}\n  Expected: {correct}\n  Student: {student}"
        )

    @pytest.mark.parametrize(
        "question,correct,student", INCORRECT_PAIRS,
        ids=[f"wrong_low_{i}" for i in range(len(INCORRECT_PAIRS))],
    )
    def test_similarity_below_incorrect_threshold(self, api_key, question, correct, student):
        """Ideally the embedder gives < 0.5 so Stage 1 alone rejects it."""
        sim = _embed_and_score(correct, student)
        print(f"  sim={sim:.3f}  Q: {question[:50]}  A: {student[:50]}")
        assert sim < SIM_INCORRECT_THRESHOLD, (
            f"sim={sim:.3f} above INCORRECT threshold ({SIM_INCORRECT_THRESHOLD}). "
            f"This wrong answer would fall to LLM fallback.\n"
            f"  Q: {question}\n  Expected: {correct}\n  Student: {student}"
        )


# ---------------------------------------------------------------------------
# Tests: correct vs incorrect for SAME question — correct should always win
# ---------------------------------------------------------------------------

class TestRelativeRanking:
    """For each question, the correct answer should always have higher
    similarity to the reference than the wrong answer."""

    PAIRED = list(zip(CORRECT_PAIRS, INCORRECT_PAIRS))

    @pytest.mark.parametrize(
        "correct_case,incorrect_case", PAIRED,
        ids=[f"rank_{i}" for i in range(len(PAIRED))],
    )
    def test_correct_ranks_higher_than_incorrect(self, api_key, correct_case, incorrect_case):
        question, correct_answer, good_student = correct_case
        _, _, bad_student = incorrect_case

        sim_good = _embed_and_score(correct_answer, good_student)
        sim_bad = _embed_and_score(correct_answer, bad_student)

        assert sim_good > sim_bad, (
            f"Correct answer similarity ({sim_good:.3f}) should exceed "
            f"incorrect answer similarity ({sim_bad:.3f}).\n"
            f"  Q: {question}\n"
            f"  Reference: {correct_answer}\n"
            f"  Good answer: {good_student}\n"
            f"  Bad answer:  {bad_student}"
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


