"use client";

import { useState } from "react";
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

// Pricing configuration with behavioral economics
const PRICING = {
    monthly: {
        price: 9.99,
        display: "$9.99",
        period: "/month",
    },
    annual: {
        price: 99,
        display: "$99",
        period: "/year",
        savings: "$21",
        monthlyEquivalent: "$8.25",
    },
};

export default function ServicesPage() {
    const [selectedPlan, setSelectedPlan] = useState<"monthly" | "annual">("annual");

    // Replace with your actual Stripe checkout URLs
    const COACHING_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfa4KhrhICuxiDLRD5UdEaFZGBtVNZ8_9YqTnPUQ0kWWnrc7w/viewform?usp=header";
    const SUBSCRIPTION_URL_MONTHLY = "#"; // Replace with Stripe monthly link
    const SUBSCRIPTION_URL_ANNUAL = "#"; // Replace with Stripe annual link

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
        "AI-powered explanations",
        "Track progress over time",
        "Priority support",
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

                {/* Premium Subscription Card with Plan Toggle */}
                <div className="card p-6 border-2 border-fire-red/30 bg-gradient-to-br from-card to-fire-red/5">
                    {/* Header with Best Value badge */}
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
                        <div className="flex items-start gap-4">
                            <div className="w-12 h-12 rounded-xl bg-fire-red/10 flex items-center justify-center flex-shrink-0">
                                <Zap className="w-6 h-6 text-fire-red" />
                            </div>
                            <div>
                                <div className="flex items-center gap-2 mb-1">
                                    <h2 className="text-xl font-bold text-foreground">
                                        Premium Subscription
                                    </h2>
                                    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-fire-red/10 text-fire-red text-xs font-medium rounded-full border border-fire-red/20">
                                        <Star className="w-3 h-3" />
                                        Most Popular
                                    </span>
                                </div>
                                <p className="text-sm text-muted max-w-md">
                                    Unlimited access to all study tools. Practice as much as you need to ace your exam.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Plan Toggle */}
                    <div className="flex gap-2 p-1 bg-background border border-card-border rounded-lg mb-6 max-w-xs">
                        <button
                            onClick={() => setSelectedPlan("monthly")}
                            className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${selectedPlan === "monthly"
                                    ? "bg-card text-foreground shadow"
                                    : "text-muted hover:text-foreground"
                                }`}
                        >
                            Monthly
                        </button>
                        <button
                            onClick={() => setSelectedPlan("annual")}
                            className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors relative ${selectedPlan === "annual"
                                    ? "bg-card text-foreground shadow"
                                    : "text-muted hover:text-foreground"
                                }`}
                        >
                            Annual
                            <span className="absolute -top-2 -right-2 px-1.5 py-0.5 bg-green-500 text-white text-xs rounded-full">
                                -{PRICING.annual.savings}
                            </span>
                        </button>
                    </div>

                    {/* Pricing Display */}
                    <div className="flex flex-col md:flex-row md:items-end gap-6 mb-6">
                        <div>
                            <div className="flex items-baseline gap-1">
                                <span className="text-4xl md:text-5xl font-bold text-fire-red">
                                    {selectedPlan === "annual"
                                        ? PRICING.annual.display
                                        : PRICING.monthly.display}
                                </span>
                                <span className="text-muted text-lg">
                                    {selectedPlan === "annual"
                                        ? PRICING.annual.period
                                        : PRICING.monthly.period}
                                </span>
                            </div>
                            {selectedPlan === "annual" && (
                                <p className="text-sm text-muted mt-1">
                                    Just {PRICING.annual.monthlyEquivalent}/month • <span className="text-green-500 font-medium">Save {PRICING.annual.savings}/year</span>
                                </p>
                            )}
                            {selectedPlan === "monthly" && (
                                <p className="text-sm text-muted mt-1">
                                    Cancel anytime
                                </p>
                            )}
                        </div>
                        <a
                            href={selectedPlan === "annual" ? SUBSCRIPTION_URL_ANNUAL : SUBSCRIPTION_URL_MONTHLY}
                            className="flex items-center justify-center gap-2 px-6 py-3 bg-fire-red text-white font-medium rounded-lg hover:bg-ember-orange transition-colors"
                        >
                            <CreditCard className="w-4 h-4" />
                            {selectedPlan === "annual" ? "Get Annual Plan" : "Subscribe Monthly"}
                            <ArrowRight className="w-4 h-4" />
                        </a>
                    </div>

                    {/* Benefits grid */}
                    <div className="pt-4 border-t border-card-border">
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                            {premiumBenefits.map((benefit) => (
                                <div key={benefit} className="flex items-center gap-2 text-sm text-muted">
                                    <Check className="w-4 h-4 text-fire-red flex-shrink-0" />
                                    {benefit}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Social Proof */}
                    <div className="mt-4 pt-4 border-t border-card-border">
                        <div className="flex items-center gap-3">
                            <div className="flex -space-x-2">
                                {[1, 2, 3, 4].map((i) => (
                                    <div
                                        key={i}
                                        className="w-8 h-8 rounded-full bg-card-border border-2 border-card"
                                    />
                                ))}
                            </div>
                            <p className="text-sm text-muted">
                                <span className="text-foreground font-medium">1,000+</span> firefighter candidates studying with us
                            </p>
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
                <div className="card p-6 md:p-8 border-2 border-blue-500/30 bg-gradient-to-br from-card to-blue-500/5">
                    {/* Package Header */}
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-8">
                        <div>
                            <h2 className="text-2xl font-bold text-foreground">
                                Premium Coaching Package
                            </h2>
                            <p className="text-muted mt-1">
                                Everything you need to ace your firefighter hiring process
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="flex items-baseline gap-1">
                                <span className="text-4xl md:text-5xl font-bold text-blue-500">$250</span>
                                <span className="text-muted text-sm">one-time</span>
                            </div>
                        </div>
                    </div>

                    {/* What's Included */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                        {coachingPackageIncludes.map((item) => {
                            const Icon = item.icon;
                            return (
                                <div key={item.title} className="card p-5 bg-background/50">
                                    <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-3">
                                        <Icon className="w-5 h-5 text-blue-500" />
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
                            className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors"
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
