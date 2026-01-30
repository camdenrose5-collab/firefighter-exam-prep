"use client";

import { useState, ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    LayoutDashboard,
    BookOpen,
    GraduationCap,
    Trophy,
    Settings,
    User,
    Menu,
    X,
    ChevronRight,
    LogOut,
    Flame,
    BarChart3,
} from "lucide-react";
import { useUserStore } from "@/lib/store";

interface AppShellProps {
    children: ReactNode;
}

const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Study Hub", href: "/study-hub", icon: BookOpen },
    { name: "Progress", href: "/progress", icon: BarChart3 },
    { name: "Coaching", href: "/services", icon: GraduationCap },
];

export default function AppShell({ children }: AppShellProps) {
    const pathname = usePathname();
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { isAuthenticated, email, tier, logout } = useUserStore();

    const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

    return (
        <div className="min-h-screen bg-background flex">
            {/* Mobile sidebar backdrop */}
            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-40 bg-black/50 lg:hidden"
                        onClick={() => setSidebarOpen(false)}
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <aside
                className={`
                    fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-card-border
                    transform transition-transform duration-200 ease-in-out
                    lg:translate-x-0 lg:static lg:inset-auto
                    ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
                `}
            >
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="flex items-center gap-3 px-6 py-5 border-b border-card-border">
                        <div className="w-10 h-10 rounded-lg bg-fire-red flex items-center justify-center">
                            <Flame className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-foreground">Captain&apos;s Academy</h1>
                            <p className="text-xs text-muted">Firefighter Prep</p>
                        </div>
                        {/* Mobile close button */}
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="ml-auto lg:hidden p-2 text-muted hover:text-foreground"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-3 py-4 space-y-1">
                        {navigation.map((item) => {
                            const Icon = item.icon;
                            const active = isActive(item.href);
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    onClick={() => setSidebarOpen(false)}
                                    className={`
                                        flex items-center gap-3 px-3 py-2.5 rounded-lg
                                        text-sm font-medium transition-colors
                                        ${active
                                            ? "bg-fire-red/10 text-fire-red"
                                            : "text-muted hover:bg-card-border/50 hover:text-foreground"
                                        }
                                    `}
                                >
                                    <Icon className="w-5 h-5" />
                                    {item.name}
                                    {active && (
                                        <ChevronRight className="w-4 h-4 ml-auto" />
                                    )}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User section */}
                    <div className="border-t border-card-border p-4">
                        {isAuthenticated ? (
                            <div className="space-y-3">
                                <div className="flex items-center gap-3 px-2">
                                    <div className="w-9 h-9 rounded-full bg-card-border flex items-center justify-center">
                                        <User className="w-5 h-5 text-muted" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-foreground truncate">
                                            {email}
                                        </p>
                                        <p className="text-xs text-muted capitalize">
                                            {tier} Plan
                                        </p>
                                    </div>
                                </div>
                                <button
                                    onClick={logout}
                                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-muted hover:text-foreground hover:bg-card-border/50 rounded-lg transition-colors"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign Out
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                <Link
                                    href="/study-hub"
                                    className="block w-full px-4 py-2.5 text-center text-sm font-medium text-white bg-fire-red rounded-lg hover:bg-ember-orange transition-colors"
                                >
                                    Get Started
                                </Link>
                                <p className="text-xs text-muted text-center">
                                    Free • No credit card required
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Tier upgrade prompt */}
                    {isAuthenticated && tier === "free" && (
                        <div className="mx-4 mb-4 p-4 rounded-lg bg-gradient-to-br from-fire-red/10 to-ember-orange/10 border border-fire-red/20">
                            <div className="flex items-center gap-2 mb-2">
                                <Trophy className="w-4 h-4 text-fire-red" />
                                <span className="text-sm font-medium text-foreground">Go Premium</span>
                            </div>
                            <p className="text-xs text-muted mb-3">
                                Unlimited quizzes, progress tracking, and more.
                            </p>
                            <Link
                                href="/services"
                                className="block text-center text-xs font-medium text-fire-red hover:text-ember-orange transition-colors"
                            >
                                View Plans →
                            </Link>
                        </div>
                    )}
                </div>
            </aside>

            {/* Main content */}
            <div className="flex-1 flex flex-col min-h-screen">
                {/* Top header (mobile) */}
                <header className="lg:hidden sticky top-0 z-30 flex items-center gap-4 px-4 py-3 bg-card border-b border-card-border">
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="p-2 text-muted hover:text-foreground rounded-lg hover:bg-card-border/50 transition-colors"
                    >
                        <Menu className="w-6 h-6" />
                    </button>
                    <div className="flex items-center gap-2">
                        <Flame className="w-5 h-5 text-fire-red" />
                        <span className="font-semibold text-foreground">Captain&apos;s Academy</span>
                    </div>
                </header>

                {/* Page content */}
                <main className="flex-1">
                    {children}
                </main>
            </div>
        </div>
    );
}
