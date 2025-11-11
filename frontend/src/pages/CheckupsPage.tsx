import { useNavigate } from 'react-router-dom';

function CheckupsPage() {
  const navigate = useNavigate();

  return (
    <div className="page">
      <h1 className="page-title">Варианты чекапов</h1>

      <div className="card">
        <p>Страница в разработке</p>
        <p>Здесь будут отображаться различные варианты медицинских чекапов.</p>
      </div>

      <button
        className="button"
        onClick={() => navigate('/')}
        style={{ marginTop: '20px' }}
      >
        Назад
      </button>
    </div>
  );
}

export default CheckupsPage;

