import { Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Onboarding from './pages/Onboarding';
import Social from './pages/Social';
import Fasting from './pages/Fasting';
import Workouts from './pages/Workouts';
import Deficit from './pages/Deficit';
import Recipes from './pages/Recipes';
import Blog from './pages/Blog';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <Onboarding />
          </ProtectedRoute>
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/social"
        element={
          <ProtectedRoute>
            <Layout>
              <Social />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/fasting"
        element={
          <ProtectedRoute>
            <Layout>
              <Fasting />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/workouts"
        element={
          <ProtectedRoute>
            <Layout>
              <Workouts />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/deficit"
        element={
          <ProtectedRoute>
            <Layout>
              <Deficit />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recipes"
        element={
          <ProtectedRoute>
            <Layout>
              <Recipes />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/blog"
        element={
          <ProtectedRoute>
            <Layout>
              <Blog />
            </Layout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
