"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, ArrowRight, Loader2 } from "lucide-react";
import preloadedQuestions from "@/data/questions.json";

// Raw question format from JSON (options is stringified)
interface RawQuestion {
    id: string;
    question: string;
    options: string; // Stringified JSON array
    correct_answer: string; // The actual answer text
    subject?: string;
}

// Processed question format for component use
interface Question {
    id: string;
    question: string;
    options: string[];
    correctAnswer: number;
    category?: string;
}

interface DiagnosticQuizProps {
    questionCount?: number;
    onComplete: (results: { correct: number; total: number; percentage: number }) => void;
}

export default function DiagnosticQuiz({ questionCount = 3, onComplete }: DiagnosticQuizProps) {
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
    const [showResult, setShowResult] = useState(false);
    const [correctCount, setCorrectCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);

    // Load random questions on mount
    useEffect(() => {
        const rawQuestions = preloadedQuestions as RawQuestion[];
        const shuffled = [...rawQuestions].sort(() => Math.random() - 0.5);
        const selected = shuffled.slice(0, questionCount);

        // Transform raw questions to processed format
        const processed = selected.map((q) => {
            // Parse the stringified options array
            let parsedOptions: string[] = [];
            try {
                parsedOptions = JSON.parse(q.options);
            } catch {
                console.error("Failed to parse options for question:", q.id);
                parsedOptions = [];
            }

            // Find the correct answer index by matching the answer text
            const correctIndex = parsedOptions.findIndex(
                (opt) => opt.trim() === q.correct_answer.trim()
            );

            return {
                id: q.id,
                question: q.question,
                options: parsedOptions,
                correctAnswer: correctIndex >= 0 ? correctIndex : 0,
                category: q.subject,
            };
        });

        setQuestions(processed);
        setIsLoading(false);
    }, [questionCount]);


    const currentQuestion = questions[currentIndex];
    const isLastQuestion = currentIndex === questions.length - 1;
    const progress = ((currentIndex + 1) / questions.length) * 100;

    // Endowed progress: Show as part of larger 30-question journey
    const endowedProgress = Math.round(((10 + currentIndex + 1) / 30) * 100);

    const handleSelectAnswer = (answerIndex: number) => {
        if (showResult) return;
        setSelectedAnswer(answerIndex);
    };

    const handleSubmitAnswer = () => {
        if (selectedAnswer === null) return;

        const isCorrect = selectedAnswer === currentQuestion.correctAnswer;
        if (isCorrect) {
            setCorrectCount(prev => prev + 1);
        }
        setShowResult(true);
    };

    const handleNextQuestion = () => {
        if (isLastQuestion) {
            const finalCorrect = correctCount + (selectedAnswer === currentQuestion.correctAnswer ? 0 : 0);
            const percentage = Math.round((finalCorrect / questions.length) * 100);
            onComplete({ correct: finalCorrect, total: questions.length, percentage });
        } else {
            setCurrentIndex(prev => prev + 1);
            setSelectedAnswer(null);
            setShowResult(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-fire-red" />
            </div>
        );
    }

    if (!currentQuestion) {
        return null;
    }

    return (
        <div className="w-full max-w-2xl mx-auto">
            {/* Progress Bar with Endowed Progress Framing */}
            <div className="mb-6">
                <div className="flex items-center justify-between text-sm text-muted mb-2">
                    <span>Question {currentIndex + 1} of {questions.length}</span>
                    <span className="text-fire-red font-medium">{endowedProgress}% of Mastery Diagnostic</span>
                </div>
                <div className="h-2 bg-card-border rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-gradient-to-r from-fire-red to-ember-orange"
                        initial={{ width: `${((10 + currentIndex) / 30) * 100}%` }}
                        animate={{ width: `${endowedProgress}%` }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                    />
                </div>
                {/* Level markers */}
                <div className="flex justify-between mt-1">
                    {[1, 2, 3, 4, 5, 6].map((level) => (
                        <div
                            key={level}
                            className={`w-2 h-2 rounded-full ${(10 + currentIndex + 1) >= level * 5
                                ? "bg-fire-red"
                                : "bg-card-border"
                                }`}
                        />
                    ))}
                </div>
            </div>

            {/* Question Card */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentIndex}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                    className="card p-6"
                >
                    <h3 className="text-lg font-medium text-foreground mb-6 leading-relaxed">
                        {currentQuestion.question}
                    </h3>

                    {/* Answer Options */}
                    <div className="space-y-3">
                        {currentQuestion.options.map((option, index) => {
                            const isSelected = selectedAnswer === index;
                            const isCorrect = index === currentQuestion.correctAnswer;
                            const showCorrect = showResult && isCorrect;
                            const showIncorrect = showResult && isSelected && !isCorrect;

                            return (
                                <button
                                    key={index}
                                    onClick={() => handleSelectAnswer(index)}
                                    disabled={showResult}
                                    className={`w-full p-4 rounded-lg border-2 text-left transition-all ${showCorrect
                                        ? "border-green-500 bg-green-500/10"
                                        : showIncorrect
                                            ? "border-red-500 bg-red-500/10"
                                            : isSelected
                                                ? "border-fire-red bg-fire-red/10"
                                                : "border-card-border hover:border-fire-red/50"
                                        }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${showCorrect
                                            ? "bg-green-500 text-white"
                                            : showIncorrect
                                                ? "bg-red-500 text-white"
                                                : isSelected
                                                    ? "bg-fire-red text-white"
                                                    : "bg-card-border text-muted"
                                            }`}>
                                            {showCorrect ? (
                                                <CheckCircle2 className="w-4 h-4" />
                                            ) : showIncorrect ? (
                                                <XCircle className="w-4 h-4" />
                                            ) : (
                                                String.fromCharCode(65 + index)
                                            )}
                                        </span>
                                        <span className={`${showCorrect ? "text-green-500" : showIncorrect ? "text-red-500" : "text-foreground"
                                            }`}>
                                            {option}
                                        </span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    {/* Action Button */}
                    <div className="mt-6">
                        {!showResult ? (
                            <button
                                onClick={handleSubmitAnswer}
                                disabled={selectedAnswer === null}
                                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${selectedAnswer === null
                                    ? "bg-card-border text-muted cursor-not-allowed"
                                    : "bg-fire-red text-white hover:bg-ember-orange"
                                    }`}
                            >
                                Check Answer
                            </button>
                        ) : (
                            <button
                                onClick={handleNextQuestion}
                                className="w-full py-3 px-4 rounded-lg font-medium bg-fire-red text-white hover:bg-ember-orange transition-colors flex items-center justify-center gap-2"
                            >
                                {isLastQuestion ? "See Your Results" : "Next Question"}
                                <ArrowRight className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                </motion.div>
            </AnimatePresence>
        </div>
    );
}
