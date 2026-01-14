"use client";

import { useState } from "react";

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAuthenticated: (token: string, email: string) => void;
}

export default function AuthModal({ isOpen, onClose, onAuthenticated }: AuthModalProps) {
    const [mode, setMode] = useState<"login" | "register">("login");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (mode === "register" && password !== confirmPassword) {
            setError("Passwords do not match");
            return;
        }

        if (password.length < 6) {
            setError("Password must be at least 6 characters");
            return;
        }

        setLoading(true);

        try {
            const endpoint = mode === "login"
                ? "http://localhost:8000/api/auth/login"
                : "http://localhost:8000/api/auth/register";

            const response = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Authentication failed");
            }

            // Save token to localStorage
            localStorage.setItem("auth_token", data.token);
            localStorage.setItem("user_email", data.email);
            localStorage.setItem("user_id", data.user_id);

            onAuthenticated(data.token, data.email);
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="card w-full max-w-md p-8 relative animate-in fade-in zoom-in duration-300">
                {/* Close button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-muted hover:text-foreground transition-colors"
                >
                    ✕
                </button>

                {/* Header */}
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-fire-red mb-2">
                        {mode === "login" ? "🔥 Welcome Back" : "🚒 Join the Crew"}
                    </h2>
                    <p className="text-muted">
                        {mode === "login"
                            ? "Sign in to access your study deck"
                            : "Create an account to save your progress"
                        }
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:border-fire-red focus:ring-1 focus:ring-fire-red outline-none transition-colors"
                            placeholder="firefighter@example.com"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:border-fire-red focus:ring-1 focus:ring-fire-red outline-none transition-colors"
                            placeholder="••••••••"
                        />
                    </div>

                    {mode === "register" && (
                        <div>
                            <label className="block text-sm font-medium mb-2">Confirm Password</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                className="w-full px-4 py-3 bg-card-bg border border-card-border rounded-lg focus:border-fire-red focus:ring-1 focus:ring-fire-red outline-none transition-colors"
                                placeholder="••••••••"
                            />
                        </div>
                    )}

                    {error && (
                        <div className="p-3 bg-fire-red/10 border border-fire-red/30 rounded-lg text-fire-red text-sm">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full btn-primary fire-glow hover:fire-glow-hover disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <span className="flex items-center justify-center gap-2">
                                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                Processing...
                            </span>
                        ) : (
                            mode === "login" ? "Sign In" : "Create Account"
                        )}
                    </button>
                </form>

                {/* Toggle mode */}
                <div className="mt-6 text-center text-sm">
                    <span className="text-muted">
                        {mode === "login" ? "Don't have an account?" : "Already have an account?"}
                    </span>
                    <button
                        onClick={() => {
                            setMode(mode === "login" ? "register" : "login");
                            setError("");
                        }}
                        className="ml-2 text-ember-orange hover:text-fire-red transition-colors font-medium"
                    >
                        {mode === "login" ? "Sign up" : "Sign in"}
                    </button>
                </div>
            </div>
        </div>
    );
}
