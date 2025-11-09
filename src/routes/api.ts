import { Router, Response } from "express";
import { z } from "zod";
import { requireTgAuth } from "../middleware/requireTgAuth";
import { AuthenticatedRequest } from "../types";
import {
  getOrCreateUser,
  updateProfile,
  updateAnalyses,
  updateRecommendations,
  notifyUpload,
} from "../db/queries";

const router = Router();

// All routes require Telegram authentication
router.use(requireTgAuth);

// Validation schemas
const updateProfileSchema = z.object({
  profile: z.record(z.any()),
});

const analysesSummarySchema = z.object({
  analyses: z.record(z.any()),
});

const recommendationsSchema = z.object({
  recommendations: z.record(z.any()),
});

const notifyUploadSchema = z.object({
  fileName: z.string(),
  mime: z.string(),
  size: z.number().int().positive(),
});

// GET /api/me - Get or create user
router.get("/me", async (req: AuthenticatedRequest, res: Response) => {
  try {
    if (!req.tgid) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    const user = await getOrCreateUser(req.tgid);
    
    res.json({
      tgid: user.tgid,
      profile: user.profile,
    });
  } catch (error) {
    console.error("Error in GET /api/me:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/me - Update profile
router.post("/me", async (req: AuthenticatedRequest, res: Response) => {
  try {
    if (!req.tgid) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    const validation = updateProfileSchema.safeParse(req.body);
    if (!validation.success) {
      return res.status(400).json({ error: "Invalid request body", details: validation.error });
    }

    const user = await updateProfile(req.tgid, validation.data.profile);
    
    res.json({
      tgid: user.tgid,
      profile: user.profile,
    });
  } catch (error) {
    console.error("Error in POST /api/me:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/analyses/summary - Update analyses
router.post("/analyses/summary", async (req: AuthenticatedRequest, res: Response) => {
  try {
    if (!req.tgid) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    const validation = analysesSummarySchema.safeParse(req.body);
    if (!validation.success) {
      return res.status(400).json({ error: "Invalid request body", details: validation.error });
    }

    const user = await updateAnalyses(req.tgid, validation.data.analyses);
    
    res.json({
      analyses: user.analyses,
    });
  } catch (error) {
    console.error("Error in POST /api/analyses/summary:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/reco/basic - Update recommendations
router.post("/reco/basic", async (req: AuthenticatedRequest, res: Response) => {
  try {
    if (!req.tgid) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    const validation = recommendationsSchema.safeParse(req.body);
    if (!validation.success) {
      return res.status(400).json({ error: "Invalid request body", details: validation.error });
    }

    const user = await updateRecommendations(req.tgid, validation.data.recommendations);
    
    res.json({
      recommendations: user.recommendations,
    });
  } catch (error) {
    console.error("Error in POST /api/reco/basic:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// POST /api/notify-upload - Notify about file upload
router.post("/notify-upload", async (req: AuthenticatedRequest, res: Response) => {
  try {
    if (!req.tgid) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    const validation = notifyUploadSchema.safeParse(req.body);
    if (!validation.success) {
      return res.status(400).json({ error: "Invalid request body", details: validation.error });
    }

    const { fileName, mime, size } = validation.data;
    const user = await notifyUpload(req.tgid, fileName, mime, size);
    
    res.json({
      fileName,
      mime,
      size,
      analyses: user.analyses,
    });
  } catch (error) {
    console.error("Error in POST /api/notify-upload:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;

