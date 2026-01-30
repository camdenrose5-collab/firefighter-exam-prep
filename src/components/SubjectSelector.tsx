"use client";

import { useState, ComponentType } from "react";
import { Check, Users, Wrench, BookOpen, Calculator, Flame, LucideProps } from "lucide-react";

export interface Subject {
    id: string;
    label: string;
    icon: ComponentType<LucideProps>;
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
        icon: Users,
        description: "Teamwork, conflict resolution, communication",
    },
    {
        id: "mechanical-aptitude",
        label: "Mechanical Aptitude",
        icon: Wrench,
        description: "Tools, leverage, hydraulics, troubleshooting",
    },
    {
        id: "fire-terms",
        label: "Fire Terms",
        icon: Flame,
        description: "GPM, PSI, SCBA, Flashover, and essential fire terminology",
    },
    {
        id: "math",
        label: "Math (Mental)",
        icon: Calculator,
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
            <div>
                <h2 className="text-xl font-bold text-foreground mb-1">
                    Choose Your Subjects
                </h2>
                <p className="text-sm text-muted">
                    Select one or more subjects to focus your study session
                </p>
            </div>

            {/* Quick Actions */}
            <div className="flex gap-4">
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
                    const Icon = subject.icon;
                    return (
                        <button
                            key={subject.id}
                            onClick={() => toggleSubject(subject.id)}
                            className={`p-4 rounded-lg border text-left transition-all ${isSelected
                                ? "border-fire-red bg-fire-red/10"
                                : "border-card-border bg-card hover:border-muted"
                                }`}
                        >
                            <div className="flex items-start gap-3">
                                {/* Checkbox */}
                                <div
                                    className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5 ${isSelected
                                        ? "bg-fire-red"
                                        : "border border-muted"
                                        }`}
                                >
                                    {isSelected && (
                                        <Check className="w-3 h-3 text-white" />
                                    )}
                                </div>

                                {/* Content */}
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Icon className={`w-4 h-4 ${isSelected ? "text-fire-red" : "text-muted"}`} />
                                        <span className="font-medium text-foreground">
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
            <div className="pt-2">
                <button
                    onClick={onContinue}
                    disabled={selected.length === 0}
                    className={`w-full sm:w-auto px-6 py-3 font-medium rounded-lg transition-all ${selected.length === 0
                        ? "bg-card-border text-muted cursor-not-allowed"
                        : "bg-fire-red text-white hover:bg-ember-orange"
                        }`}
                >
                    Continue with {selected.length} Subject{selected.length !== 1 ? "s" : ""}
                </button>
            </div>
        </div>
    );
}
