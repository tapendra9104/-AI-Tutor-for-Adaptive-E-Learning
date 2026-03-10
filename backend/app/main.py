from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .data import COURSES, STUDENTS
from .schemas import (
    AuthUser,
    CourseSummary,
    DashboardResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    QuizEvaluation,
    QuizQuestion,
    QuizResponse,
    QuizSubmission,
    TopicGraphNode,
    TutorRequest,
    TutorResponse,
)
from .services.adaptive_engine import (
    build_learning_path,
    build_metrics,
    calculate_mastery,
    classify_topic_status,
    detect_weak_topics,
    get_question_map,
    get_topic_map,
    recommended_difficulty,
    select_next_quiz,
)
from .services.auth_service import (
    authenticate_user,
    create_session,
    get_user_from_token,
    revoke_session,
    serialize_user,
)
from .services.recommendation_engine import build_recommendations
from .services.tutor_service import generate_tutor_response, infer_topic


app = FastAPI(
    title="AI Tutor for Adaptive E-Learning API",
    version="0.1.0",
    description="Starter backend for adaptive quizzes, recommendations, and tutor responses.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


def get_student(student_id: str) -> dict:
    student = STUDENTS.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' was not found.")
    return student


def get_course(course_id: str) -> dict:
    course = COURSES.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{course_id}' was not found.")
    return course


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def get_current_user(token: str = Depends(get_bearer_token)) -> dict:
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def authorize_student_access(student_id: str, current_user: dict) -> dict:
    if current_user["role"] == "student" and current_user.get("student_id") != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this student record.",
        )
    return get_student(student_id)


def build_dashboard_payload(student: dict) -> DashboardResponse:
    course = get_course(student["course_id"])
    mastery = calculate_mastery(course, student["attempts"])
    statuses = classify_topic_status(course, mastery)
    weak_topics = detect_weak_topics(course, student["attempts"], mastery)
    recommendations = build_recommendations(course, mastery, weak_topics)
    metrics = build_metrics(course, student["attempts"], mastery)
    learning_path = build_learning_path(course, mastery, statuses)

    return DashboardResponse(
        student={
            "id": student["id"],
            "name": student["name"],
            "course_id": student["course_id"],
            "skill_level": student["skill_level"],
        },
        course=CourseSummary(
            id=course["id"],
            title=course["title"],
            description=course["description"],
            topic_count=len(course["topics"]),
        ),
        metrics=metrics,
        weak_topics=weak_topics,
        recommendations=recommendations,
        learning_path=learning_path,
    )


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_session(user["id"])
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=AuthUser(**serialize_user(user)),
    )


@app.get("/api/auth/me", response_model=AuthUser)
def read_current_user(current_user: dict = Depends(get_current_user)) -> AuthUser:
    return AuthUser(**serialize_user(current_user))


@app.post("/api/auth/logout", response_model=LogoutResponse)
def logout(token: str = Depends(get_bearer_token)) -> LogoutResponse:
    revoke_session(token)
    return LogoutResponse(status="logged_out")


@app.get("/api/courses", response_model=list[CourseSummary])
def list_courses() -> list[CourseSummary]:
    return [
        CourseSummary(
            id=course["id"],
            title=course["title"],
            description=course["description"],
            topic_count=len(course["topics"]),
        )
        for course in COURSES.values()
    ]


@app.get("/api/students/{student_id}/dashboard", response_model=DashboardResponse)
def get_dashboard(student_id: str, current_user: dict = Depends(get_current_user)) -> DashboardResponse:
    student = authorize_student_access(student_id, current_user)
    return build_dashboard_payload(student)


@app.get("/api/students/{student_id}/knowledge-graph", response_model=list[TopicGraphNode])
def get_knowledge_graph(
    student_id: str,
    course_id: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> list[TopicGraphNode]:
    student = authorize_student_access(student_id, current_user)
    resolved_course = get_course(course_id or student["course_id"])
    mastery = calculate_mastery(resolved_course, student["attempts"])
    statuses = classify_topic_status(resolved_course, mastery)
    topic_map = get_topic_map(resolved_course)

    return [
        TopicGraphNode(
            topic_id=topic_id,
            title=topic_map[topic_id]["title"],
            mastery=mastery.get(topic_id, 0.0),
            status=statuses[topic_id],
            prerequisites=topic_map[topic_id]["prerequisites"],
        )
        for topic_id in topic_map
    ]


@app.get("/api/quizzes/next", response_model=list[QuizQuestion])
def get_next_quiz(
    student_id: str,
    course_id: str,
    current_user: dict = Depends(get_current_user),
) -> list[QuizQuestion]:
    student = authorize_student_access(student_id, current_user)
    course = get_course(course_id)
    topic_map = get_topic_map(course)

    return [
        QuizQuestion(
            id=question["id"],
            topic_id=question["topic_id"],
            topic_title=topic_map[question["topic_id"]]["title"],
            prompt=question["prompt"],
            options=question["options"],
            difficulty=question["difficulty"],
        )
        for question in select_next_quiz(course, student["attempts"])
    ]


@app.post("/api/quizzes/submit", response_model=QuizResponse)
def submit_quiz(payload: QuizSubmission, current_user: dict = Depends(get_current_user)) -> QuizResponse:
    student = authorize_student_access(payload.student_id, current_user)
    course = get_course(payload.course_id)
    question_map = get_question_map(course)

    if not payload.answers:
        raise HTTPException(status_code=400, detail="At least one quiz answer is required.")

    evaluations: list[QuizEvaluation] = []
    new_attempts: list[dict] = []

    for answer in payload.answers:
        question = question_map.get(answer.question_id)
        if not question:
            raise HTTPException(status_code=404, detail=f"Question '{answer.question_id}' was not found.")

        is_correct = answer.selected_option == question["correct_option"]
        evaluations.append(
            QuizEvaluation(
                question_id=question["id"],
                topic_id=question["topic_id"],
                is_correct=is_correct,
                correct_option=question["correct_option"],
                explanation=question["explanation"],
            )
        )
        new_attempts.append(
            {
                "question_id": question["id"],
                "topic_id": question["topic_id"],
                "is_correct": is_correct,
                "selected_option": answer.selected_option,
                "response_time_seconds": answer.response_time_seconds,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    student["attempts"].extend(new_attempts)
    mastery = calculate_mastery(course, student["attempts"])
    weak_topics = detect_weak_topics(course, student["attempts"], mastery)
    recommendations = build_recommendations(course, mastery, weak_topics)
    score_percent = round(
        (sum(1 for evaluation in evaluations if evaluation.is_correct) / len(evaluations)) * 100,
        1,
    )

    return QuizResponse(
        score_percent=score_percent,
        recommended_difficulty=recommended_difficulty(student["attempts"]),
        weak_topics=weak_topics,
        recommendations=recommendations,
        evaluations=evaluations,
    )


@app.post("/api/tutor/ask", response_model=TutorResponse)
def ask_tutor(payload: TutorRequest, current_user: dict = Depends(get_current_user)) -> TutorResponse:
    student = authorize_student_access(payload.student_id, current_user)
    course = get_course(student["course_id"])
    mastery = calculate_mastery(course, student["attempts"])
    topic = infer_topic(course, payload.question, payload.topic_id)
    response = generate_tutor_response(student["name"], topic, mastery.get(topic["id"], 0.0), payload.question)
    return TutorResponse(**response)
