import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';
import {
    LogOut, Activity, Sun, Moon, Home, Users, Timer,
    Dumbbell, BookOpen, Trophy, ChefHat, TrendingDown,
    HelpCircle, X, Star, Zap, Target, Award
} from 'lucide-react';

export default function Layout({ children }) {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const location = useLocation();
    const [userStats, setUserStats] = useState(null);
    const [showXPInfo, setShowXPInfo] = useState(false);

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

    // XP Level thresholds
    const levelThresholds = [0, 100, 250, 500, 850, 1300, 1900, 2600, 3500, 4600, 6000];
    const currentLevel = userStats?.level || 1;
    const currentXP = userStats?.xp || 0;
    const currentLevelXP = levelThresholds[currentLevel - 1] || 0;
    const nextLevelXP = levelThresholds[currentLevel] || levelThresholds[levelThresholds.length - 1];
    const xpProgress = ((currentXP - currentLevelXP) / (nextLevelXP - currentLevelXP)) * 100;

    // XP Earning activities
    const xpActivities = [
        { action: 'Log a meal', xp: 10, icon: '🍽️' },
        { action: 'Complete a workout', xp: 25, icon: '💪' },
        { action: 'Complete a fast', xp: 30, icon: '⏱️' },
        { action: '7-day streak', xp: 50, icon: '🔥' },
        { action: 'First meal of the day', xp: 5, icon: '🌅' },
        { action: 'Log water intake', xp: 3, icon: '💧' },
        { action: 'Share meal publicly', xp: 15, icon: '📸' },
    ];

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
                                <div className="relative">
                                    <div
                                        className="flex items-center gap-2 bg-gradient-to-r from-purple-500/10 to-pink-500/10 px-4 py-2 rounded-xl cursor-pointer hover:from-purple-500/20 hover:to-pink-500/20 transition"
                                        onClick={() => setShowXPInfo(!showXPInfo)}
                                    >
                                        <Trophy className="w-5 h-5 text-yellow-500" />
                                        <div>
                                            <p className="text-xs text-slate-500 dark:text-slate-400">Level {currentLevel}</p>
                                            <p className="text-sm font-bold text-purple-600 dark:text-purple-400">
                                                {currentXP} XP
                                            </p>
                                        </div>
                                        <HelpCircle className="w-4 h-4 text-slate-400 hover:text-purple-500 ml-1" />
                                    </div>

                                    {/* XP Progress Bar */}
                                    <div className="absolute -bottom-1 left-2 right-2 h-1 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(xpProgress, 100)}%` }}
                                        />
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

            {/* XP Info Modal */}
            <AnimatePresence>
                {showXPInfo && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4"
                        onClick={() => setShowXPInfo(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white dark:bg-slate-800 rounded-2xl w-full max-w-md overflow-hidden"
                            onClick={e => e.stopPropagation()}
                        >
                            {/* Header */}
                            <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-6 text-white">
                                <div className="flex items-center justify-between mb-4">
                                    <h2 className="text-xl font-bold flex items-center gap-2">
                                        <Star className="w-6 h-6" />
                                        XP & Leveling System
                                    </h2>
                                    <button
                                        onClick={() => setShowXPInfo(false)}
                                        className="p-1 hover:bg-white/20 rounded-full transition"
                                    >
                                        <X size={20} />
                                    </button>
                                </div>

                                {/* Current Progress */}
                                <div className="bg-white/20 rounded-xl p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-sm opacity-80">Level {currentLevel}</span>
                                        <span className="text-sm opacity-80">Level {currentLevel + 1}</span>
                                    </div>
                                    <div className="h-3 bg-white/30 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-white rounded-full transition-all duration-500"
                                            style={{ width: `${Math.min(xpProgress, 100)}%` }}
                                        />
                                    </div>
                                    <p className="text-center text-sm mt-2 opacity-90">
                                        {currentXP} / {nextLevelXP} XP ({Math.round(xpProgress)}%)
                                    </p>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="p-6">
                                {/* How it works */}
                                <div className="mb-6">
                                    <h3 className="font-semibold text-slate-800 dark:text-white mb-3 flex items-center gap-2">
                                        <Zap className="w-5 h-5 text-yellow-500" />
                                        How to Earn XP
                                    </h3>
                                    <div className="space-y-2">
                                        {xpActivities.map((activity, idx) => (
                                            <div
                                                key={idx}
                                                className="flex items-center justify-between bg-slate-50 dark:bg-slate-700/50 px-3 py-2 rounded-lg"
                                            >
                                                <div className="flex items-center gap-2">
                                                    <span className="text-lg">{activity.icon}</span>
                                                    <span className="text-sm text-slate-700 dark:text-slate-300">
                                                        {activity.action}
                                                    </span>
                                                </div>
                                                <span className="text-sm font-bold text-purple-500">
                                                    +{activity.xp} XP
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Level Benefits */}
                                <div>
                                    <h3 className="font-semibold text-slate-800 dark:text-white mb-3 flex items-center gap-2">
                                        <Award className="w-5 h-5 text-teal-500" />
                                        Level Benefits
                                    </h3>
                                    <div className="text-sm text-slate-600 dark:text-slate-400 space-y-2">
                                        <p className="flex items-center gap-2">
                                            <span className="w-2 h-2 bg-teal-500 rounded-full"></span>
                                            Unlock exclusive achievements and badges
                                        </p>
                                        <p className="flex items-center gap-2">
                                            <span className="w-2 h-2 bg-teal-500 rounded-full"></span>
                                            Show your dedication on your profile
                                        </p>
                                        <p className="flex items-center gap-2">
                                            <span className="w-2 h-2 bg-teal-500 rounded-full"></span>
                                            Track your health journey progress
                                        </p>
                                        <p className="flex items-center gap-2">
                                            <span className="w-2 h-2 bg-teal-500 rounded-full"></span>
                                            Compete with friends on leaderboards
                                        </p>
                                    </div>
                                </div>

                                {/* Level Thresholds */}
                                <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
                                    <h4 className="text-xs text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide">
                                        Level Requirements
                                    </h4>
                                    <div className="flex flex-wrap gap-2">
                                        {levelThresholds.slice(1, 8).map((xp, idx) => (
                                            <div
                                                key={idx}
                                                className={`px-2 py-1 rounded text-xs ${
                                                    currentLevel > idx + 1
                                                        ? 'bg-teal-500 text-white'
                                                        : currentLevel === idx + 1
                                                            ? 'bg-purple-500 text-white'
                                                            : 'bg-slate-100 dark:bg-slate-700 text-slate-500'
                                                }`}
                                            >
                                                L{idx + 2}: {xp} XP
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

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
