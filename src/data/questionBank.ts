// Client-side question bank for instant quiz loading
// Questions are preloaded - no API latency

import questionsData from "./questions.json";

export interface Question {
    id: string;
    subject: string;
    question: string;
    options: string; // JSON string array
    correct_answer: string;
    explanation: string;
    created_at: string;
    quality_score: number;
    reported_count: number;
    is_approved: number;
    image_path: string | null;
}

export interface ParsedQuestion {
    id: string;
    subject: string;
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
}

// Type cast the imported JSON
const allQuestions = questionsData as Question[];

// Pre-index questions by subject for O(1) lookup
const questionsBySubject: Record<string, Question[]> = {};

allQuestions.forEach((q) => {
    if (!questionsBySubject[q.subject]) {
        questionsBySubject[q.subject] = [];
    }
    questionsBySubject[q.subject].push(q);
});

// Shuffle array using Fisher-Yates algorithm
function shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

/**
 * Get random questions from the question bank
 * @param subjects - Array of subject IDs to pull from
 * @param count - Number of questions to return
 * @returns Array of parsed questions ready for quiz display
 */
export function getQuestions(subjects: string[], count: number): ParsedQuestion[] {
    // Gather all questions from selected subjects
    const pool: Question[] = [];
    subjects.forEach((subject) => {
        const subjectQuestions = questionsBySubject[subject] || [];
        pool.push(...subjectQuestions);
    });

    // Shuffle and take requested count
    const shuffled = shuffleArray(pool);
    const selected = shuffled.slice(0, count);

    // Parse options JSON string to array
    return selected.map((q) => ({
        id: q.id,
        subject: q.subject,
        question: q.question,
        options: JSON.parse(q.options) as string[],
        correct_answer: q.correct_answer,
        explanation: q.explanation,
    }));
}

/**
 * Get flashcards from the question bank
 * @param subjects - Array of subject IDs
 * @param count - Number of flashcards to return
 * @returns Array of flashcard-formatted questions
 */
export function getFlashcards(subjects: string[], count: number): ParsedQuestion[] {
    return getQuestions(subjects, count);
}

// Export metadata
export const questionBankStats = {
    totalQuestions: allQuestions.length,
    bySubject: Object.fromEntries(
        Object.entries(questionsBySubject).map(([k, v]) => [k, v.length])
    ),
};

export default { getQuestions, getFlashcards, questionBankStats };
