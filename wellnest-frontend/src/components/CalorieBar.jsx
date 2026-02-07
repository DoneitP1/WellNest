import { motion } from 'framer-motion';

export default function CalorieBar({ consumed, burned, goal }) {
    const netCalories = consumed - burned;
    const percentage = Math.min((netCalories / goal) * 100, 100);
    const remaining = goal - netCalories;
    const isOverGoal = netCalories > goal;

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700"
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400">
                    Daily Calorie Budget
                </h3>
                <span className={`text-sm font-semibold ${isOverGoal ? 'text-red-500' : 'text-teal-500'}`}>
                    {isOverGoal ? `${Math.abs(remaining)} over` : `${remaining} remaining`}
                </span>
            </div>

            {/* Progress Bar */}
            <div className="relative h-4 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    className={`h-full rounded-full ${
                        isOverGoal
                            ? 'bg-gradient-to-r from-red-400 to-red-500'
                            : 'bg-gradient-to-r from-teal-400 to-emerald-500'
                    }`}
                />
            </div>

            {/* Stats Row */}
            <div className="flex justify-between mt-4 text-sm">
                <div className="text-center">
                    <p className="text-slate-500 dark:text-slate-400">Goal</p>
                    <p className="font-semibold text-slate-800 dark:text-white">{goal}</p>
                </div>
                <div className="text-center">
                    <p className="text-slate-500 dark:text-slate-400">Food</p>
                    <p className="font-semibold text-orange-500">+{consumed}</p>
                </div>
                <div className="text-center">
                    <p className="text-slate-500 dark:text-slate-400">Exercise</p>
                    <p className="font-semibold text-green-500">-{burned}</p>
                </div>
                <div className="text-center">
                    <p className="text-slate-500 dark:text-slate-400">Net</p>
                    <p className={`font-semibold ${isOverGoal ? 'text-red-500' : 'text-teal-500'}`}>
                        {netCalories}
                    </p>
                </div>
            </div>
        </motion.div>
    );
}
