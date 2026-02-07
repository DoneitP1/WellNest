import { useState } from 'react';
import { motion } from 'framer-motion';
import { Droplets, Plus } from 'lucide-react';
import api from '../api';

export default function WaterTracker({ current, goal, onUpdate }) {
    const [loading, setLoading] = useState(false);
    const percentage = Math.min((current / goal) * 100, 100);
    const glasses = Math.floor(current / 250); // 250ml per glass

    const quickAddAmounts = [250, 500, 750];

    const addWater = async (amount) => {
        setLoading(true);
        try {
            await api.post('/health/water', { amount_ml: amount });
            onUpdate?.();
        } catch (error) {
            console.error('Failed to log water:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                    <Droplets className="w-5 h-5 text-blue-500" />
                    Water
                </h3>
                <span className="text-sm text-slate-500">
                    {glasses} glasses
                </span>
            </div>

            {/* Water Tank Visualization */}
            <div className="relative h-32 bg-slate-100 dark:bg-slate-700 rounded-xl overflow-hidden mb-4">
                <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: `${percentage}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-blue-500 to-cyan-400"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white drop-shadow-lg">
                        {(current / 1000).toFixed(1)}L
                    </span>
                </div>

                {/* Wave effect */}
                <div className="absolute bottom-0 left-0 right-0" style={{ height: `${percentage}%` }}>
                    <svg
                        className="absolute bottom-full left-0 w-full"
                        viewBox="0 0 1200 120"
                        preserveAspectRatio="none"
                        style={{ height: '20px' }}
                    >
                        <path
                            d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"
                            className="fill-blue-400 opacity-50"
                        />
                    </svg>
                </div>
            </div>

            {/* Goal Progress */}
            <div className="flex justify-between text-sm mb-4">
                <span className="text-slate-500">Progress</span>
                <span className="text-slate-800 dark:text-white font-medium">
                    {current} / {goal} ml ({percentage.toFixed(0)}%)
                </span>
            </div>

            {/* Quick Add Buttons */}
            <div className="flex gap-2">
                {quickAddAmounts.map((amount) => (
                    <button
                        key={amount}
                        onClick={() => addWater(amount)}
                        disabled={loading}
                        className="flex-1 flex items-center justify-center gap-1 py-2 px-3 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition disabled:opacity-50"
                    >
                        <Plus className="w-4 h-4" />
                        <span className="text-sm font-medium">{amount}ml</span>
                    </button>
                ))}
            </div>
        </motion.div>
    );
}
