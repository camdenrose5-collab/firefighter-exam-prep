"use client";

import { useState } from "react";

interface ReportModalProps {
    isOpen: boolean;
    questionId: string;
    onClose: () => void;
    onSubmit: (questionId: string, reason: string) => Promise<void>;
}

export default function ReportModal({ isOpen, questionId, onClose, onSubmit }: ReportModalProps) {
    const [reason, setReason] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async () => {
        setIsSubmitting(true);
        try {
            await onSubmit(questionId, reason);
            setReason("");
            onClose();
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="bg-card border border-card-border rounded-2xl p-6 max-w-md w-full mx-4 space-y-6 animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center gap-3">
                    <span className="text-3xl">⚠️</span>
                    <div>
                        <h3 className="text-xl font-bold text-foreground">Report Question</h3>
                        <p className="text-sm text-muted">Let us know what's wrong with this question</p>
                    </div>
                </div>

                {/* Explanation Input */}
                <div className="space-y-2">
                    <label className="text-sm font-medium text-foreground">
                        What&apos;s the issue? <span className="text-muted">(optional)</span>
                    </label>
                    <textarea
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        placeholder="e.g., The correct answer seems wrong, question is confusing, typo in options..."
                        className="w-full p-4 rounded-xl bg-background border border-card-border text-foreground placeholder-muted focus:outline-none focus:border-fire-red transition-colors resize-none h-32"
                        autoFocus
                    />
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-3 rounded-xl border border-card-border text-muted hover:text-foreground hover:border-ember-orange transition-all"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        className="flex-1 btn-primary py-3 rounded-xl fire-glow hover:fire-glow-hover disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                    >
                        {isSubmitting ? (
                            <>
                                <span className="animate-spin">🔄</span>
                                Submitting...
                            </>
                        ) : (
                            <>
                                <span>📤</span>
                                Submit Report
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
