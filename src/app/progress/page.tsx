"use client";

import { BarChart3, Target, BookOpen, TrendingUp, Calendar } from "lucide-react";
import AppShell from "@/components/AppShell";
import { useUserStore, FREE_TIER_LIMITS } from "@/lib/store";

export default function ProgressPage() {
    const { tier, quizCount, flashcardCount } = useUserStore();

    const todayStats = [
        {
            label: "Quizzes Completed",
            value: quizCount,
            max: tier === "premium" ? null : FREE_TIER_LIMITS.quizzesPerDay,
            icon: Target,
            color: "text-blue-500",
            bgColor: "bg-blue-500/10",
        },
        {
            label: "Flashcard Sessions",
            value: flashcardCount,
            max: tier === "premium" ? null : FREE_TIER_LIMITS.flashcardSessionsPerDay,
            icon: BookOpen,
            color: "text-green-500",
            bgColor: "bg-green-500/10",
        },
    ];

    return (
        <AppShell>
            <div className="p-6 lg:p-8 max-w-6xl mx-auto">
                {/* Page Header */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-foreground">Progress</h1>
                    <p className="text-muted mt-1">
                        Track your study activity and improvement over time.
                    </p>
                </div>

                {/* Today's Activity */}
                <div className="mb-8">
                    <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-muted" />
                        Today&apos;s Activity
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {todayStats.map((stat) => {
                            const Icon = stat.icon;
                            const percentage = stat.max ? Math.min((stat.value / stat.max) * 100, 100) : 100;
                            return (
                                <div key={stat.label} className="card p-5">
                                    <div className="flex items-center justify-between mb-3">
                                        <span className="text-sm text-muted">{stat.label}</span>
                                        <div className={`w-8 h-8 rounded-lg ${stat.bgColor} flex items-center justify-center`}>
                                            <Icon className={`w-4 h-4 ${stat.color}`} />
                                        </div>
                                    </div>
                                    <div className="flex items-baseline gap-1 mb-3">
                                        <span className="text-3xl font-bold text-foreground">{stat.value}</span>
                                        {stat.max && (
                                            <span className="text-muted">/ {stat.max}</span>
                                        )}
                                    </div>
                                    {stat.max && (
                                        <div className="w-full h-2 bg-card-border rounded-full overflow-hidden">
                                            <div
                                                className={`h-full ${stat.color.replace("text-", "bg-")} transition-all`}
                                                style={{ width: `${percentage}%` }}
                                            />
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Coming Soon Section */}
                <div className="card p-8 text-center">
                    <div className="w-12 h-12 rounded-xl bg-fire-red/10 flex items-center justify-center mx-auto mb-4">
                        <TrendingUp className="w-6 h-6 text-fire-red" />
                    </div>
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                        Detailed Analytics Coming Soon
                    </h3>
                    <p className="text-muted text-sm max-w-md mx-auto">
                        Track your performance by subject area, view historical trends,
                        and identify weak areas to focus on. Available in an upcoming update.
                    </p>
                </div>
            </div>
        </AppShell>
    );
}
