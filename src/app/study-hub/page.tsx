"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Target, BookOpen, ArrowRight, FileText, Clock, Zap } from "lucide-react";
import QuizContainer from "@/components/QuizContainer";
import FlashcardsContainer from "@/components/FlashcardsContainer";
import AuthModal from "@/components/AuthModal";
import AppShell from "@/components/AppShell";
import { useUserStore } from "@/lib/store";

type StudyMode = "quiz" | "flashcards" | null;

function StudyHubContent() {
    const searchParams = useSearchParams();
    const [activeMode, setActiveMode] = useState<StudyMode>(null);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const { isAuthenticated, email, login } = useUserStore();

    useEffect(() => {
        const mode = searchParams.get("mode");
        if (mode === "quiz" || mode === "flashcards") {
            setActiveMode(mode);
        }
    }, [searchParams]);

    const handleAuthenticated = (token: string, userEmail: string) => {
        login(userEmail, token);
        setShowAuthModal(false);
    };

    const studyModes = [
        {
            id: "quiz" as const,
            title: "Practice Quizzes",
            description: "Test your knowledge with multiple-choice questions from real fire service manuals and exam materials.",
            icon: Target,
            color: "text-blue-500",
            bgColor: "bg-blue-500/10",
            borderColor: "hover:border-blue-500/50",
            features: ["5-100 questions per session", "Instant feedback", "Track weak areas"],
        },
        {
            id: "flashcards" as const,
            title: "Flashcards",
            description: "Master key terminology and concepts using active recall. Study fire behavior, hydraulics, and more.",
            icon: BookOpen,
            color: "text-green-500",
            bgColor: "bg-green-500/10",
            borderColor: "hover:border-green-500/50",
            features: ["Spaced repetition", "Term definitions", "Quick review"],
        },
    ];

    const stats = [
        { label: "Study Materials", value: "50+", icon: FileText },
        { label: "Practice Questions", value: "1,000+", icon: Target },
        { label: "Available 24/7", value: "Always", icon: Clock },
    ];

    return (
        <AppShell>
            <div className="p-6 lg:p-8 max-w-6xl mx-auto">
                {/* Sign-up Banner for non-authenticated users */}
                {!isAuthenticated && (
                    <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-fire-red/10 to-ember-orange/10 border border-fire-red/20 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Zap className="w-5 h-5 text-fire-red" />
                            <p className="text-sm text-foreground">
                                Sign up to save your progress and track your improvement
                            </p>
                        </div>
                        <button
                            onClick={() => setShowAuthModal(true)}
                            className="px-4 py-2 bg-fire-red text-white rounded-lg text-sm font-medium hover:bg-ember-orange transition-colors"
                        >
                            Sign Up Free
                        </button>
                    </div>
                )}

                {/* Hub View - Mode Selection */}
                {!activeMode && (
                    <div className="space-y-8">
                        {/* Page Header */}
                        <div>
                            <h1 className="text-2xl font-bold text-foreground">Study Hub</h1>
                            <p className="text-muted mt-1">
                                Choose your study mode. All content sourced from official fire service materials.
                            </p>
                        </div>

                        {/* Study Mode Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {studyModes.map((mode) => {
                                const Icon = mode.icon;
                                return (
                                    <button
                                        key={mode.id}
                                        onClick={() => setActiveMode(mode.id)}
                                        className={`group p-6 card text-left transition-all ${mode.borderColor}`}
                                    >
                                        <div className={`w-12 h-12 rounded-xl ${mode.bgColor} flex items-center justify-center mb-4`}>
                                            <Icon className={`w-6 h-6 ${mode.color}`} />
                                        </div>
                                        <h3 className="text-xl font-semibold text-foreground mb-2">
                                            {mode.title}
                                        </h3>
                                        <p className="text-muted text-sm leading-relaxed mb-4">
                                            {mode.description}
                                        </p>
                                        <ul className="space-y-1 mb-4">
                                            {mode.features.map((feature) => (
                                                <li key={feature} className="text-xs text-muted flex items-center gap-2">
                                                    <span className={`w-1.5 h-1.5 rounded-full ${mode.color.replace("text-", "bg-")}`} />
                                                    {feature}
                                                </li>
                                            ))}
                                        </ul>
                                        <div className={`flex items-center gap-1 text-sm font-medium ${mode.color} group-hover:gap-2 transition-all`}>
                                            Start Studying <ArrowRight className="w-4 h-4" />
                                        </div>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-4">
                            {stats.map((stat) => {
                                const Icon = stat.icon;
                                return (
                                    <div key={stat.label} className="card p-4 text-center">
                                        <Icon className="w-5 h-5 text-muted mx-auto mb-2" />
                                        <p className="text-xl font-bold text-foreground">{stat.value}</p>
                                        <p className="text-xs text-muted">{stat.label}</p>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Info Card */}
                        <div className="card p-5 border-l-4 border-l-fire-red">
                            <h3 className="font-semibold text-foreground mb-1">Built for Firefighter Candidates</h3>
                            <p className="text-sm text-muted">
                                This platform was developed by a firefighter to help candidates prepare for written exams.
                                Content is sourced from IFSTA manuals, fire service textbooks, and department-specific materials.
                            </p>
                        </div>
                    </div>
                )}

                {/* Mode-Specific Views */}
                {activeMode === "quiz" && (
                    <QuizContainer onBack={() => setActiveMode(null)} />
                )}

                {activeMode === "flashcards" && (
                    <FlashcardsContainer onBack={() => setActiveMode(null)} />
                )}

                {/* Auth Modal */}
                <AuthModal
                    isOpen={showAuthModal}
                    onClose={() => setShowAuthModal(false)}
                    onAuthenticated={handleAuthenticated}
                />
            </div>
        </AppShell>
    );
}

export default function StudyHub() {
    return (
        <Suspense fallback={
            <AppShell>
                <div className="p-6 lg:p-8 max-w-6xl mx-auto">
                    <div className="animate-pulse space-y-4">
                        <div className="h-8 bg-card-border rounded w-1/4"></div>
                        <div className="h-4 bg-card-border rounded w-1/2"></div>
                        <div className="grid grid-cols-2 gap-6 mt-8">
                            <div className="h-48 bg-card-border rounded-lg"></div>
                            <div className="h-48 bg-card-border rounded-lg"></div>
                        </div>
                    </div>
                </div>
            </AppShell>
        }>
            <StudyHubContent />
        </Suspense>
    );
}
