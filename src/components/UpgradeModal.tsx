"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Zap, Check, ArrowRight, UserPlus, CreditCard } from "lucide-react";
import Link from "next/link";
import { useUserStore, TIER_LIMITS } from "@/lib/store";

interface UpgradeModalProps {
    isOpen: boolean;
    onClose: () => void;
    limitType: "quiz" | "flashcard";
    onSignup?: () => void;
}

export default function UpgradeModal({ isOpen, onClose, limitType, onSignup }: UpgradeModalProps) {
    const tier = useUserStore((state) => state.tier);

    const isLead = tier === "lead";
    const isFree = tier === "free";

    // Different messaging based on tier
    const getTitle = () => {
        if (isLead) return "Ready to Continue?";
        return "Daily Limit Reached";
    };

    const getMessage = () => {
        if (isLead) {
            const limit = limitType === "quiz"
                ? TIER_LIMITS.lead.totalQuestions
                : TIER_LIMITS.lead.totalFlashcards;
            return `You've used your ${limit} free ${limitType === "quiz" ? "questions" : "flashcards"}. Create a free account to get ${TIER_LIMITS.free.questionsPerDay} questions and ${TIER_LIMITS.free.flashcardsPerDay} flashcards every day.`;
        }

        const limit = limitType === "quiz"
            ? TIER_LIMITS.free.questionsPerDay
            : TIER_LIMITS.free.flashcardsPerDay;
        return `You've reached your daily limit of ${limit} ${limitType === "quiz" ? "questions" : "flashcards"}. Upgrade to Premium for unlimited access.`;
    };

    const premiumBenefits = [
        "Unlimited practice questions",
        "Unlimited flashcard sessions",
        "Track progress over time",
        "Priority support",
    ];

    const freeBenefits = [
        `${TIER_LIMITS.free.questionsPerDay} practice questions per day`,
        `${TIER_LIMITS.free.flashcardsPerDay} flashcard sessions per day`,
        "Save your progress",
        "Free forever",
    ];

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
                        {/* Header */}
                        <div className="relative px-6 pt-6 pb-4">
                            <button
                                onClick={onClose}
                                className="absolute top-4 right-4 p-2 text-muted hover:text-foreground rounded-lg hover:bg-card-border/50 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>

                            <div className="w-12 h-12 rounded-xl bg-fire-red/10 flex items-center justify-center mb-4">
                                {isLead ? (
                                    <UserPlus className="w-6 h-6 text-fire-red" />
                                ) : (
                                    <Zap className="w-6 h-6 text-fire-red" />
                                )}
                            </div>

                            <h2 className="text-xl font-bold text-foreground">
                                {getTitle()}
                            </h2>
                            <p className="text-sm text-muted mt-2">
                                {getMessage()}
                            </p>
                        </div>

                        {/* Content */}
                        <div className="px-6 pb-6 space-y-4">
                            {/* For Leads: Show signup benefits */}
                            {isLead && (
                                <div className="space-y-4">
                                    <div className="p-4 rounded-lg bg-background border border-card-border">
                                        <h3 className="font-medium text-foreground mb-3">
                                            Free Account Benefits
                                        </h3>
                                        <ul className="space-y-2">
                                            {freeBenefits.map((benefit) => (
                                                <li key={benefit} className="flex items-center gap-2 text-sm text-muted">
                                                    <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                                                    {benefit}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <button
                                        onClick={onSignup}
                                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-fire-red text-white font-medium rounded-lg hover:bg-ember-orange transition-colors"
                                    >
                                        <UserPlus className="w-4 h-4" />
                                        Create Free Account
                                    </button>

                                    <button
                                        onClick={onClose}
                                        className="w-full px-4 py-2 text-sm text-muted hover:text-foreground transition-colors"
                                    >
                                        Continue Later
                                    </button>
                                </div>
                            )}

                            {/* For Free users: Show premium upgrade */}
                            {isFree && (
                                <div className="space-y-4">
                                    <div className="p-4 rounded-lg bg-gradient-to-br from-fire-red/10 to-ember-orange/10 border border-fire-red/20">
                                        <div className="flex items-baseline gap-2 mb-3">
                                            <span className="text-2xl font-bold text-foreground">$10</span>
                                            <span className="text-sm text-muted">/month</span>
                                        </div>
                                        <ul className="space-y-2">
                                            {premiumBenefits.map((benefit) => (
                                                <li key={benefit} className="flex items-center gap-2 text-sm text-muted">
                                                    <Check className="w-4 h-4 text-fire-red flex-shrink-0" />
                                                    {benefit}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <Link
                                        href="/services"
                                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-fire-red text-white font-medium rounded-lg hover:bg-ember-orange transition-colors"
                                    >
                                        <CreditCard className="w-4 h-4" />
                                        Upgrade to Premium
                                        <ArrowRight className="w-4 h-4" />
                                    </Link>

                                    <button
                                        onClick={onClose}
                                        className="w-full px-4 py-2 text-sm text-muted hover:text-foreground transition-colors"
                                    >
                                        Come Back Tomorrow
                                    </button>
                                </div>
                            )}
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
