"use client";

import { useState } from "react";

export interface Subject {
    id: string;
    label: string;
    icon: string;
    description: string;
}

interface SubjectSelectorProps {
    onSelectionChange: (subjects: string[]) => void;
    onContinue: () => void;
    subjects?: Subject[]; // Optional custom subjects list
}

// Default subjects for Flashcards (uses Fire Terms)
const FLASHCARD_SUBJECTS: Subject[] = [
    {
        id: "human-relations",
        label: "Human Relations",
        icon: "🤝",
        description: "Teamwork, conflict resolution, communication",
    },
    {
        id: "mechanical-aptitude",
        label: "Mechanical Aptitude",
        icon: "🔧",
        description: "Tools, leverage, hydraulics, troubleshooting",
    },
    {
        id: "fire-terms",
        label: "Fire Terms",
        icon: "🔥",
        description: "GPM, PSI, SCBA, Flashover, and essential fire terminology",
    },
    {
        id: "math",
        label: "Math (Mental)",
        icon: "🧮",
        description: "Arithmetic, percentages, ratios — no calculator",
    },
];

export default function SubjectSelector({
    onSelectionChange,
    onContinue,
    subjects = FLASHCARD_SUBJECTS, // Default to flashcard subjects
}: SubjectSelectorProps) {
    const [selected, setSelected] = useState<string[]>([]);


    const toggleSubject = (subjectId: string) => {
        const newSelection = selected.includes(subjectId)
            ? selected.filter((s) => s !== subjectId)
            : [...selected, subjectId];
        setSelected(newSelection);
        onSelectionChange(newSelection);
    };

    const selectAll = () => {
        const allIds = subjects.map((s) => s.id);
        setSelected(allIds);
        onSelectionChange(allIds);
    };

    const clearAll = () => {
        setSelected([]);
        onSelectionChange([]);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="text-center">
                <h2 className="text-2xl font-bold text-foreground mb-2">
                    Choose Your Subjects
                </h2>
                <p className="text-muted">
                    Select 1 or more subjects to focus your study session
                </p>
            </div>

            {/* Quick Actions */}
            <div className="flex justify-center gap-4">
                <button
                    onClick={selectAll}
                    className="text-sm text-fire-red hover:underline"
                >
                    Select All
                </button>
                <span className="text-muted">|</span>
                <button
                    onClick={clearAll}
                    className="text-sm text-muted hover:underline"
                >
                    Clear
                </button>
            </div>

            {/* Subject Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {subjects.map((subject) => {
                    const isSelected = selected.includes(subject.id);
                    return (
                        <button
                            key={subject.id}
                            onClick={() => toggleSubject(subject.id)}
                            className={`p-5 rounded-xl border-2 text-left transition-all duration-200 ${isSelected
                                ? "border-fire-red bg-fire-red/10 fire-glow"
                                : "border-card-border bg-card hover:border-muted"
                                }`}
                        >
                            <div className="flex items-start gap-4">
                                {/* Checkbox */}
                                <div
                                    className={`w-6 h-6 rounded-md border-2 flex items-center justify-center flex-shrink-0 mt-1 ${isSelected
                                        ? "border-fire-red bg-fire-red"
                                        : "border-muted"
                                        }`}
                                >
                                    {isSelected && (
                                        <svg
                                            className="w-4 h-4 text-white"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={3}
                                                d="M5 13l4 4L19 7"
                                            />
                                        </svg>
                                    )}
                                </div>

                                {/* Content */}
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-2xl">{subject.icon}</span>
                                        <span className="font-semibold text-foreground">
                                            {subject.label}
                                        </span>
                                    </div>
                                    <p className="text-sm text-muted">{subject.description}</p>
                                </div>
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* Continue Button */}
            <div className="flex justify-center pt-4">
                <button
                    onClick={onContinue}
                    disabled={selected.length === 0}
                    className={`btn-primary px-8 py-4 text-lg font-bold rounded-xl transition-all ${selected.length === 0
                        ? "opacity-50 cursor-not-allowed"
                        : "fire-glow hover:fire-glow-hover"
                        }`}
                >
                    Continue with {selected.length} Subject{selected.length !== 1 ? "s" : ""}
                </button>
            </div>
        </div>
    );
}
