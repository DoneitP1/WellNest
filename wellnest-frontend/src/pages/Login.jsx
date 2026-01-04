import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await login(email, password);
            navigate('/');
        } catch (e) {
            setError('Login failed. Please check your credentials.');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-gradient-to-br dark:from-gray-900 dark:to-gray-800 text-slate-800 dark:text-white p-4 transition-colors duration-300">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-white/10 backdrop-blur-lg p-8 rounded-2xl shadow-xl w-full max-w-md border border-slate-200 dark:border-white/20"
            >
                <h2 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-teal-500 to-emerald-500 bg-clip-text text-transparent">Welcome Back</h2>
                {error && <div className="bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-200 p-3 rounded mb-4 text-sm">{error}</div>}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-600 dark:text-gray-300 mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-gray-800/50 border border-slate-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-900 dark:text-white transition"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-600 dark:text-gray-300 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-slate-50 dark:bg-gray-800/50 border border-slate-300 dark:border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 text-slate-900 dark:text-white transition"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-bold py-2 rounded-lg hover:opacity-90 transition transform hover:scale-[1.02]"
                    >
                        Sign In
                    </button>
                </form>
                <p className="mt-6 text-center text-slate-500 dark:text-gray-400 text-sm">
                    Don't have an account? <Link to="/register" className="text-teal-500 dark:text-teal-400 hover:text-teal-600 dark:hover:text-teal-300">Sign Up</Link>
                </p>
            </motion.div>
        </div>
    );
}
