from __future__ import annotations


def infer_topic(course: dict, question: str, explicit_topic_id: str | None) -> dict:
    if explicit_topic_id:
        for topic in course["topics"]:
            if topic["id"] == explicit_topic_id:
                return topic

    lowered = question.lower()
    for topic in course["topics"]:
        if topic["title"].lower() in lowered or topic["id"].replace("-", " ") in lowered:
            return topic

    keyword_map = {
        "loop": "loops",
        "if": "conditionals",
        "function": "functions",
        "dictionary": "data-structures",
        "list": "data-structures",
        "recursion": "recursion",
        "graph": "graphs",
    }
    for keyword, topic_id in keyword_map.items():
        if keyword in lowered:
            for topic in course["topics"]:
                if topic["id"] == topic_id:
                    return topic

    return course["topics"][0]


def generate_tutor_response(student_name: str, topic: dict, mastery: float, question: str) -> dict:
    support_level = (
        "Start with a simpler example and trace it line by line."
        if mastery < 0.4
        else "You are close. Focus on the transition between each step."
    )

    answer = (
        f"{topic['title']} means: {topic['summary']} "
        f"For example, {topic['example']} "
        f"Students usually get stuck when they try to memorize syntax without understanding why each step works. "
        f"{support_level} "
        f"Your question was: '{question}'."
    )

    follow_up = f"Next, try the resource '{topic['resource']['title']}' and answer one practice question on {topic['title']}."

    return {
        "topic_id": topic["id"],
        "topic_title": topic["title"],
        "answer": answer,
        "recommended_follow_up": follow_up,
    }
