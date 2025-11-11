import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { initTelegramWebApp } from './utils/telegram';
import { waitForBackendReady } from './api/health';
import { getMe } from './api/user';
import { isProfileComplete, getFirstIncompleteStep } from './utils/profile';
import OnboardingForm from './components/OnboardingForm';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import AnalysesPage from './pages/AnalysesPage';
import RecommendationsPage from './pages/RecommendationsPage';
import CheckupsPage from './pages/CheckupsPage';
import type { User } from './types';
import './App.css';

function App() {
  const [isBackendReady, setIsBackendReady] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Проверка соединения с сервером...');
  const [user, setUser] = useState<User | null>(null);
  const [loadingUser, setLoadingUser] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    initTelegramWebApp();

    // Ждем готовности бэкенда перед показом контента
    const checkBackend = async () => {
      try {
        setLoadingMessage('Ожидание запуска сервера...');
        await waitForBackendReady(30, 2000, 60000); // 30 попыток, по 2 секунды, максимум 60 секунд
        setIsBackendReady(true);
        setLoadingMessage('');
      } catch (error: any) {
        console.error('Не удалось дождаться готовности бэкенда:', error);
        // После всех попыток все равно показываем контент
        // Пользователь увидит ошибки при попытке использовать функции
        setIsBackendReady(true);
        setLoadingMessage('');
      }
    };

    checkBackend();
  }, []);

  // Загружаем данные пользователя после готовности бэкенда
  useEffect(() => {
    if (!isBackendReady) return;

    const loadUser = async () => {
      setLoadingUser(true);
      try {
        const userData = await getMe();
        setUser(userData);
        // Проверяем, нужно ли показать форму онбординга
        if (!isProfileComplete(userData)) {
          setShowOnboarding(true);
        }
      } catch (error: any) {
        console.error('Failed to load user data:', error);
        // Если ошибка 401 (не аутентифицирован), показываем форму онбординга
        // Форма онбординга попытается сохранить данные, что может не сработать без аутентификации
        if (error.response?.status === 401) {
          // Не показываем форму без аутентификации
          console.log('User not authenticated, skipping onboarding');
        } else {
          // Для других ошибок попробуем показать форму
          setShowOnboarding(true);
        }
      } finally {
        setLoadingUser(false);
      }
    };

    loadUser();
  }, [isBackendReady]);

  // Обработчик завершения онбординга
  const handleOnboardingComplete = async () => {
    try {
      // Перезагружаем данные пользователя
      const userData = await getMe();
      setUser(userData);
      setShowOnboarding(false);
    } catch (error: any) {
      console.error('Failed to reload user data after onboarding:', error);
      // Все равно скрываем форму онбординга
      setShowOnboarding(false);
    }
  };

  // Показываем загрузку пока бэкенд не готов или загружаются данные пользователя
  if (!isBackendReady || loadingUser) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading">{loadingMessage || 'Загрузка...'}</div>
        </div>
      </div>
    );
  }

  // Показываем форму онбординга, если профиль не заполнен
  if (showOnboarding && user) {
    const firstIncompleteStep = getFirstIncompleteStep(user);
    return (
      <div className="app">
        <OnboardingForm 
          onComplete={handleOnboardingComplete}
          initialStep={firstIncompleteStep || 'name'}
          initialData={{
            name: user.profile?.name,
            gender: user.profile?.gender,
            age: user.profile?.age,
            height: user.profile?.height,
            weight: user.profile?.weight
          }}
        />
      </div>
    );
  }
  
  // Если showOnboarding true, но user null, значит была ошибка загрузки
  // В этом случае показываем форму с начальными значениями
  if (showOnboarding) {
    return (
      <div className="app">
        <OnboardingForm onComplete={handleOnboardingComplete} />
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/analyses" element={<AnalysesPage />} />
          <Route path="/checkups" element={<CheckupsPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;

