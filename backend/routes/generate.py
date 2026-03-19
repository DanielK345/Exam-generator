import uuid
from fastapi import APIRouter, HTTPException
from models.schema import ExamConfig, ExamResponse, Question, GradeRequest, GradeResponse
from services.chunker import chunk_pages
from services.embedder import build_faiss_index
from services.retriever import retrieve_chunks
from services.generator import generate_questions
from services.validator import validate_questions
from services.grader import grade_exam

router = APIRouter()


@router.post("/generate", response_model=ExamResponse)
async def generate_exam(config: ExamConfig):
    from app import documents_store, exams_store

    # Validate document exists
    if config.document_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a file first.")

    doc = documents_store[config.document_id]
    pages = doc["pages"]

    # Step 1: Chunk the document
    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text chunks could be created from the document.")

    # Step 2: Build FAISS index
    try:
        index, indexed_chunks = build_faiss_index(chunks, config.document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # Step 3: Retrieve relevant chunks
    query = config.focus if config.focus else "key concepts, important topics, main ideas"
    retrieved = retrieve_chunks(query, index, indexed_chunks, top_k=15)

    if not retrieved:
        raise HTTPException(status_code=400, detail="No relevant content found for the given focus.")

    # Step 4: Generate + Validate (with retry)
    total_needed = config.mcq + config.true_false + config.short_answer
    all_valid = []
    max_retries = 2
    temperature = 0.7

    for attempt in range(max_retries + 1):
        # Calculate how many more we need of each type
        valid_by_type = {"mcq": 0, "true_false": 0, "short_answer": 0}
        for q in all_valid:
            valid_by_type[q["type"]] = valid_by_type.get(q["type"], 0) + 1

        need_mcq = max(0, config.mcq - valid_by_type["mcq"])
        need_tf = max(0, config.true_false - valid_by_type["true_false"])
        need_sa = max(0, config.short_answer - valid_by_type["short_answer"])

        if need_mcq + need_tf + need_sa == 0:
            break

        try:
            questions = generate_questions(
                chunks=retrieved,
                mcq=need_mcq,
                true_false=need_tf,
                short_answer=need_sa,
                difficulty=config.difficulty,
                temperature=temperature,
            )
        except Exception as e:
            if attempt < max_retries:
                temperature = 0.3
                continue
            raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

        valid, rejected = validate_questions(questions, retrieved)
        all_valid.extend(valid)

        if len(rejected) == 0 or attempt >= max_retries:
            break

        # Retry with lower temperature
        temperature = 0.3

    if not all_valid:
        raise HTTPException(status_code=500, detail="Failed to generate valid questions. Try with different settings.")

    # Build exam
    exam_id = str(uuid.uuid4())
    exam_questions = [
        Question(
            type=q["type"],
            question=q["question"],
            options=q.get("options"),
            answer=q["answer"],
            explanation=q["explanation"],
            source=q["source"],
        )
        for q in all_valid
    ]

    exam_data = ExamResponse(
        exam_id=exam_id,
        questions=exam_questions,
        time_limit=config.time_limit,
    )

    exams_store[exam_id] = exam_data

    return exam_data


@router.get("/exam/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: str):
    from app import exams_store

    if exam_id not in exams_store:
        raise HTTPException(status_code=404, detail="Exam not found.")

    return exams_store[exam_id]


@router.post("/grade", response_model=GradeResponse)
async def grade(request: GradeRequest):
    from app import exams_store

    if request.exam_id not in exams_store:
        raise HTTPException(status_code=404, detail="Exam not found.")

    exam = exams_store[request.exam_id]
    questions = [q.model_dump() for q in exam.questions]

    result = grade_exam(questions, request.answers)
    return GradeResponse(**result)
