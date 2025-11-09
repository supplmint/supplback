import crypto from "crypto";

/**
 * Verify Telegram WebApp initData signature using HMAC-SHA256
 * 
 * Algorithm:
 * 1. secret = HMAC_SHA256(key="WebAppData", data=BOT_TOKEN)
 * 2. data_check_string = sorted k=v pairs through \n (excluding hash)
 * 3. Compare hex with hash
 */
export function verifyInitData(initData: string, botToken: string): boolean {
  try {
    // Parse initData string into key-value pairs
    const params = new URLSearchParams(initData);
    const hash = params.get("hash");
    
    if (!hash) {
      return false;
    }

    // Remove hash from params for verification
    params.delete("hash");

    // Create secret: HMAC_SHA256(key="WebAppData", data=BOT_TOKEN)
    const secretKey = crypto
      .createHmac("sha256", "WebAppData")
      .update(botToken)
      .digest();

    // Build data_check_string: sort k=v pairs and join with \n
    const entries = Array.from(params.entries()) as [string, string][];
    const dataCheckString = entries
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}=${value}`)
      .join("\n");

    // Calculate HMAC of data_check_string with secret
    const calculatedHash = crypto
      .createHmac("sha256", secretKey)
      .update(dataCheckString)
      .digest("hex");

    // Compare hashes (case-insensitive)
    return calculatedHash.toLowerCase() === hash.toLowerCase();
  } catch (error) {
    console.error("Error verifying initData:", error);
    return false;
  }
}

