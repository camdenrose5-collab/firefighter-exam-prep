"use client";

import { useState, useRef, useEffect } from "react";
import SubjectSelector from "./SubjectSelector";
import FeedbackModal from "./FeedbackModal";
import { apiUrl } from "@/lib/api";

interface Message {
    role: "user" | "assistant";
    text: string;
}

interface ExplainContainerProps {
    onBack: () => void;
}

const SUBJECT_LABELS: Record<string, string> = {
    "human-relations": "Human Relations",
    "mechanical-aptitude": "Mechanical Aptitude",
    "reading-ability": "Reading Ability",
    "math": "Math (Mental)",
};

export default function ExplainContainer({ onBack }: ExplainContainerProps) {
    const [phase, setPhase] = useState<"subject-select" | "chat">("subject-select");
    const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);

    const handleSubmitFeedback = async (studyMode: string, message: string) => {
        try {
            await fetch(apiUrl("/api/feedback"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ study_mode: studyMode, message }),
            });
        } catch (err) {
            console.error("Failed to submit feedback:", err);
        }
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleContinueToChat = () => {
        if (selectedSubjects.length > 0) {
            const subjectNames = selectedSubjects
                .map((s) => SUBJECT_LABELS[s] || s)
                .join(", ");
            setMessages([
                {
                    role: "assistant",
                    text: `Hey there, candidate! You've chosen to focus on: **${subjectNames}**.\n\nWhat's got you stuck? I'll break it down in simple terms with real-world examples — no paper or calculator needed.`,
                },
            ]);
            setPhase("chat");
        }
    };

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage = input.trim();
        setInput("");
        setMessages((prev) => [...prev, { role: "user", text: userMessage }]);
        setIsLoading(true);

        try {
            const response = await fetch(apiUrl("/api/tutor/explain"), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    subject: selectedSubjects.map((s) => SUBJECT_LABELS[s]).join(", "),
                    user_input: userMessage,
                    subjects: selectedSubjects,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to get tutoring response");
            }

            const data = await response.json();
            setMessages((prev) => [
                ...prev,
                { role: "assistant", text: data.explanation },
            ]);
        } catch (err) {
            console.error("Tutoring error:", err);
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    text: "Sorry, I'm having trouble connecting right now. Try again in a moment, or ask a different question.",
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Phase 1: Subject Selection
    if (phase === "subject-select") {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-foreground">💬 Explain</h2>
                    <button
                        onClick={onBack}
                        className="text-muted hover:text-foreground transition-colors"
                    >
                        ← Back to Hub
                    </button>
                </div>
                <SubjectSelector
                    onSelectionChange={setSelectedSubjects}
                    onContinue={handleContinueToChat}
                />
            </div>
        );
    }

    // Phase 2: Chat Interface
    return (
        <div className="flex flex-col h-[600px] max-w-3xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full gradient-fire flex items-center justify-center text-2xl">
                        👨‍🚒
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-foreground">
                            Captain&apos;s Tutoring
                        </h2>
                        <p className="text-sm text-muted">
                            {selectedSubjects.length} subject{selectedSubjects.length !== 1 ? "s" : ""} • No calculator
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setFeedbackModalOpen(true)}
                        className="text-muted hover:text-ember-orange transition-colors flex items-center gap-1.5 text-sm"
                    >
                        <span>💡</span> Feedback
                    </button>
                    <button
                        onClick={() => setPhase("subject-select")}
                        className="text-muted hover:text-foreground transition-colors"
                    >
                        ← Change Subjects
                    </button>
                </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 p-4 card">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                        <div
                            className={`max-w-[85%] p-4 rounded-2xl ${message.role === "assistant"
                                ? "bg-card-border text-foreground rounded-bl-sm"
                                : "gradient-fire text-white rounded-br-sm"
                                }`}
                        >
                            <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-card-border text-foreground p-4 rounded-2xl rounded-bl-sm">
                            <div className="flex items-center gap-2">
                                <span className="animate-bounce">🔥</span>
                                <span className="text-muted">Captain is thinking...</span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="mt-4 flex gap-3">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="e.g., Help me understand percentages without a calculator..."
                    className="flex-1 p-4 rounded-xl bg-card border border-card-border text-foreground placeholder-muted focus:outline-none focus:border-fire-red transition-colors"
                    disabled={isLoading}
                />
                <button
                    onClick={handleSend}
                    disabled={isLoading || !input.trim()}
                    className="btn-primary px-6 rounded-xl fire-glow hover:fire-glow-hover disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                    Ask Cap
                </button>
            </div>

            {/* Feedback Modal */}
            <FeedbackModal
                isOpen={feedbackModalOpen}
                studyMode="explain"
                onClose={() => setFeedbackModalOpen(false)}
                onSubmit={handleSubmitFeedback}
            />
        </div>
    );
}
