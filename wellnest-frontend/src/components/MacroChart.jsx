import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

export default function MacroChart({ data, goals, isAthlete }) {
    const { protein_grams, carbs_grams, fat_grams, protein_percentage, carbs_percentage, fat_percentage } = data || {};

    const pieData = [
        { name: 'Protein', value: protein_grams || 0, color: '#f97316' },
        { name: 'Carbs', value: carbs_grams || 0, color: '#3b82f6' },
        { name: 'Fat', value: fat_grams || 0, color: '#eab308' },
    ];

    const totalMacros = (protein_grams || 0) + (carbs_grams || 0) + (fat_grams || 0);

    // Athlete view shows more details
    if (isAthlete) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700"
            >
                <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">
                    Macro Distribution
                </h3>

                {/* Pie Chart */}
                <div className="h-40 mb-4">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                innerRadius={40}
                                outerRadius={60}
                                paddingAngle={2}
                                dataKey="value"
                            >
                                {pieData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Detailed Macros */}
                <div className="space-y-4">
                    {/* Protein */}
                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span className="text-orange-500 font-medium">Protein</span>
                            <span className="text-slate-600 dark:text-slate-400">
                                {protein_grams?.toFixed(1) || 0}g
                                {goals?.protein && ` / ${goals.protein}g`}
                            </span>
                        </div>
                        <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${goals?.protein ? Math.min((protein_grams / goals.protein) * 100, 100) : protein_percentage || 0}%` }}
                                transition={{ duration: 0.5 }}
                                className="h-full bg-orange-500 rounded-full"
                            />
                        </div>
                        <p className="text-xs text-slate-500 mt-1">{protein_percentage?.toFixed(1) || 0}%</p>
                    </div>

                    {/* Carbs */}
                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span className="text-blue-500 font-medium">Carbohydrates</span>
                            <span className="text-slate-600 dark:text-slate-400">
                                {carbs_grams?.toFixed(1) || 0}g
                                {goals?.carbs && ` / ${goals.carbs}g`}
                            </span>
                        </div>
                        <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${goals?.carbs ? Math.min((carbs_grams / goals.carbs) * 100, 100) : carbs_percentage || 0}%` }}
                                transition={{ duration: 0.5, delay: 0.1 }}
                                className="h-full bg-blue-500 rounded-full"
                            />
                        </div>
                        <p className="text-xs text-slate-500 mt-1">{carbs_percentage?.toFixed(1) || 0}%</p>
                    </div>

                    {/* Fat */}
                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span className="text-yellow-500 font-medium">Fat</span>
                            <span className="text-slate-600 dark:text-slate-400">
                                {fat_grams?.toFixed(1) || 0}g
                                {goals?.fat && ` / ${goals.fat}g`}
                            </span>
                        </div>
                        <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${goals?.fat ? Math.min((fat_grams / goals.fat) * 100, 100) : fat_percentage || 0}%` }}
                                transition={{ duration: 0.5, delay: 0.2 }}
                                className="h-full bg-yellow-500 rounded-full"
                            />
                        </div>
                        <p className="text-xs text-slate-500 mt-1">{fat_percentage?.toFixed(1) || 0}%</p>
                    </div>
                </div>

                {/* Fiber note */}
                {data?.fiber_grams > 0 && (
                    <p className="text-xs text-slate-500 mt-4">
                        Fiber: {data.fiber_grams?.toFixed(1)}g
                    </p>
                )}
            </motion.div>
        );
    }

    // Simple view for regular users
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700"
        >
            <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-4">
                Today's Macros
            </h3>

            {totalMacros === 0 ? (
                <p className="text-slate-500 text-sm text-center py-4">
                    Log food to see your macros
                </p>
            ) : (
                <div className="space-y-3">
                    {/* Protein */}
                    <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-orange-500" />
                        <span className="text-sm text-slate-600 dark:text-slate-400 flex-1">Protein</span>
                        <span className="text-sm font-semibold text-slate-800 dark:text-white">
                            {protein_grams?.toFixed(0) || 0}g
                        </span>
                    </div>

                    {/* Carbs */}
                    <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-blue-500" />
                        <span className="text-sm text-slate-600 dark:text-slate-400 flex-1">Carbs</span>
                        <span className="text-sm font-semibold text-slate-800 dark:text-white">
                            {carbs_grams?.toFixed(0) || 0}g
                        </span>
                    </div>

                    {/* Fat */}
                    <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <span className="text-sm text-slate-600 dark:text-slate-400 flex-1">Fat</span>
                        <span className="text-sm font-semibold text-slate-800 dark:text-white">
                            {fat_grams?.toFixed(0) || 0}g
                        </span>
                    </div>
                </div>
            )}
        </motion.div>
    );
}
