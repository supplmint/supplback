export interface User {
  tgid: string;
  profile: Record<string, any>;
  analyses?: Record<string, any>;
  recommendations?: Record<string, any>;
}

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
}

