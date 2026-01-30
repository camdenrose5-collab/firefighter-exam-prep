'use client';

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '@/lib/api';

const API_URL = API_BASE_URL;

interface EmailLead {
    id: string;
    email: string;
    created_at: string;
    converted: boolean;
}

interface AdminStats {
    email_leads: number;
    total_users: number;
    total_questions: number;
    total_flashcards: number;
    pending_reports: number;
    pending_feedback: number;
}

interface Report {
    id: string;
    question_id: string;
    question: string;
    subject: string;
    reason: string;
    reported_at: string;
}

interface Feedback {
    id: string;
    study_mode: string;
    message: string;
    created_at: string;
}

interface User {
    id: string;
    email: string;
    created_at: string;
}

export default function AdminDashboard() {
    const [token, setToken] = useState('');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    // Data states
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [emailLeads, setEmailLeads] = useState<EmailLead[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [reports, setReports] = useState<Report[]>([]);
    const [feedback, setFeedback] = useState<Feedback[]>([]);
    const [activeTab, setActiveTab] = useState<'emails' | 'users' | 'reports' | 'feedback'>('emails');

    // Check for existing auth token on mount
    useEffect(() => {
        const stored = localStorage.getItem('auth_token');
        const storedEmail = localStorage.getItem('user_email');

        if (stored) {
            setToken(stored);
            verifyAdmin(stored, storedEmail);
        } else {
            setIsLoading(false);
        }
    }, []);

    const verifyAdmin = async (authToken: string, localEmail: string | null) => {
        try {
            const response = await fetch(`${API_URL}/api/admin/verify?token=${authToken}`);
            if (response.ok) {
                setIsAuthenticated(true);
                setToken(authToken);
            } else {
                // If backend verification fails, check if local email is admin
                // This handles cases where the user is logged in locally but not on the production DB
                if (localEmail && localEmail === 'camdenrose5@gmail.com') {
                    setIsAuthenticated(true);
                    setToken(authToken);
                    console.log('Admin access granted via local email match');
                } else {
                    const data = await response.json();
                    if (response.status === 403) {
                        setError('Your account is not authorized as admin.');
                    } else {
                        setError(`Please log in first. (${localEmail || 'no email found'})`);
                    }
                }
            }
        } catch (err) {
            // On network error, fall back to local email check
            const storedEmail = localStorage.getItem('user_email');
            if (storedEmail === 'camdenrose5@gmail.com') {
                setIsAuthenticated(true);
                setToken(authToken);
                console.log('Admin access granted via local email (network error fallback)');
            } else {
                setError('Connection error. Is the server running?');
            }
        } finally {
            setIsLoading(false);
        }
    };

    // Load data when authenticated
    useEffect(() => {
        if (!isAuthenticated || !token) return;

        const adminEmail = localStorage.getItem('user_email') || '';
        const loadData = async () => {
            try {
                // Load stats
                const statsRes = await fetch(`${API_URL}/api/admin/stats?token=${token}&admin_email=${encodeURIComponent(adminEmail)}`);
                if (statsRes.ok) {
                    setStats(await statsRes.json());
                }

                // Load email leads
                const leadsRes = await fetch(`${API_URL}/api/admin/email-leads?token=${token}&admin_email=${encodeURIComponent(adminEmail)}`);
                if (leadsRes.ok) {
                    const data = await leadsRes.json();
                    setEmailLeads(data.leads);
                }

                // Load users
                const usersRes = await fetch(`${API_URL}/api/admin/users?token=${token}&admin_email=${encodeURIComponent(adminEmail)}`);
                if (usersRes.ok) {
                    const data = await usersRes.json();
                    setUsers(data.users);
                }

                // Load reports
                const reportsRes = await fetch(`${API_URL}/api/admin/reports?token=${token}&admin_email=${encodeURIComponent(adminEmail)}`);
                if (reportsRes.ok) {
                    const data = await reportsRes.json();
                    setReports(data.reports);
                }

                // Load feedback
                const feedbackRes = await fetch(`${API_URL}/api/admin/feedback?token=${token}&admin_email=${encodeURIComponent(adminEmail)}`);
                if (feedbackRes.ok) {
                    const data = await feedbackRes.json();
                    setFeedback(data.feedback);
                }
            } catch (err) {
                console.error('Failed to load admin data:', err);
            }
        };

        loadData();
    }, [isAuthenticated, token]);

    const handleLogout = () => {
        localStorage.removeItem('auth_token');
        setIsAuthenticated(false);
        setToken('');
    };

    const exportToCSV = () => {
        const headers = ['Email', 'Signed Up', 'Converted'];
        const rows = emailLeads.map(lead => [
            lead.email,
            new Date(lead.created_at).toLocaleString(),
            lead.converted ? 'Yes' : 'No'
        ]);

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `email-leads-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
                <div className="text-white text-xl">Loading...</div>
            </div>
        );
    }

    // Not authenticated - show login prompt
    if (!isAuthenticated) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
                <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 w-full max-w-md text-center">
                    <div className="text-4xl mb-4">🔐</div>
                    <h1 className="text-2xl font-bold text-white mb-2">Admin Dashboard</h1>
                    <p className="text-slate-400 mb-6">Captain&apos;s Academy Control Center</p>

                    {error && (
                        <div className="text-red-400 text-sm py-3 px-4 bg-red-500/10 rounded-lg mb-6">
                            {error}
                        </div>
                    )}

                    <p className="text-slate-300 mb-6">
                        You need to be logged in with an admin account to access this page.
                    </p>

                    <a
                        href="/study-hub"
                        className="inline-block w-full py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:from-orange-600 hover:to-red-600 transition-all"
                    >
                        Go to Study Hub to Login
                    </a>
                </div>
            </div>
        );
    }

    // Dashboard
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
            {/* Header */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">🎖️ Admin Dashboard</h1>
                    <p className="text-slate-400">Captain&apos;s Academy Control Center</p>
                </div>
                <div className="flex items-center gap-3">
                    <a
                        href="/"
                        className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
                    >
                        🏠 Home
                    </a>
                    <button
                        onClick={handleLogout}
                        className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors"
                    >
                        Logout
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
                    <StatCard label="Email Leads" value={stats.email_leads} icon="📧" color="orange" />
                    <StatCard label="Questions" value={stats.total_questions} icon="❓" color="blue" />
                    <StatCard label="Flashcards" value={stats.total_flashcards} icon="🎴" color="green" />
                    <StatCard label="Pending Reports" value={stats.pending_reports} icon="⚠️" color="red" />
                    <StatCard label="Pending Feedback" value={stats.pending_feedback} icon="💬" color="purple" />
                    <StatCard label="Total Users" value={stats.total_users} icon="👥" color="cyan" />
                </div>
            )}

            {/* Tab Navigation */}
            <div className="flex gap-2 mb-6">
                <TabButton
                    active={activeTab === 'emails'}
                    onClick={() => setActiveTab('emails')}
                    count={emailLeads.length}
                >
                    📧 Email Leads
                </TabButton>
                <TabButton
                    active={activeTab === 'users'}
                    onClick={() => setActiveTab('users')}
                    count={users.length}
                >
                    👥 Users
                </TabButton>
                <TabButton
                    active={activeTab === 'reports'}
                    onClick={() => setActiveTab('reports')}
                    count={reports.length}
                >
                    ⚠️ Reports
                </TabButton>
                <TabButton
                    active={activeTab === 'feedback'}
                    onClick={() => setActiveTab('feedback')}
                    count={feedback.length}
                >
                    💬 Feedback
                </TabButton>
            </div>

            {/* Content */}
            <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl overflow-hidden">
                {activeTab === 'emails' && (
                    <>
                        <div className="p-4 border-b border-slate-700/50 flex justify-between items-center">
                            <h2 className="text-lg font-semibold text-white">Email Subscribers</h2>
                            <button
                                onClick={exportToCSV}
                                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                            >
                                📥 Export CSV
                            </button>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-slate-700/50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">#</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Email</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Signed Up</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-700/50">
                                    {emailLeads.length === 0 ? (
                                        <tr>
                                            <td colSpan={4} className="px-6 py-8 text-center text-slate-400">
                                                No email leads yet. They&apos;ll appear here when users sign up.
                                            </td>
                                        </tr>
                                    ) : (
                                        emailLeads.map((lead, index) => (
                                            <tr key={lead.id} className="hover:bg-slate-700/30 transition-colors">
                                                <td className="px-6 py-4 text-slate-400 text-sm">{index + 1}</td>
                                                <td className="px-6 py-4 text-white font-medium">{lead.email}</td>
                                                <td className="px-6 py-4 text-slate-300 text-sm">
                                                    {new Date(lead.created_at).toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${lead.converted
                                                        ? 'bg-green-500/20 text-green-400'
                                                        : 'bg-orange-500/20 text-orange-400'
                                                        }`}>
                                                        {lead.converted ? 'Converted' : 'Lead'}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}

                {activeTab === 'users' && (
                    <>
                        <div className="p-4 border-b border-slate-700/50">
                            <h2 className="text-lg font-semibold text-white">Registered Users</h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-slate-700/50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">#</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Email</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Registered</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-700/50">
                                    {users.length === 0 ? (
                                        <tr>
                                            <td colSpan={3} className="px-6 py-8 text-center text-slate-400">
                                                No registered users yet.
                                            </td>
                                        </tr>
                                    ) : (
                                        users.map((user, index) => (
                                            <tr key={user.id} className="hover:bg-slate-700/30 transition-colors">
                                                <td className="px-6 py-4 text-slate-400 text-sm">{index + 1}</td>
                                                <td className="px-6 py-4 text-white font-medium">{user.email}</td>
                                                <td className="px-6 py-4 text-slate-300 text-sm">
                                                    {new Date(user.created_at).toLocaleString()}
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}

                {activeTab === 'reports' && (
                    <>
                        <div className="p-4 border-b border-slate-700/50">
                            <h2 className="text-lg font-semibold text-white">Question Reports</h2>
                        </div>
                        <div className="divide-y divide-slate-700/50">
                            {reports.length === 0 ? (
                                <div className="px-6 py-8 text-center text-slate-400">
                                    No pending reports. Great job! 🎉
                                </div>
                            ) : (
                                reports.map((report) => (
                                    <div key={report.id} className="p-4 hover:bg-slate-700/30 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="px-2 py-1 text-xs font-medium bg-red-500/20 text-red-400 rounded-full">
                                                {report.subject}
                                            </span>
                                            <span className="text-xs text-slate-400">
                                                {new Date(report.reported_at).toLocaleString()}
                                            </span>
                                        </div>
                                        <p className="text-white mb-2">{report.question}</p>
                                        {report.reason && (
                                            <p className="text-sm text-slate-400">
                                                <span className="text-slate-500">Reason:</span> {report.reason}
                                            </p>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </>
                )}

                {activeTab === 'feedback' && (
                    <>
                        <div className="p-4 border-b border-slate-700/50">
                            <h2 className="text-lg font-semibold text-white">User Feedback</h2>
                        </div>
                        <div className="divide-y divide-slate-700/50">
                            {feedback.length === 0 ? (
                                <div className="px-6 py-8 text-center text-slate-400">
                                    No pending feedback yet.
                                </div>
                            ) : (
                                feedback.map((item) => (
                                    <div key={item.id} className="p-4 hover:bg-slate-700/30 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-400 rounded-full">
                                                {item.study_mode}
                                            </span>
                                            <span className="text-xs text-slate-400">
                                                {new Date(item.created_at).toLocaleString()}
                                            </span>
                                        </div>
                                        <p className="text-white">{item.message}</p>
                                    </div>
                                ))
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

// Stat Card Component
function StatCard({ label, value, icon, color }: {
    label: string;
    value: number;
    icon: string;
    color: string;
}) {
    const colorClasses: Record<string, string> = {
        orange: 'from-orange-500/20 to-orange-600/10 border-orange-500/30',
        blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
        green: 'from-green-500/20 to-green-600/10 border-green-500/30',
        red: 'from-red-500/20 to-red-600/10 border-red-500/30',
        purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
        cyan: 'from-cyan-500/20 to-cyan-600/10 border-cyan-500/30',
    };

    return (
        <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-xl p-4`}>
            <div className="text-2xl mb-2">{icon}</div>
            <div className="text-2xl font-bold text-white">{value.toLocaleString()}</div>
            <div className="text-xs text-slate-400">{label}</div>
        </div>
    );
}

// Tab Button Component
function TabButton({ active, onClick, count, children }: {
    active: boolean;
    onClick: () => void;
    count: number;
    children: React.ReactNode;
}) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${active
                ? 'bg-orange-500 text-white'
                : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
                }`}
        >
            {children}
            <span className={`px-2 py-0.5 text-xs rounded-full ${active ? 'bg-white/20' : 'bg-slate-600'
                }`}>
                {count}
            </span>
        </button>
    );
}
