from backend.app.data import COURSES, INITIAL_STUDENTS
from backend.app.services.adaptive_engine import (
    calculate_mastery,
    classify_topic_status,
    detect_weak_topics,
    select_next_quiz,
)


def test_recursion_is_detected_as_weak_topic():
    course = COURSES["python-foundations"]
    student = INITIAL_STUDENTS["student-1"]
    mastery = calculate_mastery(course, student["attempts"])
    weak_topics = detect_weak_topics(course, student["attempts"], mastery)

    assert "recursion" in weak_topics


def test_locked_topics_remain_locked_until_prerequisites_are_strong():
    course = COURSES["python-foundations"]
    student = INITIAL_STUDENTS["student-1"]
    mastery = calculate_mastery(course, student["attempts"])
    statuses = classify_topic_status(course, mastery)

    assert statuses["graphs"] == "locked"


def test_next_quiz_prioritizes_weak_or_ready_topics():
    course = COURSES["python-foundations"]
    student = INITIAL_STUDENTS["student-1"]
    questions = select_next_quiz(course, student["attempts"], limit=4)

    assert questions
    assert all(question["topic_id"] in {"conditionals", "loops", "functions", "data-structures", "recursion"} for question in questions)
