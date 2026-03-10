from __future__ import annotations

from collections import defaultdict


def get_course_topics(course: dict) -> list[dict]:
    return course["topics"]


def get_topic_map(course: dict) -> dict[str, dict]:
    return {topic["id"]: topic for topic in course["topics"]}


def get_question_map(course: dict) -> dict[str, dict]:
    return {question["id"]: question for question in course["questions"]}


def calculate_mastery(course: dict, attempts: list[dict]) -> dict[str, float]:
    attempts_by_topic: dict[str, list[dict]] = defaultdict(list)
    for attempt in attempts:
        attempts_by_topic[attempt["topic_id"]].append(attempt)

    mastery: dict[str, float] = {}
    for topic in get_course_topics(course):
        topic_attempts = attempts_by_topic.get(topic["id"], [])
        if not topic_attempts:
            mastery[topic["id"]] = 0.0
            continue

        weights = list(range(1, len(topic_attempts) + 1))
        weighted_correct = 0.0
        total_weight = 0.0
        for weight, attempt in zip(weights, topic_attempts):
            total_weight += weight
            weighted_correct += weight * (1.0 if attempt["is_correct"] else 0.0)

        mastery[topic["id"]] = round(weighted_correct / total_weight, 2)

    return mastery


def classify_topic_status(course: dict, mastery: dict[str, float]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for topic in get_course_topics(course):
        score = mastery.get(topic["id"], 0.0)
        prerequisites = topic["prerequisites"]
        prereq_ready = all(mastery.get(prereq, 0.0) >= 0.65 for prereq in prerequisites)

        if score >= 0.75:
            statuses[topic["id"]] = "mastered"
        elif score > 0 and score < 0.45:
            statuses[topic["id"]] = "weak"
        elif not prerequisites or prereq_ready:
            statuses[topic["id"]] = "ready"
        else:
            statuses[topic["id"]] = "locked"

    return statuses


def detect_weak_topics(course: dict, attempts: list[dict], mastery: dict[str, float]) -> list[str]:
    attempts_by_topic: dict[str, list[dict]] = defaultdict(list)
    for attempt in attempts:
        attempts_by_topic[attempt["topic_id"]].append(attempt)

    weak_topics: list[str] = []
    for topic in get_course_topics(course):
        topic_attempts = attempts_by_topic.get(topic["id"], [])
        if not topic_attempts:
            continue

        topic_mastery = mastery.get(topic["id"], 0.0)
        recent_wrong = not topic_attempts[-1]["is_correct"]
        if topic_mastery < 0.55 or recent_wrong:
            weak_topics.append(topic["id"])

    return weak_topics


def recommended_difficulty(attempts: list[dict]) -> str:
    if not attempts:
        return "beginner"

    recent = attempts[-4:]
    average_score = sum(1 if item["is_correct"] else 0 for item in recent) / len(recent)
    average_time = sum(item["response_time_seconds"] for item in recent) / len(recent)

    if average_score >= 0.8 and average_time <= 25:
        return "advanced"
    if average_score >= 0.5:
        return "intermediate"
    return "beginner"


def build_learning_path(course: dict, mastery: dict[str, float], statuses: dict[str, str]) -> list[dict]:
    return [
        {
            "topic_id": topic["id"],
            "title": topic["title"],
            "mastery": mastery.get(topic["id"], 0.0),
            "status": statuses[topic["id"]],
            "prerequisites": topic["prerequisites"],
        }
        for topic in get_course_topics(course)
    ]


def build_metrics(course: dict, attempts: list[dict], mastery: dict[str, float]) -> dict:
    topic_count = len(course["topics"])
    completed_topics = len([score for score in mastery.values() if score >= 0.75])
    average_mastery = round(sum(mastery.values()) / topic_count, 2) if topic_count else 0.0
    average_response = (
        round(sum(item["response_time_seconds"] for item in attempts) / len(attempts), 1)
        if attempts
        else 0.0
    )

    return {
        "mastery_average": average_mastery,
        "completion_percent": round((completed_topics / topic_count) * 100, 1) if topic_count else 0.0,
        "average_response_seconds": average_response,
        "practice_events": len(attempts),
    }


def select_next_quiz(course: dict, attempts: list[dict], limit: int = 4) -> list[dict]:
    mastery = calculate_mastery(course, attempts)
    statuses = classify_topic_status(course, mastery)
    used_recently = {attempt["question_id"] for attempt in attempts[-8:]}

    weak_topics = sorted(
        [topic_id for topic_id, status in statuses.items() if status == "weak"],
        key=lambda topic_id: mastery[topic_id],
    )
    ready_topics = sorted(
        [topic_id for topic_id, status in statuses.items() if status == "ready"],
        key=lambda topic_id: mastery[topic_id],
    )
    mastered_topics = [topic_id for topic_id, status in statuses.items() if status == "mastered"]

    priority_topics = weak_topics + ready_topics + mastered_topics
    selected_questions: list[dict] = []

    for topic_id in priority_topics:
        topic_questions = [
            question
            for question in course["questions"]
            if question["topic_id"] == topic_id and question["id"] not in used_recently
        ]
        if not topic_questions:
            topic_questions = [question for question in course["questions"] if question["topic_id"] == topic_id]

        for question in topic_questions:
            selected_questions.append(question)
            if len(selected_questions) >= limit:
                return selected_questions

    return selected_questions[:limit]
