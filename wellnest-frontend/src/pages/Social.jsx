import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';
import {
    Heart, MessageCircle, Copy, Plus, Image, Send, X,
    Loader2, ChefHat, Clock, Check
} from 'lucide-react';

export default function Social() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showNewPost, setShowNewPost] = useState(false);
    const [newPostContent, setNewPostContent] = useState('');
    const [selectedMealType, setSelectedMealType] = useState('snack');
    const [copying, setCopying] = useState(null);
    const [copySuccess, setCopySuccess] = useState(null);

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            const response = await api.get('/social/feed');
            setPosts(response.data);
        } catch (error) {
            console.error('Failed to fetch posts:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLike = async (postId) => {
        try {
            const response = await api.post(`/social/posts/${postId}/like`);
            setPosts(posts.map(post =>
                post.id === postId
                    ? { ...post, likes_count: response.data.likes_count, is_liked: response.data.action === 'liked' }
                    : post
            ));
        } catch (error) {
            console.error('Failed to like post:', error);
        }
    };

    const handleCopyMeal = async (postId) => {
        setCopying(postId);
        try {
            const response = await api.post(`/social/posts/${postId}/copy?meal_type=${selectedMealType}`);
            setCopySuccess(postId);
            setTimeout(() => setCopySuccess(null), 2000);

            // Update copy count
            setPosts(posts.map(post =>
                post.id === postId
                    ? { ...post, copies_count: post.copies_count + 1 }
                    : post
            ));
        } catch (error) {
            console.error('Failed to copy meal:', error);
            alert(error.response?.data?.detail || 'Failed to copy meal');
        } finally {
            setCopying(null);
        }
    };

    const formatTime = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(hours / 24);

        if (hours < 1) return 'Just now';
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    };

    const mealTypes = ['breakfast', 'lunch', 'dinner', 'snack'];

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
                    Social Feed
                </h1>
                <button
                    onClick={() => setShowNewPost(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition"
                >
                    <Plus size={20} />
                    Share Meal
                </button>
            </div>

            {/* Meal Type Filter for Copy */}
            <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                    When copying meals, add to:
                </p>
                <div className="flex gap-2">
                    {mealTypes.map(type => (
                        <button
                            key={type}
                            onClick={() => setSelectedMealType(type)}
                            className={`px-3 py-1 rounded-lg text-sm capitalize transition ${
                                selectedMealType === type
                                    ? 'bg-teal-500 text-white'
                                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                            }`}
                        >
                            {type}
                        </button>
                    ))}
                </div>
            </div>

            {/* Posts Feed */}
            <div className="space-y-4">
                {posts.length === 0 ? (
                    <div className="text-center py-12 bg-white dark:bg-slate-800 rounded-xl">
                        <ChefHat className="w-12 h-12 mx-auto text-slate-400 mb-4" />
                        <p className="text-slate-600 dark:text-slate-400">
                            No meals shared yet. Be the first to share!
                        </p>
                    </div>
                ) : (
                    posts.map(post => (
                        <motion.div
                            key={post.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden"
                        >
                            {/* Post Header */}
                            <div className="p-4 flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center text-white font-bold">
                                    {post.username?.charAt(0).toUpperCase() || 'U'}
                                </div>
                                <div className="flex-1">
                                    <p className="font-semibold text-slate-800 dark:text-white">
                                        {post.username}
                                    </p>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                                        <Clock size={12} />
                                        {formatTime(post.created_at)}
                                        {post.meal_type && (
                                            <span className="ml-2 px-2 py-0.5 bg-slate-100 dark:bg-slate-700 rounded text-xs capitalize">
                                                {post.meal_type}
                                            </span>
                                        )}
                                    </p>
                                </div>
                            </div>

                            {/* Post Image */}
                            {post.image_url && (
                                <img
                                    src={post.image_url}
                                    alt="Meal"
                                    className="w-full h-64 object-cover"
                                />
                            )}

                            {/* Content */}
                            {post.content && (
                                <p className="px-4 py-2 text-slate-700 dark:text-slate-300">
                                    {post.content}
                                </p>
                            )}

                            {/* Nutrition Info */}
                            {post.total_calories > 0 && (
                                <div className="px-4 py-3 bg-slate-50 dark:bg-slate-700/50">
                                    <div className="grid grid-cols-4 gap-2 text-center">
                                        <div>
                                            <p className="text-lg font-bold text-orange-500">{post.total_calories}</p>
                                            <p className="text-xs text-slate-500">kcal</p>
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-red-500">{post.total_protein}g</p>
                                            <p className="text-xs text-slate-500">Protein</p>
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-blue-500">{post.total_carbs}g</p>
                                            <p className="text-xs text-slate-500">Carbs</p>
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-yellow-500">{post.total_fat}g</p>
                                            <p className="text-xs text-slate-500">Fat</p>
                                        </div>
                                    </div>

                                    {/* Food Items */}
                                    {post.food_items && post.food_items.length > 0 && (
                                        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-600">
                                            <p className="text-xs text-slate-500 mb-2">Includes:</p>
                                            <div className="flex flex-wrap gap-1">
                                                {post.food_items.map((item, idx) => (
                                                    <span
                                                        key={idx}
                                                        className="px-2 py-1 bg-white dark:bg-slate-600 rounded text-xs text-slate-700 dark:text-slate-300"
                                                    >
                                                        {item.food_name}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Actions */}
                            <div className="px-4 py-3 flex items-center justify-between border-t border-slate-100 dark:border-slate-700">
                                <div className="flex items-center gap-4">
                                    <button
                                        onClick={() => handleLike(post.id)}
                                        className={`flex items-center gap-1 transition ${
                                            post.is_liked
                                                ? 'text-red-500'
                                                : 'text-slate-500 hover:text-red-500'
                                        }`}
                                    >
                                        <Heart size={20} fill={post.is_liked ? 'currentColor' : 'none'} />
                                        <span className="text-sm">{post.likes_count}</span>
                                    </button>

                                    <button className="flex items-center gap-1 text-slate-500 hover:text-blue-500 transition">
                                        <MessageCircle size={20} />
                                        <span className="text-sm">{post.comments_count}</span>
                                    </button>
                                </div>

                                {/* Copy Meal Button */}
                                {post.food_items && post.food_items.length > 0 && (
                                    <button
                                        onClick={() => handleCopyMeal(post.id)}
                                        disabled={copying === post.id}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition ${
                                            copySuccess === post.id
                                                ? 'bg-green-500 text-white'
                                                : 'bg-teal-100 dark:bg-teal-500/20 text-teal-600 dark:text-teal-400 hover:bg-teal-200 dark:hover:bg-teal-500/30'
                                        }`}
                                    >
                                        {copying === post.id ? (
                                            <Loader2 size={16} className="animate-spin" />
                                        ) : copySuccess === post.id ? (
                                            <Check size={16} />
                                        ) : (
                                            <Copy size={16} />
                                        )}
                                        {copySuccess === post.id ? 'Added!' : 'Add Same'}
                                        {post.copies_count > 0 && (
                                            <span className="text-xs opacity-70">({post.copies_count})</span>
                                        )}
                                    </button>
                                )}
                            </div>
                        </motion.div>
                    ))
                )}
            </div>

            {/* New Post Modal */}
            <AnimatePresence>
                {showNewPost && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                        onClick={() => setShowNewPost(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white dark:bg-slate-800 rounded-2xl p-6 w-full max-w-md"
                            onClick={e => e.stopPropagation()}
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-bold text-slate-800 dark:text-white">
                                    Share Your Meal
                                </h2>
                                <button
                                    onClick={() => setShowNewPost(false)}
                                    className="text-slate-400 hover:text-slate-600"
                                >
                                    <X size={24} />
                                </button>
                            </div>

                            <textarea
                                value={newPostContent}
                                onChange={(e) => setNewPostContent(e.target.value)}
                                placeholder="What are you eating? Share your meal with the community..."
                                className="w-full h-32 p-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-teal-500"
                            />

                            <div className="flex items-center justify-between mt-4">
                                <button className="flex items-center gap-2 text-slate-500 hover:text-teal-500">
                                    <Image size={20} />
                                    Add Photo
                                </button>

                                <button className="flex items-center gap-2 px-6 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">
                                    <Send size={18} />
                                    Share
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
