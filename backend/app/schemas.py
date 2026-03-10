from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["beginner", "intermediate", "advanced"]
TopicStatusLabel = Literal["mastered", "weak", "ready", "locked"]
UserRole = Literal["student", "teacher", "admin"]


class CourseSummary(BaseModel):
    id: str
    title: str
    description: str
    topic_count: int


class StudentSummary(BaseModel):
    id: str
    name: str
    course_id: str
    skill_level: str


class DashboardMetrics(BaseModel):
    mastery_average: float
    completion_percent: float
    average_response_seconds: float
    practice_events: int


class Recommendation(BaseModel):
    topic_id: str
    title: str
    reason: str
    action: str
    difficulty: Difficulty


class LearningPathNode(BaseModel):
    topic_id: str
    title: str
    mastery: float
    status: TopicStatusLabel
    prerequisites: list[str]


class DashboardResponse(BaseModel):
    student: StudentSummary
    course: CourseSummary
    metrics: DashboardMetrics
    weak_topics: list[str]
    recommendations: list[Recommendation]
    learning_path: list[LearningPathNode]


class QuizQuestion(BaseModel):
    id: str
    topic_id: str
    topic_title: str
    prompt: str
    options: list[str]
    difficulty: Difficulty


class QuizAnswerInput(BaseModel):
    question_id: str
    selected_option: str
    response_time_seconds: int = Field(default=30, ge=1, le=600)


class QuizSubmission(BaseModel):
    student_id: str
    course_id: str
    answers: list[QuizAnswerInput]


class QuizEvaluation(BaseModel):
    question_id: str
    topic_id: str
    is_correct: bool
    correct_option: str
    explanation: str


class QuizResponse(BaseModel):
    score_percent: float
    recommended_difficulty: Difficulty
    weak_topics: list[str]
    recommendations: list[Recommendation]
    evaluations: list[QuizEvaluation]


class TopicGraphNode(BaseModel):
    topic_id: str
    title: str
    mastery: float
    status: TopicStatusLabel
    prerequisites: list[str]


class TutorRequest(BaseModel):
    student_id: str
    question: str = Field(min_length=3, max_length=500)
    topic_id: str | None = None


class TutorResponse(BaseModel):
    topic_id: str
    topic_title: str
    answer: str
    recommended_follow_up: str


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=4, max_length=64)


class AuthUser(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    student_id: str | None = None
    course_id: str | None = None
    skill_level: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
    user: AuthUser


class LogoutResponse(BaseModel):
    status: Literal["logged_out"]
