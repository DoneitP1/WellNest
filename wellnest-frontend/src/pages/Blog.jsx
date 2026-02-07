import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api';
import {
    BookOpen, Search, Clock, User, Tag, Heart, Eye,
    Loader2, X, ArrowLeft, Share2, Bookmark, ChevronRight
} from 'lucide-react';

export default function Blog() {
    const [posts, setPosts] = useState([]);
    const [featuredPosts, setFeaturedPosts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedPost, setSelectedPost] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [postsRes, featuredRes, categoriesRes] = await Promise.all([
                api.get('/blog/'),
                api.get('/blog/featured'),
                api.get('/blog/categories')
            ]);
            setPosts(postsRes.data);
            setFeaturedPosts(featuredRes.data);
            setCategories(categoriesRes.data);
        } catch (error) {
            console.error('Failed to fetch blog data:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchPosts = async (category = '', search = '') => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (category) params.append('category', category);
            if (search) params.append('search', search);

            const response = await api.get(`/blog/?${params.toString()}`);
            setPosts(response.data);
        } catch (error) {
            console.error('Failed to fetch posts:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchPostDetails = async (postId) => {
        try {
            const response = await api.get(`/blog/${postId}`);
            setSelectedPost(response.data);
        } catch (error) {
            console.error('Failed to fetch post:', error);
        }
    };

    const handleLike = async (postId) => {
        try {
            await api.post(`/blog/${postId}/like`);
            if (selectedPost && selectedPost.id === postId) {
                setSelectedPost({
                    ...selectedPost,
                    likes_count: selectedPost.likes_count + 1
                });
            }
            fetchPosts(selectedCategory, searchQuery);
        } catch (error) {
            console.error('Failed to like post:', error);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        fetchPosts(selectedCategory, searchQuery);
    };

    const handleCategoryClick = (category) => {
        setSelectedCategory(category);
        fetchPosts(category, searchQuery);
    };

    const getAuthorBadge = (authorRole) => {
        switch (authorRole) {
            case 'doctor':
                return { text: 'Doctor', color: 'bg-blue-100 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400' };
            case 'dietician':
                return { text: 'Dietician', color: 'bg-green-100 text-green-600 dark:bg-green-500/20 dark:text-green-400' };
            case 'admin':
                return { text: 'Admin', color: 'bg-purple-100 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400' };
            default:
                return { text: 'Expert', color: 'bg-slate-100 text-slate-600' };
        }
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const estimateReadTime = (content) => {
        const wordsPerMinute = 200;
        const words = content?.split(/\s+/).length || 0;
        return Math.max(1, Math.ceil(words / wordsPerMinute));
    };

    if (loading && posts.length === 0) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="w-8 h-8 animate-spin text-teal-500" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <BookOpen className="w-8 h-8 text-teal-500" />
                <div>
                    <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
                        Expert Blog
                    </h1>
                    <p className="text-sm text-slate-500">
                        Health insights from verified doctors & dieticians
                    </p>
                </div>
            </div>

            {/* Search */}
            <form onSubmit={handleSearch} className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search articles..."
                    className="w-full pl-10 pr-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
            </form>

            {/* Categories */}
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                <button
                    onClick={() => handleCategoryClick('')}
                    className={`px-4 py-2 rounded-full whitespace-nowrap text-sm transition ${
                        !selectedCategory
                            ? 'bg-teal-500 text-white'
                            : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                    }`}
                >
                    All
                </button>
                {categories.map(cat => (
                    <button
                        key={cat.name}
                        onClick={() => handleCategoryClick(cat.name)}
                        className={`px-4 py-2 rounded-full whitespace-nowrap text-sm transition ${
                            selectedCategory === cat.name
                                ? 'bg-teal-500 text-white'
                                : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                        }`}
                    >
                        {cat.name} ({cat.count})
                    </button>
                ))}
            </div>

            {/* Featured Posts */}
            {featuredPosts.length > 0 && !selectedCategory && !searchQuery && (
                <div className="space-y-3">
                    <h2 className="font-semibold text-slate-800 dark:text-white">Featured</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {featuredPosts.slice(0, 2).map((post, idx) => (
                            <motion.div
                                key={post.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                onClick={() => fetchPostDetails(post.id)}
                                className="bg-gradient-to-br from-teal-500 to-emerald-500 rounded-xl p-5 cursor-pointer hover:shadow-lg transition text-white"
                            >
                                <span className="text-xs bg-white/20 px-2 py-1 rounded-full">
                                    {post.category}
                                </span>
                                <h3 className="font-bold text-lg mt-3 line-clamp-2">
                                    {post.title}
                                </h3>
                                <p className="text-white/80 text-sm mt-2 line-clamp-2">
                                    {post.excerpt}
                                </p>
                                <div className="flex items-center gap-3 mt-4 text-sm text-white/70">
                                    <span className="flex items-center gap-1">
                                        <User size={14} />
                                        {post.author_name}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <Clock size={14} />
                                        {post.read_time_minutes} min read
                                    </span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* All Posts */}
            <div className="space-y-3">
                <h2 className="font-semibold text-slate-800 dark:text-white">
                    {selectedCategory ? `${selectedCategory} Articles` : 'Latest Articles'}
                </h2>

                {posts.length === 0 ? (
                    <div className="text-center py-12 text-slate-500">
                        <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        <p>No articles found.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {posts.map((post, idx) => (
                            <motion.div
                                key={post.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                onClick={() => fetchPostDetails(post.id)}
                                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 cursor-pointer hover:shadow-md transition"
                            >
                                <div className="flex gap-4">
                                    {post.cover_image ? (
                                        <img
                                            src={post.cover_image}
                                            alt={post.title}
                                            className="w-24 h-24 rounded-lg object-cover flex-shrink-0"
                                        />
                                    ) : (
                                        <div className="w-24 h-24 rounded-lg bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center flex-shrink-0">
                                            <BookOpen className="w-8 h-8 text-white/50" />
                                        </div>
                                    )}

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 px-2 py-0.5 rounded">
                                                {post.category}
                                            </span>
                                            {post.author_role && (
                                                <span className={`text-xs px-2 py-0.5 rounded ${getAuthorBadge(post.author_role).color}`}>
                                                    {getAuthorBadge(post.author_role).text}
                                                </span>
                                            )}
                                        </div>

                                        <h3 className="font-semibold text-slate-800 dark:text-white line-clamp-2">
                                            {post.title}
                                        </h3>

                                        <p className="text-sm text-slate-500 line-clamp-2 mt-1">
                                            {post.excerpt}
                                        </p>

                                        <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
                                            <span className="flex items-center gap-1">
                                                <User size={12} />
                                                {post.author_name}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Clock size={12} />
                                                {post.read_time_minutes} min
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Eye size={12} />
                                                {post.views_count}
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Heart size={12} />
                                                {post.likes_count}
                                            </span>
                                        </div>
                                    </div>

                                    <ChevronRight className="w-5 h-5 text-slate-400 self-center" />
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>

            {/* Post Detail Modal */}
            <AnimatePresence>
                {selectedPost && (
                    <div
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
                        onClick={() => setSelectedPost(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white dark:bg-slate-800 w-full h-full md:rounded-2xl md:w-[90%] md:max-w-3xl md:h-[90vh] overflow-y-auto"
                            onClick={e => e.stopPropagation()}
                        >
                            {/* Header */}
                            <div className="sticky top-0 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 p-4 flex items-center justify-between z-10">
                                <button
                                    onClick={() => setSelectedPost(null)}
                                    className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white"
                                >
                                    <ArrowLeft size={20} />
                                    Back
                                </button>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handleLike(selectedPost.id)}
                                        className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full"
                                    >
                                        <Heart size={20} className="text-red-500" />
                                    </button>
                                    <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full">
                                        <Bookmark size={20} />
                                    </button>
                                    <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full">
                                        <Share2 size={20} />
                                    </button>
                                </div>
                            </div>

                            {/* Cover Image */}
                            {selectedPost.cover_image && (
                                <img
                                    src={selectedPost.cover_image}
                                    alt={selectedPost.title}
                                    className="w-full h-48 md:h-64 object-cover"
                                />
                            )}

                            {/* Content */}
                            <div className="p-6">
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="text-sm bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 px-3 py-1 rounded-full">
                                        {selectedPost.category}
                                    </span>
                                    {selectedPost.tags?.split(',').slice(0, 3).map((tag, idx) => (
                                        <span key={idx} className="text-xs bg-teal-100 dark:bg-teal-500/20 text-teal-600 dark:text-teal-400 px-2 py-1 rounded">
                                            #{tag.trim()}
                                        </span>
                                    ))}
                                </div>

                                <h1 className="text-2xl md:text-3xl font-bold text-slate-800 dark:text-white mb-4">
                                    {selectedPost.title}
                                </h1>

                                {/* Author Info */}
                                <div className="flex items-center gap-3 mb-6 pb-6 border-b border-slate-200 dark:border-slate-700">
                                    <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-emerald-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                                        {selectedPost.author_name?.charAt(0)}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <p className="font-medium text-slate-800 dark:text-white">
                                                {selectedPost.author_name}
                                            </p>
                                            {selectedPost.author_role && (
                                                <span className={`text-xs px-2 py-0.5 rounded ${getAuthorBadge(selectedPost.author_role).color}`}>
                                                    {getAuthorBadge(selectedPost.author_role).text}
                                                </span>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-3 text-sm text-slate-500">
                                            <span>{formatDate(selectedPost.published_at)}</span>
                                            <span>·</span>
                                            <span>{selectedPost.read_time_minutes} min read</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Article Content */}
                                <div className="prose dark:prose-invert max-w-none">
                                    {selectedPost.content?.split('\n').map((paragraph, idx) => (
                                        paragraph.trim() && (
                                            <p key={idx} className="text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
                                                {paragraph}
                                            </p>
                                        )
                                    ))}
                                </div>

                                {/* Stats */}
                                <div className="flex items-center gap-6 mt-8 pt-6 border-t border-slate-200 dark:border-slate-700">
                                    <button
                                        onClick={() => handleLike(selectedPost.id)}
                                        className="flex items-center gap-2 text-slate-600 dark:text-slate-400 hover:text-red-500 transition"
                                    >
                                        <Heart size={20} />
                                        <span>{selectedPost.likes_count} likes</span>
                                    </button>
                                    <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                                        <Eye size={20} />
                                        <span>{selectedPost.views_count} views</span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
