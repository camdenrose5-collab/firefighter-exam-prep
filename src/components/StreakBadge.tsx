"use client";

import { motion } from "framer-motion";
import { Flame } from "lucide-react";
import { useUserStore } from "@/lib/store";

interface StreakBadgeProps {
    className?: string;
}

export default function StreakBadge({ className = "" }: StreakBadgeProps) {
    const { currentStreak, longestStreak } = useUserStore();

    if (currentStreak === 0) {
        return null;
    }

    const isOnFire = currentStreak >= 5;

    return (
        <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-fire-red/10 to-ember-orange/10 border border-fire-red/20 ${className}`}
        >
            <motion.div
                animate={isOnFire ? {
                    scale: [1, 1.2, 1],
                } : {}}
                transition={{
                    duration: 0.6,
                    repeat: isOnFire ? Infinity : 0,
                    repeatType: "reverse",
                }}
            >
                <Flame className={`w-4 h-4 ${isOnFire ? "text-fire-red" : "text-ember-orange"}`} />
            </motion.div>
            <span className="text-sm font-semibold text-foreground">
                {currentStreak}
            </span>
            <span className="text-xs text-muted">
                streak
            </span>
            {currentStreak === longestStreak && longestStreak > 1 && (
                <span className="text-xs text-fire-red font-medium ml-1">
                    🏆 Best!
                </span>
            )}
        </motion.div>
    );
}
