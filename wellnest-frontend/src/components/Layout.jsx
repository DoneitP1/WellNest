import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { LogOut, Activity, Sun, Moon } from 'lucide-react';

export default function Layout({ children }) {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300">
            <nav className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 transition-colors duration-300">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center">
                            <Link to="/" className="text-xl font-bold bg-gradient-to-r from-teal-500 to-emerald-500 bg-clip-text text-transparent flex items-center gap-2">
                                <Activity className="text-teal-500" />
                                WellNest
                            </Link>
                        </div>

                        <div className="flex items-center gap-6">
                            <button
                                onClick={toggleTheme}
                                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition"
                            >
                                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                            </button>

                            {user && (
                                <>
                                    <Link to="/" className="text-slate-600 dark:text-gray-300 hover:text-teal-500 dark:hover:text-teal-400 transition text-sm font-medium">Dashboard</Link>
                                    <div className="flex items-center gap-4">
                                        <span className="text-slate-500 dark:text-slate-400 text-xs hidden md:block">{user.email}</span>
                                        <button
                                            onClick={handleLogout}
                                            className="text-slate-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition"
                                        >
                                            <LogOut size={18} />
                                        </button>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                {children}
            </main>
        </div>
    );
}
