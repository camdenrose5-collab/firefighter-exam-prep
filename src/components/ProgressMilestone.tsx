"use client";

import { motion } from "framer-motion";
import { useUserStore } from "@/lib/store";

interface ProgressMilestoneProps {
    className?: string;
    showLabels?: boolean;
}

// Constants for endowed progress effect
const ARTIFICIAL_ADVANCEMENT = 10; // Pre-filled questions
const TOTAL_MILESTONE_TARGET = 30; // Frame as 30-question journey
const QUESTIONS_PER_LEVEL = 5;
const TOTAL_LEVELS = 6;

export default function ProgressMilestone({
    className = "",
    showLabels = true
}: ProgressMilestoneProps) {
    const { totalQuestionsAnswered, currentLevel } = useUserStore();

    // Calculate progress with artificial advancement
    const effectiveProgress = ARTIFICIAL_ADVANCEMENT + totalQuestionsAnswered;
    const progressPercentage = Math.min(100, (effectiveProgress / TOTAL_MILESTONE_TARGET) * 100);

    // Calculate questions until next level
    const questionsInCurrentLevel = totalQuestionsAnswered % QUESTIONS_PER_LEVEL;
    const questionsToNextLevel = QUESTIONS_PER_LEVEL - questionsInCurrentLevel;

    return (
        <div className={`w-full ${className}`}>
            {showLabels && (
                <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-muted">
                        Mastery Progress
                    </span>
                    <span className="text-foreground font-medium">
                        {effectiveProgress} / {TOTAL_MILESTONE_TARGET}
                    </span>
                </div>
            )}

            {/* Progress Bar */}
            <div className="relative h-3 bg-card-border rounded-full overflow-hidden">
                <motion.div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-fire-red to-ember-orange rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progressPercentage}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                />

                {/* Level markers */}
                {Array.from({ length: TOTAL_LEVELS - 1 }, (_, i) => {
                    const markerPosition = ((i + 1) * QUESTIONS_PER_LEVEL / TOTAL_MILESTONE_TARGET) * 100;
                    return (
                        <div
                            key={i}
                            className="absolute top-0 bottom-0 w-0.5 bg-background/50"
                            style={{ left: `${markerPosition}%` }}
                        />
                    );
                })}
            </div>

            {/* Level Indicators */}
            <div className="flex justify-between mt-2">
                {Array.from({ length: TOTAL_LEVELS }, (_, i) => {
                    const level = i + 1;
                    const isComplete = currentLevel > level;
                    const isCurrent = currentLevel === level;

                    return (
                        <div
                            key={level}
                            className="flex flex-col items-center"
                        >
                            <motion.div
                                initial={false}
                                animate={{
                                    scale: isCurrent ? 1.1 : 1,
                                    backgroundColor: isComplete
                                        ? "rgb(239, 68, 68)" // fire-red
                                        : isCurrent
                                            ? "rgb(251, 146, 60)" // ember-orange
                                            : "rgb(55, 65, 81)", // card-border
                                }}
                                className={`w-4 h-4 rounded-full flex items-center justify-center`}
                            >
                                {isComplete && (
                                    <motion.span
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="text-white text-xs"
                                    >
                                        ✓
                                    </motion.span>
                                )}
                            </motion.div>
                            {showLabels && (
                                <span className={`text-xs mt-1 ${isCurrent ? "text-fire-red font-medium" : "text-muted"
                                    }`}>
                                    L{level}
                                </span>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Next milestone hint */}
            {currentLevel < TOTAL_LEVELS && showLabels && (
                <p className="text-xs text-muted text-center mt-3">
                    {questionsToNextLevel === 1
                        ? "1 question to Level " + (currentLevel + 1) + "!"
                        : `${questionsToNextLevel} questions to Level ${currentLevel + 1}`
                    }
                </p>
            )}
        </div>
    );
}
