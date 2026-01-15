"use client";

import { useState } from "react";

interface FeedbackModalProps {
    isOpen: boolean;
    studyMode: "quiz" | "flashcards" | "explain";
    onClose: () => void;
    onSubmit: (studyMode: string, message: string) => Promise<void>;
}

const MODE_LABELS: Record<string, string> = {
    quiz: "📝 Quiz",
    flashcards: "📇 Flashcards",
    explain: "💬 Explain",
};

export default function FeedbackModal({ isOpen, studyMode, onClose, onSubmit }: FeedbackModalProps) {
    const [message, setMessage] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async () => {
        if (!message.trim()) return;

        setIsSubmitting(true);
        try {
            await onSubmit(studyMode, message);
            setSubmitted(true);
            setTimeout(() => {
                setMessage("");
                setSubmitted(false);
                onClose();
            }, 1500);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (submitted) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                <div className="bg-card border border-green-500/30 rounded-2xl p-8 max-w-sm w-full mx-4 text-center animate-in fade-in zoom-in-95 duration-200">
                    <span className="text-5xl block mb-4">✅</span>
                    <h3 className="text-xl font-bold text-foreground mb-2">Thanks for your feedback!</h3>
                    <p className="text-muted">Your ideas help make studying better.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="bg-card border border-card-border rounded-2xl p-6 max-w-md w-full mx-4 space-y-6 animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center gap-3">
                    <span className="text-3xl">💡</span>
                    <div>
                        <h3 className="text-xl font-bold text-foreground">Share Feedback</h3>
                        <p className="text-sm text-muted">Ideas or suggestions for improvement</p>
                    </div>
                </div>

                {/* Study Mode Badge */}
                <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-card-border/50 rounded-full text-sm text-muted">
                    {MODE_LABELS[studyMode] || studyMode}
                </div>

                {/* Message Input */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-foreground">
                        What&apos;s on your mind?
                    </label>
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="e.g., Add more questions about hydraulics, make flashcards flip faster, include audio explanations..."
                        className="w-full p-4 rounded-xl bg-background border border-card-border text-foreground placeholder-muted focus:outline-none focus:border-ember-orange transition-colors resize-none h-32"
                        autoFocus
                    />
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-3 rounded-xl border border-card-border text-muted hover:text-foreground hover:border-fire-red transition-all"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isSubmitting || !message.trim()}
                        className="flex-1 btn-primary py-3 rounded-xl fire-glow hover:fire-glow-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                    >
                        {isSubmitting ? (
                            <>
                                <span className="animate-spin">🔄</span>
                                Sending...
                            </>
                        ) : (
                            <>
                                <span>📤</span>
                                Send Feedback
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
