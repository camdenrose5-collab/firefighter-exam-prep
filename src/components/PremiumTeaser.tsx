"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X, ArrowRight } from "lucide-react";
import { useState } from "react";
import Link from "next/link";

type TeaserType = "explanation" | "unlimited" | "accuracy" | "streak";

interface PremiumTeaserProps {
    type: TeaserType;
    onDismiss?: () => void;
    className?: string;
}

const teaserConfig: Record<TeaserType, {
    message: string;
    cta: string;
}> = {
    explanation: {
        message: "AI-powered explanations available in Pro",
        cta: "Unlock",
    },
    unlimited: {
        message: "Pro members never hit daily limits",
        cta: "Go Unlimited",
    },
    accuracy: {
        message: "You're crushing it! Take your prep to the next level",
        cta: "Upgrade",
    },
    streak: {
        message: "Protect your streak with Premium",
        cta: "Keep Going",
    },
};

export default function PremiumTeaser({
    type,
    onDismiss,
    className = ""
}: PremiumTeaserProps) {
    const [isDismissed, setIsDismissed] = useState(false);
    const config = teaserConfig[type];

    const handleDismiss = () => {
        setIsDismissed(true);
        onDismiss?.();
    };

    return (
        <AnimatePresence>
            {!isDismissed && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`p-3 rounded-lg bg-gradient-to-r from-fire-red/10 to-ember-orange/10 border border-fire-red/20 ${className}`}
                >
                    <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-fire-red flex-shrink-0" />
                            <p className="text-sm text-muted">
                                {config.message}
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <a
                                href="https://buy.stripe.com/00wfZa8V6fOZasO1pf1ZS03"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 px-3 py-1 bg-fire-red text-white text-xs font-medium rounded-full hover:bg-ember-orange transition-colors"
                            >
                                {config.cta}
                                <ArrowRight className="w-3 h-3" />
                            </a>
                            {onDismiss && (
                                <button
                                    onClick={handleDismiss}
                                    className="p-1 text-muted hover:text-foreground transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            )}
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
