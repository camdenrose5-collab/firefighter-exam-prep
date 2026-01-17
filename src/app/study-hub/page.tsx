"use client";

import { useState, useEffect } from "react";
import QuizContainer from "@/components/QuizContainer";
import ExplainContainer from "@/components/ExplainContainer";
import FlashcardsContainer from "@/components/FlashcardsContainer";
import AuthModal from "@/components/AuthModal";

type StudyMode = "quiz" | "flashcards" | "explain" | null;

export default function StudyHub() {
    const [activeMode, setActiveMode] = useState<StudyMode>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [showAuthModal, setShowAuthModal] = useState(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);

    useEffect(() => {
        // Check auth status on mount
        const token = localStorage.getItem("auth_token");
        const email = localStorage.getItem("user_email");
        if (token && email) {
            setIsAuthenticated(true);
            setUserEmail(email);
        }
    }, []);

    const handleAuthenticated = (token: string, email: string) => {
        setIsAuthenticated(true);
        setUserEmail(email);
        setShowAuthModal(false);
    };

    const handleLogout = () => {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("user_email");
        localStorage.removeItem("user_id");
        setIsAuthenticated(false);
        setUserEmail(null);
    };

    return (
        <div className="min-h-screen bg-background">
            {/* Sign-up Banner for non-authenticated users */}
            {!isAuthenticated && (
                <div className="bg-gradient-to-r from-fire-red/10 to-ember-orange/10 border-b border-ember-orange/20">
                    <div className="max-w-7xl mx-auto px-6 py-2 flex items-center justify-between">
                        <p className="text-sm text-ember-orange">
                            📌 Sign up to save your progress and build your study deck
                        </p>
                        <button
                            onClick={() => setShowAuthModal(true)}
                            className="px-4 py-1.5 bg-ember-orange/20 hover:bg-ember-orange/30 text-ember-orange rounded-lg text-sm font-medium transition-colors"
                        >
                            Sign Up Free
                        </button>
                    </div>
                </div>
            )}

            {/* Header */}
            <header className="border-b border-card-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg gradient-fire flex items-center justify-center">
                            <span className="text-2xl">🔥</span>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-foreground">Captain&apos;s Academy</h1>
                            <p className="text-xs text-muted">Study Hub</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        {isAuthenticated ? (
                            <>
                                <span className="text-sm text-muted">{userEmail}</span>
                                <button
                                    onClick={handleLogout}
                                    className="text-sm text-muted hover:text-foreground transition-colors"
                                >
                                    Logout
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setShowAuthModal(true)}
                                className="text-sm text-ember-orange hover:text-fire-red transition-colors font-medium"
                            >
                                Sign In
                            </button>
                        )}
                        <div className="flex items-center gap-2 text-sm text-muted">
                            <span className="w-2 h-2 rounded-full bg-green-500"></span>
                            Brain Ready
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Hub View - The 3 Core CTAs */}
                {!activeMode && (
                    <div className="space-y-8">
                        {/* Welcome Section */}
                        <div className="text-center mb-12">
                            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
                                🎯 Station 1: Study Mentor
                            </h2>
                            <p className="text-lg text-muted max-w-2xl mx-auto">
                                Choose your training mode. All content is powered by the Fire Captain&apos;s Brain —
                                built from real fire service manuals and exam materials.
                            </p>
                        </div>

                        {/* CTA Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Quiz Me */}
                            <button
                                onClick={() => setActiveMode("quiz")}
                                className="group p-8 card border-2 border-transparent hover:border-fire-red transition-all duration-300 hover:fire-glow text-left"
                            >
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center text-3xl mb-6 group-hover:scale-110 transition-transform">
                                    📝
                                </div>
                                <h3 className="text-2xl font-bold text-foreground mb-2">Quiz Me</h3>
                                <p className="text-muted leading-relaxed">
                                    5-100 multiple-choice questions from the manuals. Test your knowledge with
                                    immediate feedback from the Captain.
                                </p>
                                <div className="mt-6 flex items-center gap-2 text-fire-red font-semibold">
                                    Start Quiz <span className="group-hover:translate-x-1 transition-transform">→</span>
                                </div>
                            </button>

                            {/* Flashcards */}
                            <button
                                onClick={() => setActiveMode("flashcards")}
                                className="group p-8 card border-2 border-transparent hover:border-ember-orange transition-all duration-300 hover:fire-glow text-left"
                            >
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-700 flex items-center justify-center text-3xl mb-6 group-hover:scale-110 transition-transform">
                                    📇
                                </div>
                                <h3 className="text-2xl font-bold text-foreground mb-2">Flashcards</h3>
                                <p className="text-muted leading-relaxed">
                                    Master fire service terms with active recall. Flip through key definitions
                                    from hydraulics, fire behavior, and more.
                                </p>
                                <div className="mt-6 flex items-center gap-2 text-ember-orange font-semibold">
                                    Study Cards <span className="group-hover:translate-x-1 transition-transform">→</span>
                                </div>
                            </button>

                            {/* Explain */}
                            <button
                                onClick={() => setActiveMode("explain")}
                                className="group p-8 card border-2 border-transparent hover:border-green-500 transition-all duration-300 hover:fire-glow text-left"
                            >
                                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-green-600 to-green-800 flex items-center justify-center text-3xl mb-6 group-hover:scale-110 transition-transform">
                                    💬
                                </div>
                                <h3 className="text-2xl font-bold text-foreground mb-2">Explain</h3>
                                <p className="text-muted leading-relaxed">
                                    Ask questions or get help with tough concepts. The Captain uses firehouse
                                    analogies to make math and physics click.
                                </p>
                                <div className="mt-6 flex items-center gap-2 text-green-500 font-semibold">
                                    Ask Captain <span className="group-hover:translate-x-1 transition-transform">→</span>
                                </div>
                            </button>
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-3 gap-4 mt-12 max-w-xl mx-auto">
                            <div className="text-center p-4 card">
                                <p className="text-2xl font-bold text-fire-red">50+</p>
                                <p className="text-xs text-muted uppercase tracking-wider">PDFs Loaded</p>
                            </div>
                            <div className="text-center p-4 card">
                                <p className="text-2xl font-bold text-ember-orange">∞</p>
                                <p className="text-xs text-muted uppercase tracking-wider">Questions</p>
                            </div>
                            <div className="text-center p-4 card">
                                <p className="text-2xl font-bold text-green-500">24/7</p>
                                <p className="text-xs text-muted uppercase tracking-wider">Available</p>
                            </div>
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

                {activeMode === "explain" && (
                    <ExplainContainer onBack={() => setActiveMode(null)} />
                )}
            </div>

            {/* Footer */}
            <footer className="border-t border-card-border mt-16 py-8">
                <div className="max-w-7xl mx-auto px-6 text-center">
                    {/* Built by a Firefighter message */}
                    <div className="mb-4 p-4 rounded-lg bg-gradient-to-r from-fire-red/5 to-ember-orange/5 border border-ember-orange/20 max-w-2xl mx-auto">
                        <p className="text-foreground font-medium mb-2">
                            👨‍🚒 Built by a firefighter, for future firefighters
                        </p>
                        <p className="text-sm text-muted">
                            This platform was created by someone who&apos;s been in your boots. Your feedback helps make it better for the next candidate.
                            <span className="text-ember-orange font-medium"> Hit the feedback button in any study mode to share your thoughts!</span>
                        </p>
                    </div>
                    <p className="text-sm text-muted">🔥 Captain&apos;s Academy — Your AI Fire Instructor</p>
                    <p className="mt-1 text-xs text-muted">Powered by Vertex AI + Discovery Engine</p>
                </div>
            </footer>

            {/* Auth Modal */}
            <AuthModal
                isOpen={showAuthModal}
                onClose={() => setShowAuthModal(false)}
                onAuthenticated={handleAuthenticated}
            />
        </div>
    );
}
