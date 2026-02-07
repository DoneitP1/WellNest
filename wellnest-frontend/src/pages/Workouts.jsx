import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import api from '../api';
import {
    Dumbbell, Plus, Flame, Clock, TrendingUp, Target,
    Calendar, Loader2, X, Play, ChevronRight
} from 'lucide-react';

export default function Workouts() {
    const [workouts, setWorkouts] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showNewWorkout, setShowNewWorkout] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const [newWorkout, setNewWorkout] = useState({
        workout_type: 'strength',
        name: '',
        duration_minutes: 30,
        intensity: 'moderate',
        calories_burned: null,
        notes: ''
    });

    const workoutTypes = [
        { value: 'strength', label: 'Strength', icon: '🏋️' },
        { value: 'cardio', label: 'Cardio', icon: '🏃' },
        { value: 'hiit', label: 'HIIT', icon: '⚡' },
        { value: 'yoga', label: 'Yoga', icon: '🧘' },
        { value: 'swimming', label: 'Swimming', icon: '🏊' },
        { value: 'cycling', label: 'Cycling', icon: '🚴' },
        { value: 'running', label: 'Running', icon: '🏃' },
        { value: 'walking', label: 'Walking', icon: '🚶' },
        { value: 'sports', label: 'Sports', icon: '⚽' },
        { value: 'other', label: 'Other', icon: '🎯' },
    ];

    const intensityLevels = [
        { value: 'low', label: 'Low', color: 'text-green-500' },
        { value: 'moderate', label: 'Moderate', color: 'text-yellow-500' },
        { value: 'high', label: 'High', color: 'text-orange-500' },
        { value: 'very_high', label: 'Very High', color: 'text-red-500' },
    ];

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [workoutsRes, statsRes] = await Promise.all([
                api.get('/workouts/?limit=20'),
                api.get('/workouts/stats')
            ]);
            setWorkouts(workoutsRes.data);
            setStats(statsRes.data);
        } catch (error) {
            console.error('Failed to fetch workouts:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const response = await api.post('/workouts/', {
                ...newWorkout,
                start_time: new Date().toISOString(),
                duration_minutes: parseInt(newWorkout.duration_minutes)
            });

            setWorkouts([response.data, ...workouts]);
            setShowNewWorkout(false);
            setNewWorkout({
                workout_type: 'strength',
                name: '',
                duration_minutes: 30,
                intensity: 'moderate',
                calories_burned: null,
                notes: ''
            });
            fetchData(); // Refresh stats
        } catch (error) {
            alert(error.response?.data?.detail || 'Failed to log workout');
        } finally {
            setSubmitting(false);
        }
    };

    const getWorkoutIcon = (type) => {
        const found = workoutTypes.find(w => w.value === type);
        return found?.icon || '🎯';
    };

    if (loading) {
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
                    <Dumbbell className="w-8 h-8 text-teal-500" />
                    <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
                        Workouts
                    </h1>
                </div>
                <button
                    onClick={() => setShowNewWorkout(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition"
                >
                    <Plus size={20} />
                    Log Workout
                </button>
            </div>

            {/* Stats Grid */}
            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-gradient-to-br from-orange-500 to-red-500 p-4 rounded-xl text-white"
                    >
                        <Flame className="w-6 h-6 mb-2 opacity-80" />
                        <p className="text-2xl font-bold">{stats.total_calories_burned}</p>
                        <p className="text-sm opacity-80">Total Calories Burned</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="bg-gradient-to-br from-teal-500 to-emerald-500 p-4 rounded-xl text-white"
                    >
                        <Target className="w-6 h-6 mb-2 opacity-80" />
                        <p className="text-2xl font-bold">{stats.total_workouts}</p>
                        <p className="text-sm opacity-80">Total Workouts</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="bg-gradient-to-br from-purple-500 to-pink-500 p-4 rounded-xl text-white"
                    >
                        <Clock className="w-6 h-6 mb-2 opacity-80" />
                        <p className="text-2xl font-bold">{Math.round(stats.total_minutes / 60)}h</p>
                        <p className="text-sm opacity-80">Total Time</p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="bg-gradient-to-br from-blue-500 to-cyan-500 p-4 rounded-xl text-white"
                    >
                        <Calendar className="w-6 h-6 mb-2 opacity-80" />
                        <p className="text-2xl font-bold">{stats.workouts_this_week}</p>
                        <p className="text-sm opacity-80">This Week</p>
                    </motion.div>
                </div>
            )}

            {/* Workout History */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
                <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                    <h3 className="font-semibold text-slate-800 dark:text-white">Recent Workouts</h3>
                </div>

                {workouts.length === 0 ? (
                    <div className="p-8 text-center text-slate-500">
                        <Dumbbell className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No workouts logged yet. Start your fitness journey!</p>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-100 dark:divide-slate-700">
                        {workouts.map((workout, idx) => (
                            <motion.div
                                key={workout.id}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="p-4 flex items-center gap-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition"
                            >
                                <div className="w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-2xl">
                                    {getWorkoutIcon(workout.workout_type)}
                                </div>

                                <div className="flex-1">
                                    <p className="font-medium text-slate-800 dark:text-white">
                                        {workout.name || workout.workout_type.charAt(0).toUpperCase() + workout.workout_type.slice(1)}
                                    </p>
                                    <div className="flex items-center gap-3 text-sm text-slate-500">
                                        <span className="flex items-center gap-1">
                                            <Clock size={14} />
                                            {workout.duration_minutes} min
                                        </span>
                                        <span className={intensityLevels.find(i => i.value === workout.intensity)?.color}>
                                            {workout.intensity}
                                        </span>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <p className="text-lg font-bold text-orange-500">
                                        {workout.calories_burned} kcal
                                    </p>
                                    <p className="text-xs text-slate-500">
                                        {new Date(workout.start_time).toLocaleDateString()}
                                    </p>
                                </div>

                                {workout.xp_earned > 0 && (
                                    <div className="bg-purple-100 dark:bg-purple-500/20 px-2 py-1 rounded text-xs font-semibold text-purple-600 dark:text-purple-400">
                                        +{workout.xp_earned} XP
                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>

            {/* New Workout Modal */}
            {showNewWorkout && (
                <div
                    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                    onClick={() => setShowNewWorkout(false)}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="bg-white dark:bg-slate-800 rounded-2xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-slate-800 dark:text-white">
                                Log Workout
                            </h2>
                            <button
                                onClick={() => setShowNewWorkout(false)}
                                className="text-slate-400 hover:text-slate-600"
                            >
                                <X size={24} />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            {/* Workout Type */}
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
                                    Workout Type
                                </label>
                                <div className="grid grid-cols-5 gap-2">
                                    {workoutTypes.map(type => (
                                        <button
                                            key={type.value}
                                            type="button"
                                            onClick={() => setNewWorkout({ ...newWorkout, workout_type: type.value })}
                                            className={`p-3 rounded-xl text-center transition ${
                                                newWorkout.workout_type === type.value
                                                    ? 'bg-teal-500 text-white'
                                                    : 'bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600'
                                            }`}
                                        >
                                            <span className="text-xl">{type.icon}</span>
                                            <p className="text-xs mt-1">{type.label}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Name */}
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Workout Name (optional)
                                </label>
                                <input
                                    type="text"
                                    value={newWorkout.name}
                                    onChange={(e) => setNewWorkout({ ...newWorkout, name: e.target.value })}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    placeholder="e.g., Morning Run, Leg Day"
                                />
                            </div>

                            {/* Duration */}
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Duration (minutes)
                                </label>
                                <input
                                    type="number"
                                    value={newWorkout.duration_minutes}
                                    onChange={(e) => setNewWorkout({ ...newWorkout, duration_minutes: e.target.value })}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    min="1"
                                    required
                                />
                            </div>

                            {/* Intensity */}
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
                                    Intensity
                                </label>
                                <div className="flex gap-2">
                                    {intensityLevels.map(level => (
                                        <button
                                            key={level.value}
                                            type="button"
                                            onClick={() => setNewWorkout({ ...newWorkout, intensity: level.value })}
                                            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition ${
                                                newWorkout.intensity === level.value
                                                    ? 'bg-teal-500 text-white'
                                                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                                            }`}
                                        >
                                            {level.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Calories (optional) */}
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Calories Burned (optional - auto-calculated if empty)
                                </label>
                                <input
                                    type="number"
                                    value={newWorkout.calories_burned || ''}
                                    onChange={(e) => setNewWorkout({ ...newWorkout, calories_burned: e.target.value ? parseInt(e.target.value) : null })}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    placeholder="Leave empty for auto-calculation"
                                />
                            </div>

                            {/* Notes */}
                            <div>
                                <label className="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                                    Notes
                                </label>
                                <textarea
                                    value={newWorkout.notes}
                                    onChange={(e) => setNewWorkout({ ...newWorkout, notes: e.target.value })}
                                    className="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-4 py-2 h-20 resize-none focus:outline-none focus:ring-2 focus:ring-teal-500"
                                    placeholder="How did it feel?"
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={submitting}
                                className="w-full bg-teal-500 hover:bg-teal-600 text-white font-bold py-3 rounded-lg transition flex items-center justify-center gap-2"
                            >
                                {submitting ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Play size={20} />
                                )}
                                Log Workout
                            </button>
                        </form>
                    </motion.div>
                </div>
            )}
        </div>
    );
}
