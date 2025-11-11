import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, updateProfile, getAnalysesHistory, type AnalysisItem } from '../api/user';
import type { User } from '../types';
import './ProfilePage.css';

function ProfilePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [profileData, setProfileData] = useState<Record<string, any>>({});
  const [editingField, setEditingField] = useState<string | null>(null);
  const [showAnalysesHistory, setShowAnalysesHistory] = useState(false);
  const [analysesHistory, setAnalysesHistory] = useState<AnalysisItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

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
      setEditingField(null);
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

  const handleFieldSave = async (key: string) => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const updated = await updateProfile(profileData);
      setUser(updated);
      setEditingField(null);
      setSuccess('Изменения сохранены!');
      setTimeout(() => setSuccess(null), 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  const getGenderLabel = (gender: string) => {
    switch (gender) {
      case 'male': return 'Мужской';
      case 'female': return 'Женский';
      default: return 'Не указан';
    }
  };

  const handleOpenAnalysesHistory = async () => {
    setShowAnalysesHistory(true);
    setLoadingHistory(true);
    setError(null);
    
    try {
      const response = await getAnalysesHistory();
      setAnalysesHistory(response.analyses || []);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Ошибка загрузки истории анализов');
      setAnalysesHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Дата не указана';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="page">
      <h1 className="page-title">Профиль</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="profile-container">
        {/* Имя */}
        <div className="profile-field-card">
          <div className="profile-field-header">
            <span className="profile-field-label">Имя</span>
            {editingField !== 'name' && (
              <button 
                className="profile-edit-btn"
                onClick={() => setEditingField('name')}
              >
                <img src="/edit.png" alt="Редактировать" className="profile-edit-icon" />
              </button>
            )}
          </div>
          {editingField === 'name' ? (
            <div className="profile-field-edit">
        <input
                className="profile-input"
          type="text"
          value={profileData.name || ''}
          onChange={(e) => updateField('name', e.target.value)}
          placeholder="Введите имя"
                autoFocus
              />
              <div className="profile-field-actions">
                <button 
                  className="profile-save-btn"
                  onClick={() => handleFieldSave('name')}
                  disabled={saving}
                >
                  Сохранить
                </button>
                <button 
                  className="profile-cancel-btn"
                  onClick={() => {
                    setEditingField(null);
                    const userData = user?.profile || {};
                    setProfileData({ ...profileData, name: userData.name });
                  }}
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-field-value">
              {profileData.name || 'Не указано'}
            </div>
          )}
        </div>

        {/* Пол */}
        <div className="profile-field-card">
          <div className="profile-field-header">
            <span className="profile-field-label">Пол</span>
            {editingField !== 'gender' && (
              <button 
                className="profile-edit-btn"
                onClick={() => setEditingField('gender')}
              >
                <img src="/edit.png" alt="Редактировать" className="profile-edit-icon" />
              </button>
            )}
          </div>
          {editingField === 'gender' ? (
            <div className="profile-field-edit">
        <select
                className="profile-input"
          value={profileData.gender || ''}
          onChange={(e) => updateField('gender', e.target.value)}
        >
          <option value="">Выберите пол</option>
          <option value="male">Мужской</option>
          <option value="female">Женский</option>
        </select>
              <div className="profile-field-actions">
                <button 
                  className="profile-save-btn"
                  onClick={() => handleFieldSave('gender')}
                  disabled={saving}
                >
                  Сохранить
                </button>
                <button 
                  className="profile-cancel-btn"
                  onClick={() => {
                    setEditingField(null);
                    const userData = user?.profile || {};
                    setProfileData({ ...profileData, gender: userData.gender });
                  }}
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-field-value">
              {getGenderLabel(profileData.gender || '')}
            </div>
          )}
        </div>

        {/* Возраст */}
        <div className="profile-field-card">
          <div className="profile-field-header">
            <span className="profile-field-label">Возраст</span>
            {editingField !== 'age' && (
              <button 
                className="profile-edit-btn"
                onClick={() => setEditingField('age')}
              >
                <img src="/edit.png" alt="Редактировать" className="profile-edit-icon" />
              </button>
            )}
          </div>
          {editingField === 'age' ? (
            <div className="profile-field-edit">
              <input
                className="profile-input"
                type="number"
                value={profileData.age || ''}
                onChange={(e) => updateField('age', e.target.value ? parseInt(e.target.value) : '')}
                placeholder="Введите возраст"
                autoFocus
              />
              <div className="profile-field-actions">
                <button 
                  className="profile-save-btn"
                  onClick={() => handleFieldSave('age')}
                  disabled={saving}
                >
                  Сохранить
                </button>
                <button 
                  className="profile-cancel-btn"
                  onClick={() => {
                    setEditingField(null);
                    const userData = user?.profile || {};
                    setProfileData({ ...profileData, age: userData.age });
                  }}
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-field-value">
              {profileData.age ? `${profileData.age} лет` : 'Не указан'}
            </div>
          )}
        </div>

        {/* Рост */}
        <div className="profile-field-card">
          <div className="profile-field-header">
            <span className="profile-field-label">Рост</span>
            {editingField !== 'height' && (
              <button 
                className="profile-edit-btn"
                onClick={() => setEditingField('height')}
              >
                <img src="/edit.png" alt="Редактировать" className="profile-edit-icon" />
              </button>
            )}
          </div>
          {editingField === 'height' ? (
            <div className="profile-field-edit">
              <input
                className="profile-input"
                type="number"
                step="0.1"
                value={profileData.height || ''}
                onChange={(e) => updateField('height', e.target.value ? parseFloat(e.target.value) : '')}
                placeholder="Введите рост (см)"
                autoFocus
              />
              <div className="profile-field-actions">
                <button 
                  className="profile-save-btn"
                  onClick={() => handleFieldSave('height')}
                  disabled={saving}
                >
                  Сохранить
                </button>
                <button 
                  className="profile-cancel-btn"
                  onClick={() => {
                    setEditingField(null);
                    const userData = user?.profile || {};
                    setProfileData({ ...profileData, height: userData.height });
                  }}
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-field-value">
              {profileData.height ? `${profileData.height} см` : 'Не указан'}
            </div>
          )}
        </div>

        {/* Вес */}
        <div className="profile-field-card">
          <div className="profile-field-header">
            <span className="profile-field-label">Вес</span>
            {editingField !== 'weight' && (
              <button 
                className="profile-edit-btn"
                onClick={() => setEditingField('weight')}
              >
                <img src="/edit.png" alt="Редактировать" className="profile-edit-icon" />
              </button>
            )}
          </div>
          {editingField === 'weight' ? (
            <div className="profile-field-edit">
              <input
                className="profile-input"
                type="number"
                step="0.1"
                value={profileData.weight || ''}
                onChange={(e) => updateField('weight', e.target.value ? parseFloat(e.target.value) : '')}
                placeholder="Введите вес (кг)"
                autoFocus
              />
              <div className="profile-field-actions">
                <button 
                  className="profile-save-btn"
                  onClick={() => handleFieldSave('weight')}
                  disabled={saving}
                >
                  Сохранить
                </button>
                <button 
                  className="profile-cancel-btn"
                  onClick={() => {
                    setEditingField(null);
                    const userData = user?.profile || {};
                    setProfileData({ ...profileData, weight: userData.weight });
                  }}
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <div className="profile-field-value">
              {profileData.weight ? `${profileData.weight} кг` : 'Не указан'}
            </div>
          )}
        </div>
      </div>

            <button 
              className="button profile-history-btn" 
              onClick={handleOpenAnalysesHistory}
            >
              История анализов
            </button>

      <button
        className="profile-back-btn"
        onClick={() => navigate('/')}
        aria-label="Назад"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke="#dc2626" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Модальное окно истории анализов */}
      {showAnalysesHistory && (
        <div className="analyses-modal-overlay" onClick={() => setShowAnalysesHistory(false)}>
          <div className="analyses-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="analyses-modal-header">
              <h2 className="analyses-modal-title">История анализов</h2>
              <button 
                className="analyses-modal-close"
                onClick={() => setShowAnalysesHistory(false)}
                aria-label="Закрыть"
              >
                ✕
              </button>
            </div>
            
            <div className="analyses-modal-body">
              {loadingHistory ? (
                <div className="analyses-loading">Загрузка...</div>
              ) : analysesHistory.length === 0 ? (
                <div className="analyses-empty">
                  <p>История анализов пуста</p>
                  <p className="analyses-empty-subtitle">Анализы появятся здесь после обработки</p>
                </div>
              ) : (
                <div className="analyses-list">
                  {analysesHistory.map((analysis, index) => (
                    <div key={index} className="analysis-card">
                      <div className="analysis-card-header">
                        <span className="analysis-file-name">
                          {analysis.fileName || analysis.file_name || `Анализ #${index + 1}`}
                        </span>
                        <span className="analysis-date">
                          {formatDate(analysis.createdAt || analysis.created_at)}
                        </span>
                      </div>
                      <div className="analysis-card-content">
                        <div className="analysis-text">
                          {analysis.text || analysis.report || 'Содержимое анализа недоступно'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfilePage;

