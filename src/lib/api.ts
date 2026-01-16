// API Configuration
// Uses environment variable for the backend API URL
// Falls back to localhost for development

export const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Helper to build API endpoints
export function apiUrl(path: string): string {
    return `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}
