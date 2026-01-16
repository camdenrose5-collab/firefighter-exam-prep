"use client";

import { useState, useEffect } from "react";
import SubjectSelector from "./SubjectSelector";
import FeedbackModal from "./FeedbackModal";
import { apiUrl } from "@/lib/api";

interface Flashcard {
    id?: string;
    front_content: string;
    back_content: string;
    card_type?: string;
    hint?: string | null;
    source: string | null;
}

interface FlashcardsContainerProps {
    onBack: () => void;
}

const SUBJECT_LABELS: Record<string, string> = {
    "human-relations": "Human Relations",
    "mechanical-aptitude": "Mechanical Aptitude",
    "fire-terms": "Fire Terms",
    "math": "Math (Mental)",
};

export default function FlashcardsContainer({ onBack }: FlashcardsContainerProps) {
    const [phase, setPhase] = useState<"subject-select" | "study">("subject-select");
    const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
    const [currentCard, setCurrentCard] = useState<Flashcard | null>(null);
    const [isFlipped, setIsFlipped] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [cardsReviewed, setCardsReviewed] = useState(0);
    const [cardHistory, setCardHistory] = useState<Flashcard[]>([]);
    const [totalCards, setTotalCards] = useState(10); // Target number of cards
    const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);

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
        if (selectedSubjects.length > 0) {
            setPhase("study");
            fetchNextCard();
        }
    };

    const fetchNextCard = async () => {
        setIsLoading(true);
        setIsFlipped(false);

        try {
            const response = await fetch(
                apiUrl(`/api/quiz/flashcards?subjects=${selectedSubjects.join(",")}`)
            );
            if (!response.ok) throw new Error("Failed to fetch flashcard");

            const card = await response.json();
            setCurrentCard(card);
            setCardHistory((prev) => [...prev, card]);
        } catch (err) {
            console.error("Flashcard error:", err);
            setCurrentCard({
                front_content: "Connection Error",
                back_content: "Unable to load flashcard. Please check your connection and try again.",
                source: null,
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleFlip = () => {
        setIsFlipped(!isFlipped);
    };

    const handleNext = () => {
        setCardsReviewed((prev) => prev + 1);
        fetchNextCard();
    };

    const handlePrevious = () => {
        if (cardHistory.length > 1) {
            const newHistory = [...cardHistory];
            newHistory.pop();
            const previousCard = newHistory[newHistory.length - 1];
            setCurrentCard(previousCard);
            setCardHistory(newHistory);
            setIsFlipped(false);
        }
    };

    // Phase 1: Subject Selection
    if (phase === "subject-select") {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-foreground">📇 Flashcards</h2>
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
            </div>
        );
    }

    // Phase 2: Study Mode
    return (
        <div className="max-w-2xl mx-auto space-y-8">
            {/* Header with Progress */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-foreground">📇 Flashcards</h2>
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
                    <span>Card {cardsReviewed + 1}</span>
                    <span>{cardsReviewed} reviewed</span>
                </div>
                <div className="w-full h-2 bg-card-border rounded-full overflow-hidden">
                    <div
                        className="h-full bg-fire-red transition-all duration-300"
                        style={{ width: `${Math.min((cardsReviewed / totalCards) * 100, 100)}%` }}
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
                    {/* Front - Term */}
                    <div
                        className="absolute w-full h-full backface-hidden"
                        style={{ backfaceVisibility: "hidden" }}
                    >
                        <div className="card p-8 h-full flex flex-col items-center justify-center text-center border-2 border-fire-red">
                            {isLoading ? (
                                <div className="flex flex-col items-center gap-4">
                                    <span className="text-4xl animate-bounce">🔥</span>
                                    <p className="text-muted">Loading card...</p>
                                </div>
                            ) : (
                                <>
                                    <p className="text-sm text-muted mb-4 uppercase tracking-wider">
                                        Term
                                    </p>
                                    <h3 className="text-2xl md:text-3xl font-bold text-foreground leading-relaxed">
                                        {currentCard?.front_content}
                                    </h3>
                                    <p className="text-muted text-sm mt-8">Tap to reveal definition</p>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Back - Definition */}
                    <div
                        className="absolute w-full h-full backface-hidden"
                        style={{
                            backfaceVisibility: "hidden",
                            transform: "rotateY(180deg)",
                        }}
                    >
                        <div className="card p-8 h-full flex flex-col items-center justify-center text-center border-2 border-caution-yellow bg-card">
                            <p className="text-sm text-caution-yellow mb-4 uppercase tracking-wider">
                                Definition
                            </p>
                            <p className="text-lg md:text-xl text-foreground leading-relaxed">
                                {currentCard?.back_content}
                            </p>
                            {currentCard?.source && (
                                <p className="text-sm text-muted mt-6">
                                    📚 Source: {currentCard.source}
                                </p>
                            )}
                            <p className="text-muted text-sm mt-6">Tap to flip back</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex justify-between items-center">
                <button
                    onClick={handlePrevious}
                    disabled={cardHistory.length <= 1}
                    className="px-6 py-3 rounded-lg border border-card-border text-muted hover:text-foreground hover:border-ember-orange transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                >
                    ← Previous
                </button>

                <div className="text-center">
                    <p className="text-sm text-muted">Card {cardHistory.length}</p>
                </div>

                <button
                    onClick={handleNext}
                    disabled={isLoading}
                    className="btn-primary px-6 py-3 rounded-lg fire-glow hover:fire-glow-hover disabled:opacity-50"
                >
                    Next Card →
                </button>
            </div>

            {/* Hint and Feedback */}
            <div className="flex justify-between items-center text-sm text-muted">
                <p>💡 Click card to flip • Use buttons to navigate</p>
                <button
                    onClick={() => setFeedbackModalOpen(true)}
                    className="hover:text-ember-orange transition-colors flex items-center gap-1.5"
                >
                    <span>💡</span> Feedback
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
