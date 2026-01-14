"use client";

import { useState } from "react";
import QuizView, { QuizQuestion } from "./QuizView";
import SubjectSelector from "./SubjectSelector";

// The 4 core exam subjects
const EXAM_SUBJECTS = [
    { id: "human-relations", label: "Human Relations" },
    { id: "mechanical-aptitude", label: "Mechanical Aptitude" },
    { id: "reading-ability", label: "Reading Ability" },
    { id: "math", label: "Math (Mental)" },
];

const QUESTION_COUNTS = [5, 10, 15, 25, 50];

interface QuizContainerProps {
    onBack: () => void;
}

type Phase = "subject-select" | "count-select" | "quiz";

export default function QuizContainer({ onBack }: QuizContainerProps) {
    const [phase, setPhase] = useState<Phase>("subject-select");
    const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
    const [questionCount, setQuestionCount] = useState(10);
    const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

    const handleSubjectsSelected = (subjects: string[]) => {
        setSelectedSubjects(subjects);
    };

    const handleContinueToCount = () => {
        if (selectedSubjects.length > 0) {
            setPhase("count-select");
        }
    };

    const handleStartQuiz = async () => {
        if (selectedSubjects.length === 0) return;

        setIsGenerating(true);
        setQuizQuestions([]);

        try {
            // Use batch endpoint for parallel generation
            const topics = selectedSubjects.map(
                (s) => EXAM_SUBJECTS.find((sub) => sub.id === s)?.label || s
            );

            const res = await fetch("http://localhost:8000/api/quiz/batch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    topics: topics,
                    count: questionCount,
                }),
            });

            if (!res.ok) {
                throw new Error("Failed to generate quiz");
            }

            const data = await res.json();
            const questions: QuizQuestion[] = data.questions.map(
                (q: Omit<QuizQuestion, "id">) => ({
                    ...q,
                    id: crypto.randomUUID(),
                })
            );

            if (questions.length === 0) {
                alert("Failed to generate quiz questions. Please check your connection.");
                setIsGenerating(false);
                return;
            }

            // Shuffle questions
            const shuffled = questions.sort(() => Math.random() - 0.5);
            setQuizQuestions(shuffled);
            setCurrentQuestionIndex(0);
            setPhase("quiz");
        } catch (err) {
            console.error("Quiz generation error:", err);
            alert("Error generating quiz. Please try again.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleReportQuestion = async (id: string) => {
        try {
            await fetch("http://localhost:8000/api/quiz/report", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question_id: id, reason: "User flagged in UI" }),
            });
        } catch (err) {
            console.error("Failed to report question:", err);
        }
    };

    const handleQuizComplete = (results: { correct: number; total: number }) => {
        const percentage = Math.round((results.correct / results.total) * 100);
        alert(
            `Quiz Complete! 🔥\n\nScore: ${results.correct}/${results.total} (${percentage}%)\n\n${percentage >= 80
                ? "Outstanding work, candidate!"
                : percentage >= 60
                    ? "Good effort. Keep studying!"
                    : "Let's hit the books harder, rookie."
            }`
        );
        setPhase("subject-select");
        setQuizQuestions([]);
        setSelectedSubjects([]);
    };

    // Phase 1: Subject Selection
    if (phase === "subject-select") {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-foreground">📝 Quiz Me</h2>
                    <button
                        onClick={onBack}
                        className="text-muted hover:text-foreground transition-colors"
                    >
                        ← Back to Hub
                    </button>
                </div>
                <SubjectSelector
                    onSelectionChange={handleSubjectsSelected}
                    onContinue={handleContinueToCount}
                />
            </div>
        );
    }

    // Phase 2: Question Count Selection
    if (phase === "count-select") {
        return (
            <div className="max-w-3xl mx-auto space-y-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-foreground">📝 Quiz Setup</h2>
                        <p className="text-muted mt-1">
                            {selectedSubjects.length} subject{selectedSubjects.length !== 1 ? "s" : ""} selected
                        </p>
                    </div>
                    <button
                        onClick={() => setPhase("subject-select")}
                        className="text-muted hover:text-foreground transition-colors"
                    >
                        ← Change Subjects
                    </button>
                </div>

                {/* Question Count */}
                <div className="card p-6">
                    <h3 className="text-lg font-semibold mb-4 text-foreground">
                        Number of Questions
                    </h3>
                    <div className="flex flex-wrap gap-3">
                        {QUESTION_COUNTS.map((count) => (
                            <button
                                key={count}
                                onClick={() => setQuestionCount(count)}
                                className={`px-6 py-3 rounded-xl border-2 font-bold transition-all ${questionCount === count
                                    ? "border-fire-red bg-fire-red text-white"
                                    : "border-card-border text-muted hover:border-ember-orange hover:text-foreground"
                                    }`}
                            >
                                {count}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Start Button */}
                <button
                    onClick={handleStartQuiz}
                    disabled={isGenerating}
                    className="w-full btn-primary py-5 text-xl font-bold rounded-xl fire-glow hover:fire-glow-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    {isGenerating ? (
                        <span className="flex items-center justify-center gap-3">
                            <span className="animate-spin">🔥</span> Generating {questionCount} Questions...
                        </span>
                    ) : (
                        `🚒 Start Quiz (${questionCount} Questions)`
                    )}
                </button>
            </div>
        );
    }

    // Phase 3: Quiz in Progress
    if (phase === "quiz" && quizQuestions.length > 0) {
        return (
            <div>
                {/* Progress Bar */}
                <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                        <button
                            onClick={() => {
                                if (confirm("Are you sure you want to exit the quiz?")) {
                                    setPhase("subject-select");
                                    setQuizQuestions([]);
                                }
                            }}
                            className="text-muted hover:text-foreground transition-colors"
                        >
                            ← Exit Quiz
                        </button>
                        <span className="text-sm font-medium text-muted">
                            Question {currentQuestionIndex + 1} / {quizQuestions.length}
                        </span>
                    </div>
                    {/* Progress bar visual */}
                    <div className="w-full h-2 bg-card-border rounded-full overflow-hidden">
                        <div
                            className="h-full bg-fire-red transition-all duration-300"
                            style={{
                                width: `${((currentQuestionIndex + 1) / quizQuestions.length) * 100}%`,
                            }}
                        />
                    </div>
                </div>

                <QuizView
                    questions={quizQuestions}
                    onReportQuestion={handleReportQuestion}
                    onComplete={handleQuizComplete}
                    onQuestionChange={(index) => setCurrentQuestionIndex(index)}
                />
            </div>
        );
    }

    return null;
}
