import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../api';
import {
    TrendingDown, TrendingUp, Flame, Activity, Dumbbell,
    Target, Calendar, Loader2, Info, ChevronLeft, ChevronRight
} from 'lucide-react';

export default function Deficit() {
    const [data, setData] = useState(null);
    const [weeklyData, setWeeklyData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

    useEffect(() => {
        fetchData();
    }, [selectedDate]);

    const fetchData = async () => {
        try {
            const [dailyRes, weeklyRes] = await Promise.all([
                api.get(`/deficit/daily?date=${selectedDate}`),
                api.get('/deficit/weekly')
            ]);
            setData(dailyRes.data);
            setWeeklyData(weeklyRes.data);
        } catch (error) {
            console.error('Failed to fetch deficit data:', error);
        } finally {
            setLoading(false);
        }
    };

    const changeDate = (days) => {
        const date = new Date(selectedDate);
        date.setDate(date.getDate() + days);
        if (date <= new Date()) {
            setSelectedDate(date.toISOString().split('T')[0]);
        }
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        if (date.toDateString() === today.toDateString()) return 'Today';
        if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
        return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
            </div>
        );
    }

    const isDeficit = data?.net_balance < 0;
    const balanceColor = isDeficit ? 'text-green-500' : 'text-red-500';
    const balanceIcon = isDeficit ? TrendingDown : TrendingUp;
    const BalanceIcon = balanceIcon;

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header with Date Navigation */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <TrendingDown className="w-8 h-8 text-teal-500" />
                    <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
                        Calorie Deficit
                    </h1>
                </div>

                <div className="flex items-center gap-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-1">
                    <button
                        onClick={() => changeDate(-1)}
                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <span className="px-3 py-1 font-medium text-slate-700 dark:text-slate-300 min-w-[120px] text-center">
                        {formatDate(selectedDate)}
                    </span>
                    <button
                        onClick={() => changeDate(1)}
                        disabled={selectedDate === new Date().toISOString().split('T')[0]}
                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded disabled:opacity-50"
                    >
                        <ChevronRight size={20} />
                    </button>
                </div>
            </div>

            {/* Main Balance Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-6 rounded-2xl ${
                    isDeficit
                        ? 'bg-gradient-to-br from-green-500 to-emerald-600'
                        : 'bg-gradient-to-br from-red-500 to-orange-500'
                } text-white`}
            >
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <p className="text-white/80 text-sm">Net Calorie Balance</p>
                        <p className="text-4xl font-bold mt-1">
                            {data?.net_balance > 0 ? '+' : ''}{data?.net_balance} kcal
                        </p>
                    </div>
                    <div className={`w-16 h-16 rounded-full ${isDeficit ? 'bg-green-400/30' : 'bg-red-400/30'} flex items-center justify-center`}>
                        <BalanceIcon className="w-8 h-8" />
                    </div>
                </div>

                <p className="text-white/90 text-sm">
                    {isDeficit
                        ? `You're in a ${Math.abs(data?.net_balance)} calorie deficit. Keep it up!`
                        : `You're ${data?.net_balance} calories over your goal.`
                    }
                </p>

                {/* Formula Display */}
                <div className="mt-4 pt-4 border-t border-white/20">
                    <p className="text-xs text-white/70 mb-2">Calculation:</p>
                    <div className="flex items-center gap-2 text-sm flex-wrap">
                        <span className="bg-white/20 px-2 py-1 rounded">
                            {data?.calories_consumed} eaten
                        </span>
                        <span>-</span>
                        <span className="bg-white/20 px-2 py-1 rounded">
                            {data?.total_calories_out} burned
                        </span>
                        <span>=</span>
                        <span className="bg-white/30 px-2 py-1 rounded font-bold">
                            {data?.net_balance > 0 ? '+' : ''}{data?.net_balance}
                        </span>
                    </div>
                </div>
            </motion.div>

            {/* Breakdown Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <Flame className="w-5 h-5 text-orange-500" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Consumed</span>
                    </div>
                    <p className="text-2xl font-bold text-slate-800 dark:text-white">
                        {data?.calories_consumed}
                    </p>
                    <p className="text-xs text-slate-500">kcal eaten</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-5 h-5 text-blue-500" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">BMR</span>
                    </div>
                    <p className="text-2xl font-bold text-slate-800 dark:text-white">
                        {data?.bmr}
                    </p>
                    <p className="text-xs text-slate-500">base metabolism</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <Target className="w-5 h-5 text-purple-500" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Activity</span>
                    </div>
                    <p className="text-2xl font-bold text-slate-800 dark:text-white">
                        {data?.activity_calories}
                    </p>
                    <p className="text-xs text-slate-500">NEAT calories</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <Dumbbell className="w-5 h-5 text-teal-500" />
                        <span className="text-sm text-slate-600 dark:text-slate-400">Workouts</span>
                    </div>
                    <p className="text-2xl font-bold text-slate-800 dark:text-white">
                        {data?.workout_calories}
                    </p>
                    <p className="text-xs text-slate-500">exercise burn</p>
                </motion.div>
            </div>

            {/* Weekly Summary */}
            {weeklyData && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6"
                >
                    <div className="flex items-center gap-2 mb-4">
                        <Calendar className="w-5 h-5 text-teal-500" />
                        <h3 className="font-semibold text-slate-800 dark:text-white">Weekly Summary</h3>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-6">
                        <div className="text-center">
                            <p className={`text-2xl font-bold ${weeklyData.total_deficit < 0 ? 'text-green-500' : 'text-red-500'}`}>
                                {weeklyData.total_deficit > 0 ? '+' : ''}{weeklyData.total_deficit}
                            </p>
                            <p className="text-sm text-slate-500">Weekly Balance</p>
                        </div>
                        <div className="text-center">
                            <p className="text-2xl font-bold text-slate-800 dark:text-white">
                                {Math.round(weeklyData.avg_daily_deficit)}
                            </p>
                            <p className="text-sm text-slate-500">Avg Daily</p>
                        </div>
                        <div className="text-center">
                            <p className={`text-2xl font-bold ${weeklyData.projected_weight_change < 0 ? 'text-green-500' : 'text-orange-500'}`}>
                                {weeklyData.projected_weight_change > 0 ? '+' : ''}{weeklyData.projected_weight_change} kg
                            </p>
                            <p className="text-sm text-slate-500">Projected Change</p>
                        </div>
                    </div>

                    {/* Daily Bars */}
                    <div className="space-y-2">
                        {weeklyData.daily_breakdown?.map((day, idx) => {
                            const maxVal = Math.max(...weeklyData.daily_breakdown.map(d => Math.abs(d.net_balance)));
                            const width = Math.min((Math.abs(day.net_balance) / maxVal) * 100, 100);
                            const isNegative = day.net_balance < 0;

                            return (
                                <div key={idx} className="flex items-center gap-3">
                                    <span className="w-12 text-xs text-slate-500">
                                        {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                                    </span>
                                    <div className="flex-1 h-6 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full rounded-full transition-all ${
                                                isNegative ? 'bg-green-500' : 'bg-red-500'
                                            }`}
                                            style={{ width: `${width}%` }}
                                        />
                                    </div>
                                    <span className={`w-16 text-right text-sm font-medium ${
                                        isNegative ? 'text-green-500' : 'text-red-500'
                                    }`}>
                                        {day.net_balance > 0 ? '+' : ''}{day.net_balance}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </motion.div>
            )}

            {/* Info Card */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-blue-50 dark:bg-blue-500/10 rounded-xl p-4 flex gap-3"
            >
                <Info className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-700 dark:text-blue-300">
                    <p className="font-medium mb-1">How Deficit Works</p>
                    <p className="text-blue-600 dark:text-blue-400">
                        A calorie deficit of ~500 kcal/day leads to approximately 0.5 kg weight loss per week.
                        Your Total Calories Out = BMR (base metabolism) + Activity (NEAT) + Exercise.
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
