import { User } from '../types';

/**
 * Проверяет, заполнен ли профиль пользователя обязательными полями
 * @param user Профиль пользователя
 * @returns true, если профиль заполнен (есть имя, пол, возраст, рост и вес)
 */
export function isProfileComplete(user: User | null): boolean {
  if (!user || !user.profile) {
    return false;
  }

  const profile = user.profile;
  
  // Проверяем наличие обязательных полей
  const hasName = profile.name && typeof profile.name === 'string' && profile.name.trim().length >= 2;
  const hasGender = profile.gender && (profile.gender === 'male' || profile.gender === 'female');
  const hasAge = profile.age && typeof profile.age === 'number' && profile.age > 0 && profile.age <= 150;
  const hasHeight = profile.height && typeof profile.height === 'number' && profile.height > 0 && profile.height <= 250;
  const hasWeight = profile.weight && typeof profile.weight === 'number' && profile.weight > 0 && profile.weight <= 500;

  return hasName && hasGender && hasAge && hasHeight && hasWeight;
}

/**
 * Определяет первый незаполненный шаг онбординга
 * @param user Профиль пользователя
 * @returns 'name' | 'gender' | 'age' | 'height' | 'weight' | null (если все заполнено)
 */
export function getFirstIncompleteStep(user: User | null): 'name' | 'gender' | 'age' | 'height' | 'weight' | null {
  if (!user || !user.profile) {
    return 'name';
  }

  const profile = user.profile;
  
  // Проверяем по порядку: имя, пол, возраст, рост, вес
  const hasName = profile.name && typeof profile.name === 'string' && profile.name.trim().length >= 2;
  if (!hasName) {
    return 'name';
  }
  
  const hasGender = profile.gender && (profile.gender === 'male' || profile.gender === 'female');
  if (!hasGender) {
    return 'gender';
  }
  
  const hasAge = profile.age && typeof profile.age === 'number' && profile.age > 0 && profile.age <= 150;
  if (!hasAge) {
    return 'age';
  }
  
  const hasHeight = profile.height && typeof profile.height === 'number' && profile.height > 0 && profile.height <= 250;
  if (!hasHeight) {
    return 'height';
  }
  
  const hasWeight = profile.weight && typeof profile.weight === 'number' && profile.weight > 0 && profile.weight <= 500;
  if (!hasWeight) {
    return 'weight';
  }
  
  return null; // Все заполнено
}

