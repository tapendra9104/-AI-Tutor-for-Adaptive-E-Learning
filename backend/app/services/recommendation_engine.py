from __future__ import annotations


def build_recommendations(course: dict, mastery: dict[str, float], weak_topics: list[str]) -> list[dict]:
    topic_map = {topic["id"]: topic for topic in course["topics"]}
    recommendations: list[dict] = []
    recommended_topic_ids: set[str] = set()

    for topic_id in weak_topics:
        topic = topic_map[topic_id]
        recommendations.append(
            {
                "topic_id": topic_id,
                "title": topic["title"],
                "reason": f"Mastery is {int(mastery.get(topic_id, 0.0) * 100)}% and recent answers show confusion.",
                "action": f"Review {topic['resource']['title']} and retry targeted practice.",
                "difficulty": "beginner" if mastery.get(topic_id, 0.0) < 0.35 else "intermediate",
            }
        )
        recommended_topic_ids.add(topic_id)

    for topic in course["topics"]:
        if topic["id"] in recommended_topic_ids:
            continue

        prerequisites_met = all(mastery.get(prereq, 0.0) >= 0.65 for prereq in topic["prerequisites"])
        if prerequisites_met and mastery.get(topic["id"], 0.0) < 0.75:
            recommendations.append(
                {
                    "topic_id": topic["id"],
                    "title": topic["title"],
                    "reason": "Prerequisites are strong enough to unlock the next concept.",
                    "action": f"Study {topic['resource']['title']} and take the next adaptive quiz.",
                    "difficulty": "advanced" if mastery.get(topic["id"], 0.0) >= 0.5 else "intermediate",
                }
            )
            recommended_topic_ids.add(topic["id"])

        if len(recommendations) >= 3:
            break

    if not recommendations and course["topics"]:
        topic = course["topics"][0]
        recommendations.append(
            {
                "topic_id": topic["id"],
                "title": topic["title"],
                "reason": "No active weak areas were detected, so the system is suggesting spaced revision.",
                "action": f"Use {topic['resource']['title']} as a quick recap before moving ahead.",
                "difficulty": "intermediate",
            }
        )

    return recommendations[:3]
