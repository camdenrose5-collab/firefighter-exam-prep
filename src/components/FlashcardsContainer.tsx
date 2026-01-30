"use client";

import { useState } from "react";
import SubjectSelector from "./SubjectSelector";
import FeedbackModal from "./FeedbackModal";
import UpgradeModal from "./UpgradeModal";
import { getFlashcards, ParsedQuestion } from "@/data/questionBank";
import { apiUrl } from "@/lib/api";
import { useUserStore, useCanStartFlashcards, FREE_TIER_LIMITS } from "@/lib/store";

interface Flashcard {
    id: string;
    front_content: string;
    back_content: string;
}

interface FlashcardsContainerProps {
    onBack: () => void;
}

const TOTAL_CARDS = 10;

export default function FlashcardsContainer({ onBack }: FlashcardsContainerProps) {
    const [phase, setPhase] = useState<"subject-select" | "study">("subject-select");
    const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
    const [allFlashcards, setAllFlashcards] = useState<Flashcard[]>([]);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [isFlipped, setIsFlipped] = useState(false);
    const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
    const [upgradeModalOpen, setUpgradeModalOpen] = useState(false);

    // Freemium state
    const canStartFlashcards = useCanStartFlashcards();
    const incrementFlashcardCount = useUserStore((state) => state.incrementFlashcardCount);
    const tier = useUserStore((state) => state.tier);
    const flashcardCount = useUserStore((state) => state.flashcardCount);
    const remainingFlashcards = tier === "premium" ? Infinity : Math.max(0, FREE_TIER_LIMITS.flashcardSessionsPerDay - flashcardCount);

    const handleSubmitFeedback = async (studyMode: string, message: string) => {
        try {
            await fetch(apiUrl("/api/feedback"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ study_mode: studyMode, message }),
            });
        } catch (err) {
            console.error("Failed to submit feedback:", err);
        }
    };

    const handleContinueToStudy = () => {
        // Check freemium limit before proceeding
        if (!canStartFlashcards) {
            setUpgradeModalOpen(true);
            return;
        }
        if (selectedSubjects.length > 0) {
            // Get flashcards instantly from client-side bank (no API latency)
            const questions = getFlashcards(selectedSubjects, TOTAL_CARDS);

            // Convert questions to flashcard format
            const cards: Flashcard[] = questions.map((q) => ({
                id: q.id,
                front_content: q.question,
                back_content: `${q.correct_answer}\n\n${q.explanation}`,
            }));

            if (cards.length === 0) {
                alert("No flashcards available for selected subjects.");
                return;
            }

            setAllFlashcards(cards);
            setCurrentCardIndex(0);
            setIsFlipped(false);
            setPhase("study");

            // Track flashcard session usage
            incrementFlashcardCount();
        }
    };

    const currentCard = allFlashcards[currentCardIndex];

    const handleFlip = () => {
        setIsFlipped(!isFlipped);
    };

    const handleNext = () => {
        if (currentCardIndex < allFlashcards.length - 1) {
            setCurrentCardIndex((prev) => prev + 1);
            setIsFlipped(false);
        }
    };

    const handlePrevious = () => {
        if (currentCardIndex > 0) {
            setCurrentCardIndex((prev) => prev - 1);
            setIsFlipped(false);
        }
    };

    // Phase 1: Subject Selection
    if (phase === "subject-select") {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h2 className="text-xl font-bold text-foreground">Flashcards</h2>
                        {tier === "free" && (
                            <p className="text-sm text-muted mt-1">
                                {remainingFlashcards === Infinity ? "Unlimited" : `${remainingFlashcards} of ${FREE_TIER_LIMITS.flashcardSessionsPerDay}`} sessions remaining today
                            </p>
                        )}
                    </div>
                    <button
                        onClick={onBack}
                        className="text-muted hover:text-foreground transition-colors"
                    >
                        ← Back to Hub
                    </button>
                </div>
                <SubjectSelector
                    onSelectionChange={setSelectedSubjects}
                    onContinue={handleContinueToStudy}
                />

                {/* Upgrade Modal */}
                <UpgradeModal
                    isOpen={upgradeModalOpen}
                    onClose={() => setUpgradeModalOpen(false)}
                    limitType="flashcard"
                />
            </div>
        );
    }

    // Phase 2: Study Mode
    return (
        <div className="max-w-2xl mx-auto space-y-8">
            {/* Header with Progress */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-foreground">Flashcards</h2>
                    <p className="text-muted mt-1">
                        {selectedSubjects.length} subject{selectedSubjects.length !== 1 ? "s" : ""}
                    </p>
                </div>
                <button
                    onClick={() => setPhase("subject-select")}
                    className="text-muted hover:text-foreground transition-colors"
                >
                    ← Change Subjects
                </button>
            </div>

            {/* Progress Bar */}
            <div className="space-y-2">
                <div className="flex justify-between text-sm text-muted">
                    <span>Card {currentCardIndex + 1} of {allFlashcards.length}</span>
                    <span>{currentCardIndex} reviewed</span>
                </div>
                <div className="w-full h-2 bg-card-border rounded-full overflow-hidden">
                    <div
                        className="h-full bg-fire-red transition-all duration-300"
                        style={{ width: `${((currentCardIndex + 1) / allFlashcards.length) * 100}%` }}
                    />
                </div>
            </div>

            {/* Flashcard */}
            <div
                onClick={handleFlip}
                className="relative cursor-pointer perspective-1000"
                style={{ perspective: "1000px" }}
            >
                <div
                    className="relative w-full min-h-[300px] transition-transform duration-500 transform-style-3d"
                    style={{
                        transformStyle: "preserve-3d",
                        transform: isFlipped ? "rotateY(180deg)" : "rotateY(0)",
                    }}
                >
                    {/* Front - Question */}
                    <div
                        className="absolute w-full h-full backface-hidden"
                        style={{ backfaceVisibility: "hidden" }}
                    >
                        <div className="card p-8 h-full flex flex-col items-center justify-center text-center border-2 border-fire-red min-h-[300px]">
                            <p className="text-sm text-muted mb-4 uppercase tracking-wider">
                                Question
                            </p>
                            <h3 className="text-lg md:text-xl font-medium text-foreground leading-relaxed">
                                {currentCard?.front_content}
                            </h3>
                            <p className="text-muted text-sm mt-8">Tap to reveal answer</p>
                        </div>
                    </div>

                    {/* Back - Answer */}
                    <div
                        className="absolute w-full h-full backface-hidden"
                        style={{
                            backfaceVisibility: "hidden",
                            transform: "rotateY(180deg)",
                        }}
                    >
                        <div className="card p-8 h-full flex flex-col items-center justify-center text-center border-2 border-caution-yellow bg-card min-h-[300px]">
                            <p className="text-sm text-caution-yellow mb-4 uppercase tracking-wider">
                                Answer
                            </p>
                            <p className="text-lg md:text-xl text-foreground leading-relaxed whitespace-pre-line">
                                {currentCard?.back_content}
                            </p>
                            <p className="text-muted text-sm mt-6">Tap to flip back</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex justify-between items-center">
                <button
                    onClick={handlePrevious}
                    disabled={currentCardIndex === 0}
                    className="px-6 py-3 rounded-lg border border-card-border text-muted hover:text-foreground hover:border-ember-orange transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                >
                    ← Previous
                </button>

                <div className="text-center">
                    <p className="text-sm text-muted">Card {currentCardIndex + 1}</p>
                </div>

                <button
                    onClick={handleNext}
                    disabled={currentCardIndex >= allFlashcards.length - 1}
                    className="btn-primary px-6 py-3 rounded-lg fire-glow hover:fire-glow-hover disabled:opacity-50"
                >
                    Next Card →
                </button>
            </div>

            {/* Hint and Feedback */}
            <div className="flex justify-between items-center text-sm text-muted">
                <p>Click card to flip • Use buttons to navigate</p>
                <button
                    onClick={() => setFeedbackModalOpen(true)}
                    className="hover:text-ember-orange transition-colors"
                >
                    Feedback
                </button>
            </div>

            {/* Feedback Modal */}
            <FeedbackModal
                isOpen={feedbackModalOpen}
                studyMode="flashcards"
                onClose={() => setFeedbackModalOpen(false)}
                onSubmit={handleSubmitFeedback}
            />
        </div>
    );
}
