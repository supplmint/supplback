import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { updateAnalyses } from '../api/analyses';
import { notifyUpload } from '../api/upload';

function AnalysesPage() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await updateAnalyses(analyses);
      setSuccess('Анализы успешно сохранены!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Ошибка сохранения анализов');
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      await notifyUpload(file.name, file.type, file.size);
      setSuccess(`Файл ${file.name} успешно загружен!`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Ошибка загрузки файла');
    } finally {
      setLoading(false);
      // Reset input
      event.target.value = '';
    }
  };

  const updateField = (key: string, value: any) => {
    setAnalyses((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="page">
      <h1 className="page-title">Анализы</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="card">
        <label className="label">Загрузить файл анализа</label>
        <input
          type="file"
          onChange={handleFileUpload}
          disabled={loading}
          style={{ marginBottom: '12px', width: '100%' }}
        />
        {loading && <div className="loading">Загрузка...</div>}
      </div>

      <div className="card">
        <label className="label">Данные анализов (JSON)</label>
        <textarea
          className="input"
          rows={12}
          value={JSON.stringify(analyses, null, 2)}
          onChange={(e) => {
            try {
              const parsed = JSON.parse(e.target.value);
              setAnalyses(parsed);
            } catch {
              // Invalid JSON, ignore
            }
          }}
          placeholder='{"blood_test": {"hemoglobin": 140}, "urine_test": {}}'
        />
      </div>

      <button className="button" onClick={handleSave} disabled={saving}>
        {saving ? 'Сохранение...' : 'Сохранить анализы'}
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

export default AnalysesPage;

