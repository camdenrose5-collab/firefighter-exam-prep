"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
    Flame,
    Shield,
    Target,
    Users,
    BookOpen,
    TrendingUp,
    CheckCircle2,
    Star,
    ArrowRight
} from "lucide-react";
import DiagnosticQuiz from "@/components/DiagnosticQuiz";
import EmailCaptureModal from "@/components/EmailCaptureModal";

export default function LandingPage() {
    const router = useRouter();
    const [showQuiz, setShowQuiz] = useState(false);
    const [showEmailModal, setShowEmailModal] = useState(false);
    const [quizResults, setQuizResults] = useState<{
        correct: number;
        total: number;
        percentage: number;
    } | null>(null);

    const handleQuizComplete = (results: { correct: number; total: number; percentage: number }) => {
        setQuizResults(results);
        setShowEmailModal(true);
    };

    const handleEmailComplete = () => {
        setShowEmailModal(false);
        router.push("/study-hub");
    };

    const stats = [
        { value: "15,952", label: "Practice Questions" },
        { value: "50+", label: "Study Sources" },
        { value: "24/7", label: "Available" },
    ];

    const features = [
        { icon: Target, label: "Real exam questions" },
        { icon: BookOpen, label: "Flashcards & study tools" },
        { icon: TrendingUp, label: "Track your progress" },
        { icon: Users, label: "Join 1,000+ candidates" },
    ];

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-md border-b border-card-border">
                <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-fire-red flex items-center justify-center">
                            <Flame className="w-5 h-5 text-white" />
                        </div>
                        <span className="font-bold text-foreground">Captain&apos;s Academy</span>
                    </div>
                    <button
                        onClick={() => router.push("/study-hub")}
                        className="text-sm text-muted hover:text-foreground transition-colors"
                    >
                        Sign In
                    </button>
                </div>
            </header>

            <main className="pt-16">
                {!showQuiz ? (
                    <>
                        {/* Hero Section */}
                        <section className="px-4 py-16 md:py-24">
                            <div className="max-w-4xl mx-auto text-center">
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.5 }}
                                >
                                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-fire-red/10 border border-fire-red/20 text-sm text-fire-red mb-6">
                                        <Shield className="w-4 h-4" />
                                        Built by a firefighter, for firefighters
                                    </div>

                                    <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
                                        Pass Your Firefighter{" "}
                                        <span className="text-fire-red">Written Exam</span>
                                    </h1>

                                    <p className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-8">
                                        Take a quick 3-question diagnostic to see where you stand.
                                        Then access thousands of practice questions from real exam materials.
                                    </p>

                                    {/* CTA Button */}
                                    <button
                                        onClick={() => setShowQuiz(true)}
                                        className="inline-flex items-center gap-2 px-8 py-4 bg-fire-red text-white font-semibold rounded-xl hover:bg-ember-orange transition-colors text-lg shadow-lg shadow-fire-red/20"
                                    >
                                        <Target className="w-5 h-5" />
                                        Take Free Diagnostic
                                        <ArrowRight className="w-5 h-5" />
                                    </button>

                                    <p className="text-sm text-muted mt-4">
                                        No signup required • 3 questions • 2 minutes
                                    </p>
                                </motion.div>
                            </div>
                        </section>

                        {/* Stats Bar */}
                        <section className="px-4 py-8 bg-card border-y border-card-border">
                            <div className="max-w-4xl mx-auto">
                                <div className="grid grid-cols-3 gap-4">
                                    {stats.map((stat) => (
                                        <div key={stat.label} className="text-center">
                                            <p className="text-2xl md:text-3xl font-bold text-foreground">
                                                {stat.value}
                                            </p>
                                            <p className="text-sm text-muted">{stat.label}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </section>

                        {/* Features Grid */}
                        <section className="px-4 py-16">
                            <div className="max-w-4xl mx-auto">
                                <h2 className="text-2xl md:text-3xl font-bold text-foreground text-center mb-12">
                                    Everything you need to ace your exam
                                </h2>

                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {features.map((feature) => {
                                        const Icon = feature.icon;
                                        return (
                                            <div
                                                key={feature.label}
                                                className="p-4 rounded-xl bg-card border border-card-border text-center"
                                            >
                                                <div className="w-12 h-12 rounded-lg bg-fire-red/10 flex items-center justify-center mx-auto mb-3">
                                                    <Icon className="w-6 h-6 text-fire-red" />
                                                </div>
                                                <p className="text-sm font-medium text-foreground">
                                                    {feature.label}
                                                </p>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </section>

                        {/* Social Proof */}
                        <section className="px-4 py-16 bg-card border-y border-card-border">
                            <div className="max-w-4xl mx-auto text-center">
                                <div className="flex items-center justify-center gap-1 mb-4">
                                    {[1, 2, 3, 4, 5].map((i) => (
                                        <Star key={i} className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                                    ))}
                                </div>
                                <blockquote className="text-lg md:text-xl text-foreground mb-4 italic">
                                    &quot;This platform helped me score in the top 10% on my written exam.
                                    The practice questions were exactly like what I saw on test day.&quot;
                                </blockquote>
                                <p className="text-sm text-muted">
                                    — Recent Firefighter Candidate
                                </p>
                            </div>
                        </section>

                        {/* Final CTA */}
                        <section className="px-4 py-16">
                            <div className="max-w-2xl mx-auto text-center">
                                <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
                                    Ready to see where you stand?
                                </h2>
                                <p className="text-muted mb-8">
                                    Take the free diagnostic and get personalized study recommendations.
                                </p>
                                <button
                                    onClick={() => setShowQuiz(true)}
                                    className="inline-flex items-center gap-2 px-8 py-4 bg-fire-red text-white font-semibold rounded-xl hover:bg-ember-orange transition-colors text-lg"
                                >
                                    Start Diagnostic
                                    <ArrowRight className="w-5 h-5" />
                                </button>
                            </div>
                        </section>
                    </>
                ) : (
                    /* Diagnostic Quiz Section */
                    <section className="px-4 py-12">
                        <div className="max-w-2xl mx-auto">
                            <div className="text-center mb-8">
                                <h2 className="text-2xl font-bold text-foreground mb-2">
                                    Quick Knowledge Check
                                </h2>
                                <p className="text-muted">
                                    Answer 3 questions to see your baseline score
                                </p>
                            </div>

                            <DiagnosticQuiz
                                questionCount={3}
                                onComplete={handleQuizComplete}
                            />

                            <div className="mt-8 text-center">
                                <button
                                    onClick={() => setShowQuiz(false)}
                                    className="text-sm text-muted hover:text-foreground transition-colors"
                                >
                                    ← Back to home
                                </button>
                            </div>
                        </div>
                    </section>
                )}
            </main>

            {/* Footer */}
            <footer className="px-4 py-8 border-t border-card-border">
                <div className="max-w-4xl mx-auto text-center text-sm text-muted">
                    <p>© 2026 Captain&apos;s Academy. Built for firefighter candidates.</p>
                </div>
            </footer>

            {/* Email Capture Modal */}
            {quizResults && (
                <EmailCaptureModal
                    isOpen={showEmailModal}
                    onClose={() => setShowEmailModal(false)}
                    onComplete={handleEmailComplete}
                    quizResults={quizResults}
                />
            )}
        </div>
    );
}
