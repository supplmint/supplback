import { useState, ChangeEvent, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadFileToWebhook } from '../api/upload';
import { getMe, getAnalysesHistory, type AnalysisItem } from '../api/user';
import { getTelegramUser } from '../utils/telegram';
import { ReportViewer } from '../components/ReportViewer';
import './AnalysesPage.css';

function AnalysesPage() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [lastReport, setLastReport] = useState<string | null>(null);
  const [showAllAnalyses, setShowAllAnalyses] = useState(false);
  const [allAnalyses, setAllAnalyses] = useState<AnalysisItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);
  const previousReportRef = useRef<string>('');
  const [expandedAnalysisIndex, setExpandedAnalysisIndex] = useState<number | null>(null);

  // Load last report from analyses.last_report
  useEffect(() => {
    const loadLastReport = async () => {
      try {
        const user = await getMe();
        
        // Просто берем данные из analyses.last_report.text
        let reportText = null;
        if (user?.analyses?.last_report?.text) {
          reportText = user.analyses.last_report.text;
        } else if (user?.analyses?.last_report?.report) {
          reportText = user.analyses.last_report.report;
        }
        
        // Если данные есть и это строка, устанавливаем
        if (reportText && typeof reportText === 'string' && reportText.trim().length > 0) {
          // Проверяем, изменился ли отчет (новый отчет пришел)
          if (previousReportRef.current !== reportText) {
            console.log('[AnalysesPage] Setting lastReport, length:', reportText.length);
            setLastReport(reportText);
            previousReportRef.current = reportText;
            setFileUploaded(false); // Сбрасываем флаг, когда новый отчет получен
          }
        } else {
          // Если отчета нет и мы не ждем загрузку, сбрасываем
          if (!fileUploaded) {
            console.log('[AnalysesPage] No valid report text found');
            setLastReport('');
            previousReportRef.current = '';
          }
        }
      } catch (err: any) {
        console.error('Failed to load last report:', err);
        if (!fileUploaded) {
          setLastReport('');
          previousReportRef.current = '';
        }
      }
    };
    
    loadLastReport();
    
    // Poll for updates every 5 seconds
    const interval = setInterval(loadLastReport, 5000);
    return () => clearInterval(interval);
  }, [fileUploaded]);

  // Load analyses history on mount to check if there are any analyses
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await getAnalysesHistory();
        setAllAnalyses(response.analyses || []);
      } catch (err: any) {
        console.error('Failed to load analyses history:', err);
        setAllAnalyses([]);
      }
    };
    
    loadHistory();
    
    // Poll for updates every 5 seconds
    const interval = setInterval(loadHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleOpenAllAnalyses = async () => {
    setShowAllAnalyses(true);
    setLoadingHistory(true);
    setError(null);

    try {
      const response = await getAnalysesHistory();
      setAllAnalyses(response.analyses || []);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Ошибка загрузки истории анализов');
      setAllAnalyses([]);
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

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Файл слишком большой. Максимальный размер: 10MB');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setLastReport(''); // Сбрасываем отчет при начале новой загрузки
    previousReportRef.current = ''; // Сбрасываем предыдущий отчет
    setFileUploaded(true); // Устанавливаем флаг загрузки, чтобы показать кружок

    // Timeout after 60 seconds
    const timeoutId = setTimeout(() => {
      setLoading(false);
      setError('Таймаут загрузки. Попробуйте еще раз или выберите файл меньшего размера.');
    }, 60000);

    try {
      const tgUser = getTelegramUser();
      if (!tgUser) {
        throw new Error('Telegram user not found');
      }

      console.log('Starting file upload:', file.name, file.size, 'bytes');
      console.log('Telegram user ID:', tgUser.id);

      // Upload file through backend (proxy to webhook)
      console.log('Uploading file through backend...');
      const startTime = Date.now();
      
      const result = await uploadFileToWebhook(file);
      
      const duration = Date.now() - startTime;
      console.log(`✅ Upload completed in ${duration}ms`);
      console.log('Upload result:', result);
      console.log('Webhook status:', result.webhookStatus);
      console.log('Webhook response:', result.webhookResponse);
      
      if (result.success) {
        clearTimeout(timeoutId);
        setSuccess(`Файл ${file.name} успешно отправлен на обработку!`);
        setFileUploaded(true);
        setTimeout(() => setSuccess(null), 5000);
      } else {
        throw new Error('Загрузка не удалась');
      }
    } catch (err: any) {
      clearTimeout(timeoutId);
      console.error('Upload error:', err);
      
      // Check if it's a 404 error
      if (err.response?.status === 404) {
        setError(`Endpoint не найден (404). Проверьте URL: ${err.config?.url || 'unknown'}`);
      } else if (err.response?.status) {
        const errorMessage = err.response?.data?.detail || err.response?.data?.error || err.message || 'Ошибка загрузки файла';
        setError(`Ошибка ${err.response.status}: ${errorMessage}`);
      } else if (err.code === 'ECONNABORTED') {
        setError('Таймаут загрузки. Файл может быть слишком большим.');
      } else {
        setError(err.message || 'Ошибка загрузки файла');
      }
      
      console.error('Full error details:', {
        message: err.message,
        code: err.code,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        url: err.config?.url,
        stack: err.stack,
      });
    } finally {
      setLoading(false);
      // Reset input
      if (e.target) {
        e.target.value = '';
      }
    }
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
          accept="image/*,application/pdf,.doc,.docx,.txt"
          style={{ marginBottom: '12px', width: '100%' }}
        />
        {loading && (
          <div className="loading">
            Загрузка файла... {loading && <span style={{ fontSize: '12px', opacity: 0.7 }}>(проверьте консоль для деталей)</span>}
          </div>
        )}
      </div>

      {/* Show last report if available */}
      <div className="card">
        <h2 style={{ marginBottom: '12px', fontSize: '20px', fontWeight: '600' }}>Ваш отчет</h2>
        <div className="report-viewer-container" style={{ minHeight: '100px' }}>
          {fileUploaded ? (
            <div style={{ padding: '20px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <div className="loading-spinner" style={{ 
                width: '40px', 
                height: '40px', 
                border: '4px solid rgba(220, 38, 38, 0.2)', 
                borderTop: '4px solid #dc2626', 
                borderRadius: '50%', 
                animation: 'spin 1s linear infinite' 
              }}></div>
              <div style={{ color: 'var(--text-secondary, #6b6b6b)' }}>Обработка...</div>
            </div>
          ) : lastReport && lastReport.trim() ? (
            <div style={{ 
              whiteSpace: 'pre-wrap', 
              padding: '12px',
              fontSize: '14px',
              lineHeight: '1.6',
              color: 'var(--text-primary, #2d2d2d)'
            }}>
              {lastReport}
            </div>
          ) : (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-secondary, #6b6b6b)' }}>
              Анализы появятся здесь после обработки
            </div>
          )}
        </div>
      </div>
      
      {/* Debug info - можно удалить позже */}
      {process.env.NODE_ENV === 'development' && lastReport && (
        <div className="card" style={{ fontSize: '12px', opacity: 0.7, marginTop: '12px' }}>
          <strong>Debug:</strong> Last report length: {lastReport.length} chars
          <br />
          First 200 chars: {lastReport.substring(0, 200)}...
        </div>
      )}

      <div className="card">
        <h2 style={{ marginBottom: '12px', fontSize: '20px', fontWeight: '600' }}>Все анализы</h2>
        <div style={{ minHeight: '100px' }}>
          {allAnalyses.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-secondary, #6b6b6b)' }}>
              История анализов пуста
            </div>
          ) : (
            <button 
              className="button analyses-all-btn" 
              onClick={handleOpenAllAnalyses}
              style={{ width: '100%' }}
            >
              Открыть историю
            </button>
          )}
        </div>
      </div>

      <button
        className="analyses-back-btn"
        onClick={() => navigate('/')}
        aria-label="Назад"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke="#dc2626" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Модальное окно всех анализов */}
      {showAllAnalyses && (
        <div className="analyses-modal-overlay" onClick={() => setShowAllAnalyses(false)}>
          <div className="analyses-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="analyses-modal-header">
              <h2 className="analyses-modal-title">Все анализы</h2>
              <button 
                className="analyses-modal-close"
                onClick={() => setShowAllAnalyses(false)}
                aria-label="Закрыть"
              >
                ✕
              </button>
            </div>
            
            <div className="analyses-modal-body">
              {loadingHistory ? (
                <div className="analyses-loading">Загрузка...</div>
              ) : allAnalyses.length === 0 ? (
                <div className="analyses-empty">
                  <p>История анализов пуста</p>
                </div>
              ) : (
                <div className="analyses-list">
                  {allAnalyses.map((analysis, index) => {
                    const isExpanded = expandedAnalysisIndex === index;
                    return (
                      <div key={index} className="analysis-card">
                        <div 
                          className="analysis-card-header"
                          onClick={() => setExpandedAnalysisIndex(isExpanded ? null : index)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                            <span className="analysis-file-name">
                              {analysis.fileName || analysis.file_name || `Анализ #${index + 1}`}
                            </span>
                            <span className="analysis-date" style={{ marginTop: '4px' }}>
                              {formatDate(analysis.createdAt || analysis.created_at)}
                            </span>
                          </div>
                          <svg 
                            width="28" 
                            height="28" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            xmlns="http://www.w3.org/2000/svg"
                            style={{ 
                              color: '#dc2626',
                              transition: 'transform 0.3s ease',
                              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                              marginLeft: '12px',
                              flexShrink: 0
                            }}
                          >
                            <path 
                              d="M6 9L12 15L18 9" 
                              stroke="#dc2626" 
                              strokeWidth="2.5" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                            />
                          </svg>
                        </div>
                        {isExpanded && (
                          <div className="analysis-card-content">
                            <div className="analysis-text" style={{ whiteSpace: 'pre-wrap' }}>
                              {analysis.text || analysis.report || 'Содержимое анализа недоступно'}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalysesPage;

