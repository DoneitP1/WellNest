import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useState, useEffect } from 'react';
import api from '../api';
import {
    LogOut, Activity, Sun, Moon, Home, Users, Timer,
    Dumbbell, BookOpen, Trophy, ChefHat, TrendingDown
} from 'lucide-react';

export default function Layout({ children }) {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const [userStats, setUserStats] = useState(null);

    useEffect(() => {
        fetchUserStats();
    }, []);

    const fetchUserStats = async () => {
        try {
            const response = await api.get('/users/me');
            setUserStats(response.data);
        } catch (e) {
            console.error('Failed to fetch user stats:', e);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navItems = [
        { path: '/dashboard', icon: Home, label: 'Dashboard' },
        { path: '/social', icon: Users, label: 'Social' },
        { path: '/fasting', icon: Timer, label: 'Fasting' },
        { path: '/workouts', icon: Dumbbell, label: 'Training' },
        { path: '/deficit', icon: TrendingDown, label: 'Deficit' },
        { path: '/recipes', icon: ChefHat, label: 'Recipes' },
        { path: '/blog', icon: BookOpen, label: 'Blog' },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-300">
            {/* Top Navigation */}
            <nav className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 transition-colors duration-300 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <div className="flex items-center">
                            <Link to="/" className="text-xl font-bold bg-gradient-to-r from-teal-500 to-emerald-500 bg-clip-text text-transparent flex items-center gap-2">
                                <Activity className="text-teal-500" />
                                WellNest
                            </Link>
                        </div>

                        {/* User Stats (XP & Level) */}
                        {userStats && (
                            <div className="hidden md:flex items-center gap-4">
                                <div className="flex items-center gap-2 bg-gradient-to-r from-purple-500/10 to-pink-500/10 px-4 py-2 rounded-xl">
                                    <Trophy className="w-5 h-5 text-yellow-500" />
                                    <div>
                                        <p className="text-xs text-slate-500 dark:text-slate-400">Level {userStats.level || 1}</p>
                                        <p className="text-sm font-bold text-purple-600 dark:text-purple-400">
                                            {userStats.xp || 0} XP
                                        </p>
                                    </div>
                                </div>

                                {userStats.streak_days > 0 && (
                                    <div className="flex items-center gap-1 text-orange-500">
                                        <span className="text-lg">🔥</span>
                                        <span className="font-bold">{userStats.streak_days}</span>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Right Side */}
                        <div className="flex items-center gap-4">
                            <button
                                onClick={toggleTheme}
                                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition"
                            >
                                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                            </button>

                            {user && (
                                <div className="flex items-center gap-4">
                                    <span className="text-slate-500 dark:text-slate-400 text-xs hidden lg:block">
                                        {user.email}
                                    </span>
                                    <button
                                        onClick={handleLogout}
                                        className="p-2 text-slate-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition"
                                    >
                                        <LogOut size={18} />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="border-t border-slate-200 dark:border-slate-700">
                    <div className="max-w-7xl mx-auto px-4">
                        <div className="flex gap-1 overflow-x-auto py-2 scrollbar-hide">
                            {navItems.map(item => (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium transition ${
                                        isActive(item.path)
                                            ? 'bg-teal-500 text-white'
                                            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'
                                    }`}
                                >
                                    <item.icon size={18} />
                                    {item.label}
                                </Link>
                            ))}
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                {children}
            </main>

            {/* Mobile Bottom Navigation */}
            <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 md:hidden z-50">
                <div className="flex justify-around py-2">
                    {navItems.slice(0, 5).map(item => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex flex-col items-center p-2 ${
                                isActive(item.path)
                                    ? 'text-teal-500'
                                    : 'text-slate-500 dark:text-slate-400'
                            }`}
                        >
                            <item.icon size={20} />
                            <span className="text-xs mt-1">{item.label}</span>
                        </Link>
                    ))}
                </div>
            </nav>

            {/* Spacer for mobile bottom nav */}
            <div className="h-20 md:hidden" />
        </div>
    );
}
