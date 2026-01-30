"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Zap, Check, ArrowRight, UserPlus, CreditCard, Star, Flame } from "lucide-react";
import Link from "next/link";
import { useUserStore, TIER_LIMITS } from "@/lib/store";

interface UpgradeModalProps {
    isOpen: boolean;
    onClose: () => void;
    limitType: "quiz" | "flashcard";
    onSignup?: () => void;
    streakAtRisk?: boolean;
}

// Pricing configuration with behavioral economics
const PRICING = {
    monthly: {
        price: 9.99,
        display: "$9.99",
        period: "/month",
    },
    annual: {
        price: 99,
        display: "$99",
        period: "/year",
        savings: "$21",
        monthlyEquivalent: "$8.25",
    },
};

export default function UpgradeModal({
    isOpen,
    onClose,
    limitType,
    onSignup,
    streakAtRisk = false
}: UpgradeModalProps) {
    const tier = useUserStore((state) => state.tier);
    const currentStreak = useUserStore((state) => state.currentStreak);
    const [selectedPlan, setSelectedPlan] = useState<"monthly" | "annual">("annual");

    const isLead = tier === "lead";
    const isFree = tier === "free";

    // Different messaging based on tier and context
    const getTitle = () => {
        if (isLead) return "Ready to Continue?";
        if (streakAtRisk && currentStreak > 0) return `Don't Lose Your ${currentStreak}-Day Streak!`;
        return "Unlock Unlimited Access";
    };

    const getMessage = () => {
        if (isLead) {
            return `You've sampled our content. Create a free account to get ${TIER_LIMITS.free.questionsPerDay} questions and ${TIER_LIMITS.free.flashcardsPerDay} flashcards every day.`;
        }
        if (streakAtRisk && currentStreak > 0) {
            return "Keep your momentum going with unlimited access. Premium members never hit daily limits.";
        }
        const limit = limitType === "quiz"
            ? TIER_LIMITS.free.questionsPerDay
            : TIER_LIMITS.free.flashcardsPerDay;
        return `You've reached your daily limit of ${limit} ${limitType === "quiz" ? "questions" : "flashcards"}.`;
    };

    const premiumBenefits = [
        "Unlimited practice questions",
        "Unlimited flashcard sessions",
        "Track progress over time",
        "AI-powered explanations",
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
                                ) : streakAtRisk ? (
                                    <Flame className="w-6 h-6 text-fire-red" />
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

                            {/* For Free users: Show premium upgrade with 3-tier pricing */}
                            {isFree && (
                                <div className="space-y-4">
                                    {/* Plan Toggle */}
                                    <div className="flex gap-2 p-1 bg-background border border-card-border rounded-lg">
                                        <button
                                            onClick={() => setSelectedPlan("monthly")}
                                            className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${selectedPlan === "monthly"
                                                    ? "bg-card text-foreground shadow"
                                                    : "text-muted hover:text-foreground"
                                                }`}
                                        >
                                            Monthly
                                        </button>
                                        <button
                                            onClick={() => setSelectedPlan("annual")}
                                            className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors relative ${selectedPlan === "annual"
                                                    ? "bg-card text-foreground shadow"
                                                    : "text-muted hover:text-foreground"
                                                }`}
                                        >
                                            Annual
                                            <span className="absolute -top-2 -right-2 px-1.5 py-0.5 bg-green-500 text-white text-xs rounded-full">
                                                Save {PRICING.annual.savings}
                                            </span>
                                        </button>
                                    </div>

                                    {/* Pricing Card */}
                                    <div className={`p-4 rounded-lg border-2 transition-colors ${selectedPlan === "annual"
                                            ? "bg-gradient-to-br from-fire-red/10 to-ember-orange/10 border-fire-red/30"
                                            : "bg-background border-card-border"
                                        }`}>
                                        {selectedPlan === "annual" && (
                                            <div className="flex items-center gap-1.5 text-xs text-fire-red font-medium mb-2">
                                                <Star className="w-3 h-3" />
                                                Best Value
                                            </div>
                                        )}

                                        <div className="flex items-baseline gap-1 mb-1">
                                            <span className="text-3xl font-bold text-foreground">
                                                {selectedPlan === "annual"
                                                    ? PRICING.annual.display
                                                    : PRICING.monthly.display}
                                            </span>
                                            <span className="text-sm text-muted">
                                                {selectedPlan === "annual"
                                                    ? PRICING.annual.period
                                                    : PRICING.monthly.period}
                                            </span>
                                        </div>

                                        {selectedPlan === "annual" && (
                                            <p className="text-xs text-muted mb-3">
                                                Just {PRICING.annual.monthlyEquivalent}/month • Save {PRICING.annual.savings}/year
                                            </p>
                                        )}

                                        <ul className="space-y-2 mt-3">
                                            {premiumBenefits.map((benefit) => (
                                                <li key={benefit} className="flex items-center gap-2 text-sm text-muted">
                                                    <Check className="w-4 h-4 text-fire-red flex-shrink-0" />
                                                    {benefit}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Social Proof */}
                                    <div className="flex items-center justify-center gap-2 text-sm text-muted">
                                        <div className="flex -space-x-2">
                                            {[1, 2, 3].map((i) => (
                                                <div
                                                    key={i}
                                                    className="w-6 h-6 rounded-full bg-card-border border-2 border-card"
                                                />
                                            ))}
                                        </div>
                                        <span>Join 1,000+ candidates studying with us</span>
                                    </div>

                                    <Link
                                        href="/services"
                                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-fire-red text-white font-medium rounded-lg hover:bg-ember-orange transition-colors"
                                    >
                                        <CreditCard className="w-4 h-4" />
                                        {selectedPlan === "annual" ? "Get Annual Plan" : "Upgrade to Premium"}
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
