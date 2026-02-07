import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import api from '../api';
import {
    Timer, Play, Square, Clock, Flame, Target,
    TrendingUp, Award, Loader2, Check, History
} from 'lucide-react';

export default function Fasting() {
    const [currentFast, setCurrentFast] = useState(null);
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedType, setSelectedType] = useState('16:8');
    const [timeRemaining, setTimeRemaining] = useState(null);
    const [starting, setStarting] = useState(false);
    const [ending, setEnding] = useState(false);

    const fastingTypes = [
        { value: '16:8', hours: 16, eating: 8, description: 'Most popular for beginners' },
        { value: '18:6', hours: 18, eating: 6, description: 'Intermediate level' },
        { value: '20:4', hours: 20, eating: 4, description: 'Advanced - Warrior Diet' },
        { value: 'OMAD', hours: 23, eating: 1, description: 'One Meal A Day' },
    ];

    useEffect(() => {
        fetchData();
    }, []);

    useEffect(() => {
        if (currentFast?.is_active) {
            const interval = setInterval(() => {
                const remaining = currentFast.time_remaining_seconds - 1;
                setTimeRemaining(remaining > 0 ? remaining : 0);
            }, 1000);
            return () => clearInterval(interval);
        }
    }, [currentFast]);

    const fetchData = async () => {
        try {
            const [currentRes, statsRes, historyRes] = await Promise.all([
                api.get('/fasting/current'),
                api.get('/fasting/stats'),
                api.get('/fasting/history?limit=10')
            ]);

            setCurrentFast(currentRes.data);
            setStats(statsRes.data);
            setHistory(historyRes.data);

            if (currentRes.data?.time_remaining_seconds) {
                setTimeRemaining(currentRes.data.time_remaining_seconds);
            }
        } catch (error) {
            console.error('Failed to fetch fasting data:', error);
        } finally {
            setLoading(false);
        }
    };

    const startFast = async () => {
        setStarting(true);
        try {
            const response = await api.post('/fasting/start', {
                fasting_type: selectedType
            });
            setCurrentFast(response.data);
            setTimeRemaining(response.data.time_remaining_seconds);
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to start fast');
        } finally {
            setStarting(false);
        }
    };

    const endFast = async () => {
        setEnding(true);
        try {
            const response = await api.post('/fasting/end', {});
            setCurrentFast(null);
            setTimeRemaining(null);
            fetchData(); // Refresh stats
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to end fast');
        } finally {
            setEnding(false);
        }
    };

    const formatTime = (seconds) => {
        if (!seconds || seconds < 0) return '00:00:00';
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const getProgress = () => {
        if (!currentFast) return 0;
        return Math.min(100, currentFast.progress_percentage);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <Timer className="w-8 h-8 text-teal-500" />
                <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
                    Intermittent Fasting
                </h1>
            </div>

            {/* Main Timer Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-br from-slate-800 to-slate-900 dark:from-slate-700 dark:to-slate-800 p-8 rounded-3xl text-white"
            >
                {currentFast?.is_active ? (
                    <>
                        {/* Active Fast */}
                        <div className="text-center">
                            <p className="text-slate-400 mb-2">
                                {currentFast.fasting_type} Fast in Progress
                            </p>

                            {/* Circular Progress */}
                            <div className="relative w-64 h-64 mx-auto my-6">
                                <svg className="w-full h-full transform -rotate-90">
                                    {/* Background circle */}
                                    <circle
                                        cx="128"
                                        cy="128"
                                        r="110"
                                        fill="none"
                                        stroke="rgba(255,255,255,0.1)"
                                        strokeWidth="12"
                                    />
                                    {/* Progress circle */}
                                    <circle
                                        cx="128"
                                        cy="128"
                                        r="110"
                                        fill="none"
                                        stroke="url(#gradient)"
                                        strokeWidth="12"
                                        strokeLinecap="round"
                                        strokeDasharray={691.15}
                                        strokeDashoffset={691.15 - (691.15 * getProgress()) / 100}
                                        className="transition-all duration-1000"
                                    />
                                    <defs>
                                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                            <stop offset="0%" stopColor="#14b8a6" />
                                            <stop offset="100%" stopColor="#22c55e" />
                                        </linearGradient>
                                    </defs>
                                </svg>

                                {/* Timer Display */}
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <p className="text-sm text-slate-400 mb-1">Time Remaining</p>
                                    <p className="text-4xl font-mono font-bold">
                                        {formatTime(timeRemaining)}
                                    </p>
                                    <p className="text-lg text-teal-400 mt-2">
                                        {getProgress().toFixed(1)}%
                                    </p>
                                </div>
                            </div>

                            <p className="text-slate-400 text-sm">
                                Started: {new Date(currentFast.start_time).toLocaleTimeString()}
                            </p>
                            <p className="text-slate-400 text-sm">
                                Goal: {new Date(currentFast.planned_end_time).toLocaleTimeString()}
                            </p>

                            <button
                                onClick={endFast}
                                disabled={ending}
                                className="mt-6 flex items-center gap-2 px-8 py-3 bg-red-500 hover:bg-red-600 rounded-xl font-semibold mx-auto transition disabled:opacity-50"
                            >
                                {ending ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Square size={20} />
                                )}
                                End Fast
                            </button>
                        </div>
                    </>
                ) : (
                    <>
                        {/* No Active Fast */}
                        <div className="text-center">
                            <Clock className="w-16 h-16 mx-auto text-slate-500 mb-4" />
                            <h2 className="text-2xl font-bold mb-2">Ready to Start Fasting?</h2>
                            <p className="text-slate-400 mb-6">
                                Choose your fasting window and begin
                            </p>

                            {/* Fasting Type Selection */}
                            <div className="grid grid-cols-2 gap-3 mb-6">
                                {fastingTypes.map(type => (
                                    <button
                                        key={type.value}
                                        onClick={() => setSelectedType(type.value)}
                                        className={`p-4 rounded-xl text-left transition ${
                                            selectedType === type.value
                                                ? 'bg-teal-500/20 border-2 border-teal-500'
                                                : 'bg-white/5 border-2 border-transparent hover:bg-white/10'
                                        }`}
                                    >
                                        <p className="font-bold text-xl">{type.value}</p>
                                        <p className="text-sm text-slate-400">
                                            {type.hours}h fast / {type.eating}h eat
                                        </p>
                                        <p className="text-xs text-slate-500 mt-1">
                                            {type.description}
                                        </p>
                                    </button>
                                ))}
                            </div>

                            <button
                                onClick={startFast}
                                disabled={starting}
                                className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 rounded-xl font-semibold mx-auto transition disabled:opacity-50"
                            >
                                {starting ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Play size={20} />
                                )}
                                Start {selectedType} Fast
                            </button>
                        </div>
                    </>
                )}
            </motion.div>

            {/* Stats Grid */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Target size={16} />
                            <span className="text-sm">Total Fasts</span>
                        </div>
                        <p className="text-2xl font-bold text-slate-800 dark:text-white">
                            {stats.total_fasts}
                        </p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Check size={16} />
                            <span className="text-sm">Completed</span>
                        </div>
                        <p className="text-2xl font-bold text-green-500">
                            {stats.completed_fasts}
                        </p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Clock size={16} />
                            <span className="text-sm">Total Hours</span>
                        </div>
                        <p className="text-2xl font-bold text-teal-500">
                            {stats.total_hours_fasted}h
                        </p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Flame size={16} />
                            <span className="text-sm">Streak</span>
                        </div>
                        <p className="text-2xl font-bold text-orange-500">
                            {stats.current_streak} 🔥
                        </p>
                    </div>
                </div>
            )}

            {/* Fasting History */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
                <div className="p-4 border-b border-slate-200 dark:border-slate-700 flex items-center gap-2">
                    <History size={20} className="text-slate-500" />
                    <h3 className="font-semibold text-slate-800 dark:text-white">Recent Fasts</h3>
                </div>

                {history.length === 0 ? (
                    <div className="p-8 text-center text-slate-500">
                        No fasting history yet. Start your first fast!
                    </div>
                ) : (
                    <div className="divide-y divide-slate-100 dark:divide-slate-700">
                        {history.map(fast => (
                            <div
                                key={fast.id}
                                className="p-4 flex items-center justify-between"
                            >
                                <div>
                                    <p className="font-medium text-slate-800 dark:text-white">
                                        {fast.fasting_type}
                                    </p>
                                    <p className="text-sm text-slate-500">
                                        {new Date(fast.start_time).toLocaleDateString()}
                                    </p>
                                </div>

                                <div className="text-right">
                                    <p className={`font-semibold ${
                                        fast.completed ? 'text-green-500' : fast.cancelled ? 'text-red-500' : 'text-yellow-500'
                                    }`}>
                                        {fast.completed ? 'Completed' : fast.cancelled ? 'Cancelled' : 'In Progress'}
                                    </p>
                                    <p className="text-sm text-slate-500">
                                        {fast.actual_hours?.toFixed(1) || fast.target_hours}h
                                    </p>
                                </div>

                                <div className="w-24">
                                    <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full rounded-full ${
                                                fast.completed ? 'bg-green-500' : fast.cancelled ? 'bg-red-500' : 'bg-teal-500'
                                            }`}
                                            style={{ width: `${fast.progress_percentage}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
