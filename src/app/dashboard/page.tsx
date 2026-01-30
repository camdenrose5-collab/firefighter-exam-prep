"use client";

import Link from "next/link";
import {
    BookOpen,
    GraduationCap,
    Target,
    TrendingUp,
    Clock,
    CheckCircle2,
    ArrowRight,
    Flame
} from "lucide-react";
import AppShell from "@/components/AppShell";
import { useUserStore, FREE_TIER_LIMITS } from "@/lib/store";

export default function DashboardPage() {
    const { tier, quizCount, flashcardCount, isAuthenticated } = useUserStore();

    const stats = [
        {
            label: "Quizzes Today",
            value: quizCount,
            max: tier === "premium" ? "∞" : FREE_TIER_LIMITS.quizzesPerDay,
            icon: Target,
            color: "text-blue-500",
            bgColor: "bg-blue-500/10",
        },
        {
            label: "Flashcard Sessions",
            value: flashcardCount,
            max: tier === "premium" ? "∞" : FREE_TIER_LIMITS.flashcardSessionsPerDay,
            icon: BookOpen,
            color: "text-green-500",
            bgColor: "bg-green-500/10",
        },
    ];

    const quickActions = [
        {
            title: "Start a Quiz",
            description: "Test your knowledge with practice questions",
            href: "/study-hub?mode=quiz",
            icon: Target,
            color: "text-blue-500",
            bgColor: "bg-blue-500/10",
        },
        {
            title: "Study Flashcards",
            description: "Review key terms and concepts",
            href: "/study-hub?mode=flashcards",
            icon: BookOpen,
            color: "text-green-500",
            bgColor: "bg-green-500/10",
        },
        {
            title: "Get Coaching",
            description: "1-on-1 interview prep and resume review",
            href: "/services",
            icon: GraduationCap,
            color: "text-fire-red",
            bgColor: "bg-fire-red/10",
        },
    ];

    return (
        <AppShell>
            <div className="p-6 lg:p-8 max-w-6xl mx-auto">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
                    <p className="text-muted mt-1">
                        Welcome back. Ready to train?
                    </p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
                    {stats.map((stat) => {
                        const Icon = stat.icon;
                        return (
                            <div key={stat.label} className="card p-5">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="text-sm text-muted">{stat.label}</span>
                                    <div className={`w-8 h-8 rounded-lg ${stat.bgColor} flex items-center justify-center`}>
                                        <Icon className={`w-4 h-4 ${stat.color}`} />
                                    </div>
                                </div>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-3xl font-bold text-foreground">{stat.value}</span>
                                    <span className="text-muted">/ {stat.max}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Quick Actions */}
                <div className="mb-8">
                    <h2 className="text-lg font-semibold text-foreground mb-4">Quick Actions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {quickActions.map((action) => {
                            const Icon = action.icon;
                            return (
                                <Link
                                    key={action.title}
                                    href={action.href}
                                    className="card p-5 hover:border-fire-red/50 transition-all group"
                                >
                                    <div className={`w-10 h-10 rounded-lg ${action.bgColor} flex items-center justify-center mb-4`}>
                                        <Icon className={`w-5 h-5 ${action.color}`} />
                                    </div>
                                    <h3 className="font-semibold text-foreground mb-1 group-hover:text-fire-red transition-colors">
                                        {action.title}
                                    </h3>
                                    <p className="text-sm text-muted">{action.description}</p>
                                    <div className="flex items-center gap-1 mt-3 text-sm text-muted group-hover:text-fire-red transition-colors">
                                        Get started <ArrowRight className="w-4 h-4" />
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                </div>

                {/* Study Tips */}
                <div className="card p-6">
                    <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-lg bg-fire-red/10 flex items-center justify-center flex-shrink-0">
                            <Flame className="w-5 h-5 text-fire-red" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-foreground mb-1">Pro Tip</h3>
                            <p className="text-sm text-muted">
                                Consistency beats intensity. Study for 20-30 minutes daily rather than cramming for hours.
                                Your written exam score matters — most departments use it to rank candidates.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </AppShell>
    );
}
