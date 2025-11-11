import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAnalysesHistory, type AnalysisItem } from '../api/user';
import { getRecommendation } from '../api/recommendations';
import './RecommendationsPage.css';
import './AnalysesPage.css';

function RecommendationsPage() {
  const navigate = useNavigate();
  const [showAnalysisSelection, setShowAnalysisSelection] = useState(false);
  const [allAnalyses, setAllAnalyses] = useState<AnalysisItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisItem | null>(null);
  const [recommendation, setRecommendation] = useState<string | null>(null);
  const [loadingRecommendation, setLoadingRecommendation] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load analyses history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        setLoadingHistory(true);
        const response = await getAnalysesHistory();
        const analyses = response.analyses || [];
        setAllAnalyses(analyses);
        
        // Show selection modal if there are analyses and we haven't selected one yet
        if (analyses.length > 0 && !selectedAnalysis) {
          setShowAnalysisSelection(true);
        }
      } catch (err: any) {
        console.error('Failed to load analyses history:', err);
        setAllAnalyses([]);
      } finally {
        setLoadingHistory(false);
      }
    };
    
    loadHistory();
    
    // Poll for updates every 5 seconds
    const interval = setInterval(loadHistory, 5000);
    return () => clearInterval(interval);
  }, [selectedAnalysis]);

  const handleSelectAnalysis = async (analysis: AnalysisItem, index: number) => {
    setSelectedAnalysis(analysis);
    setLoadingRecommendation(true);
    setError(null);
    setRecommendation(null);

    try {
      // Use index as analysis_id, or create a unique ID from fileName and createdAt
      const analysisId = analysis.fileName && analysis.createdAt 
        ? `${analysis.fileName}_${analysis.createdAt}`
        : `analysis_${index}`;
      
      const response = await getRecommendation(analysisId);
      setRecommendation(response.recommendation);
      setShowAnalysisSelection(false);
    } catch (err: any) {
      console.error('Failed to load recommendation:', err);
      setError(err.response?.data?.error || err.message || 'Ошибка загрузки рекомендации');
    } finally {
      setLoadingRecommendation(false);
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

  const handleBackToSelection = () => {
    setShowAnalysisSelection(true);
    setSelectedAnalysis(null);
    setRecommendation(null);
  };

  return (
    <div className="page">
      <h1 className="page-title">Рекомендации по добавкам</h1>

      {error && <div className="error">{error}</div>}

      {/* Модальное окно выбора анализа */}
      {showAnalysisSelection && (
        <div className="analyses-modal-overlay" onClick={() => navigate('/')}>
          <div className="analyses-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="analyses-modal-header">
              <h2 className="analyses-modal-title">Выберите анализ</h2>
              <button 
                className="analyses-modal-close"
                onClick={() => navigate('/')}
                aria-label="Закрыть"
              >
                ✕
              </button>
            </div>
            
            <div className="analyses-modal-body">
              <p style={{ marginBottom: '16px', color: 'var(--text-secondary, #6b6b6b)' }}>
                По какому анализу вам нужна рекомендация?
              </p>
              
              {loadingHistory ? (
                <div className="analyses-loading">Загрузка...</div>
              ) : allAnalyses.length === 0 ? (
                <div className="analyses-empty">
                  <p>История анализов пуста</p>
                  <p className="analyses-empty-subtitle">Загрузите анализы, чтобы получить рекомендации</p>
                </div>
              ) : (
                <div className="analyses-list">
                  {allAnalyses.map((analysis, index) => (
                    <div 
                      key={index} 
                      className="analysis-card"
                      onClick={() => handleSelectAnalysis(analysis, index)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="analysis-card-header">
                        <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                          <span className="analysis-file-name">
                            {analysis.fileName || analysis.file_name || `Анализ #${index + 1}`}
                          </span>
                          <span className="analysis-date" style={{ marginTop: '4px' }}>
                            {formatDate(analysis.createdAt || analysis.created_at)}
                          </span>
                        </div>
                        <svg 
                          width="24" 
                          height="24" 
                          viewBox="0 0 24 24" 
                          fill="none" 
                          xmlns="http://www.w3.org/2000/svg"
                          style={{ 
                            color: '#dc2626',
                            marginLeft: '12px',
                            flexShrink: 0
                          }}
                        >
                          <path 
                            d="M9 18L15 12L9 6" 
                            stroke="#dc2626" 
                            strokeWidth="2.5" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                          />
                        </svg>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Отображение рекомендации */}
      {selectedAnalysis && !showAnalysisSelection && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
              Рекомендация по анализу
            </h2>
            <button 
              className="button"
              onClick={handleBackToSelection}
              style={{ 
                padding: '8px 16px',
                fontSize: '14px',
                background: 'var(--tg-theme-secondary-bg-color, #f0f0f0)',
                color: 'var(--tg-theme-text-color, #000000)'
              }}
            >
              Выбрать другой анализ
            </button>
          </div>
          
          <div style={{ marginBottom: '12px', fontSize: '14px', color: 'var(--text-secondary, #6b6b6b)' }}>
            <strong>Файл:</strong> {selectedAnalysis.fileName || selectedAnalysis.file_name || 'Не указан'}
            <br />
            <strong>Дата:</strong> {formatDate(selectedAnalysis.createdAt || selectedAnalysis.created_at)}
          </div>

          {loadingRecommendation ? (
            <div className="loading" style={{ padding: '40px', textAlign: 'center' }}>
              Загрузка рекомендации...
            </div>
          ) : recommendation ? (
            <div className="recommendation-content" style={{ 
              whiteSpace: 'pre-wrap', 
              padding: '16px',
              fontSize: '14px',
              lineHeight: '1.6',
              color: 'var(--text-primary, #2d2d2d)',
              background: 'rgba(255, 255, 255, 0.3)',
              borderRadius: '12px',
              maxHeight: '600px',
              overflowY: 'auto'
            }}>
              {recommendation}
            </div>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary, #6b6b6b)' }}>
              Рекомендация не найдена
            </div>
          )}
        </div>
      )}

      {!showAnalysisSelection && !selectedAnalysis && allAnalyses.length === 0 && (
        <div className="card">
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary, #6b6b6b)' }}>
            <p>История анализов пуста</p>
            <p style={{ marginTop: '8px', fontSize: '14px' }}>
              Загрузите анализы, чтобы получить рекомендации
            </p>
          </div>
        </div>
      )}

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
