import { useState, useEffect } from 'react';
import api from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Scale } from 'lucide-react';

export default function WeightChart({ onLogSuccess }) {
    const [data, setData] = useState([]);
    const [weight, setWeight] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchData = async () => {
        try {
            const res = await api.get('/health/weight');
            if (Array.isArray(res.data)) {
                const formatted = res.data.map(d => ({
                    date: new Date(d.date).toLocaleDateString(),
                    weight: d.weight,
                    fullDate: d.date,
                })).reverse();
                setData(formatted);
            } else {
                setData([]);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleLogWeight = async (e) => {
        e.preventDefault();
        if (!weight) return;
        setLoading(true);
        try {
            await api.post('/health/weight', { weight: parseFloat(weight) });
            setWeight('');
            fetchData();
            onLogSuccess();
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 transition">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
                    <span className="bg-teal-100 dark:bg-teal-500/10 text-teal-600 dark:text-teal-400 p-2 rounded-lg"><Scale size={20} /></span>
                    Weight History
                </h3>
            </div>

            <div className="h-64 w-full mb-6">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#94a3b8" strokeOpacity={0.2} />
                        <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                        <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={['auto', 'auto']} />
                        <Tooltip
                            contentStyle={{ backgroundColor: 'var(--tooltip-bg)', borderColor: 'var(--tooltip-border)', borderRadius: '8px', color: 'var(--tooltip-text)' }}
                            itemStyle={{ color: '#14b8a6' }}
                        />
                        <Line type="monotone" dataKey="weight" stroke="#14b8a6" strokeWidth={3} dot={{ r: 4, fill: '#14b8a6' }} activeDot={{ r: 6 }} />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Inline style hack for tooltip theme support until passing props is cleaner */}
            <style>{`
         :root {
           --tooltip-bg: #ffffff;
           --tooltip-border: #e2e8f0;
           --tooltip-text: #0f172a;
         }
         .dark {
           --tooltip-bg: #1e293b;
           --tooltip-border: #334155;
           --tooltip-text: #ffffff;
         }
       `}</style>

            <form onSubmit={handleLogWeight} className="flex gap-2">
                <input
                    type="number"
                    step="0.1"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    className="flex-1 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg px-4 py-2 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500 transition"
                    placeholder="New Weight (kg)"
                />
                <button
                    type="submit"
                    disabled={loading}
                    className="bg-teal-500 hover:bg-teal-600 text-white font-bold px-6 py-2 rounded-lg transition"
                >
                    Log
                </button>
            </form>
        </div>
    );
}
