import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Three-tier system:
// - lead: Email captured but not signed up. 10 total questions OR flashcards, then must sign up
// - free: Signed up. 10 questions AND 10 flashcards per day, then asked to subscribe
// - premium: $10/month. Unlimited access

type UserTier = 'lead' | 'free' | 'premium';

interface UserState {
    // Authentication
    isAuthenticated: boolean;
    email: string | null;
    userId: string | null;

    // Subscription tier
    tier: UserTier;

    // Usage tracking
    // For leads: total lifetime usage (no reset)
    // For free: daily usage (resets each day)
    quizCount: number;
    flashcardCount: number;
    lastResetDate: string | null;

    // Actions
    login: (email: string, token: string) => void;
    signup: (email: string, userId: string, token: string) => void;
    captureLeadEmail: (email: string) => void;
    logout: () => void;
    upgradeToPremium: () => void;
    incrementQuizCount: () => void;
    incrementFlashcardCount: () => void;
    resetDailyLimits: () => void;
}

// Tier limits
export const TIER_LIMITS = {
    lead: {
        totalQuestions: 10,    // Total lifetime limit
        totalFlashcards: 10,   // Total lifetime limit
    },
    free: {
        questionsPerDay: 10,
        flashcardsPerDay: 10,
    },
    premium: {
        unlimited: true,
    },
};

// Backwards compatibility export
export const FREE_TIER_LIMITS = {
    quizzesPerDay: TIER_LIMITS.free.questionsPerDay,
    flashcardSessionsPerDay: TIER_LIMITS.free.flashcardsPerDay,
};

const getTodayString = () => new Date().toISOString().split('T')[0];

export const useUserStore = create<UserState>()(
    persist(
        (set, get) => ({
            // Initial state - start as lead
            isAuthenticated: false,
            email: null,
            userId: null,
            tier: 'lead',
            quizCount: 0,
            flashcardCount: 0,
            lastResetDate: null,

            // Capture lead email (before signup)
            captureLeadEmail: (email) => {
                set({ email, tier: 'lead' });
            },

            // Login existing user (promotes to free)
            login: (email, token) => {
                localStorage.setItem('auth_token', token);
                localStorage.setItem('user_email', email);
                const state = get();
                set({
                    isAuthenticated: true,
                    email,
                    // Promote from lead to free on login, reset daily counts
                    tier: state.tier === 'premium' ? 'premium' : 'free',
                    quizCount: 0,
                    flashcardCount: 0,
                    lastResetDate: getTodayString(),
                });
            },

            // Signup new user (promotes to free)
            signup: (email, userId, token) => {
                localStorage.setItem('auth_token', token);
                localStorage.setItem('user_email', email);
                localStorage.setItem('user_id', userId);
                set({
                    isAuthenticated: true,
                    email,
                    userId,
                    tier: 'free',
                    // Reset counts on signup
                    quizCount: 0,
                    flashcardCount: 0,
                    lastResetDate: getTodayString(),
                });
            },

            logout: () => {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_email');
                localStorage.removeItem('user_id');
                set({
                    isAuthenticated: false,
                    email: null,
                    userId: null,
                    tier: 'lead',
                    quizCount: 0,
                    flashcardCount: 0,
                    lastResetDate: null,
                });
            },

            upgradeToPremium: () => {
                set({ tier: 'premium' });
            },

            incrementQuizCount: () => {
                const state = get();
                const today = getTodayString();

                // For free tier, check if we need to reset daily limits
                if (state.tier === 'free' && state.lastResetDate !== today) {
                    set({ quizCount: 1, flashcardCount: 0, lastResetDate: today });
                } else {
                    set({ quizCount: state.quizCount + 1 });
                }
            },

            incrementFlashcardCount: () => {
                const state = get();
                const today = getTodayString();

                // For free tier, check if we need to reset daily limits
                if (state.tier === 'free' && state.lastResetDate !== today) {
                    set({ quizCount: 0, flashcardCount: 1, lastResetDate: today });
                } else {
                    set({ flashcardCount: state.flashcardCount + 1 });
                }
            },

            resetDailyLimits: () => {
                set({
                    quizCount: 0,
                    flashcardCount: 0,
                    lastResetDate: getTodayString(),
                });
            },
        }),
        {
            name: 'captains-academy-user',
        }
    )
);

// Selector hooks for common checks
export const useCanStartQuiz = () => {
    const { tier, quizCount, lastResetDate } = useUserStore();

    if (tier === 'premium') return true;

    if (tier === 'lead') {
        // Leads have a lifetime limit
        return quizCount < TIER_LIMITS.lead.totalQuestions;
    }

    // Free tier - daily limits
    const today = getTodayString();
    if (lastResetDate !== today) return true; // New day, limits reset

    return quizCount < TIER_LIMITS.free.questionsPerDay;
};

export const useCanStartFlashcards = () => {
    const { tier, flashcardCount, lastResetDate } = useUserStore();

    if (tier === 'premium') return true;

    if (tier === 'lead') {
        // Leads have a lifetime limit
        return flashcardCount < TIER_LIMITS.lead.totalFlashcards;
    }

    // Free tier - daily limits
    const today = getTodayString();
    if (lastResetDate !== today) return true;

    return flashcardCount < TIER_LIMITS.free.flashcardsPerDay;
};

export const useRemainingQuizzes = () => {
    const { tier, quizCount, lastResetDate } = useUserStore();

    if (tier === 'premium') return Infinity;

    if (tier === 'lead') {
        return Math.max(0, TIER_LIMITS.lead.totalQuestions - quizCount);
    }

    const today = getTodayString();
    if (lastResetDate !== today) return TIER_LIMITS.free.questionsPerDay;

    return Math.max(0, TIER_LIMITS.free.questionsPerDay - quizCount);
};

export const useRemainingFlashcards = () => {
    const { tier, flashcardCount, lastResetDate } = useUserStore();

    if (tier === 'premium') return Infinity;

    if (tier === 'lead') {
        return Math.max(0, TIER_LIMITS.lead.totalFlashcards - flashcardCount);
    }

    const today = getTodayString();
    if (lastResetDate !== today) return TIER_LIMITS.free.flashcardsPerDay;

    return Math.max(0, TIER_LIMITS.free.flashcardsPerDay - flashcardCount);
};

// Check if user needs to sign up (lead hit limit)
export const useNeedsSignup = () => {
    const { tier, quizCount, flashcardCount } = useUserStore();

    if (tier !== 'lead') return false;

    return quizCount >= TIER_LIMITS.lead.totalQuestions ||
        flashcardCount >= TIER_LIMITS.lead.totalFlashcards;
};

// Check if free user needs to subscribe
export const useNeedsSubscription = () => {
    const { tier, quizCount, flashcardCount, lastResetDate } = useUserStore();

    if (tier !== 'free') return false;

    const today = getTodayString();
    if (lastResetDate !== today) return false; // New day, limits reset

    return quizCount >= TIER_LIMITS.free.questionsPerDay ||
        flashcardCount >= TIER_LIMITS.free.flashcardsPerDay;
};
