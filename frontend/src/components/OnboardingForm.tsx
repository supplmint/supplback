import { useState } from 'react';
import { updateProfile } from '../api/user';
import './OnboardingForm.css';

interface OnboardingFormProps {
  onComplete: () => void;
  initialStep?: 'name' | 'gender' | 'age' | 'height' | 'weight';
  initialData?: {
    name?: string;
    gender?: string;
    age?: number;
    height?: number;
    weight?: number;
  };
}

type Step = 'name' | 'gender' | 'age' | 'height' | 'weight';

export default function OnboardingForm({ 
  onComplete, 
  initialStep = 'name',
  initialData = {}
}: OnboardingFormProps) {
  const [currentStep, setCurrentStep] = useState<Step>(initialStep);
  const [name, setName] = useState(initialData.name?.toString() || '');
  const [gender, setGender] = useState(initialData.gender?.toString() || '');
  const [age, setAge] = useState(initialData.age?.toString() || '');
  const [height, setHeight] = useState(initialData.height?.toString() || '');
  const [weight, setWeight] = useState(initialData.weight?.toString() || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const steps: Step[] = ['name', 'gender', 'age', 'height', 'weight'];
  const currentStepIndex = steps.indexOf(currentStep);

  const stepLabels = {
    name: 'Имя',
    gender: 'Пол',
    age: 'Возраст',
    height: 'Рост',
    weight: 'Вес'
  };

  const stepPlaceholders = {
    name: 'Введите ваше имя',
    gender: 'Выберите ваш пол',
    age: 'Введите ваш возраст',
    height: 'Введите ваш рост',
    weight: 'Введите ваш вес'
  };

  const validateStep = (step: Step, value: string): boolean => {
    switch (step) {
      case 'name':
        return value.trim().length >= 2;
      case 'gender':
        return value === 'male' || value === 'female';
      case 'age':
        const ageNum = parseInt(value, 10);
        return !isNaN(ageNum) && ageNum > 0 && ageNum <= 150;
      case 'height':
        const heightNum = parseFloat(value);
        return !isNaN(heightNum) && heightNum > 0 && heightNum <= 250;
      case 'weight':
        const weightNum = parseFloat(value);
        return !isNaN(weightNum) && weightNum > 0 && weightNum <= 500;
      default:
        return false;
    }
  };

  const handleNext = async () => {
    setError(null);
    
    let value = '';
    
    switch (currentStep) {
      case 'name':
        value = name;
        break;
      case 'gender':
        value = gender;
        break;
      case 'age':
        value = age;
        break;
      case 'height':
        value = height;
        break;
      case 'weight':
        value = weight;
        break;
    }

    if (!validateStep(currentStep, value)) {
      setError(`Пожалуйста, введите корректное значение для ${stepLabels[currentStep]}`);
      return;
    }

    setLoading(true);

    try {
      // Собираем все данные профиля для сохранения
      const profileData: Record<string, any> = {};
      
      // Сохраняем имя, если оно введено
      if (name.trim()) {
        profileData.name = name.trim();
      }
      
      // Сохраняем пол, если он выбран
      if (gender && validateStep('gender', gender)) {
        profileData.gender = gender;
      }
      
      // Сохраняем возраст, если он введен
      if (age && validateStep('age', age)) {
        profileData.age = parseInt(age, 10);
      }
      
      // Сохраняем рост, если он введен
      if (height && validateStep('height', height)) {
        profileData.height = parseFloat(height);
      }
      
      // Сохраняем вес, если он введен
      if (weight && validateStep('weight', weight)) {
        profileData.weight = parseFloat(weight);
      }

      // Логирование для отладки
      console.log('Saving profile data:', profileData);
      console.log('Profile keys:', Object.keys(profileData));
      console.log('Current step:', currentStep);
      console.log('All values - name:', name, 'gender:', gender, 'age:', age, 'height:', height, 'weight:', weight);

      // Сохраняем профиль на каждом шаге
      const result = await updateProfile(profileData);
      console.log('Profile update result:', result);

      // Переходим к следующему шагу или завершаем
      if (currentStepIndex < steps.length - 1) {
        setCurrentStep(steps[currentStepIndex + 1]);
      } else {
        // Все шаги завершены
        onComplete();
      }
    } catch (err: any) {
      console.error('Error saving profile:', err);
      setError('Не удалось сохранить данные. Попробуйте еще раз.');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentValue = (): string => {
    switch (currentStep) {
      case 'name':
        return name;
      case 'gender':
        return gender;
      case 'age':
        return age;
      case 'height':
        return height;
      case 'weight':
        return weight;
      default:
        return '';
    }
  };

  const setCurrentValue = (value: string) => {
    switch (currentStep) {
      case 'name':
        setName(value);
        break;
      case 'gender':
        setGender(value);
        break;
      case 'age':
        setAge(value);
        break;
      case 'height':
        setHeight(value);
        break;
      case 'weight':
        setWeight(value);
        break;
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) {
      handleNext();
    }
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        <div className="onboarding-header">
          <h2 className="onboarding-title">Добро пожаловать! 👋</h2>
          <p className="onboarding-subtitle">
            Давайте заполним ваш профиль
          </p>
        </div>

        <div className="onboarding-progress">
          {steps.map((step, index) => {
            const isCompleted = index < currentStepIndex;
            const isActive = index === currentStepIndex;
            const isClickable = isCompleted; // Завершенные шаги можно редактировать
            
            return (
              <div
                key={step}
                className={`onboarding-progress-step ${
                  isCompleted
                    ? 'completed'
                    : isActive
                    ? 'active'
                    : 'pending'
                } ${isClickable ? 'clickable' : ''}`}
                onClick={() => {
                  if (isClickable) {
                    setCurrentStep(step);
                    setError(null);
                  }
                }}
                title={isClickable ? `Нажмите, чтобы изменить ${stepLabels[step].toLowerCase()}` : ''}
              >
                <div className="onboarding-progress-circle">
                  {isCompleted ? '✓' : index + 1}
                </div>
                <span className="onboarding-progress-label">{stepLabels[step]}</span>
              </div>
            );
          })}
        </div>

        <div className="onboarding-form">
          <div className="onboarding-form-group">
            <label className="onboarding-label">
              {stepLabels[currentStep]}
            </label>
            {currentStep === 'gender' ? (
              <select
                className="onboarding-select"
                value={getCurrentValue()}
                onChange={(e) => setCurrentValue(e.target.value)}
                disabled={loading}
                autoFocus
              >
                <option value="">Выберите пол</option>
                <option value="male">Мужской</option>
                <option value="female">Женский</option>
              </select>
            ) : (
              <div className="onboarding-input-wrapper">
                <input
                  type={currentStep === 'name' ? 'text' : 'number'}
                  className="onboarding-input"
                  placeholder={stepPlaceholders[currentStep]}
                  value={getCurrentValue()}
                  onChange={(e) => setCurrentValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                  autoFocus
                />
                {currentStep === 'age' && (
                  <span className="onboarding-hint">лет</span>
                )}
                {currentStep === 'height' && (
                  <span className="onboarding-hint">см</span>
                )}
                {currentStep === 'weight' && (
                  <span className="onboarding-hint">кг</span>
                )}
              </div>
            )}
          </div>

          {error && <div className="onboarding-error">{error}</div>}

          <button
            className="onboarding-button"
            onClick={handleNext}
            disabled={loading || !validateStep(currentStep, getCurrentValue())}
          >
            {loading ? 'Сохранение...' : currentStepIndex < steps.length - 1 ? 'Далее' : 'Завершить'}
          </button>
        </div>
      </div>
    </div>
  );
}

