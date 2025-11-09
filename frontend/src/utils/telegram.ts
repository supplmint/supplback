/**
 * Get Telegram WebApp initData for authentication
 */
export function getTelegramInitData(): string | null {
  if (typeof window === 'undefined' || !window.Telegram?.WebApp) {
    return null;
  }
  return window.Telegram.WebApp.initData;
}

/**
 * Initialize Telegram WebApp
 */
export function initTelegramWebApp(): void {
  if (typeof window === 'undefined' || !window.Telegram?.WebApp) {
    console.warn('Telegram WebApp is not available');
    return;
  }

  const tg = window.Telegram.WebApp;
  tg.ready();
  tg.expand();
}

/**
 * Get current Telegram user
 */
export function getTelegramUser() {
  if (typeof window === 'undefined' || !window.Telegram?.WebApp) {
    return null;
  }
  return window.Telegram.WebApp.initDataUnsafe.user;
}

