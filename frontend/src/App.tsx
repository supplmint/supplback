import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { initTelegramWebApp } from './utils/telegram';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import AnalysesPage from './pages/AnalysesPage';
import RecommendationsPage from './pages/RecommendationsPage';
import './App.css';

function App() {
  useEffect(() => {
    initTelegramWebApp();
  }, []);

  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/analyses" element={<AnalysesPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

