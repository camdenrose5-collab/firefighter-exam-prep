"use client";

import { useState } from "react";

interface WelcomeModalProps {
    isOpen: boolean;
    onEmailSubmit: (email: string) => void;
}

export default function WelcomeModal({ isOpen, onEmailSubmit }: WelcomeModalProps) {
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (!email || !email.includes("@")) {
            setError("Please enter a valid email address");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch("http://localhost:8000/api/leads", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Something went wrong");
            }

            // Save to localStorage to prevent showing again
            localStorage.setItem("email_submitted", email);
            onEmailSubmit(email);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="card w-full max-w-lg p-8 relative animate-in fade-in zoom-in duration-300">
                {/* Hero Icon */}
                <div className="text-center mb-6">
                    <div className="w-20 h-20 mx-auto rounded-2xl gradient-fire flex items-center justify-center text-4xl mb-4 fire-glow">
                        🔥
                    </div>
                    <h2 className="text-3xl font-bold text-foreground mb-2">
                        Welcome to Captain&apos;s Academy
                    </h2>
                    <p className="text-muted text-lg">
                        Your AI-powered firefighter exam prep assistant
                    </p>
                </div>

                {/* Value Props */}
                <div className="grid grid-cols-3 gap-3 mb-8">
                    <div className="text-center p-3 bg-card-bg rounded-lg border border-card-border">
                        <div className="text-2xl mb-1">📝</div>
                        <p className="text-xs text-muted font-medium">Quizzes</p>
                    </div>
                    <div className="text-center p-3 bg-card-bg rounded-lg border border-card-border">
                        <div className="text-2xl mb-1">📇</div>
                        <p className="text-xs text-muted font-medium">Flashcards</p>
                    </div>
                    <div className="text-center p-3 bg-card-bg rounded-lg border border-card-border">
                        <div className="text-2xl mb-1">💬</div>
                        <p className="text-xs text-muted font-medium">AI Tutor</p>
                    </div>
                </div>

                {/* Email Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2 text-foreground">
                            Enter your email to get started
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="firefighter@example.com"
                            className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:border-fire-red focus:ring-1 focus:ring-fire-red outline-none transition-colors text-foreground placeholder:text-muted"
                        />
                    </div>

                    {error && (
                        <div className="p-3 bg-fire-red/10 border border-fire-red/30 rounded-lg text-fire-red text-sm">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full btn-primary fire-glow hover:fire-glow-hover py-4 text-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <span className="flex items-center justify-center gap-2">
                                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                Starting...
                            </span>
                        ) : (
                            <span className="flex items-center justify-center gap-2">
                                🚒 Try it Free
                            </span>
                        )}
                    </button>
                </form>

                {/* Fine print */}
                <p className="text-center text-xs text-muted mt-4">
                    Free to try • Sign up later to save progress
                </p>
            </div>
        </div>
    );
}
