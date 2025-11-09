/**
 * Parse Telegram WebApp initData string into object
 * Extracts user field and parses it as JSON
 */
export interface ParsedInitData {
  query_id?: string;
  user?: string;
  receiver?: string;
  chat?: string;
  chat_type?: string;
  chat_instance?: string;
  start_param?: string;
  can_send_after?: string;
  auth_date?: string;
  hash?: string;
  [key: string]: string | undefined;
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

export interface ParsedInitDataWithUser extends ParsedInitData {
  parsedUser?: TelegramUser;
}

export function parseInitData(initData: string): ParsedInitDataWithUser {
  const params = new URLSearchParams(initData);
  const result: ParsedInitDataWithUser = {};

  // Parse all parameters
  for (const [key, value] of params.entries()) {
    result[key] = value;
  }

  // Parse user field as JSON if present
  if (result.user) {
    try {
      result.parsedUser = JSON.parse(result.user) as TelegramUser;
    } catch (error) {
      console.error("Error parsing user field:", error);
    }
  }

  return result;
}

