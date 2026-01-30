"use client";

import Link from "next/link";
import {
    Video,
    FileText,
    Check,
    Phone,
    MessageSquare,
    Target,
    AlertTriangle,
    FileCheck,
    Brain,
    ArrowRight,
    Star,
    Zap,
    CreditCard
} from "lucide-react";
import AppShell from "@/components/AppShell";
import { TIER_LIMITS } from "@/lib/store";

export default function ServicesPage() {
    // Replace with your actual Stripe checkout URLs
    const COACHING_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfa4KhrhICuxiDLRD5UdEaFZGBtVNZ8_9YqTnPUQ0kWWnrc7w/viewform?usp=header";
    const SUBSCRIPTION_URL = "#"; // Replace with Stripe subscription link

    const coachingPackageIncludes = [
        {
            icon: Video,
            title: "3 Mock Interviews",
            description: "Practice with real oral board questions and get detailed feedback on your answers, delivery, and body language.",
        },
        {
            icon: FileText,
            title: "Resume Review",
            description: "Professional review and optimization of your firefighter resume to stand out from the stack.",
        },
    ];

    const coachingFeatures = [
        { icon: Target, label: "Customized study plan" },
        { icon: Phone, label: "Direct access via text/call" },
        { icon: MessageSquare, label: "Panel question strategy" },
        { icon: AlertTriangle, label: "Red flag identification" },
        { icon: FileCheck, label: "Application strategy" },
        { icon: Brain, label: "Test anxiety techniques" },
    ];

    const premiumBenefits = [
        "Unlimited practice questions",
        "Unlimited flashcard sessions",
        "Track progress over time",
        "Priority support",
        "New content updates",
    ];

    return (
        <AppShell>
            <div className="p-6 lg:p-8 max-w-5xl mx-auto space-y-8">
                {/* Page Header */}
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
                        Level Up Your Fire Career
                    </h1>
                    <p className="text-muted max-w-2xl">
                        Get direct support from someone who&apos;s been through the process.
                        Whether you need help with the written exam, oral boards, or figuring out where to start.
                    </p>
                </div>

                {/* Premium Subscription Card */}
                <div className="card p-6 border-2 border-blue-500/30 bg-gradient-to-br from-card to-blue-500/5">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                        <div className="flex items-start gap-4">
                            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                                <Zap className="w-6 h-6 text-blue-500" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-foreground mb-1">
                                    Premium Subscription
                                </h2>
                                <p className="text-sm text-muted max-w-md">
                                    Unlimited access to all study tools. Practice as much as you need to ace your exam.
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="text-right">
                                <div className="flex items-baseline gap-1">
                                    <span className="text-3xl font-bold text-blue-500">$10</span>
                                    <span className="text-muted text-sm">/month</span>
                                </div>
                                <p className="text-xs text-muted">Cancel anytime</p>
                            </div>
                            <a
                                href={SUBSCRIPTION_URL}
                                className="flex items-center gap-2 px-5 py-2.5 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors"
                            >
                                <CreditCard className="w-4 h-4" />
                                Subscribe
                            </a>
                        </div>
                    </div>

                    {/* Benefits grid */}
                    <div className="mt-4 pt-4 border-t border-card-border">
                        <div className="flex flex-wrap gap-x-6 gap-y-2">
                            {premiumBenefits.map((benefit) => (
                                <div key={benefit} className="flex items-center gap-2 text-sm text-muted">
                                    <Check className="w-4 h-4 text-blue-500 flex-shrink-0" />
                                    {benefit}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Divider */}
                <div className="flex items-center gap-4">
                    <div className="flex-1 h-px bg-card-border" />
                    <span className="text-sm text-muted">Or get personalized coaching</span>
                    <div className="flex-1 h-px bg-card-border" />
                </div>

                {/* Coaching Package Card */}
                <div className="card p-6 md:p-8 border-2 border-fire-red/30 bg-gradient-to-br from-card to-fire-red/5">
                    {/* Package Header */}
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-8">
                        <div>
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-fire-red/10 border border-fire-red/30 text-xs text-fire-red mb-3">
                                <Star className="w-3 h-3" />
                                Best Value
                            </div>
                            <h2 className="text-2xl font-bold text-foreground">
                                Premium Coaching Package
                            </h2>
                        </div>
                        <div className="text-right">
                            <div className="flex items-baseline gap-1">
                                <span className="text-4xl md:text-5xl font-bold text-fire-red">$250</span>
                                <span className="text-muted text-sm">one-time</span>
                            </div>
                        </div>
                    </div>

                    <p className="text-muted mb-8 max-w-2xl">
                        Get everything you need to ace your firefighter hiring process. This comprehensive
                        package combines personalized interview prep with professional resume optimization.
                    </p>

                    {/* What's Included */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                        {coachingPackageIncludes.map((item) => {
                            const Icon = item.icon;
                            return (
                                <div key={item.title} className="card p-5 bg-background/50">
                                    <div className="w-10 h-10 rounded-lg bg-fire-red/10 flex items-center justify-center mb-3">
                                        <Icon className="w-5 h-5 text-fire-red" />
                                    </div>
                                    <h3 className="font-semibold text-foreground mb-1">
                                        {item.title}
                                    </h3>
                                    <p className="text-sm text-muted">
                                        {item.description}
                                    </p>
                                </div>
                            );
                        })}
                    </div>

                    {/* Features List */}
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8">
                        {coachingFeatures.map((feature) => (
                            <div key={feature.label} className="flex items-center gap-2 text-sm text-muted">
                                <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                                {feature.label}
                            </div>
                        ))}
                    </div>

                    {/* CTA Button */}
                    <div className="flex flex-col sm:flex-row gap-4">
                        <a
                            href={COACHING_URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-fire-red text-white font-medium rounded-lg hover:bg-ember-orange transition-colors"
                        >
                            Get Started Today
                            <ArrowRight className="w-4 h-4" />
                        </a>
                    </div>
                </div>

                {/* Free tier info */}
                <div className="card p-5 border-l-4 border-l-green-500">
                    <h3 className="font-semibold text-foreground mb-1">Free Account</h3>
                    <p className="text-sm text-muted">
                        Not ready to commit? Create a free account to get {TIER_LIMITS.free.questionsPerDay} practice
                        questions and {TIER_LIMITS.free.flashcardsPerDay} flashcard sessions every day.
                        <Link href="/study-hub" className="text-fire-red hover:underline ml-1">
                            Start studying →
                        </Link>
                    </p>
                </div>
            </div>
        </AppShell>
    );
}
