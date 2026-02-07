import { useState, useRef, useEffect } from 'react';
import api from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Camera, X, Check, Loader2, ChevronDown } from 'lucide-react';

export default function FoodLogger({ onLogSuccess }) {
    // Search state
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [searching, setSearching] = useState(false);
    const [showResults, setShowResults] = useState(false);

    // Selected food state
    const [selectedFood, setSelectedFood] = useState(null);
    const [servings, setServings] = useState(1);

    // Manual entry state
    const [manualMode, setManualMode] = useState(false);
    const [foodName, setFoodName] = useState('');
    const [calories, setCalories] = useState('');
    const [protein, setProtein] = useState('');
    const [carbs, setCarbs] = useState('');
    const [fat, setFat] = useState('');

    // Photo analysis state
    const [showPhotoUpload, setShowPhotoUpload] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [analyzedFoods, setAnalyzedFoods] = useState([]);
    const [previewImage, setPreviewImage] = useState(null);
    const fileInputRef = useRef(null);

    // Meal type
    const [mealType, setMealType] = useState('snack');

    // Loading
    const [loading, setLoading] = useState(false);

    // Debounced search
    useEffect(() => {
        const timer = setTimeout(() => {
            if (searchQuery.length >= 2) {
                searchFoods(searchQuery);
            } else {
                setSearchResults([]);
                setShowResults(false);
            }
        }, 300);

        return () => clearTimeout(timer);
    }, [searchQuery]);

    const searchFoods = async (query) => {
        setSearching(true);
        try {
            const response = await api.get(`/health/food/search?query=${encodeURIComponent(query)}&max_results=8`);
            setSearchResults(response.data.results || []);
            setShowResults(true);
        } catch (error) {
            console.error('Search failed:', error);
            setSearchResults([]);
        } finally {
            setSearching(false);
        }
    };

    const selectFood = (food) => {
        setSelectedFood(food);
        setSearchQuery(food.food_name);
        setShowResults(false);
        setServings(1);
    };

    const handlePhotoUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => setPreviewImage(e.target.result);
        reader.readAsDataURL(file);

        setAnalyzing(true);
        setShowPhotoUpload(true);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('meal_type', mealType);

            const response = await api.post('/health/food/analyze/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (response.data.success && response.data.food_items.length > 0) {
                setAnalyzedFoods(response.data.food_items);
            } else {
                alert(response.data.error_message || 'Could not identify food in the image');
                setShowPhotoUpload(false);
            }
        } catch (error) {
            console.error('Analysis failed:', error);
            alert('Failed to analyze image. Please try again.');
            setShowPhotoUpload(false);
        } finally {
            setAnalyzing(false);
        }
    };

    const addAnalyzedFood = async (food) => {
        setLoading(true);
        try {
            await api.post('/health/food', {
                food_name: food.name,
                calories: food.calories,
                protein: food.protein,
                carbs: food.carbs,
                fat: food.fat,
                fiber: food.fiber || 0,
                meal_type: mealType,
                ai_analyzed: true,
                ai_confidence_score: food.confidence
            });
            onLogSuccess?.();
            // Remove from analyzed list
            setAnalyzedFoods(prev => prev.filter(f => f.name !== food.name));
            if (analyzedFoods.length <= 1) {
                setShowPhotoUpload(false);
                setPreviewImage(null);
            }
        } catch (error) {
            console.error('Failed to log food:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (manualMode) {
            if (!foodName || !calories) return;
            setLoading(true);
            try {
                await api.post('/health/food', {
                    food_name: foodName,
                    calories: parseInt(calories),
                    protein: parseFloat(protein) || 0,
                    carbs: parseFloat(carbs) || 0,
                    fat: parseFloat(fat) || 0,
                    meal_type: mealType
                });
                resetForm();
                onLogSuccess?.();
            } catch (error) {
                console.error('Failed to log food:', error);
            } finally {
                setLoading(false);
            }
        } else if (selectedFood) {
            setLoading(true);
            try {
                await api.post('/health/food', {
                    food_name: selectedFood.food_name,
                    calories: Math.round(selectedFood.calories * servings),
                    protein: Math.round(selectedFood.protein * servings * 10) / 10,
                    carbs: Math.round(selectedFood.carbs * servings * 10) / 10,
                    fat: Math.round(selectedFood.fat * servings * 10) / 10,
                    fiber: Math.round(selectedFood.fiber * servings * 10) / 10,
                    serving_size: servings,
                    serving_unit: selectedFood.serving_description,
                    meal_type: mealType
                });
                resetForm();
                onLogSuccess?.();
            } catch (error) {
                console.error('Failed to log food:', error);
            } finally {
                setLoading(false);
            }
        }
    };

    const resetForm = () => {
        setSearchQuery('');
        setSelectedFood(null);
        setServings(1);
        setFoodName('');
        setCalories('');
        setProtein('');
        setCarbs('');
        setFat('');
        setShowResults(false);
    };

    const mealTypes = [
        { value: 'breakfast', label: 'Breakfast' },
        { value: 'lunch', label: 'Lunch' },
        { value: 'dinner', label: 'Dinner' },
        { value: 'snack', label: 'Snack' }
    ];

    return (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 transition">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
                    <span className="bg-teal-100 dark:bg-teal-500/10 text-teal-600 dark:text-teal-400 p-2 rounded-lg">
                        <Plus size={20} />
                    </span>
                    Log Food
                </h3>

                {/* Photo Upload Button */}
                <button
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-2 px-3 py-2 bg-purple-100 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-500/20 transition"
                >
                    <Camera size={18} />
                    <span className="text-sm font-medium">Scan Food</span>
                </button>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    capture="environment"
                    onChange={handlePhotoUpload}
                    className="hidden"
                />
            </div>

            {/* Photo Analysis Modal */}
            <AnimatePresence>
                {showPhotoUpload && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mb-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl p-4"
                    >
                        <div className="flex items-start gap-4">
                            {previewImage && (
                                <img
                                    src={previewImage}
                                    alt="Food"
                                    className="w-24 h-24 object-cover rounded-lg"
                                />
                            )}
                            <div className="flex-1">
                                {analyzing ? (
                                    <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                        <span>Analyzing your food...</span>
                                    </div>
                                ) : (
                                    <>
                                        <p className="text-sm text-slate-600 dark:text-slate-300 mb-2">
                                            Detected foods:
                                        </p>
                                        <div className="space-y-2">
                                            {analyzedFoods.map((food, idx) => (
                                                <div
                                                    key={idx}
                                                    className="flex items-center justify-between bg-white dark:bg-slate-600 p-2 rounded-lg"
                                                >
                                                    <div>
                                                        <p className="font-medium text-slate-800 dark:text-white">
                                                            {food.name}
                                                        </p>
                                                        <p className="text-xs text-slate-500 dark:text-slate-400">
                                                            {food.calories} kcal | P: {food.protein}g | C: {food.carbs}g | F: {food.fat}g
                                                        </p>
                                                    </div>
                                                    <button
                                                        onClick={() => addAnalyzedFood(food)}
                                                        disabled={loading}
                                                        className="p-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition disabled:opacity-50"
                                                    >
                                                        <Check size={16} />
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </>
                                )}
                            </div>
                            <button
                                onClick={() => {
                                    setShowPhotoUpload(false);
                                    setAnalyzedFoods([]);
                                    setPreviewImage(null);
                                }}
                                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                            >
                                <X size={20} />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Meal Type Selector */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                {mealTypes.map(type => (
                    <button
                        key={type.value}
                        onClick={() => setMealType(type.value)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${
                            mealType === type.value
                                ? 'bg-teal-500 text-white'
                                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                        }`}
                    >
                        {type.label}
                    </button>
                ))}
            </div>

            {/* Mode Toggle */}
            <div className="flex gap-2 mb-4">
                <button
                    onClick={() => { setManualMode(false); resetForm(); }}
                    className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition ${
                        !manualMode
                            ? 'bg-teal-100 dark:bg-teal-500/20 text-teal-600 dark:text-teal-400'
                            : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                    }`}
                >
                    <Search size={16} className="inline mr-2" />
                    Search
                </button>
                <button
                    onClick={() => { setManualMode(true); resetForm(); }}
                    className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition ${
                        manualMode
                            ? 'bg-teal-100 dark:bg-teal-500/20 text-teal-600 dark:text-teal-400'
                            : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                    }`}
                >
                    <Plus size={16} className="inline mr-2" />
                    Manual
                </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                {!manualMode ? (
                    <>
                        {/* Search Input */}
                        <div className="relative">
                            <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">
                                Search Food
                            </label>
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onFocus={() => searchResults.length > 0 && setShowResults(true)}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg pl-10 pr-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                                    placeholder="e.g., Banana, Chicken, Rice..."
                                />
                                {searching && (
                                    <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 animate-spin" />
                                )}
                            </div>

                            {/* Search Results Dropdown */}
                            <AnimatePresence>
                                {showResults && searchResults.length > 0 && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="absolute z-10 w-full mt-1 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg shadow-lg max-h-64 overflow-y-auto"
                                    >
                                        {searchResults.map((food, idx) => (
                                            <button
                                                key={food.food_id || idx}
                                                type="button"
                                                onClick={() => selectFood(food)}
                                                className="w-full p-3 text-left hover:bg-slate-50 dark:hover:bg-slate-600 border-b border-slate-100 dark:border-slate-600 last:border-0 transition"
                                            >
                                                <p className="font-medium text-slate-800 dark:text-white">
                                                    {food.food_name}
                                                </p>
                                                <p className="text-xs text-slate-500 dark:text-slate-400">
                                                    {food.serving_description} - {food.calories} kcal
                                                </p>
                                                <p className="text-xs text-slate-400 dark:text-slate-500">
                                                    P: {food.protein}g | C: {food.carbs}g | F: {food.fat}g
                                                </p>
                                            </button>
                                        ))}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Selected Food Details */}
                        {selectedFood && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-teal-50 dark:bg-teal-500/10 p-4 rounded-lg"
                            >
                                <div className="flex items-center justify-between mb-3">
                                    <div>
                                        <p className="font-semibold text-teal-800 dark:text-teal-300">
                                            {selectedFood.food_name}
                                        </p>
                                        <p className="text-sm text-teal-600 dark:text-teal-400">
                                            {selectedFood.serving_description}
                                        </p>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => { setSelectedFood(null); setSearchQuery(''); }}
                                        className="p-1 text-teal-400 hover:text-teal-600"
                                    >
                                        <X size={18} />
                                    </button>
                                </div>

                                {/* Servings */}
                                <div className="mb-3">
                                    <label className="block text-sm text-teal-700 dark:text-teal-400 mb-1">
                                        Servings
                                    </label>
                                    <input
                                        type="number"
                                        min="0.5"
                                        step="0.5"
                                        value={servings}
                                        onChange={(e) => setServings(parseFloat(e.target.value) || 1)}
                                        className="w-24 bg-white dark:bg-slate-700 border border-teal-300 dark:border-slate-600 rounded-lg px-3 py-1 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    />
                                </div>

                                {/* Nutrition Info */}
                                <div className="grid grid-cols-4 gap-2 text-center">
                                    <div className="bg-white dark:bg-slate-700 p-2 rounded">
                                        <p className="text-lg font-bold text-orange-500">
                                            {Math.round(selectedFood.calories * servings)}
                                        </p>
                                        <p className="text-xs text-slate-500">kcal</p>
                                    </div>
                                    <div className="bg-white dark:bg-slate-700 p-2 rounded">
                                        <p className="text-lg font-bold text-red-500">
                                            {(selectedFood.protein * servings).toFixed(1)}g
                                        </p>
                                        <p className="text-xs text-slate-500">Protein</p>
                                    </div>
                                    <div className="bg-white dark:bg-slate-700 p-2 rounded">
                                        <p className="text-lg font-bold text-blue-500">
                                            {(selectedFood.carbs * servings).toFixed(1)}g
                                        </p>
                                        <p className="text-xs text-slate-500">Carbs</p>
                                    </div>
                                    <div className="bg-white dark:bg-slate-700 p-2 rounded">
                                        <p className="text-lg font-bold text-yellow-500">
                                            {(selectedFood.fat * servings).toFixed(1)}g
                                        </p>
                                        <p className="text-xs text-slate-500">Fat</p>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </>
                ) : (
                    <>
                        {/* Manual Entry Fields */}
                        <div>
                            <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">
                                Food Name
                            </label>
                            <input
                                type="text"
                                value={foodName}
                                onChange={(e) => setFoodName(e.target.value)}
                                className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                                placeholder="e.g., Homemade Salad"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">
                                    Calories *
                                </label>
                                <input
                                    type="number"
                                    value={calories}
                                    onChange={(e) => setCalories(e.target.value)}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                                    placeholder="kcal"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">
                                    Protein (g)
                                </label>
                                <input
                                    type="number"
                                    value={protein}
                                    onChange={(e) => setProtein(e.target.value)}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                                    placeholder="0"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">
                                    Carbs (g)
                                </label>
                                <input
                                    type="number"
                                    value={carbs}
                                    onChange={(e) => setCarbs(e.target.value)}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                                    placeholder="0"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-gray-400 mb-1">
                                    Fat (g)
                                </label>
                                <input
                                    type="number"
                                    value={fat}
                                    onChange={(e) => setFat(e.target.value)}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                                    placeholder="0"
                                />
                            </div>
                        </div>
                    </>
                )}

                <button
                    type="submit"
                    disabled={loading || (!manualMode && !selectedFood) || (manualMode && (!foodName || !calories))}
                    className="w-full bg-teal-500 hover:bg-teal-600 disabled:bg-slate-300 disabled:dark:bg-slate-600 text-white font-bold py-3 rounded-lg transition flex items-center justify-center gap-2"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Adding...
                        </>
                    ) : (
                        <>
                            <Plus size={20} />
                            Add Food
                        </>
                    )}
                </button>
            </form>
        </div>
    );
}
