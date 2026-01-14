"use client";

import { useState } from "react";

interface Document {
    id: string;
    name: string;
}

interface CaptainsReviewProps {
    documents: Document[];
}

interface ReviewResponse {
    grade: "correct" | "partial" | "incorrect";
    feedback: string;
    textbook_answer: string;
    citations: Array<{
        source: string;
        page?: number;
        excerpt: string;
    }>;
}

export default function CaptainsReview({ documents }: CaptainsReviewProps) {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [review, setReview] = useState<ReviewResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!question.trim() || !answer.trim()) return;

        setIsLoading(true);
        setError(null);
        setReview(null);

        try {
            const response = await fetch("http://localhost:8000/api/review", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question,
                    answer,
                    document_ids: documents.map((d) => d.id),
                }),
            });

            if (!response.ok) {
                throw new Error("Review request failed");
            }

            const data = await response.json();
            setReview(data);
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "Failed to get review. Is the backend running?"
            );
        } finally {
            setIsLoading(false);
        }
    };

    const getGradeStyles = (grade: string) => {
        switch (grade) {
            case "correct":
                return "bg-green-500/20 border-green-500/50 text-green-400";
            case "partial":
                return "bg-caution-yellow/20 border-caution-yellow/50 text-caution-yellow";
            case "incorrect":
                return "bg-fire-red/20 border-fire-red/50 text-fire-red";
            default:
                return "bg-card-border border-muted text-muted";
        }
    };

    const getGradeLabel = (grade: string) => {
        switch (grade) {
            case "correct":
                return "✅ Correct";
            case "partial":
                return "⚠️ Partially Correct";
            case "incorrect":
                return "❌ Incorrect";
            default:
                return "Unknown";
        }
    };

    return (
        <div className="card p-8">
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
                <span className="text-3xl">👨‍🚒</span> Captain&apos;s Review
            </h2>
            <p className="text-muted mb-6">
                Submit a question and your answer. The Captain will review it against your training materials.
            </p>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Question Input */}
                <div>
                    <label className="block text-sm font-semibold mb-2">
                        Question
                    </label>
                    <textarea
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Enter an exam question, e.g.: What are the three classes of fire?"
                        className="w-full h-24 px-4 py-3 bg-card-border border border-card-border rounded-lg text-foreground placeholder:text-muted focus:outline-none focus:border-fire-red focus:ring-1 focus:ring-fire-red resize-none"
                        disabled={isLoading}
                    />
                </div>

                {/* Answer Input */}
                <div>
                    <label className="block text-sm font-semibold mb-2">
                        Your Answer
                    </label>
                    <textarea
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        placeholder="Type your answer here..."
                        className="w-full h-32 px-4 py-3 bg-card-border border border-card-border rounded-lg text-foreground placeholder:text-muted focus:outline-none focus:border-fire-red focus:ring-1 focus:ring-fire-red resize-none"
                        disabled={isLoading}
                    />
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isLoading || !question.trim() || !answer.trim()}
                    className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isLoading ? (
                        <>
                            <span className="animate-spin">⏳</span> Captain is reviewing...
                        </>
                    ) : (
                        <>
                            <span>🎖️</span> Submit for Review
                        </>
                    )}
                </button>
            </form>

            {/* Error Message */}
            {error && (
                <div className="mt-6 p-4 bg-fire-red/20 border border-fire-red/50 rounded-lg text-fire-red">
                    <p className="font-semibold">⚠️ {error}</p>
                    <p className="text-sm mt-1 opacity-80">
                        Make sure the backend server is running on port 8000
                    </p>
                </div>
            )}

            {/* Review Result */}
            {review && (
                <div className="mt-8 space-y-6">
                    {/* Grade Badge */}
                    <div
                        className={`inline-block px-4 py-2 rounded-lg border font-bold text-lg ${getGradeStyles(
                            review.grade
                        )}`}
                    >
                        {getGradeLabel(review.grade)}
                    </div>

                    {/* Feedback */}
                    <div className="p-4 bg-card-border rounded-lg">
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <span>💬</span> Captain&apos;s Feedback
                        </h4>
                        <p className="text-foreground leading-relaxed">{review.feedback}</p>
                    </div>

                    {/* Textbook Answer */}
                    <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                        <h4 className="font-semibold mb-2 flex items-center gap-2 text-green-400">
                            <span>📖</span> Textbook Answer
                        </h4>
                        <p className="text-foreground leading-relaxed">
                            {review.textbook_answer}
                        </p>
                    </div>

                    {/* Citations */}
                    {review.citations.length > 0 && (
                        <div>
                            <h4 className="font-semibold mb-3 flex items-center gap-2">
                                <span>📚</span> Sources
                            </h4>
                            <div className="space-y-3">
                                {review.citations.map((citation, idx) => (
                                    <div
                                        key={idx}
                                        className="p-3 bg-card-border/50 rounded-lg border-l-4 border-fire-red"
                                    >
                                        <div className="flex items-center gap-2 text-sm text-muted mb-1">
                                            <span className="font-mono bg-fire-red/20 text-fire-red px-1.5 py-0.5 rounded text-xs">
                                                [{idx + 1}]
                                            </span>
                                            <span className="truncate">{citation.source}</span>
                                            {citation.page && (
                                                <span className="text-xs">• Page {citation.page}</span>
                                            )}
                                        </div>
                                        <p className="text-sm text-foreground/80 italic">
                                            &ldquo;{citation.excerpt}&rdquo;
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Using Documents */}
            <div className="mt-8 pt-6 border-t border-card-border">
                <p className="text-xs text-muted">
                    📌 Review is based on {documents.length} uploaded document{documents.length !== 1 ? "s" : ""}
                </p>
            </div>
        </div>
    );
}
