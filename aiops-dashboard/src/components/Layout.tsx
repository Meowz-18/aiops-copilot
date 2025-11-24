import React from 'react';
import { LayoutDashboard, LogOut, User } from 'lucide-react';

interface LayoutProps {
    children: React.ReactNode;
    user?: { name: string; email: string };
    onLogout?: () => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, user, onLogout }) => {
    return (
        <div className="min-h-screen flex flex-col bg-gray-50">
            <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-10">
                <div className="flex items-center gap-2">
                    <LayoutDashboard className="w-6 h-6 text-blue-600" />
                    <h1 className="text-xl font-bold text-gray-900">AIOps Incident Co-Pilot</h1>
                </div>
                {user && (
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                            <User className="w-4 h-4" />
                            <span>{user.name}</span>
                        </div>
                        <button
                            onClick={onLogout}
                            className="p-2 hover:bg-gray-100 rounded-full text-gray-500 transition-colors"
                            title="Logout"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                )}
            </header>
            <main className="flex-1 p-6 overflow-auto">
                <div className="max-w-7xl mx-auto">
                    {children}
                </div>
            </main>
        </div>
    );
};
