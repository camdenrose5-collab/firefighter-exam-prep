"use client";

import { useState } from "react";
import { Users, Wrench, BookOpen, Calculator } from "lucide-react";
import QuizView, { QuizQuestion } from "./QuizView";
import SubjectSelector, { Subject } from "./SubjectSelector";
import ReportModal from "./ReportModal";
import FeedbackModal from "./FeedbackModal";
import UpgradeModal from "./UpgradeModal";
import { getQuestions } from "@/data/questionBank";
import { apiUrl } from "@/lib/api";
import { useUserStore, useCanStartQuiz, useRemainingQuizzes, FREE_TIER_LIMITS } from "@/lib/store";
import confetti from "canvas-confetti";

// Quiz subjects - uses Reading Comprehension (for reading prompts)
const QUIZ_SUBJECTS: Subject[] = [
    {
        id: "human-relations",
        label: "Human Relations",
        icon: Users,
        description: "Teamwork, conflict resolution, communication",
    },
    {
        id: "mechanical-aptitude",
        label: "Mechanical Aptitude",
        icon: Wrench,
        description: "Tools, leverage, hydraulics, troubleshooting",
    },
    {
        id: "reading-comprehension",
        label: "Reading Comprehension",
        icon: BookOpen,
        description: "Passage comprehension, following instructions",
    },
    {
        id: "math",
        label: "Math (Mental)",
        icon: Calculator,
        description: "Arithmetic, percentages, ratios — no calculator",
    },
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

    // Modal state
    const [reportModalOpen, setReportModalOpen] = useState(false);
    const [reportQuestionId, setReportQuestionId] = useState<string | null>(null);
    const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
    const [upgradeModalOpen, setUpgradeModalOpen] = useState(false);

    // Freemium state
    const canStartQuiz = useCanStartQuiz();
    const remainingQuizzes = useRemainingQuizzes();
    const incrementQuizCount = useUserStore((state) => state.incrementQuizCount);
    const tier = useUserStore((state) => state.tier);

    const handleSubjectsSelected = (subjects: string[]) => {
        setSelectedSubjects(subjects);
    };

    const handleContinueToCount = () => {
        // Check freemium limit before proceeding
        if (!canStartQuiz) {
            setUpgradeModalOpen(true);
            return;
        }
        if (selectedSubjects.length > 0) {
            setPhase("count-select");
        }
    };

    const handleStartQuiz = () => {
        if (selectedSubjects.length === 0) return;

        // Get questions instantly from client-side bank (no API latency)
        const questions = getQuestions(selectedSubjects, questionCount);

        if (questions.length === 0) {
            alert("No questions available for selected subjects.");
            return;
        }

        // Map to QuizQuestion format
        const quizQuestions: QuizQuestion[] = questions.map((q) => ({
            id: q.id,
            question: q.question,
            options: q.options,
            correct_answer: q.correct_answer,
            explanation: q.explanation,
        }));

        setQuizQuestions(quizQuestions);
        setCurrentQuestionIndex(0);
        setPhase("quiz");

        // Track quiz usage for freemium limits
        incrementQuizCount();
    };

    const handleReportQuestion = async (id: string, reason: string) => {
        try {
            await fetch(apiUrl("/api/quiz/report"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question_id: id, reason: reason || "User flagged in UI" }),
            });
        } catch (err) {
            console.error("Failed to report question:", err);
        }
    };

    const handleOpenReportModal = (questionId: string) => {
        setReportQuestionId(questionId);
        setReportModalOpen(true);
    };

    const handleSubmitFeedback = async (studyMode: string, message: string) => {
        try {
            await fetch(apiUrl("/api/feedback"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ study_mode: studyMode, message }),
            });
        } catch (err) {
            console.error("Failed to submit feedback:", err);
        }
    };

    const handleQuizComplete = (results: { correct: number; total: number }) => {
        const percentage = Math.round((results.correct / results.total) * 100);

        // Trigger confetti for good scores!
        if (percentage >= 70) {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }

        alert(
            `Quiz Complete! 🔥\n\nScore: ${results.correct}/${results.total} (${percentage}%)\n\n${percentage >= 80
                ? "Outstanding work, candidate!"
                : percentage >= 60
                    ? "Good effort. Keep studying!"
                    : "Let's hit the books harder. You've got this!"
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
                    <div>
                        <h2 className="text-xl font-bold text-foreground">Practice Quiz</h2>
                        {tier === "free" && (
                            <p className="text-sm text-muted mt-1">
                                {remainingQuizzes === Infinity ? "Unlimited" : `${remainingQuizzes} of ${FREE_TIER_LIMITS.quizzesPerDay}`} quizzes remaining today
                            </p>
                        )}
                    </div>
                    <button
                        onClick={onBack}
                        className="text-muted hover:text-foreground transition-colors"
                    >
                        ← Back to Hub
                    </button>
                </div>
                <SubjectSelector
                    subjects={QUIZ_SUBJECTS}
                    onSelectionChange={handleSubjectsSelected}
                    onContinue={handleContinueToCount}
                />

                {/* Upgrade Modal */}
                <UpgradeModal
                    isOpen={upgradeModalOpen}
                    onClose={() => setUpgradeModalOpen(false)}
                    limitType="quiz"
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
                        <h2 className="text-xl font-bold text-foreground">Quiz Setup</h2>
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
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setFeedbackModalOpen(true)}
                                className="text-muted hover:text-ember-orange transition-colors flex items-center gap-1.5 text-sm"
                            >
                                <span>💡</span> Feedback
                            </button>
                            <span className="text-sm font-medium text-muted">
                                Question {currentQuestionIndex + 1} / {quizQuestions.length}
                            </span>
                        </div>
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
                    onReportQuestion={(id) => handleReportQuestion(id, "")}
                    onOpenReportModal={handleOpenReportModal}
                    onComplete={handleQuizComplete}
                    onQuestionChange={(index) => setCurrentQuestionIndex(index)}
                />

                {/* Report Modal */}
                <ReportModal
                    isOpen={reportModalOpen}
                    questionId={reportQuestionId || ""}
                    onClose={() => {
                        setReportModalOpen(false);
                        setReportQuestionId(null);
                    }}
                    onSubmit={handleReportQuestion}
                />

                {/* Feedback Modal */}
                <FeedbackModal
                    isOpen={feedbackModalOpen}
                    studyMode="quiz"
                    onClose={() => setFeedbackModalOpen(false)}
                    onSubmit={handleSubmitFeedback}
                />
            </div>
        );
    }

    return null;
}
