import { Request, Response, NextFunction } from "express";
import { verifyInitData } from "../telegram/verifyInitData";
import { parseInitData } from "../telegram/parseInitData";
import { AuthenticatedRequest } from "../types";

export function requireTgAuth(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const initData = req.headers["x-telegram-initdata"] as string;
  const botToken = process.env.BOT_TOKEN;

  if (!initData) {
    return res.status(401).json({ error: "Missing x-telegram-initdata header" });
  }

  if (!botToken) {
    console.error("BOT_TOKEN is not set in environment variables");
    return res.status(500).json({ error: "Server configuration error" });
  }

  // Verify signature
  if (!verifyInitData(initData, botToken)) {
    return res.status(401).json({ error: "Invalid Telegram initData signature" });
  }

  // Parse initData and extract user ID
  const parsed = parseInitData(initData);
  
  if (!parsed.parsedUser || !parsed.parsedUser.id) {
    return res.status(401).json({ error: "Invalid user data in initData" });
  }

  // Set tgid on request object
  req.tgid = String(parsed.parsedUser.id);
  
  next();
}

