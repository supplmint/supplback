import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, updateProfile } from '../api/user';
import type { User } from '../types';

function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [profileData, setProfileData] = useState<Record<string, any>>({});

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await getMe();
        setUser(userData);
        setProfileData(userData.profile || {});
      } catch (err: any) {
        setError(err.response?.data?.error || err.message || 'Ошибка загрузки профиля');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const updated = await updateProfile(profileData);
      setUser(updated);
      setSuccess('Профиль успешно обновлён!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Ошибка сохранения профиля');
    } finally {
      setSaving(false);
    }
  };

  const updateField = (key: string, value: any) => {
    setProfileData((prev) => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="page">
      <h1 className="page-title">Профиль</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <label className="label">Имя</label>
        <input
          className="input"
          type="text"
          value={profileData.name || ''}
          onChange={(e) => updateField('name', e.target.value)}
          placeholder="Введите имя"
        />

        <label className="label">Возраст</label>
        <input
          className="input"
          type="number"
          value={profileData.age || ''}
          onChange={(e) => updateField('age', e.target.value ? parseInt(e.target.value) : '')}
          placeholder="Введите возраст"
        />

        <label className="label">Пол</label>
        <select
          className="input"
          value={profileData.gender || ''}
          onChange={(e) => updateField('gender', e.target.value)}
        >
          <option value="">Выберите пол</option>
          <option value="male">Мужской</option>
          <option value="female">Женский</option>
          <option value="other">Другое</option>
        </select>

        <label className="label">Дополнительная информация (JSON)</label>
        <textarea
          className="input"
          rows={6}
          value={JSON.stringify(profileData, null, 2)}
          onChange={(e) => {
            try {
              const parsed = JSON.parse(e.target.value);
              setProfileData(parsed);
            } catch {
              // Invalid JSON, ignore
            }
          }}
          placeholder='{"key": "value"}'
        />
      </div>

      <button className="button" onClick={handleSave} disabled={saving}>
        {saving ? 'Сохранение...' : 'Сохранить профиль'}
      </button>

      <button
        className="button"
        onClick={() => navigate('/')}
        style={{ marginTop: '12px', background: 'var(--tg-theme-secondary-bg-color, #f0f0f0)', color: 'var(--tg-theme-text-color, #000000)' }}
      >
        Назад
      </button>
    </div>
  );
}

export default ProfilePage;

