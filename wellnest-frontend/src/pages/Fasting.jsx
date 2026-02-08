import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import api from '../api';
import {
    Timer, Play, Square, Clock, Flame, Target,
    TrendingUp, Award, Loader2, Check, History, Info
} from 'lucide-react';

export default function Fasting() {
    const [currentFast, setCurrentFast] = useState(null);
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedType, setSelectedType] = useState('16:8');
    const [elapsedSeconds, setElapsedSeconds] = useState(0);
    const [starting, setStarting] = useState(false);
    const [ending, setEnding] = useState(false);
    const intervalRef = useRef(null);

    const fastingTypes = [
        { value: '16:8', hours: 16, eating: 8, description: 'Most popular for beginners' },
        { value: '18:6', hours: 18, eating: 6, description: 'Intermediate level' },
        { value: '20:4', hours: 20, eating: 4, description: 'Advanced - Warrior Diet' },
        { value: 'OMAD', hours: 23, eating: 1, description: 'One Meal A Day' },
    ];

    useEffect(() => {
        fetchData();
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, []);

    // Real-time timer effect
    useEffect(() => {
        if (currentFast?.is_active && currentFast?.start_time) {
            // Calculate initial elapsed time
            const startTime = new Date(currentFast.start_time).getTime();
            const now = Date.now();
            const initialElapsed = Math.floor((now - startTime) / 1000);
            setElapsedSeconds(initialElapsed);

            // Clear any existing interval
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }

            // Start real-time counter
            intervalRef.current = setInterval(() => {
                setElapsedSeconds(prev => prev + 1);
            }, 1000);

            return () => {
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                }
            };
        } else {
            setElapsedSeconds(0);
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        }
    }, [currentFast?.is_active, currentFast?.start_time]);

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
        } catch (error) {
            console.error('Failed to fetch fasting data:', error);
            // Set default values if API fails
            setStats({
                total_fasts: 0,
                completed_fasts: 0,
                total_hours_fasted: 0,
                current_streak: 0
            });
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
            setElapsedSeconds(0);
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to start fast');
        } finally {
            setStarting(false);
        }
    };

    const endFast = async () => {
        setEnding(true);
        try {
            await api.post('/fasting/end', {});
            setCurrentFast(null);
            setElapsedSeconds(0);
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

    const getTargetSeconds = () => {
        if (!currentFast) return 0;
        const type = fastingTypes.find(t => t.value === currentFast.fasting_type);
        return (type?.hours || 16) * 3600;
    };

    const getProgress = () => {
        const targetSeconds = getTargetSeconds();
        if (!targetSeconds) return 0;
        return Math.min(100, (elapsedSeconds / targetSeconds) * 100);
    };

    const getTimeRemaining = () => {
        const targetSeconds = getTargetSeconds();
        const remaining = targetSeconds - elapsedSeconds;
        return remaining > 0 ? remaining : 0;
    };

    const isCompleted = () => {
        return elapsedSeconds >= getTargetSeconds();
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
                                        stroke={isCompleted() ? "#22c55e" : "url(#gradient)"}
                                        strokeWidth="12"
                                        strokeLinecap="round"
                                        strokeDasharray={691.15}
                                        strokeDashoffset={691.15 - (691.15 * getProgress()) / 100}
                                        className="transition-all duration-300"
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
                                    {isCompleted() ? (
                                        <>
                                            <Check className="w-12 h-12 text-green-500 mb-2" />
                                            <p className="text-lg text-green-400 font-bold">Goal Reached!</p>
                                            <p className="text-3xl font-mono font-bold mt-1">
                                                {formatTime(elapsedSeconds)}
                                            </p>
                                        </>
                                    ) : (
                                        <>
                                            <p className="text-sm text-slate-400 mb-1">Time Remaining</p>
                                            <p className="text-4xl font-mono font-bold">
                                                {formatTime(getTimeRemaining())}
                                            </p>
                                            <p className="text-lg text-teal-400 mt-2">
                                                {getProgress().toFixed(1)}%
                                            </p>
                                        </>
                                    )}
                                </div>
                            </div>

                            {/* Elapsed time display */}
                            <div className="bg-white/10 rounded-xl p-3 mb-4">
                                <p className="text-sm text-slate-400">Fasting for</p>
                                <p className="text-2xl font-mono font-bold text-teal-400">
                                    {formatTime(elapsedSeconds)}
                                </p>
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
                                className={`mt-6 flex items-center gap-2 px-8 py-3 rounded-xl font-semibold mx-auto transition disabled:opacity-50 ${
                                    isCompleted()
                                        ? 'bg-green-500 hover:bg-green-600'
                                        : 'bg-red-500 hover:bg-red-600'
                                }`}
                            >
                                {ending ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : isCompleted() ? (
                                    <Check size={20} />
                                ) : (
                                    <Square size={20} />
                                )}
                                {isCompleted() ? 'Complete Fast' : 'End Fast Early'}
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
                            {stats.total_fasts || 0}
                        </p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Check size={16} />
                            <span className="text-sm">Completed</span>
                        </div>
                        <p className="text-2xl font-bold text-green-500">
                            {stats.completed_fasts || 0}
                        </p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Clock size={16} />
                            <span className="text-sm">Total Hours</span>
                        </div>
                        <p className="text-2xl font-bold text-teal-500">
                            {stats.total_hours_fasted || 0}h
                        </p>
                    </div>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Flame size={16} />
                            <span className="text-sm">Streak</span>
                        </div>
                        <p className="text-2xl font-bold text-orange-500">
                            {stats.current_streak || 0} 🔥
                        </p>
                    </div>
                </div>
            )}

            {/* Info Card */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-blue-50 dark:bg-blue-500/10 rounded-xl p-4 flex gap-3"
            >
                <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-700 dark:text-blue-300">
                    <p className="font-medium mb-1">Benefits of Intermittent Fasting</p>
                    <p className="text-blue-600 dark:text-blue-400">
                        IF can help with weight loss, improved insulin sensitivity, cellular repair (autophagy),
                        and mental clarity. Start with 16:8 and gradually increase your fasting window.
                    </p>
                </div>
            </motion.div>

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
                                            style={{ width: `${Math.min(fast.progress_percentage || 0, 100)}%` }}
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
