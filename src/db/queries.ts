import { pool } from "./config";
import { HealthAppRecord } from "../types";

/**
 * Get or create user record by tgid
 */
export async function getOrCreateUser(tgid: string): Promise<HealthAppRecord> {
  const client = await pool.connect();
  
  try {
    // Try to get existing user
    const selectResult = await client.query(
      "SELECT * FROM health_app WHERE tgid = $1",
      [tgid]
    );

    if (selectResult.rows.length > 0) {
      return selectResult.rows[0];
    }

    // Create new user
    const insertResult = await client.query(
      `INSERT INTO health_app (tgid, profile, analyses, recommendations)
       VALUES ($1, '{}'::jsonb, '{}'::jsonb, '{}'::jsonb)
       RETURNING *`,
      [tgid]
    );

    return insertResult.rows[0];
  } finally {
    client.release();
  }
}

/**
 * Update user profile (merge with existing)
 * Creates user if doesn't exist
 */
export async function updateProfile(tgid: string, profile: Record<string, any>): Promise<HealthAppRecord> {
  // Ensure user exists first
  await getOrCreateUser(tgid);
  
  const client = await pool.connect();
  
  try {
    const result = await client.query(
      `UPDATE health_app
       SET profile = profile || $1::jsonb,
           updated_at = now()
       WHERE tgid = $2
       RETURNING *`,
      [JSON.stringify(profile), tgid]
    );

    return result.rows[0];
  } finally {
    client.release();
  }
}

/**
 * Update analyses
 * Creates user if doesn't exist
 */
export async function updateAnalyses(tgid: string, analyses: Record<string, any>): Promise<HealthAppRecord> {
  // Ensure user exists first
  await getOrCreateUser(tgid);
  
  const client = await pool.connect();
  
  try {
    const result = await client.query(
      `UPDATE health_app
       SET analyses = $1::jsonb,
           updated_at = now()
       WHERE tgid = $2
       RETURNING *`,
      [JSON.stringify(analyses), tgid]
    );

    return result.rows[0];
  } finally {
    client.release();
  }
}

/**
 * Update recommendations
 * Creates user if doesn't exist
 */
export async function updateRecommendations(tgid: string, recommendations: Record<string, any>): Promise<HealthAppRecord> {
  // Ensure user exists first
  await getOrCreateUser(tgid);
  
  const client = await pool.connect();
  
  try {
    const result = await client.query(
      `UPDATE health_app
       SET recommendations = $1::jsonb,
           updated_at = now()
       WHERE tgid = $2
       RETURNING *`,
      [JSON.stringify(recommendations), tgid]
    );

    return result.rows[0];
  } finally {
    client.release();
  }
}

/**
 * Update analyses with upload notification
 * Creates user if doesn't exist
 */
export async function notifyUpload(
  tgid: string,
  fileName: string,
  mime: string,
  size: number
): Promise<HealthAppRecord> {
  // Ensure user exists first
  const user = await getOrCreateUser(tgid);
  const currentAnalyses = user.analyses || {};
  
  const client = await pool.connect();
  
  try {
    // Update last_upload and history
    const updatedAnalyses = {
      ...currentAnalyses,
      last_upload: {
        fileName,
        mime,
        size,
        uploadedAt: new Date().toISOString(),
      },
      upload_history: [
        ...(Array.isArray(currentAnalyses.upload_history) ? currentAnalyses.upload_history : []),
        {
          fileName,
          mime,
          size,
          uploadedAt: new Date().toISOString(),
        },
      ],
    };

    const result = await client.query(
      `UPDATE health_app
       SET analyses = $1::jsonb,
           updated_at = now()
       WHERE tgid = $2
       RETURNING *`,
      [JSON.stringify(updatedAnalyses), tgid]
    );

    return result.rows[0];
  } finally {
    client.release();
  }
}

