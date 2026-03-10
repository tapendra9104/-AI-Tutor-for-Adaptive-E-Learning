from copy import deepcopy
import hashlib


PASSWORD_SALT = "ai-tutor-demo-salt"


def hash_password(password: str) -> str:
    payload = f"{PASSWORD_SALT}:{password}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


COURSES = {
    "python-foundations": {
        "id": "python-foundations",
        "title": "Python Foundations",
        "description": "Adaptive Python course covering core programming concepts.",
        "topics": [
            {
                "id": "python-basics",
                "title": "Python Basics",
                "summary": "Variables, data types, expressions, and simple input/output.",
                "example": "If x = 3 and y = 4, then x + y evaluates to 7.",
                "prerequisites": [],
                "resource": {
                    "title": "Variables and Expressions",
                    "type": "lesson",
                    "duration": "15 min",
                },
            },
            {
                "id": "conditionals",
                "title": "Conditionals",
                "summary": "Use if, elif, and else blocks to control program flow.",
                "example": "Use if score >= 50: print('Pass') to branch on a condition.",
                "prerequisites": ["python-basics"],
                "resource": {
                    "title": "Control Flow with If Statements",
                    "type": "lesson",
                    "duration": "20 min",
                },
            },
            {
                "id": "loops",
                "title": "Loops",
                "summary": "Repeat work with for and while loops.",
                "example": "A for loop walks over each item in a list one by one.",
                "prerequisites": ["python-basics"],
                "resource": {
                    "title": "Repetition Patterns",
                    "type": "practice",
                    "duration": "25 min",
                },
            },
            {
                "id": "functions",
                "title": "Functions",
                "summary": "Group reusable logic with parameters and return values.",
                "example": "def area(width, height): return width * height",
                "prerequisites": ["conditionals", "loops"],
                "resource": {
                    "title": "Function Design Lab",
                    "type": "lesson",
                    "duration": "30 min",
                },
            },
            {
                "id": "data-structures",
                "title": "Data Structures",
                "summary": "Model collections with lists, tuples, sets, and dictionaries.",
                "example": "Use a dictionary when you need key-value lookups.",
                "prerequisites": ["loops"],
                "resource": {
                    "title": "Collections Workshop",
                    "type": "lab",
                    "duration": "30 min",
                },
            },
            {
                "id": "recursion",
                "title": "Recursion",
                "summary": "Solve a problem by reducing it to smaller versions of itself.",
                "example": "factorial(n) calls factorial(n - 1) until it reaches 1.",
                "prerequisites": ["functions"],
                "resource": {
                    "title": "Recursion Basics",
                    "type": "lesson",
                    "duration": "35 min",
                },
            },
            {
                "id": "graphs",
                "title": "Graph Thinking",
                "summary": "Represent relationships between entities using nodes and edges.",
                "example": "A course prerequisite graph links one topic to the next.",
                "prerequisites": ["data-structures", "recursion"],
                "resource": {
                    "title": "Knowledge Graph Introduction",
                    "type": "lesson",
                    "duration": "20 min",
                },
            },
        ],
        "questions": [
            {
                "id": "q-basics-1",
                "topic_id": "python-basics",
                "prompt": "What does print(2 + 3) output?",
                "options": ["23", "5", "2 + 3", "Error"],
                "correct_option": "5",
                "difficulty": "beginner",
                "explanation": "The + operator adds the two integers before print displays the result.",
            },
            {
                "id": "q-basics-2",
                "topic_id": "python-basics",
                "prompt": "Which data type is used for True or False values?",
                "options": ["int", "str", "bool", "list"],
                "correct_option": "bool",
                "difficulty": "beginner",
                "explanation": "Boolean values are represented by the bool type.",
            },
            {
                "id": "q-conditionals-1",
                "topic_id": "conditionals",
                "prompt": "Which keyword checks the second condition after an if block?",
                "options": ["then", "elif", "loop", "switch"],
                "correct_option": "elif",
                "difficulty": "beginner",
                "explanation": "elif allows you to check another condition if the first one is false.",
            },
            {
                "id": "q-conditionals-2",
                "topic_id": "conditionals",
                "prompt": "What is the result of: 5 > 3?",
                "options": ["True", "False", "5", "3"],
                "correct_option": "True",
                "difficulty": "beginner",
                "explanation": "The comparison evaluates to True because 5 is greater than 3.",
            },
            {
                "id": "q-loops-1",
                "topic_id": "loops",
                "prompt": "Which loop is best for iterating over a list in Python?",
                "options": ["if", "for", "class", "match"],
                "correct_option": "for",
                "difficulty": "beginner",
                "explanation": "A for loop is the standard way to iterate through list items.",
            },
            {
                "id": "q-loops-2",
                "topic_id": "loops",
                "prompt": "What happens in a while loop?",
                "options": [
                    "Code runs once only",
                    "Code repeats while a condition stays true",
                    "Code defines a function",
                    "Code creates a dictionary",
                ],
                "correct_option": "Code repeats while a condition stays true",
                "difficulty": "intermediate",
                "explanation": "A while loop keeps repeating until its condition becomes false.",
            },
            {
                "id": "q-functions-1",
                "topic_id": "functions",
                "prompt": "What is returned by this function?\n\ndef add(a, b):\n    return a + b",
                "options": ["The sum of a and b", "The product of a and b", "Nothing", "A loop"],
                "correct_option": "The sum of a and b",
                "difficulty": "intermediate",
                "explanation": "The return statement sends back the sum of the two parameters.",
            },
            {
                "id": "q-functions-2",
                "topic_id": "functions",
                "prompt": "What is a parameter in a function definition?",
                "options": [
                    "A repeated loop",
                    "An input variable to the function",
                    "The output value",
                    "A conditional branch",
                ],
                "correct_option": "An input variable to the function",
                "difficulty": "intermediate",
                "explanation": "Parameters are named inputs that the function receives.",
            },
            {
                "id": "q-data-1",
                "topic_id": "data-structures",
                "prompt": "Which structure stores key-value pairs?",
                "options": ["list", "tuple", "dictionary", "set"],
                "correct_option": "dictionary",
                "difficulty": "intermediate",
                "explanation": "A dictionary maps keys to values.",
            },
            {
                "id": "q-data-2",
                "topic_id": "data-structures",
                "prompt": "Which structure preserves insertion order and allows duplicates?",
                "options": ["list", "set", "bool", "float"],
                "correct_option": "list",
                "difficulty": "intermediate",
                "explanation": "Lists are ordered collections and can contain repeated values.",
            },
            {
                "id": "q-recursion-1",
                "topic_id": "recursion",
                "prompt": "What must every recursive function have to stop calling itself forever?",
                "options": ["A list", "A base case", "A class", "A print statement"],
                "correct_option": "A base case",
                "difficulty": "advanced",
                "explanation": "The base case defines when the function should stop recurring.",
            },
            {
                "id": "q-recursion-2",
                "topic_id": "recursion",
                "prompt": "In recursion, each call typically works on:",
                "options": [
                    "A larger version of the same problem",
                    "An unrelated problem",
                    "A smaller version of the same problem",
                    "A database row",
                ],
                "correct_option": "A smaller version of the same problem",
                "difficulty": "advanced",
                "explanation": "Recursive solutions reduce the original problem step by step.",
            },
            {
                "id": "q-graphs-1",
                "topic_id": "graphs",
                "prompt": "A knowledge graph is mainly built from:",
                "options": [
                    "Tables and images",
                    "Nodes and edges",
                    "Only numbers",
                    "Loops and functions",
                ],
                "correct_option": "Nodes and edges",
                "difficulty": "advanced",
                "explanation": "Graphs represent entities as nodes and relationships as edges.",
            },
        ],
    }
}


INITIAL_STUDENTS = {
    "student-1": {
        "id": "student-1",
        "name": "Ananya Sharma",
        "role": "student",
        "course_id": "python-foundations",
        "skill_level": "intermediate",
        "attempts": [
            {
                "question_id": "q-basics-1",
                "topic_id": "python-basics",
                "is_correct": True,
                "selected_option": "5",
                "response_time_seconds": 18,
                "submitted_at": "2026-03-10T09:00:00Z",
            },
            {
                "question_id": "q-basics-2",
                "topic_id": "python-basics",
                "is_correct": True,
                "selected_option": "bool",
                "response_time_seconds": 22,
                "submitted_at": "2026-03-10T09:02:00Z",
            },
            {
                "question_id": "q-conditionals-1",
                "topic_id": "conditionals",
                "is_correct": True,
                "selected_option": "elif",
                "response_time_seconds": 21,
                "submitted_at": "2026-03-10T09:05:00Z",
            },
            {
                "question_id": "q-conditionals-2",
                "topic_id": "conditionals",
                "is_correct": False,
                "selected_option": "False",
                "response_time_seconds": 34,
                "submitted_at": "2026-03-10T09:07:00Z",
            },
            {
                "question_id": "q-loops-1",
                "topic_id": "loops",
                "is_correct": True,
                "selected_option": "for",
                "response_time_seconds": 27,
                "submitted_at": "2026-03-10T09:10:00Z",
            },
            {
                "question_id": "q-loops-2",
                "topic_id": "loops",
                "is_correct": False,
                "selected_option": "Code runs once only",
                "response_time_seconds": 46,
                "submitted_at": "2026-03-10T09:12:00Z",
            },
            {
                "question_id": "q-functions-1",
                "topic_id": "functions",
                "is_correct": False,
                "selected_option": "The product of a and b",
                "response_time_seconds": 55,
                "submitted_at": "2026-03-10T09:15:00Z",
            },
            {
                "question_id": "q-recursion-1",
                "topic_id": "recursion",
                "is_correct": False,
                "selected_option": "A list",
                "response_time_seconds": 62,
                "submitted_at": "2026-03-10T09:18:00Z",
            },
        ],
    },
    "student-2": {
        "id": "student-2",
        "name": "Rahul Verma",
        "role": "student",
        "course_id": "python-foundations",
        "skill_level": "beginner",
        "attempts": [
            {
                "question_id": "q-basics-1",
                "topic_id": "python-basics",
                "is_correct": True,
                "selected_option": "5",
                "response_time_seconds": 24,
                "submitted_at": "2026-03-10T10:00:00Z",
            },
            {
                "question_id": "q-basics-2",
                "topic_id": "python-basics",
                "is_correct": False,
                "selected_option": "str",
                "response_time_seconds": 38,
                "submitted_at": "2026-03-10T10:03:00Z",
            },
            {
                "question_id": "q-conditionals-1",
                "topic_id": "conditionals",
                "is_correct": False,
                "selected_option": "switch",
                "response_time_seconds": 49,
                "submitted_at": "2026-03-10T10:08:00Z",
            },
        ],
    },
}


INITIAL_USERS = {
    "user-student-1": {
        "id": "user-student-1",
        "name": "Ananya Sharma",
        "email": "ananya@tutorflow.dev",
        "role": "student",
        "student_id": "student-1",
        "password_hash": hash_password("demo123"),
    },
    "user-student-2": {
        "id": "user-student-2",
        "name": "Rahul Verma",
        "email": "rahul@tutorflow.dev",
        "role": "student",
        "student_id": "student-2",
        "password_hash": hash_password("demo123"),
    },
}


def clone_students():
    return deepcopy(INITIAL_STUDENTS)


def clone_users():
    return deepcopy(INITIAL_USERS)


STUDENTS = clone_students()
USERS = clone_users()
ACTIVE_SESSIONS: dict[str, dict] = {}
