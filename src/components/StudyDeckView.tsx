"use client";

import { useState, useEffect } from "react";
import { apiUrl } from "@/lib/api";

interface StudyDeckQuestion {
    id: string;
    subject: string;
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
    added_at: string;
}

interface StudyDeckViewProps {
    onStartQuiz: (questions: StudyDeckQuestion[]) => void;
}

export default function StudyDeckView({ onStartQuiz }: StudyDeckViewProps) {
    const [questions, setQuestions] = useState<StudyDeckQuestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [expandedId, setExpandedId] = useState<string | null>(null);

    useEffect(() => {
        fetchStudyDeck();
    }, []);

    const fetchStudyDeck = async () => {
        const token = localStorage.getItem("auth_token");
        if (!token) {
            setError("Please log in to view your study deck");
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(apiUrl(`/api/study-deck?token=${token}`));
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Failed to fetch study deck");
            }

            setQuestions(data.questions);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    const removeFromDeck = async (questionId: string) => {
        const token = localStorage.getItem("auth_token");
        if (!token) return;

        try {
            const response = await fetch(
                apiUrl(`/api/study-deck/${questionId}?token=${token}`),
                { method: "DELETE" }
            );

            if (response.ok) {
                setQuestions(questions.filter(q => q.id !== questionId));
            }
        } catch (err) {
            console.error("Failed to remove from deck:", err);
        }
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric"
        });
    };

    const getSubjectColor = (subject: string) => {
        const colors: Record<string, string> = {
            "human-relations": "text-blue-400 bg-blue-400/10 border-blue-400/30",
            "mechanical-aptitude": "text-purple-400 bg-purple-400/10 border-purple-400/30",
            "reading-ability": "text-green-400 bg-green-400/10 border-green-400/30",
            "math": "text-amber-400 bg-amber-400/10 border-amber-400/30",
        };
        return colors[subject] || "text-gray-400 bg-gray-400/10 border-gray-400/30";
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin h-8 w-8 border-4 border-fire-red border-t-transparent rounded-full" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="card p-8 text-center">
                <p className="text-fire-red mb-4">{error}</p>
                <button onClick={fetchStudyDeck} className="btn-secondary">
                    Try Again
                </button>
            </div>
        );
    }

    if (questions.length === 0) {
        return (
            <div className="card p-12 text-center">
                <div className="text-6xl mb-4">📚</div>
                <h2 className="text-2xl font-bold mb-2">Your Study Deck is Empty</h2>
                <p className="text-muted mb-6">
                    Save questions during quizzes to review them later.
                    <br />
                    Just click "Save to Deck" after answering a question!
                </p>
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-ember-orange/10 text-ember-orange text-sm">
                    💡 Tip: Focus on questions you got wrong or want to review
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">📚 Study Deck</h2>
                    <p className="text-muted">{questions.length} saved questions</p>
                </div>

                <button
                    onClick={() => onStartQuiz(questions)}
                    className="btn-primary fire-glow hover:fire-glow-hover flex items-center gap-2"
                >
                    🎯 Quiz from Deck
                </button>
            </div>

            {/* Question List */}
            <div className="space-y-4">
                {questions.map((q) => (
                    <div key={q.id} className="card overflow-hidden">
                        {/* Question Header */}
                        <div
                            className="p-4 cursor-pointer hover:bg-card-border/20 transition-colors"
                            onClick={() => setExpandedId(expandedId === q.id ? null : q.id)}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className={`px-2 py-0.5 rounded-full text-xs border ${getSubjectColor(q.subject)}`}>
                                            {q.subject.replace("-", " ")}
                                        </span>
                                        <span className="text-xs text-muted">
                                            Added {formatDate(q.added_at)}
                                        </span>
                                    </div>
                                    <p className="font-medium line-clamp-2">{q.question}</p>
                                </div>

                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            removeFromDeck(q.id);
                                        }}
                                        className="text-muted hover:text-fire-red transition-colors p-2"
                                        title="Remove from deck"
                                    >
                                        🗑️
                                    </button>
                                    <span className="text-muted">
                                        {expandedId === q.id ? "▲" : "▼"}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Expanded Details */}
                        {expandedId === q.id && (
                            <div className="border-t border-card-border p-4 bg-card-bg/50 space-y-4 animate-in slide-in-from-top-2 duration-200">
                                <div>
                                    <h4 className="text-sm font-medium text-muted mb-2">Options:</h4>
                                    <div className="space-y-2">
                                        {q.options.map((opt, idx) => (
                                            <div
                                                key={idx}
                                                className={`p-2 rounded-lg border ${opt === q.correct_answer
                                                    ? "border-green-500/50 bg-green-500/10 text-green-400"
                                                    : "border-card-border"
                                                    }`}
                                            >
                                                <span className="text-muted mr-2">{String.fromCharCode(65 + idx)}.</span>
                                                {opt}
                                                {opt === q.correct_answer && <span className="ml-2">✓</span>}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="bg-card-bg/50 border-l-4 border-l-ember-orange p-4 rounded-r-lg">
                                    <h4 className="font-bold text-ember-orange mb-2">👨‍🚒 Captain's Explanation</h4>
                                    <p className="text-foreground/90">{q.explanation}</p>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
