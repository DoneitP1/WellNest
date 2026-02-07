import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';
import { User, Ruler, Weight, Target, Activity, ChevronRight, ChevronLeft, Check, Dumbbell } from 'lucide-react';

const STEPS = [
    { id: 'basic', title: 'Basic Info', icon: User },
    { id: 'body', title: 'Body Metrics', icon: Ruler },
    { id: 'goals', title: 'Your Goals', icon: Target },
    { id: 'activity', title: 'Activity Level', icon: Activity },
    { id: 'review', title: 'Review', icon: Check },
];

const ACTIVITY_LEVELS = [
    { value: 'sedentary', label: 'Sedentary', description: 'Little or no exercise' },
    { value: 'light', label: 'Lightly Active', description: '1-3 days/week' },
    { value: 'moderate', label: 'Moderately Active', description: '3-5 days/week' },
    { value: 'active', label: 'Very Active', description: '6-7 days/week' },
    { value: 'very_active', label: 'Extra Active', description: 'Professional athlete' },
];

const GOAL_TYPES = [
    { value: 'lose_weight', label: 'Lose Weight', description: 'Calorie deficit for fat loss' },
    { value: 'maintain', label: 'Maintain Weight', description: 'Keep current weight' },
    { value: 'gain_muscle', label: 'Build Muscle', description: 'Calorie surplus for muscle' },
    { value: 'improve_health', label: 'Improve Health', description: 'General wellness' },
];

export default function Onboarding() {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [calculatedGoals, setCalculatedGoals] = useState(null);

    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        height: '',
        current_weight: '',
        target_weight: '',
        birth_date: '',
        gender: 'male',
        activity_level: 'moderate',
        goal_type: 'maintain',
        is_athlete: false,
        preferred_unit: 'metric',
    });

    const updateField = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const nextStep = async () => {
        if (currentStep === STEPS.length - 2) {
            // Before review, calculate goals
            await calculatePreview();
        }
        setCurrentStep(prev => Math.min(prev + 1, STEPS.length - 1));
    };

    const prevStep = () => {
        setCurrentStep(prev => Math.max(prev - 1, 0));
    };

    const calculatePreview = async () => {
        try {
            const res = await api.post('/users/calculate-goals', {
                ...formData,
                height: parseFloat(formData.height),
                current_weight: parseFloat(formData.current_weight),
                target_weight: formData.target_weight ? parseFloat(formData.target_weight) : null,
            });
            setCalculatedGoals(res.data);
        } catch (err) {
            console.error('Failed to calculate goals:', err);
        }
    };

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);

        try {
            await api.post('/users/onboarding', {
                ...formData,
                height: parseFloat(formData.height),
                current_weight: parseFloat(formData.current_weight),
                target_weight: formData.target_weight ? parseFloat(formData.target_weight) : null,
            });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to save profile');
        } finally {
            setLoading(false);
        }
    };

    const isStepValid = () => {
        switch (currentStep) {
            case 0: // Basic Info
                return formData.birth_date && formData.gender;
            case 1: // Body Metrics
                return formData.height && formData.current_weight;
            case 2: // Goals
                return formData.goal_type;
            case 3: // Activity
                return formData.activity_level;
            default:
                return true;
        }
    };

    const renderStep = () => {
        switch (currentStep) {
            case 0:
                return (
                    <div className="space-y-6">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    First Name
                                </label>
                                <input
                                    type="text"
                                    value={formData.first_name}
                                    onChange={(e) => updateField('first_name', e.target.value)}
                                    className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                    placeholder="John"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                    Last Name
                                </label>
                                <input
                                    type="text"
                                    value={formData.last_name}
                                    onChange={(e) => updateField('last_name', e.target.value)}
                                    className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                    placeholder="Doe"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                Date of Birth *
                            </label>
                            <input
                                type="date"
                                value={formData.birth_date}
                                onChange={(e) => updateField('birth_date', e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                Gender *
                            </label>
                            <div className="flex gap-3">
                                {['male', 'female', 'other'].map((gender) => (
                                    <button
                                        key={gender}
                                        onClick={() => updateField('gender', gender)}
                                        className={`flex-1 py-3 px-4 rounded-xl border-2 capitalize transition ${
                                            formData.gender === gender
                                                ? 'border-teal-500 bg-teal-50 dark:bg-teal-900/30 text-teal-600'
                                                : 'border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-400'
                                        }`}
                                    >
                                        {gender}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                );

            case 1:
                return (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                Height (cm) *
                            </label>
                            <input
                                type="number"
                                value={formData.height}
                                onChange={(e) => updateField('height', e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                placeholder="175"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                Current Weight (kg) *
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={formData.current_weight}
                                onChange={(e) => updateField('current_weight', e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                placeholder="70"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                                Target Weight (kg)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={formData.target_weight}
                                onChange={(e) => updateField('target_weight', e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                placeholder="65"
                            />
                        </div>
                    </div>
                );

            case 2:
                return (
                    <div className="space-y-4">
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                            What's your main health goal?
                        </p>
                        {GOAL_TYPES.map((goal) => (
                            <button
                                key={goal.value}
                                onClick={() => updateField('goal_type', goal.value)}
                                className={`w-full p-4 rounded-xl border-2 text-left transition ${
                                    formData.goal_type === goal.value
                                        ? 'border-teal-500 bg-teal-50 dark:bg-teal-900/30'
                                        : 'border-slate-200 dark:border-slate-600'
                                }`}
                            >
                                <p className={`font-medium ${formData.goal_type === goal.value ? 'text-teal-600' : 'text-slate-800 dark:text-white'}`}>
                                    {goal.label}
                                </p>
                                <p className="text-sm text-slate-500">{goal.description}</p>
                            </button>
                        ))}

                        <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                            <label className="flex items-center gap-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={formData.is_athlete}
                                    onChange={(e) => updateField('is_athlete', e.target.checked)}
                                    className="w-5 h-5 rounded border-slate-300 text-teal-500 focus:ring-teal-500"
                                />
                                <div className="flex items-center gap-2">
                                    <Dumbbell className="w-5 h-5 text-slate-500" />
                                    <span className="text-slate-700 dark:text-slate-300">
                                        I'm a professional athlete
                                    </span>
                                </div>
                            </label>
                            <p className="text-xs text-slate-500 ml-8 mt-1">
                                Unlocks advanced metrics like recovery scores and training load
                            </p>
                        </div>
                    </div>
                );

            case 3:
                return (
                    <div className="space-y-4">
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                            How active are you on a typical week?
                        </p>
                        {ACTIVITY_LEVELS.map((level) => (
                            <button
                                key={level.value}
                                onClick={() => updateField('activity_level', level.value)}
                                className={`w-full p-4 rounded-xl border-2 text-left transition ${
                                    formData.activity_level === level.value
                                        ? 'border-teal-500 bg-teal-50 dark:bg-teal-900/30'
                                        : 'border-slate-200 dark:border-slate-600'
                                }`}
                            >
                                <p className={`font-medium ${formData.activity_level === level.value ? 'text-teal-600' : 'text-slate-800 dark:text-white'}`}>
                                    {level.label}
                                </p>
                                <p className="text-sm text-slate-500">{level.description}</p>
                            </button>
                        ))}
                    </div>
                );

            case 4:
                return (
                    <div className="space-y-6">
                        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-4">
                            <h4 className="font-medium text-slate-800 dark:text-white mb-3">Your Profile</h4>
                            <div className="space-y-2 text-sm">
                                <p className="flex justify-between">
                                    <span className="text-slate-500">Name</span>
                                    <span className="text-slate-800 dark:text-white">{formData.first_name} {formData.last_name}</span>
                                </p>
                                <p className="flex justify-between">
                                    <span className="text-slate-500">Height</span>
                                    <span className="text-slate-800 dark:text-white">{formData.height} cm</span>
                                </p>
                                <p className="flex justify-between">
                                    <span className="text-slate-500">Weight</span>
                                    <span className="text-slate-800 dark:text-white">{formData.current_weight} kg</span>
                                </p>
                                <p className="flex justify-between">
                                    <span className="text-slate-500">Goal</span>
                                    <span className="text-slate-800 dark:text-white capitalize">{formData.goal_type.replace('_', ' ')}</span>
                                </p>
                            </div>
                        </div>

                        {calculatedGoals && (
                            <div className="bg-teal-50 dark:bg-teal-900/30 rounded-xl p-4 border border-teal-200 dark:border-teal-800">
                                <h4 className="font-medium text-teal-800 dark:text-teal-200 mb-3">
                                    Your Personalized Goals
                                </h4>
                                <div className="space-y-2 text-sm">
                                    <p className="flex justify-between">
                                        <span className="text-teal-600 dark:text-teal-300">Daily Calories</span>
                                        <span className="font-semibold text-teal-800 dark:text-teal-100">{calculatedGoals.daily_calories} kcal</span>
                                    </p>
                                    <p className="flex justify-between">
                                        <span className="text-teal-600 dark:text-teal-300">Protein</span>
                                        <span className="font-semibold text-teal-800 dark:text-teal-100">{calculatedGoals.protein_grams}g</span>
                                    </p>
                                    <p className="flex justify-between">
                                        <span className="text-teal-600 dark:text-teal-300">Carbs</span>
                                        <span className="font-semibold text-teal-800 dark:text-teal-100">{calculatedGoals.carbs_grams}g</span>
                                    </p>
                                    <p className="flex justify-between">
                                        <span className="text-teal-600 dark:text-teal-300">Fat</span>
                                        <span className="font-semibold text-teal-800 dark:text-teal-100">{calculatedGoals.fat_grams}g</span>
                                    </p>
                                    <p className="flex justify-between">
                                        <span className="text-teal-600 dark:text-teal-300">Water</span>
                                        <span className="font-semibold text-teal-800 dark:text-teal-100">{(calculatedGoals.water_ml / 1000).toFixed(1)}L</span>
                                    </p>
                                </div>
                            </div>
                        )}

                        {error && (
                            <p className="text-red-500 text-sm text-center">{error}</p>
                        )}
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-lg bg-white dark:bg-slate-800 rounded-3xl shadow-xl overflow-hidden"
            >
                {/* Progress Steps */}
                <div className="px-6 pt-6">
                    <div className="flex justify-between mb-2">
                        {STEPS.map((step, index) => (
                            <div
                                key={step.id}
                                className={`flex flex-col items-center ${index <= currentStep ? 'text-teal-500' : 'text-slate-300 dark:text-slate-600'}`}
                            >
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                    index < currentStep
                                        ? 'bg-teal-500 text-white'
                                        : index === currentStep
                                        ? 'bg-teal-100 dark:bg-teal-900 text-teal-500'
                                        : 'bg-slate-100 dark:bg-slate-700'
                                }`}>
                                    {index < currentStep ? (
                                        <Check className="w-4 h-4" />
                                    ) : (
                                        <step.icon className="w-4 h-4" />
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="flex gap-1 mb-6">
                        {STEPS.map((_, index) => (
                            <div
                                key={index}
                                className={`h-1 flex-1 rounded-full ${
                                    index <= currentStep ? 'bg-teal-500' : 'bg-slate-200 dark:bg-slate-700'
                                }`}
                            />
                        ))}
                    </div>
                </div>

                {/* Step Content */}
                <div className="px-6 pb-6">
                    <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">
                        {STEPS[currentStep].title}
                    </h2>
                    <p className="text-slate-500 mb-6">Step {currentStep + 1} of {STEPS.length}</p>

                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentStep}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.2 }}
                        >
                            {renderStep()}
                        </motion.div>
                    </AnimatePresence>
                </div>

                {/* Navigation */}
                <div className="px-6 pb-6 flex gap-3">
                    {currentStep > 0 && (
                        <button
                            onClick={prevStep}
                            className="flex items-center gap-2 px-6 py-3 rounded-xl border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                        >
                            <ChevronLeft className="w-5 h-5" />
                            Back
                        </button>
                    )}

                    {currentStep < STEPS.length - 1 ? (
                        <button
                            onClick={nextStep}
                            disabled={!isStepValid()}
                            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-teal-500 text-white hover:bg-teal-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Continue
                            <ChevronRight className="w-5 h-5" />
                        </button>
                    ) : (
                        <button
                            onClick={handleSubmit}
                            disabled={loading}
                            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-teal-500 text-white hover:bg-teal-600 transition disabled:opacity-50"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    Complete Setup
                                    <Check className="w-5 h-5" />
                                </>
                            )}
                        </button>
                    )}
                </div>
            </motion.div>
        </div>
    );
}
