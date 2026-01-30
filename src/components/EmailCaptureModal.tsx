"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Mail, TrendingUp, Check, ArrowRight, Sparkles } from "lucide-react";
import { useUserStore } from "@/lib/store";

interface EmailCaptureModalProps {
    isOpen: boolean;
    onClose: () => void;
    onComplete: () => void;
    quizResults: {
        correct: number;
        total: number;
        percentage: number;
    };
}

export default function EmailCaptureModal({
    isOpen,
    onClose,
    onComplete,
    quizResults,
}: EmailCaptureModalProps) {
    const [email, setEmail] = useState("");
    const [isValid, setIsValid] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const captureLeadEmail = useUserStore((state) => state.captureLeadEmail);
    const setDiagnosticComplete = useUserStore((state) => state.setDiagnosticComplete);

    const validateEmail = (email: string) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    };

    const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setEmail(value);
        setIsValid(validateEmail(value));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isValid) return;

        setIsSubmitting(true);

        // Capture email and mark diagnostic complete
        captureLeadEmail(email);
        setDiagnosticComplete(quizResults.percentage);

        // Brief delay for animation
        await new Promise(resolve => setTimeout(resolve, 500));

        setShowResults(true);
        setIsSubmitting(false);
    };

    const handleContinue = () => {
        onComplete();
    };

    // Calculate percentile (simulated for now)
    const percentile = Math.min(95, Math.max(50, quizResults.percentage + 20));

    // Performance message based on score
    const getPerformanceMessage = () => {
        if (quizResults.percentage >= 80) return "Excellent! You're already ahead of most candidates.";
        if (quizResults.percentage >= 60) return "Good foundation! A little practice will take you far.";
        return "Great start! Our study tools will help you improve quickly.";
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: "spring", duration: 0.3 }}
                        className="w-full max-w-md bg-card border border-card-border rounded-xl shadow-2xl overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {!showResults ? (
                            <>
                                {/* Email Capture View */}
                                <div className="relative px-6 pt-6 pb-4">
                                    <button
                                        onClick={onClose}
                                        className="absolute top-4 right-4 p-2 text-muted hover:text-foreground rounded-lg hover:bg-card-border/50 transition-colors"
                                    >
                                        <X className="w-5 h-5" />
                                    </button>

                                    <div className="w-12 h-12 rounded-xl bg-fire-red/10 flex items-center justify-center mb-4">
                                        <TrendingUp className="w-6 h-6 text-fire-red" />
                                    </div>

                                    <h2 className="text-xl font-bold text-foreground">
                                        Your Results Are Ready!
                                    </h2>

                                    {/* Teaser - Curiosity Gap */}
                                    <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-fire-red/10 to-ember-orange/10 border border-fire-red/20">
                                        <p className="text-sm text-muted">
                                            <span className="text-foreground font-medium">Preview:</span>{" "}
                                            You scored better than approximately{" "}
                                            <span className="text-fire-red font-bold">{percentile}%</span>{" "}
                                            of firefighter candidates...
                                        </p>
                                        <p className="text-xs text-muted mt-2 flex items-center gap-1">
                                            <Sparkles className="w-3 h-3 text-fire-red" />
                                            Enter your email to see your full Knowledge Score
                                        </p>
                                    </div>
                                </div>

                                <form onSubmit={handleSubmit} className="px-6 pb-6 space-y-4">
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
                                        <input
                                            type="email"
                                            inputMode="email"
                                            autoComplete="email"
                                            placeholder="Your email address"
                                            value={email}
                                            onChange={handleEmailChange}
                                            className="w-full pl-10 pr-10 py-3 bg-background border border-card-border rounded-lg text-foreground placeholder:text-muted focus:outline-none focus:border-fire-red transition-colors"
                                        />
                                        {email && (
                                            <div className="absolute right-3 top-1/2 -translate-y-1/2">
                                                {isValid ? (
                                                    <Check className="w-5 h-5 text-green-500" />
                                                ) : (
                                                    <X className="w-5 h-5 text-red-500" />
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={!isValid || isSubmitting}
                                        className={`w-full py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${isValid && !isSubmitting
                                                ? "bg-fire-red text-white hover:bg-ember-orange"
                                                : "bg-card-border text-muted cursor-not-allowed"
                                            }`}
                                    >
                                        {isSubmitting ? (
                                            "Loading..."
                                        ) : (
                                            <>
                                                See My Score
                                                <ArrowRight className="w-4 h-4" />
                                            </>
                                        )}
                                    </button>

                                    <p className="text-xs text-center text-muted">
                                        We&apos;ll send you study tips to help you pass your exam. Unsubscribe anytime.
                                    </p>
                                </form>
                            </>
                        ) : (
                            <>
                                {/* Results Revealed View */}
                                <div className="px-6 pt-6 pb-4">
                                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-fire-red to-ember-orange flex items-center justify-center mx-auto mb-4">
                                        <span className="text-2xl font-bold text-white">
                                            {quizResults.correct}/{quizResults.total}
                                        </span>
                                    </div>

                                    <h2 className="text-xl font-bold text-foreground text-center mb-2">
                                        Your Knowledge Score
                                    </h2>

                                    {/* Score Display */}
                                    <div className="text-center mb-4">
                                        <span className="text-5xl font-bold text-fire-red">
                                            {quizResults.percentage}%
                                        </span>
                                        <p className="text-sm text-muted mt-2">
                                            Top {100 - percentile}% of candidates
                                        </p>
                                    </div>

                                    {/* Performance Message */}
                                    <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-center">
                                        <p className="text-sm text-foreground">
                                            {getPerformanceMessage()}
                                        </p>
                                    </div>
                                </div>

                                <div className="px-6 pb-6 space-y-3">
                                    {/* Benefits Preview */}
                                    <div className="p-4 rounded-lg bg-card-border/50">
                                        <p className="text-sm font-medium text-foreground mb-2">
                                            Continue your journey:
                                        </p>
                                        <ul className="space-y-1 text-sm text-muted">
                                            <li className="flex items-center gap-2">
                                                <Check className="w-4 h-4 text-green-500" />
                                                10 more practice questions
                                            </li>
                                            <li className="flex items-center gap-2">
                                                <Check className="w-4 h-4 text-green-500" />
                                                Track your progress
                                            </li>
                                            <li className="flex items-center gap-2">
                                                <Check className="w-4 h-4 text-green-500" />
                                                Flashcards & study tools
                                            </li>
                                        </ul>
                                    </div>

                                    <button
                                        onClick={handleContinue}
                                        className="w-full py-3 px-4 rounded-lg font-medium bg-fire-red text-white hover:bg-ember-orange transition-colors flex items-center justify-center gap-2"
                                    >
                                        Continue to Study Hub
                                        <ArrowRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </>
                        )}
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
