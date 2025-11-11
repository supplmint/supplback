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
  // Wait for Telegram WebApp SDK to load
  if (typeof window === 'undefined') {
    return;
  }

  // Check if Telegram WebApp is available (might not be in browser version)
  if (!window.Telegram?.WebApp) {
    console.warn('Telegram WebApp is not available - running in browser mode');
    return;
  }

  try {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();
  } catch (error) {
    console.warn('Error initializing Telegram WebApp:', error);
  }
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

