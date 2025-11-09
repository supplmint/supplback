import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { updateRecommendations } from '../api/recommendations';

function RecommendationsPage() {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<Record<string, any>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await updateRecommendations(recommendations);
      setSuccess('Рекомендации успешно сохранены!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Ошибка сохранения рекомендаций');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page">
      <h1 className="page-title">Рекомендации</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <label className="label">Рекомендации (JSON)</label>
        <textarea
          className="input"
          rows={12}
          value={JSON.stringify(recommendations, null, 2)}
          onChange={(e) => {
            try {
              const parsed = JSON.parse(e.target.value);
              setRecommendations(parsed);
            } catch {
              // Invalid JSON, ignore
            }
          }}
          placeholder='{"diet": ["Ешьте больше овощей"], "exercise": ["Ходите 10000 шагов в день"], "medications": []}'
        />
      </div>

      <button className="button" onClick={handleSave} disabled={saving}>
        {saving ? 'Сохранение...' : 'Сохранить рекомендации'}
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

export default RecommendationsPage;

