import { useState } from 'react';
import api from '../api';
import { Plus } from 'lucide-react';

export default function FoodLogger({ onLogSuccess }) {
    const [foodName, setFoodName] = useState('');
    const [calories, setCalories] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!foodName || !calories) return;

        setLoading(true);
        try {
            await api.post('/health/food', {
                food_name: foodName,
                calories: parseInt(calories),
            });
            setFoodName('');
            setCalories('');
            onLogSuccess();
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 transition">
            <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
                <span className="bg-teal-100 dark:bg-teal-500/10 text-teal-600 dark:text-teal-400 p-2 rounded-lg"><Plus size={20} /></span>
                Log Food
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">Food Name</label>
                    <input
                        type="text"
                        value={foodName}
                        onChange={(e) => setFoodName(e.target.value)}
                        className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                        placeholder="e.g., Banana"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">Calories</label>
                    <input
                        type="number"
                        value={calories}
                        onChange={(e) => setCalories(e.target.value)}
                        className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                        placeholder="e.g., 105"
                    />
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-teal-500 hover:bg-teal-600 text-white font-bold py-2 rounded-lg transition"
                >
                    {loading ? 'Adding...' : 'Add Food'}
                </button>
            </form>
        </div>
    );
}
