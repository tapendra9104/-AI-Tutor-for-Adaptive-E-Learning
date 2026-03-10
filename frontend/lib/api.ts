export type Recommendation = {
  topic_id: string;
  title: string;
  reason: string;
  action: string;
  difficulty: "beginner" | "intermediate" | "advanced";
};

export type LearningPathNode = {
  topic_id: string;
  title: string;
  mastery: number;
  status: "mastered" | "weak" | "ready" | "locked";
  prerequisites: string[];
};

export type Dashboard = {
  student: {
    id: string;
    name: string;
    course_id: string;
    skill_level: string;
  };
  course: {
    id: string;
    title: string;
    description: string;
    topic_count: number;
  };
  metrics: {
    mastery_average: number;
    completion_percent: number;
    average_response_seconds: number;
    practice_events: number;
  };
  weak_topics: string[];
  recommendations: Recommendation[];
  learning_path: LearningPathNode[];
};

export type QuizQuestion = {
  id: string;
  topic_id: string;
  topic_title: string;
  prompt: string;
  options: string[];
  difficulty: "beginner" | "intermediate" | "advanced";
};

export type QuizResponse = {
  score_percent: number;
  recommended_difficulty: "beginner" | "intermediate" | "advanced";
  weak_topics: string[];
  recommendations: Recommendation[];
  evaluations: {
    question_id: string;
    topic_id: string;
    is_correct: boolean;
    correct_option: string;
    explanation: string;
  }[];
};

export type TutorResponse = {
  topic_id: string;
  topic_title: string;
  answer: string;
  recommended_follow_up: string;
};

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  role: "student" | "teacher" | "admin";
  student_id: string | null;
  course_id: string | null;
  skill_level: string | null;
};

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function apiFetch<T>(path: string, options?: RequestInit, token?: string): Promise<T> {
  const headers = new Headers(options?.headers ?? {});
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store"
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}
