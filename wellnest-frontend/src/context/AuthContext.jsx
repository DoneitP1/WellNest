import { createContext, useState, useContext, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            // Decoded token would be better, but for now consistent object shape is key
            setUser({ token, email: 'User' }); // Placeholder email until we have a /me endpoint or decode JWT
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await api.post('/auth/token', formData);
            localStorage.setItem('token', response.data.access_token);
            setUser({ email, token: response.data.access_token });
            return true;
        } catch (e) {
            throw e;
        }
    };

    const register = async (email, password) => {
        await api.post('/auth/register', { email, password });
        await login(email, password);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
