import { useState, useEffect } from 'react';
import api from '../api';
import FoodLogger from '../components/FoodLogger';
import WeightChart from '../components/WeightChart';
import CalorieBar from '../components/CalorieBar';
import MacroChart from '../components/MacroChart';
import WaterTracker from '../components/WaterTracker';
import { motion } from 'framer-motion';
import { Activity, Flame, Droplets, Scale, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function Dashboard() {
    const [dashboardData, setDashboardData] = useState(null);
    const [macroData, setMacroData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [userProfile, setUserProfile] = useState(null);

    const fetchDashboard = async () => {
        try {
            setError(null);
            const [dashRes, macroRes, profileRes] = await Promise.all([
                api.get('/health/dashboard'),
                api.get('/health/macros/today').catch(() => ({ data: null })),
                api.get('/users/me').catch(() => ({ data: null }))
            ]);
            setDashboardData(dashRes.data);
            setMacroData(macroRes.data);
            setUserProfile(profileRes.data);
        } catch (e) {
            console.error(e);
            setError('Failed to load dashboard data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, []);

    const refreshData = () => {
        fetchDashboard();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center p-10 text-red-500">
                <p>{error}</p>
                <button onClick={refreshData} className="mt-4 px-4 py-2 bg-teal-500 text-white rounded hover:bg-teal-600 transition">
                    Retry
                </button>
            </div>
        );
    }

    const weightTrend = dashboardData?.weight_change_week;
    const getTrendIcon = () => {
        if (!weightTrend) return <Minus className="w-4 h-4" />;
        if (weightTrend < 0) return <TrendingDown className="w-4 h-4 text-green-500" />;
        return <TrendingUp className="w-4 h-4 text-orange-500" />;
    };

    const isAthlete = userProfile?.is_athlete;
    const hasCompletedOnboarding = userProfile?.profile?.onboarding_completed;

    return (
        <div className="space-y-6 px-4 pb-8">
            {/* Onboarding reminder */}
            {!hasCompletedOnboarding && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4"
                >
                    <p className="text-amber-800 dark:text-amber-200 text-sm">
                        Complete your profile setup to get personalized calorie and macro goals.
                        <a href="/onboarding" className="ml-2 font-semibold underline">Start Now</a>
                    </p>
                </motion.div>
            )}

            {/* Main Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Calories Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-br from-orange-500 to-red-500 p-5 rounded-2xl shadow-lg text-white"
                >
                    <div className="flex items-center justify-between mb-2">
                        <Flame className="w-6 h-6 opacity-80" />
                        <span className="text-xs opacity-80">Eaten</span>
                    </div>
                    <div className="text-3xl font-bold">{dashboardData?.today_calories || 0}</div>
                    <div className="text-sm opacity-80">kcal</div>
                </motion.div>

                {/* Remaining Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.05 }}
                    className="bg-gradient-to-br from-teal-500 to-emerald-500 p-5 rounded-2xl shadow-lg text-white"
                >
                    <div className="flex items-center justify-between mb-2">
                        <Activity className="w-6 h-6 opacity-80" />
                        <span className="text-xs opacity-80">Remaining</span>
                    </div>
                    <div className="text-3xl font-bold">
                        {dashboardData?.calories_remaining ?? '--'}
                    </div>
                    <div className="text-sm opacity-80">kcal</div>
                </motion.div>

                {/* Weight Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white dark:bg-slate-800 p-5 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700"
                >
                    <div className="flex items-center justify-between mb-2">
                        <Scale className="w-6 h-6 text-slate-400" />
                        <div className="flex items-center gap-1 text-xs text-slate-500">
                            {getTrendIcon()}
                            {weightTrend && <span>{Math.abs(weightTrend)}kg</span>}
                        </div>
                    </div>
                    <div className="text-3xl font-bold text-slate-800 dark:text-white">
                        {dashboardData?.current_weight || '--'}
                    </div>
                    <div className="text-sm text-slate-500">kg</div>
                </motion.div>

                {/* Water Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    className="bg-gradient-to-br from-blue-500 to-cyan-500 p-5 rounded-2xl shadow-lg text-white"
                >
                    <div className="flex items-center justify-between mb-2">
                        <Droplets className="w-6 h-6 opacity-80" />
                        <span className="text-xs opacity-80">Water</span>
                    </div>
                    <div className="text-3xl font-bold">
                        {((dashboardData?.today_water_ml || 0) / 1000).toFixed(1)}
                    </div>
                    <div className="text-sm opacity-80">/ {(dashboardData?.water_goal || 2500) / 1000}L</div>
                </motion.div>
            </div>

            {/* Calorie Progress Bar */}
            {dashboardData?.calorie_goal && (
                <CalorieBar
                    consumed={dashboardData.today_calories}
                    burned={dashboardData.calories_burned}
                    goal={dashboardData.calorie_goal}
                />
            )}

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Food Logger */}
                <div className="lg:col-span-2 space-y-6">
                    <FoodLogger onLogSuccess={refreshData} />
                </div>

                {/* Right Column - Macros & Water */}
                <div className="space-y-6">
                    {/* Macro Chart - Athlete View vs Simple View */}
                    {macroData && (
                        <MacroChart
                            data={macroData}
                            goals={{
                                protein: dashboardData?.protein_goal,
                                carbs: dashboardData?.carbs_goal,
                                fat: dashboardData?.fat_goal
                            }}
                            isAthlete={isAthlete}
                        />
                    )}

                    {/* Water Tracker */}
                    <WaterTracker
                        current={dashboardData?.today_water_ml || 0}
                        goal={dashboardData?.water_goal || 2500}
                        onUpdate={refreshData}
                    />
                </div>
            </div>

            {/* Weight Chart */}
            <WeightChart onLogSuccess={refreshData} />

            {/* Recovery Score for Athletes */}
            {isAthlete && dashboardData?.recovery_score && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700"
                >
                    <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">
                        Recovery Score
                    </h3>
                    <div className="flex items-center gap-8">
                        <div className="relative w-24 h-24">
                            <svg className="w-24 h-24 transform -rotate-90">
                                <circle
                                    cx="48"
                                    cy="48"
                                    r="40"
                                    stroke="currentColor"
                                    strokeWidth="8"
                                    fill="none"
                                    className="text-slate-200 dark:text-slate-700"
                                />
                                <circle
                                    cx="48"
                                    cy="48"
                                    r="40"
                                    stroke="currentColor"
                                    strokeWidth="8"
                                    fill="none"
                                    strokeDasharray={251.2}
                                    strokeDashoffset={251.2 - (dashboardData.recovery_score / 100) * 251.2}
                                    className={
                                        dashboardData.recovery_score >= 70 ? 'text-green-500' :
                                        dashboardData.recovery_score >= 40 ? 'text-yellow-500' : 'text-red-500'
                                    }
                                />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-2xl font-bold text-slate-800 dark:text-white">
                                    {dashboardData.recovery_score}
                                </span>
                            </div>
                        </div>
                        <div>
                            <p className="text-slate-600 dark:text-slate-400">
                                {dashboardData.recovery_score >= 70 ? 'Ready for high-intensity training' :
                                 dashboardData.recovery_score >= 40 ? 'Moderate training recommended' :
                                 'Rest and recovery recommended'}
                            </p>
                            {dashboardData.sleep_hours && (
                                <p className="text-sm text-slate-500 mt-1">
                                    Sleep: {dashboardData.sleep_hours}h
                                </p>
                            )}
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
