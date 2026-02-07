import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';
import {
    ChefHat, Search, Clock, Flame, Filter, X, Plus,
    Loader2, Star, Bookmark, ChevronRight, Users
} from 'lucide-react';

export default function Recipes() {
    const [recipes, setRecipes] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedRecipe, setSelectedRecipe] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [filters, setFilters] = useState({
        category: '',
        difficulty: '',
        maxCalories: '',
        minProtein: ''
    });
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        fetchRecipes();
        fetchCategories();
    }, []);

    const fetchRecipes = async (search = '') => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (search) params.append('search', search);
            if (filters.category) params.append('category', filters.category);
            if (filters.difficulty) params.append('difficulty', filters.difficulty);
            if (filters.maxCalories) params.append('max_calories', filters.maxCalories);
            if (filters.minProtein) params.append('min_protein', filters.minProtein);

            const response = await api.get(`/recipes/?${params.toString()}`);
            setRecipes(response.data);
        } catch (error) {
            console.error('Failed to fetch recipes:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await api.get('/recipes/categories');
            setCategories(response.data);
        } catch (error) {
            console.error('Failed to fetch categories:', error);
        }
    };

    const fetchRecipeDetails = async (recipeId) => {
        try {
            const response = await api.get(`/recipes/${recipeId}`);
            setSelectedRecipe(response.data);
        } catch (error) {
            console.error('Failed to fetch recipe:', error);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        fetchRecipes(searchQuery);
    };

    const handleLogRecipe = async (recipe, servings = 1, mealType = 'snack') => {
        try {
            await api.post(`/recipes/${recipe.id}/log?servings=${servings}&meal_type=${mealType}`);
            alert(`Added ${recipe.name} to your food log!`);
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to log recipe');
        }
    };

    const handleSaveRecipe = async (recipeId) => {
        try {
            await api.post(`/recipes/${recipeId}/save`);
            fetchRecipes(searchQuery);
        } catch (error) {
            console.error('Failed to save recipe:', error);
        }
    };

    const getDifficultyColor = (difficulty) => {
        switch (difficulty) {
            case 'easy': return 'text-green-500 bg-green-100 dark:bg-green-500/20';
            case 'medium': return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-500/20';
            case 'hard': return 'text-red-500 bg-red-100 dark:bg-red-500/20';
            default: return 'text-slate-500 bg-slate-100';
        }
    };

    if (loading && recipes.length === 0) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <ChefHat className="w-8 h-8 text-teal-500" />
                    <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
                        Recipes
                    </h1>
                </div>
            </div>

            {/* Search & Filter */}
            <div className="flex gap-2">
                <form onSubmit={handleSearch} className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search recipes..."
                        className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                    />
                </form>
                <button
                    onClick={() => setShowFilters(!showFilters)}
                    className={`px-4 py-3 rounded-xl border transition ${
                        showFilters
                            ? 'bg-teal-500 text-white border-teal-500'
                            : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
                    }`}
                >
                    <Filter size={20} />
                </button>
            </div>

            {/* Filters Panel */}
            <AnimatePresence>
                {showFilters && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 overflow-hidden"
                    >
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Category
                                </label>
                                <select
                                    value={filters.category}
                                    onChange={(e) => setFilters({...filters, category: e.target.value})}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2"
                                >
                                    <option value="">All</option>
                                    {categories.map(cat => (
                                        <option key={cat.name} value={cat.name}>{cat.name} ({cat.count})</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Difficulty
                                </label>
                                <select
                                    value={filters.difficulty}
                                    onChange={(e) => setFilters({...filters, difficulty: e.target.value})}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2"
                                >
                                    <option value="">All</option>
                                    <option value="easy">Easy</option>
                                    <option value="medium">Medium</option>
                                    <option value="hard">Hard</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Max Calories
                                </label>
                                <input
                                    type="number"
                                    value={filters.maxCalories}
                                    onChange={(e) => setFilters({...filters, maxCalories: e.target.value})}
                                    placeholder="e.g., 500"
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Min Protein (g)
                                </label>
                                <input
                                    type="number"
                                    value={filters.minProtein}
                                    onChange={(e) => setFilters({...filters, minProtein: e.target.value})}
                                    placeholder="e.g., 20"
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-3 py-2"
                                />
                            </div>
                        </div>

                        <div className="flex justify-end gap-2 mt-4">
                            <button
                                onClick={() => {
                                    setFilters({ category: '', difficulty: '', maxCalories: '', minProtein: '' });
                                    fetchRecipes(searchQuery);
                                }}
                                className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
                            >
                                Clear
                            </button>
                            <button
                                onClick={() => fetchRecipes(searchQuery)}
                                className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600"
                            >
                                Apply Filters
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Category Pills */}
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                {categories.slice(0, 6).map(cat => (
                    <button
                        key={cat.name}
                        onClick={() => {
                            setFilters({...filters, category: cat.name});
                            fetchRecipes(searchQuery);
                        }}
                        className={`px-4 py-2 rounded-full whitespace-nowrap text-sm transition ${
                            filters.category === cat.name
                                ? 'bg-teal-500 text-white'
                                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                        }`}
                    >
                        {cat.name}
                    </button>
                ))}
            </div>

            {/* Recipe Grid */}
            {recipes.length === 0 ? (
                <div className="text-center py-12 text-slate-500">
                    <ChefHat className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>No recipes found. Try adjusting your filters.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {recipes.map((recipe, idx) => (
                        <motion.div
                            key={recipe.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.05 }}
                            onClick={() => fetchRecipeDetails(recipe.id)}
                            className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden cursor-pointer hover:shadow-lg transition"
                        >
                            {recipe.image_url ? (
                                <img
                                    src={recipe.image_url}
                                    alt={recipe.name}
                                    className="w-full h-40 object-cover"
                                />
                            ) : (
                                <div className="w-full h-40 bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center">
                                    <ChefHat className="w-12 h-12 text-white/50" />
                                </div>
                            )}

                            <div className="p-4">
                                <div className="flex items-start justify-between mb-2">
                                    <h3 className="font-semibold text-slate-800 dark:text-white line-clamp-1">
                                        {recipe.name}
                                    </h3>
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getDifficultyColor(recipe.difficulty)}`}>
                                        {recipe.difficulty}
                                    </span>
                                </div>

                                <p className="text-sm text-slate-500 line-clamp-2 mb-3">
                                    {recipe.description}
                                </p>

                                <div className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-3">
                                        <span className="flex items-center gap-1 text-slate-500">
                                            <Clock size={14} />
                                            {recipe.total_time_minutes} min
                                        </span>
                                        <span className="flex items-center gap-1 text-orange-500">
                                            <Flame size={14} />
                                            {recipe.calories_per_serving} kcal
                                        </span>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        {recipe.rating_avg > 0 && (
                                            <span className="flex items-center gap-1 text-yellow-500">
                                                <Star size={14} fill="currentColor" />
                                                {recipe.rating_avg.toFixed(1)}
                                            </span>
                                        )}
                                        <span className="flex items-center gap-1 text-slate-400">
                                            <Bookmark size={14} />
                                            {recipe.saves_count}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}

            {/* Recipe Detail Modal */}
            <AnimatePresence>
                {selectedRecipe && (
                    <div
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                        onClick={() => setSelectedRecipe(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white dark:bg-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
                            onClick={e => e.stopPropagation()}
                        >
                            {/* Header Image */}
                            {selectedRecipe.image_url ? (
                                <img
                                    src={selectedRecipe.image_url}
                                    alt={selectedRecipe.name}
                                    className="w-full h-48 object-cover"
                                />
                            ) : (
                                <div className="w-full h-48 bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center">
                                    <ChefHat className="w-16 h-16 text-white/50" />
                                </div>
                            )}

                            <div className="p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div>
                                        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">
                                            {selectedRecipe.name}
                                        </h2>
                                        <p className="text-slate-500 mt-1">{selectedRecipe.description}</p>
                                    </div>
                                    <button
                                        onClick={() => setSelectedRecipe(null)}
                                        className="text-slate-400 hover:text-slate-600"
                                    >
                                        <X size={24} />
                                    </button>
                                </div>

                                {/* Quick Stats */}
                                <div className="grid grid-cols-4 gap-4 mb-6">
                                    <div className="text-center p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                                        <Clock className="w-5 h-5 mx-auto mb-1 text-slate-500" />
                                        <p className="text-sm font-medium">{selectedRecipe.total_time_minutes} min</p>
                                    </div>
                                    <div className="text-center p-3 bg-orange-50 dark:bg-orange-500/20 rounded-lg">
                                        <Flame className="w-5 h-5 mx-auto mb-1 text-orange-500" />
                                        <p className="text-sm font-medium text-orange-600">{selectedRecipe.calories_per_serving} kcal</p>
                                    </div>
                                    <div className="text-center p-3 bg-blue-50 dark:bg-blue-500/20 rounded-lg">
                                        <Users className="w-5 h-5 mx-auto mb-1 text-blue-500" />
                                        <p className="text-sm font-medium text-blue-600">{selectedRecipe.servings} servings</p>
                                    </div>
                                    <div className="text-center p-3 bg-teal-50 dark:bg-teal-500/20 rounded-lg">
                                        <span className="text-lg">🥩</span>
                                        <p className="text-sm font-medium text-teal-600">{selectedRecipe.protein_per_serving}g protein</p>
                                    </div>
                                </div>

                                {/* Macros */}
                                <div className="bg-slate-50 dark:bg-slate-700 rounded-xl p-4 mb-6">
                                    <h3 className="font-semibold text-slate-800 dark:text-white mb-3">Nutrition per Serving</h3>
                                    <div className="grid grid-cols-4 gap-4 text-center">
                                        <div>
                                            <p className="text-lg font-bold text-orange-500">{selectedRecipe.calories_per_serving}</p>
                                            <p className="text-xs text-slate-500">Calories</p>
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-red-500">{selectedRecipe.protein_per_serving}g</p>
                                            <p className="text-xs text-slate-500">Protein</p>
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-blue-500">{selectedRecipe.carbs_per_serving}g</p>
                                            <p className="text-xs text-slate-500">Carbs</p>
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-yellow-500">{selectedRecipe.fat_per_serving}g</p>
                                            <p className="text-xs text-slate-500">Fat</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Ingredients */}
                                <div className="mb-6">
                                    <h3 className="font-semibold text-slate-800 dark:text-white mb-3">Ingredients</h3>
                                    <ul className="space-y-2">
                                        {selectedRecipe.ingredients?.map((ing, idx) => (
                                            <li key={idx} className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                                                <span className="w-2 h-2 bg-teal-500 rounded-full" />
                                                {ing.amount} {ing.unit} {ing.name}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Instructions */}
                                <div className="mb-6">
                                    <h3 className="font-semibold text-slate-800 dark:text-white mb-3">Instructions</h3>
                                    <ol className="space-y-3">
                                        {selectedRecipe.instructions?.map((step, idx) => (
                                            <li key={idx} className="flex gap-3">
                                                <span className="w-6 h-6 bg-teal-500 text-white rounded-full flex items-center justify-center text-sm flex-shrink-0">
                                                    {idx + 1}
                                                </span>
                                                <p className="text-slate-600 dark:text-slate-300">{step}</p>
                                            </li>
                                        ))}
                                    </ol>
                                </div>

                                {/* Actions */}
                                <div className="flex gap-3">
                                    <button
                                        onClick={() => handleSaveRecipe(selectedRecipe.id)}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 border border-slate-200 dark:border-slate-600 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                                    >
                                        <Bookmark size={20} />
                                        Save Recipe
                                    </button>
                                    <button
                                        onClick={() => handleLogRecipe(selectedRecipe)}
                                        className="flex-1 flex items-center justify-center gap-2 py-3 bg-teal-500 text-white rounded-xl hover:bg-teal-600 transition"
                                    >
                                        <Plus size={20} />
                                        Add to Food Log
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
