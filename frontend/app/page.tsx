"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiFetch, AuthUser, Dashboard, LoginResponse, QuizQuestion, QuizResponse, TutorResponse } from "../lib/api";

const STORAGE_KEY = "tutorflow-session";

type AnswersState = Record<string, string>;
type LearningNode = Dashboard["learning_path"][number];
type SessionState = {
  token: string;
  user: AuthUser;
};

export default function Home() {
  const [session, setSession] = useState<SessionState | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [quiz, setQuiz] = useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = useState<AnswersState>({});
  const [quizResult, setQuizResult] = useState<QuizResponse | null>(null);
  const [tutorQuestion, setTutorQuestion] = useState("Explain recursion in simple terms.");
  const [tutorReply, setTutorReply] = useState<TutorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [loginBusy, setLoginBusy] = useState(false);
  const [credentials, setCredentials] = useState({
    email: "ananya@tutorflow.dev",
    password: "demo123"
  });

  useEffect(() => {
    let isCancelled = false;

    async function restoreSession() {
      const rawSession = window.localStorage.getItem(STORAGE_KEY);
      if (!rawSession) {
        if (!isCancelled) {
          setAuthReady(true);
        }
        return;
      }

      try {
        const storedSession = JSON.parse(rawSession) as SessionState;
        const user = await apiFetch<AuthUser>("/api/auth/me", undefined, storedSession.token);
        if (!isCancelled) {
          setSession({ token: storedSession.token, user });
        }
      } catch {
        window.localStorage.removeItem(STORAGE_KEY);
      } finally {
        if (!isCancelled) {
          setAuthReady(true);
        }
      }
    }

    void restoreSession();

    return () => {
      isCancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!authReady || !session) {
      if (!session) {
        setDashboard(null);
        setQuiz([]);
        setQuizResult(null);
        setTutorReply(null);
      }
      return;
    }

    void loadData(session);
  }, [authReady, session]);

  async function loadData(activeSession: SessionState) {
    if (!activeSession.user.student_id || !activeSession.user.course_id) {
      setError("This account is not linked to a student workspace.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [dashboardData, quizData] = await Promise.all([
        apiFetch<Dashboard>(
          `/api/students/${activeSession.user.student_id}/dashboard`,
          undefined,
          activeSession.token
        ),
        apiFetch<QuizQuestion[]>(
          `/api/quizzes/next?student_id=${activeSession.user.student_id}&course_id=${activeSession.user.course_id}`,
          undefined,
          activeSession.token
        )
      ]);
      setDashboard(dashboardData);
      setQuiz(quizData);
      setAnswers({});
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoginBusy(true);
    setAuthError(null);

    try {
      const response = await apiFetch<LoginResponse>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials)
      });
      const nextSession = {
        token: response.access_token,
        user: response.user
      };
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
      setSession(nextSession);
      setQuizResult(null);
      setTutorReply(null);
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setLoginBusy(false);
    }
  }

  async function handleLogout() {
    if (session) {
      try {
        await apiFetch("/api/auth/logout", { method: "POST" }, session.token);
      } catch {
        // Local session cleanup is still safe if logout fails.
      }
    }

    window.localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setDashboard(null);
    setQuiz([]);
    setAnswers({});
    setQuizResult(null);
    setTutorReply(null);
    setError(null);
    setAuthError(null);
  }

  async function handleQuizSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session?.user.student_id || !session.user.course_id || !quiz.length) {
      return;
    }

    const unanswered = quiz.some((question) => !answers[question.id]);
    if (unanswered) {
      setError("Answer every question before submitting the quiz.");
      return;
    }

    setBusy(true);
    setError(null);
    try {
      const payload = {
        student_id: session.user.student_id,
        course_id: session.user.course_id,
        answers: quiz.map((question) => ({
          question_id: question.id,
          selected_option: answers[question.id],
          response_time_seconds: 30
        }))
      };

      const result = await apiFetch<QuizResponse>(
        "/api/quizzes/submit",
        {
          method: "POST",
          body: JSON.stringify(payload)
        },
        session.token
      );

      setQuizResult(result);
      await loadData(session);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit quiz");
    } finally {
      setBusy(false);
    }
  }

  async function handleTutorAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session?.user.student_id) {
      return;
    }

    setBusy(true);
    setError(null);
    try {
      const reply = await apiFetch<TutorResponse>(
        "/api/tutor/ask",
        {
          method: "POST",
          body: JSON.stringify({
            student_id: session.user.student_id,
            question: tutorQuestion
          })
        },
        session.token
      );
      setTutorReply(reply);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tutor request failed");
    } finally {
      setBusy(false);
    }
  }

  if (!authReady) {
    return (
      <main className="page-shell auth-page">
        <div className="auth-loading-card">
          <div className="brand-lockup">
            <div className="brand-mark">T</div>
            <div>
              <strong>TutorFlow</strong>
              <span>Checking your learning workspace</span>
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (!session) {
    return (
      <main className="page-shell auth-page">
        <section className="topbar">
          <div className="brand-lockup">
            <div className="brand-mark">T</div>
            <div>
              <strong>TutorFlow</strong>
              <span>Adaptive learning workspace</span>
            </div>
          </div>
        </section>

        <section className="auth-grid">
          <div className="auth-copy surface-card">
            <span className="hero-kicker">Smarter than a one-size-fits-all course</span>
            <h1>Sign in to continue your personalized learning path.</h1>
            <p className="hero-text">
              TutorFlow tracks mastery, adapts question difficulty, and shows the exact topic sequence each learner
              should take next.
            </p>

            <div className="auth-feature-grid">
              <FeaturePill title="Adaptive practice" description="Quizzes shift difficulty from real performance." />
              <FeaturePill title="Weak-topic detection" description="Confused concepts surface before they become gaps." />
              <FeaturePill title="Tutor support" description="Ask for a teacher-style explanation whenever needed." />
            </div>
          </div>

          <div className="auth-panel surface-card">
            <div className="section-header compact">
              <span className="section-eyebrow">Login</span>
              <h2>Access your dashboard</h2>
              <p>Use one of the demo student accounts below or enter the credentials manually.</p>
            </div>

            <div className="demo-accounts">
              <button
                className="demo-card"
                onClick={() => setCredentials({ email: "ananya@tutorflow.dev", password: "demo123" })}
                type="button"
              >
                <strong>Ananya Sharma</strong>
                <span>ananya@tutorflow.dev</span>
                <span>Adaptive learner profile with intermediate history</span>
              </button>
              <button
                className="demo-card"
                onClick={() => setCredentials({ email: "rahul@tutorflow.dev", password: "demo123" })}
                type="button"
              >
                <strong>Rahul Verma</strong>
                <span>rahul@tutorflow.dev</span>
                <span>Beginner profile with early-stage progress</span>
              </button>
            </div>

            <form className="auth-form" onSubmit={handleLogin}>
              <label className="field">
                <span>Email</span>
                <input
                  className="text-input"
                  onChange={(event) => setCredentials((current) => ({ ...current, email: event.target.value }))}
                  type="email"
                  value={credentials.email}
                />
              </label>

              <label className="field">
                <span>Password</span>
                <input
                  className="text-input"
                  onChange={(event) => setCredentials((current) => ({ ...current, password: event.target.value }))}
                  type="password"
                  value={credentials.password}
                />
              </label>

              {authError ? <div className="alert error">{authError}</div> : null}

              <button className="primary-cta wide" disabled={loginBusy} type="submit">
                {loginBusy ? "Signing in..." : "Login to TutorFlow"}
              </button>
            </form>
          </div>
        </section>
      </main>
    );
  }

  const learningPath = dashboard?.learning_path ?? [];
  const topicLookup = Object.fromEntries(learningPath.map((node) => [node.topic_id, node]));
  const weakTopicNodes = dashboard?.weak_topics.map((topicId) => topicLookup[topicId]).filter(Boolean) ?? [];
  const masteredCount = learningPath.filter((node) => node.status === "mastered").length;
  const readyCount = learningPath.filter((node) => node.status === "ready").length;
  const lockedCount = learningPath.filter((node) => node.status === "locked").length;
  const currentFocus = dashboard?.recommendations[0] ?? null;
  const currentFocusNode = currentFocus ? topicLookup[currentFocus.topic_id] : learningPath[0];
  const greetingName = dashboard?.student.name.split(" ")[0] ?? session.user.name.split(" ")[0];

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">T</div>
          <div>
            <strong>TutorFlow</strong>
            <span>Adaptive learning workspace</span>
          </div>
        </div>

        <nav className="topnav">
          <a href="#learning-path">Courses</a>
          <a href="#insights">Progress</a>
          <a href="#adaptive-quiz">Practice</a>
          <a href="#tutor-desk">Tutor</a>
        </nav>

        <div className="topbar-utilities">
          <div className="student-chip">
            <span>Active learner</span>
            <strong>{dashboard?.student.name ?? session.user.name}</strong>
          </div>
          <button className="topbar-action" onClick={handleLogout} type="button">
            Logout
          </button>
        </div>
      </header>

      <section className="hero-shell">
        <div className="hero-copy animate-rise">
          <p className="hero-kicker">Built for students who do not learn at the same speed</p>
          <h1>One course. A different path for every learner.</h1>
          <p className="hero-text">
            Practice gets easier or harder in real time, weak concepts surface early, and each next topic unlocks from
            actual progress instead of a fixed course sequence.
          </p>

          <div className="hero-actions">
            <button className="primary-cta" onClick={() => jumpTo("adaptive-quiz")} type="button">
              Start practice
            </button>
            <button className="secondary-cta" onClick={() => jumpTo("learning-path")} type="button">
              View roadmap
            </button>
          </div>

          <div className="hero-points">
            <InfoPill label="Course" value={dashboard?.course.title ?? session.user.course_id ?? "Course"} />
            <InfoPill label="Weak areas" value={`${weakTopicNodes.length}`} />
            <InfoPill label="Mastered" value={`${masteredCount}/${learningPath.length || 7}`} />
          </div>
        </div>

        <div className="hero-board animate-rise-delay">
          <div className="board-topline">
            <span className="board-label">Today&apos;s study plan</span>
            <span className="board-live">Live adaptive</span>
          </div>

          <div className="focus-card">
            <div className="focus-copy">
              <span className="status-pill focus">Current focus</span>
              <h2>{currentFocusNode?.title ?? "Loading focus"}</h2>
              <p>
                {currentFocus?.action ??
                  "The engine is preparing the next lesson and quiz based on recent answers and response time."}
              </p>
            </div>

            <div className="focus-stats">
              <MiniStat label="Mastery" value={`${Math.round((dashboard?.metrics.mastery_average ?? 0) * 100)}%`} />
              <MiniStat label="Unlocked" value={`${masteredCount + readyCount}`} />
              <MiniStat label="Locked" value={`${lockedCount}`} />
            </div>
          </div>

          <div className="syllabus-preview">
            {learningPath.length ? (
              learningPath.slice(0, 5).map((node, index) => (
                <div className="syllabus-row" key={node.topic_id}>
                  <div className="syllabus-index">{String(index + 1).padStart(2, "0")}</div>
                  <div className="syllabus-content">
                    <div className="syllabus-line">
                      <strong>{node.title}</strong>
                      <span className={`status-pill ${node.status}`}>{node.status}</span>
                    </div>
                    <div className="progress-track compact">
                      <span style={{ width: `${Math.max(8, Math.round(node.mastery * 100))}%` }} />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-card">Loading learning path...</div>
            )}
          </div>
        </div>
      </section>

      {error ? <div className="alert error">{error}</div> : null}

      {loading && !dashboard ? (
        <section className="loading-grid">
          <div className="loading-card" />
          <div className="loading-card" />
          <div className="loading-card" />
          <div className="loading-card" />
        </section>
      ) : null}

      {dashboard ? (
        <>
          <section className="stats-ribbon">
            <MetricCard label="Average mastery" value={`${Math.round(dashboard.metrics.mastery_average * 100)}%`} />
            <MetricCard label="Course completion" value={`${dashboard.metrics.completion_percent}%`} />
            <MetricCard label="Average response" value={`${dashboard.metrics.average_response_seconds}s`} />
            <MetricCard label="Practice events" value={`${dashboard.metrics.practice_events}`} />
          </section>

          <section className="workspace-layout">
            <div className="main-column">
              <section className="panel surface" id="learning-path">
                <SectionHeader
                  eyebrow="Learning roadmap"
                  title={`${greetingName}, here is your topic progression`}
                  subtitle="Each module reflects real readiness, not a static syllabus. Weak topics stay visible until recovery."
                />

                <div className="module-list">
                  {learningPath.map((node, index) => (
                    <article className="module-card" key={node.topic_id}>
                      <div className={`module-number ${node.status}`}>{String(index + 1).padStart(2, "0")}</div>
                      <div className="module-body">
                        <div className="module-topline">
                          <h3>{node.title}</h3>
                          <span className={`status-pill ${node.status}`}>{node.status}</span>
                        </div>
                        <p>{describeNode(node)}</p>
                        <div className="progress-track">
                          <span style={{ width: `${Math.max(8, Math.round(node.mastery * 100))}%` }} />
                        </div>
                        <div className="module-meta">
                          <span>Mastery: {Math.round(node.mastery * 100)}%</span>
                          <span>
                            Prerequisites: {node.prerequisites.length ? node.prerequisites.join(", ") : "None"}
                          </span>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </section>

              <section className="studio-grid">
                <form className="panel surface" id="adaptive-quiz" onSubmit={handleQuizSubmit}>
                  <SectionHeader
                    eyebrow="Adaptive practice"
                    title="Next quiz set"
                    subtitle="The system prioritizes weak concepts first, then moves into newly ready topics."
                  />

                  <div className="question-stack">
                    {quiz.map((question) => (
                      <fieldset className="quiz-card" key={question.id}>
                        <legend>
                          {question.topic_title} - {question.difficulty}
                        </legend>
                        <p className="question-text">{question.prompt}</p>
                        <div className="option-grid">
                          {question.options.map((option) => (
                            <label className="option-card" key={option}>
                              <input
                                checked={answers[question.id] === option}
                                name={question.id}
                                onChange={() => setAnswers((current) => ({ ...current, [question.id]: option }))}
                                type="radio"
                                value={option}
                              />
                              <span>{option}</span>
                            </label>
                          ))}
                        </div>
                      </fieldset>
                    ))}
                  </div>

                  <button className="primary-cta wide" disabled={busy || !quiz.length} type="submit">
                    Submit answers
                  </button>

                  {quizResult ? (
                    <div className="result-card">
                      <div className="result-summary">
                        <div>
                          <span className="result-label">Latest score</span>
                          <h3>{quizResult.score_percent}%</h3>
                        </div>
                        <div>
                          <span className="result-label">Next difficulty</span>
                          <h3 className="capitalize">{quizResult.recommended_difficulty}</h3>
                        </div>
                      </div>

                      <div className="evaluation-list">
                        {quizResult.evaluations.map((evaluation) => (
                          <div className="evaluation-row" key={evaluation.question_id}>
                            <strong>{evaluation.is_correct ? "Correct answer" : "Needs revision"}</strong>
                            <p>{evaluation.explanation}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </form>

                <form className="panel surface tutor-surface" id="tutor-desk" onSubmit={handleTutorAsk}>
                  <SectionHeader
                    eyebrow="Tutor desk"
                    title="Ask for a teacher-style explanation"
                    subtitle="The tutor replies with concept help, a concrete example, and the next revision step."
                  />

                  <div className="tutor-shell">
                    <textarea
                      className="tutor-input"
                      onChange={(event) => setTutorQuestion(event.target.value)}
                      rows={7}
                      value={tutorQuestion}
                    />
                    <button className="primary-cta wide" disabled={busy} type="submit">
                      Ask tutor
                    </button>
                  </div>

                  {tutorReply ? (
                    <article className="tutor-response">
                      <div className="reply-badge">Topic: {tutorReply.topic_title}</div>
                      <p>{tutorReply.answer}</p>
                      <p className="reply-followup">{tutorReply.recommended_follow_up}</p>
                    </article>
                  ) : (
                    <div className="placeholder-card">
                      Use the tutor for doubts, concept revision, or simpler explanations before the next quiz.
                    </div>
                  )}
                </form>
              </section>
            </div>

            <aside className="side-column" id="insights">
              <section className="panel side-panel">
                <SectionHeader
                  eyebrow="Continue learning"
                  title={currentFocus?.title ?? "Personalized next step"}
                  subtitle="Chosen from recent mistakes, speed, and prerequisite readiness."
                />
                <div className="priority-card">
                  <span className={`status-pill ${currentFocus?.difficulty ?? "intermediate"}`}>
                    {currentFocus?.difficulty ?? "intermediate"}
                  </span>
                  <p>{currentFocus?.reason ?? "Adaptive recommendations will appear here once the dashboard loads."}</p>
                  <strong>{currentFocus?.action ?? "Continue with the next module."}</strong>
                </div>
              </section>

              <section className="panel side-panel">
                <SectionHeader
                  eyebrow="Weak concepts"
                  title="Topics needing attention"
                  subtitle="These modules are slowing down progression and should be revised first."
                />
                <div className="topic-stack">
                  {weakTopicNodes.length ? (
                    weakTopicNodes.map((node) => (
                      <div className="topic-alert" key={node.topic_id}>
                        <div>
                          <strong>{node.title}</strong>
                          <p>{Math.round(node.mastery * 100)}% mastery</p>
                        </div>
                        <span className="alert-dot" />
                      </div>
                    ))
                  ) : (
                    <div className="placeholder-card">No weak topics are active right now.</div>
                  )}
                </div>
              </section>

              <section className="panel side-panel">
                <SectionHeader
                  eyebrow="Recommended next"
                  title="Your next three moves"
                  subtitle="A tighter, more product-like breakdown of what to do now."
                />
                <div className="recommendation-list">
                  {dashboard.recommendations.map((recommendation) => (
                    <article className="recommendation-tile" key={recommendation.topic_id}>
                      <span className={`status-pill ${recommendation.difficulty}`}>{recommendation.difficulty}</span>
                      <h3>{recommendation.title}</h3>
                      <p>{recommendation.reason}</p>
                    </article>
                  ))}
                </div>
              </section>
            </aside>
          </section>
        </>
      ) : null}
    </main>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function InfoPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="info-pill">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="mini-stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function SectionHeader({
  eyebrow,
  title,
  subtitle
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="section-header">
      <span className="section-eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      <p>{subtitle}</p>
    </div>
  );
}

function FeaturePill({ title, description }: { title: string; description: string }) {
  return (
    <div className="feature-pill">
      <strong>{title}</strong>
      <span>{description}</span>
    </div>
  );
}

function describeNode(node: LearningNode) {
  if (node.status === "mastered") {
    return "This topic is stable. Use spaced revision while moving to the next concept.";
  }

  if (node.status === "weak") {
    return "Recent answers show confusion here. Keep practice focused until performance recovers.";
  }

  if (node.status === "ready") {
    return "Prerequisites are strong enough. This module can be started now.";
  }

  return "This module is still locked behind prerequisite performance.";
}

function jumpTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}
