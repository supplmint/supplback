import { Link } from 'react-router-dom';
import { useState } from 'react';
import './HomePage.css';

function HomePage() {
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});
  const [showFAQ, setShowFAQ] = useState(false);

  const handleImageError = (imageName: string) => {
    setImageErrors(prev => ({ ...prev, [imageName]: true }));
  };

  const handleSupportClick = () => {
    window.open('https://t.me/digitalbysak', '_blank');
  };

  return (
    <div className="page">
      <h1 className="page-title">suppl.</h1>

      <nav className="nav-menu-grid">
        <Link to="/profile" className="nav-item-square nav-item-large nav-item-profile">
          <div className="nav-item-image-wrapper">
            {imageErrors.profile ? (
              <span className="nav-item-fallback">👤</span>
            ) : (
              <img 
                src={`/profile.png?v=${Date.now()}`}
                alt="Профиль" 
                className="nav-item-image" 
                onError={() => handleImageError('profile')}
              />
            )}
          </div>
          <span className="nav-item-text">Профиль</span>
        </Link>
        <Link to="/analyses" className="nav-item-square">
          <div className="nav-item-image-wrapper">
            {imageErrors.zagruz ? (
              <span className="nav-item-fallback">📤</span>
            ) : (
              <img 
                src={`/zagruz.png?v=${Date.now()}`}
                alt="Загрузка анализов" 
                className="nav-item-image" 
                onError={() => handleImageError('zagruz')}
              />
            )}
          </div>
          <span className="nav-item-text">Загрузка анализов</span>
        </Link>
        <Link to="/checkups" className="nav-item-square">
          <div className="nav-item-image-wrapper">
            {imageErrors.checkup ? (
              <span className="nav-item-fallback">🏥</span>
            ) : (
              <img 
                src={`/checkup.png?v=${Date.now()}`}
                alt="Варианты чекапов" 
                className="nav-item-image" 
                onError={() => handleImageError('checkup')}
              />
            )}
          </div>
          <span className="nav-item-text">Варианты чекапов</span>
        </Link>
        <Link to="/recommendations" className="nav-item-square nav-item-large">
          <div className="nav-item-image-wrapper">
            {imageErrors.rekom ? (
              <span className="nav-item-fallback">💊</span>
            ) : (
              <img 
                src={`/rekom.png?v=${Date.now()}`}
                alt="Рекомендации по добавкам" 
                className="nav-item-image" 
                onError={() => handleImageError('rekom')}
              />
            )}
          </div>
          <span className="nav-item-text">Рекомендации по добавкам</span>
        </Link>
      </nav>

      <div className="home-footer-buttons">
        <button 
          className="home-footer-btn"
          onClick={() => setShowFAQ(true)}
        >
          FAQ
        </button>
        <button 
          className="home-footer-btn"
          onClick={handleSupportClick}
        >
          Служба заботы
        </button>
      </div>

      {/* FAQ Modal */}
      {showFAQ && (
        <div className="faq-modal-overlay" onClick={() => setShowFAQ(false)}>
          <div className="faq-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="faq-modal-header">
              <h2 className="faq-modal-title">FAQ</h2>
              <button 
                className="faq-modal-close"
                onClick={() => setShowFAQ(false)}
                aria-label="Закрыть"
              >
                ✕
              </button>
            </div>
            <div className="faq-modal-body">
              <div className="faq-content">
                <h3>О приложении suppl.</h3>
                <p>
                  suppl. — это приложение для управления вашим здоровьем и анализами. 
                  Здесь вы можете:
                </p>
                <ul>
                  <li><strong>Профиль</strong> — сохранить и редактировать свои данные: имя, возраст, пол, рост и вес</li>
                  <li><strong>Загрузка анализов</strong> — загружать фотографии или файлы анализов для автоматической обработки</li>
                  <li><strong>Варианты чекапов</strong> — просматривать доступные варианты медицинских обследований</li>
                  <li><strong>Рекомендации по добавкам</strong> — получать персональные рекомендации по витаминам и добавкам</li>
                </ul>
                <p>
                  Все ваши данные хранятся безопасно и используются только для предоставления 
                  персональных рекомендаций.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;

