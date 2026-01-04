import { useState, useEffect } from 'react';
import api from '../api';
import FoodLogger from '../components/FoodLogger';
import WeightChart from '../components/WeightChart';
import { motion } from 'framer-motion';

export default function Dashboard() {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchDashboard = async () => {
        try {
            const res = await api.get('/health/dashboard');
            setDashboardData(res.data);
        } catch (e) {
            console.error(e);
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

    if (loading) return <div className="text-center p-10 text-gray-500">Loading dashboard...</div>;

    return (
        <div className="space-y-6 px-4">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 transition"
                >
                    <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Daily Calories</h3>
                    <div className="mt-2 flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-teal-500 dark:text-teal-400">{dashboardData?.today_calories || 0}</span>
                        <span className="text-gray-600 dark:text-gray-500">kcal</span>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 transition"
                >
                    <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium">Current Weight</h3>
                    <div className="mt-2 flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-teal-500 dark:text-teal-400">{dashboardData?.current_weight || '--'}</span>
                        <span className="text-gray-600 dark:text-gray-500">kg</span>
                    </div>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <FoodLogger onLogSuccess={refreshData} />
                <WeightChart onLogSuccess={refreshData} />
            </div>
        </div>
    );
}
