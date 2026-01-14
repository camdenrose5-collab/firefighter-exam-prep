"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-card-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg gradient-fire flex items-center justify-center">
              <span className="text-2xl">🔥</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Captain&apos;s Academy</h1>
              <p className="text-xs text-muted">Firefighter Exam Prep</p>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex items-center justify-center px-6">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-card border border-card-border text-sm text-muted">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Brain Loaded • 50+ Fire Service PDFs
          </div>

          {/* Main Headline */}
          <h2 className="text-4xl md:text-6xl font-bold text-foreground leading-tight">
            Your{" "}
            <span className="text-transparent bg-clip-text gradient-fire bg-gradient-to-r from-fire-red to-ember-orange">
              AI Fire Captain
            </span>
            <br />
            is Ready to Train
          </h2>

          {/* Subheadline */}
          <p className="text-xl text-muted max-w-2xl mx-auto leading-relaxed">
            Quizzes, flashcards, and personalized tutoring — all powered by real fire service
            manuals, not generic AI. Pass your written exam with the Captain&apos;s help.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Link
              href="/study-hub"
              className="btn-primary px-10 py-5 text-xl font-bold rounded-xl fire-glow hover:fire-glow-hover transition-all"
            >
              🎯 Enter Study Hub
            </Link>
          </div>

          {/* Features Preview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
            <div className="card p-6 text-left">
              <div className="text-3xl mb-3">📝</div>
              <h3 className="font-bold text-foreground mb-2">Quiz Me</h3>
              <p className="text-sm text-muted">
                Generate 5-100 questions on any topic from the loaded manuals.
              </p>
            </div>
            <div className="card p-6 text-left">
              <div className="text-3xl mb-3">📇</div>
              <h3 className="font-bold text-foreground mb-2">Flashcards</h3>
              <p className="text-sm text-muted">
                Master key terms with active recall — flip, learn, repeat.
              </p>
            </div>
            <div className="card p-6 text-left">
              <div className="text-3xl mb-3">💬</div>
              <h3 className="font-bold text-foreground mb-2">Explain</h3>
              <p className="text-sm text-muted">
                Ask questions and get explanations using firehouse analogies.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-card-border py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-muted">
          <p>🔥 Captain&apos;s Academy — Your AI Fire Instructor</p>
          <p className="mt-1 text-xs">Powered by Vertex AI + Discovery Engine</p>
        </div>
      </footer>
    </div>
  );
}
