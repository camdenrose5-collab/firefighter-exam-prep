"use client";

import { useState } from "react";

export interface QuizQuestion {
    id: string;
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
}

interface QuizViewProps {
    questions: QuizQuestion[];
    onReportQuestion: (questionId: string) => void;
    onComplete: (results: { correct: number; total: number }) => void;
    onQuestionChange?: (index: number) => void;
    onSaveToStudyDeck?: (questionId: string) => Promise<boolean>;
}

export default function QuizView({
    questions,
    onReportQuestion,
    onComplete,
    onQuestionChange,
    onSaveToStudyDeck,
}: QuizViewProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedOption, setSelectedOption] = useState<string | null>(null);
    const [isAnswered, setIsAnswered] = useState(false);
    const [score, setScore] = useState(0);
    const [savedQuestions, setSavedQuestions] = useState<Set<string>>(new Set());
    const [savingQuestion, setSavingQuestion] = useState(false);

    const currentQuestion = questions[currentIndex];
    const progress = ((currentIndex + 1) / questions.length) * 100;

    const handleOptionSelect = (option: string) => {
        if (isAnswered) return;

        setSelectedOption(option);
        setIsAnswered(true);

        if (option === currentQuestion.correct_answer) {
            setScore((prev) => prev + 1);
        }
    };

    const handleNext = () => {
        if (currentIndex < questions.length - 1) {
            const newIndex = currentIndex + 1;
            setCurrentIndex(newIndex);
            setSelectedOption(null);
            setIsAnswered(false);
            onQuestionChange?.(newIndex);
        } else {
            onComplete({ correct: score, total: questions.length });
        }
    };

    // Helper to determine option style
    const getOptionStyle = (option: string) => {
        if (!isAnswered) {
            if (selectedOption === option) return "border-fire-red bg-fire-red/10 text-foreground"; // Selected but not submitted? No, we submit immediately on select for this design or wait? 
            // Design plan says: "Answer Selection — Visual feedback for selected/correct/incorrect states"
            // Let's assume immediate feedback style like many quiz apps.
            return "border-card-border hover:border-ember-orange hover:bg-card-border/50";
        }

        if (option === currentQuestion.correct_answer) {
            return "border-green-500 bg-green-500/10 text-green-400 font-medium";
        }

        if (selectedOption === option && option !== currentQuestion.correct_answer) {
            return "border-fire-red bg-fire-red/10 text-fire-red";
        }

        return "border-card-border opacity-50";
    };

    if (!currentQuestion) return <div>Loading quiz...</div>;

    return (
        <div className="max-w-3xl mx-auto space-y-8">
            {/* Progress Bar */}
            <div className="w-full bg-card-border rounded-full h-2.5 overflow-hidden">
                <div
                    className="gradient-fire h-2.5 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                />
            </div>

            <div className="flex justify-between items-center text-sm text-muted">
                <span>Question {currentIndex + 1} of {questions.length}</span>
                <button
                    onClick={() => onReportQuestion(currentQuestion.id)}
                    className="text-muted hover:text-caution-yellow transition-colors flex items-center gap-1.5"
                >
                    <span>⚠️</span> Report Question
                </button>
            </div>

            {/* Question Card */}
            <div className="card p-6 md:p-8 space-y-8">
                <h2 className="text-xl md:text-2xl font-bold leading-relaxed text-foreground">
                    {currentQuestion.question}
                </h2>

                {/* Options */}
                <div className="space-y-3">
                    {currentQuestion.options.map((option, idx) => (
                        <button
                            key={idx}
                            onClick={() => handleOptionSelect(option)}
                            disabled={isAnswered}
                            className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 flex items-start gap-3 group ${getOptionStyle(option)}`}
                        >
                            <span className="mt-0.5 flex-shrink-0 w-6 h-6 rounded-full border border-current flex items-center justify-center text-xs opacity-70">
                                {String.fromCharCode(65 + idx)}
                            </span>
                            <span className="leading-relaxed">{option}</span>
                        </button>
                    ))}
                </div>

                {/* Explanation / Next Button Area */}
                <div className={`transition-all duration-500 overflow-hidden ${isAnswered ? 'max-h-[800px] opacity-100' : 'max-h-0 opacity-0'}`}>
                    {isAnswered && (
                        <div className="space-y-6 pt-6 border-t border-card-border animate-in fade-in slide-in-from-top-4 duration-300">

                            {/* Fire Captain Feedback */}
                            <div className="bg-card-bg/50 border-l-4 border-l-ember-orange p-4 rounded-r-lg">
                                <h3 className="font-bold text-lg mb-2 flex items-center gap-2 text-ember-orange">
                                    <span>👨‍🚒</span> Captain&apos;s Feedback
                                </h3>
                                <p className="text-foreground/90 leading-relaxed">
                                    {currentQuestion.explanation}
                                </p>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex justify-between items-center">
                                {/* Save to Study Deck */}
                                {onSaveToStudyDeck && (
                                    <button
                                        onClick={async () => {
                                            if (savedQuestions.has(currentQuestion.id)) return;
                                            setSavingQuestion(true);
                                            const success = await onSaveToStudyDeck(currentQuestion.id);
                                            if (success) {
                                                setSavedQuestions(prev => new Set(prev).add(currentQuestion.id));
                                            }
                                            setSavingQuestion(false);
                                        }}
                                        disabled={savingQuestion || savedQuestions.has(currentQuestion.id)}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${savedQuestions.has(currentQuestion.id)
                                                ? "border-green-500/50 text-green-400 bg-green-500/10"
                                                : "border-card-border hover:border-ember-orange hover:text-ember-orange"
                                            }`}
                                    >
                                        {savedQuestions.has(currentQuestion.id) ? (
                                            <><span>✓</span> Saved to Deck</>
                                        ) : savingQuestion ? (
                                            <><span className="animate-spin">⏳</span> Saving...</>
                                        ) : (
                                            <><span>📚</span> Save to Study Deck</>
                                        )}
                                    </button>
                                )}

                                {/* Next Button */}
                                <button
                                    onClick={handleNext}
                                    className="btn-primary flex items-center gap-2 fire-glow hover:fire-glow-hover ml-auto"
                                >
                                    {currentIndex === questions.length - 1 ? "Finish Quiz" : "Next Question"} <span>→</span>
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
