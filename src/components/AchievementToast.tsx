"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Flame, Target, Trophy, Zap, Star } from "lucide-react";
import { useEffect, useState } from "react";

type AchievementType = "streak" | "level" | "first_quiz" | "accuracy" | "milestone";

interface AchievementToastProps {
    type: AchievementType;
    value?: number;
    onClose: () => void;
    showPremiumTeaser?: boolean;
}

const achievementConfig: Record<AchievementType, {
    icon: typeof Flame;
    title: string;
    getMessage: (value?: number) => string;
    color: string;
    bgColor: string;
}> = {
    streak: {
        icon: Flame,
        title: "Streak Achieved!",
        getMessage: (value) => `${value}-correct streak! You're on fire!`,
        color: "text-fire-red",
        bgColor: "bg-fire-red/10",
    },
    level: {
        icon: Trophy,
        title: "Level Up!",
        getMessage: (value) => `You've reached Level ${value}!`,
        color: "text-yellow-500",
        bgColor: "bg-yellow-500/10",
    },
    first_quiz: {
        icon: Target,
        title: "First Quiz Complete!",
        getMessage: () => "Great start! Keep the momentum going.",
        color: "text-blue-500",
        bgColor: "bg-blue-500/10",
    },
    accuracy: {
        icon: Star,
        title: "High Accuracy!",
        getMessage: (value) => `${value}% accuracy this session!`,
        color: "text-green-500",
        bgColor: "bg-green-500/10",
    },
    milestone: {
        icon: Zap,
        title: "Milestone Reached!",
        getMessage: (value) => `${value} total questions answered!`,
        color: "text-purple-500",
        bgColor: "bg-purple-500/10",
    },
};

export default function AchievementToast({
    type,
    value,
    onClose,
    showPremiumTeaser = false,
}: AchievementToastProps) {
    const [isVisible, setIsVisible] = useState(true);
    const config = achievementConfig[type];
    const Icon = config.icon;

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
        }, 4000);

        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: -50, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.95 }}
                    transition={{ type: "spring", duration: 0.5 }}
                    className="fixed top-20 left-1/2 -translate-x-1/2 z-50 w-full max-w-sm px-4"
                >
                    <div className="bg-card border border-card-border rounded-xl shadow-xl overflow-hidden">
                        <div className="p-4 flex items-start gap-3">
                            <motion.div
                                initial={{ rotate: -15, scale: 0.8 }}
                                animate={{ rotate: 0, scale: 1 }}
                                transition={{ type: "spring", delay: 0.1 }}
                                className={`w-10 h-10 rounded-lg ${config.bgColor} flex items-center justify-center flex-shrink-0`}
                            >
                                <Icon className={`w-5 h-5 ${config.color}`} />
                            </motion.div>
                            <div className="flex-1 min-w-0">
                                <p className="font-semibold text-foreground">
                                    {config.title}
                                </p>
                                <p className="text-sm text-muted">
                                    {config.getMessage(value)}
                                </p>
                            </div>
                            <button
                                onClick={() => setIsVisible(false)}
                                className="text-muted hover:text-foreground transition-colors text-sm"
                            >
                                ✕
                            </button>
                        </div>

                        {showPremiumTeaser && (
                            <div className="px-4 pb-4">
                                <div className="p-3 rounded-lg bg-gradient-to-r from-fire-red/10 to-ember-orange/10 border border-fire-red/20">
                                    <p className="text-xs text-muted">
                                        <span className="text-fire-red font-medium">Pro tip:</span>{" "}
                                        Upgrade to Premium to unlock unlimited practice and scale your success.
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

// Hook to manage achievement toasts
export function useAchievementToast() {
    const [toast, setToast] = useState<{
        type: AchievementType;
        value?: number;
        showPremiumTeaser?: boolean;
    } | null>(null);

    const showAchievement = (
        type: AchievementType,
        value?: number,
        showPremiumTeaser = false
    ) => {
        setToast({ type, value, showPremiumTeaser });
    };

    const hideAchievement = () => {
        setToast(null);
    };

    return { toast, showAchievement, hideAchievement };
}
