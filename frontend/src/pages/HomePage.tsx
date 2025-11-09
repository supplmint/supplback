import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getTelegramUser } from '../utils/telegram';
import { getMe } from '../api/user';
import { checkHealth } from '../api/health';
import type { User } from '../types';

function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [healthStatus, setHealthStatus] = useState<string>('checking...');

  const tgUser = getTelegramUser();

  useEffect(() => {
    const loadData = async () => {
      try {
        // Check backend health
        const health = await checkHealth();
        setHealthStatus(health.status);

        // Load user data
        const userData = await getMe();
        setUser(userData);
      } catch (err: any) {
        setError(err.response?.data?.error || err.message || 'Ошибка загрузки данных');
        setHealthStatus('error');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="page">
      <h1 className="page-title">Health App</h1>

      {error && <div className="error">{error}</div>}

      <div className="card">
        <h2>Статус системы</h2>
        <p>Backend: {healthStatus}</p>
        {tgUser && (
          <>
            <p>Пользователь: {tgUser.first_name} {tgUser.last_name || ''}</p>
            <p>ID: {tgUser.id}</p>
          </>
        )}
      </div>

      {user && (
        <div className="card">
          <h2>Ваш профиль</h2>
          <p>TGID: {user.tgid}</p>
          {Object.keys(user.profile).length > 0 && (
            <pre style={{ fontSize: '12px', overflow: 'auto' }}>
              {JSON.stringify(user.profile, null, 2)}
            </pre>
          )}
        </div>
      )}

      <nav className="nav-menu">
        <Link to="/profile" className="nav-item">
          📝 Профиль
        </Link>
        <Link to="/analyses" className="nav-item">
          🔬 Анализы
        </Link>
        <Link to="/recommendations" className="nav-item">
          💊 Рекомендации
        </Link>
      </nav>
    </div>
  );
}

export default HomePage;

