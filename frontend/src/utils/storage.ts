import { storage } from '../firebase/config';
import { ref, uploadBytes, getDownloadURL, UploadResult } from 'firebase/storage';

/**
 * Upload file to Firebase Storage
 */
export async function uploadFile(
  file: File,
  path: string
): Promise<{ url: string; fileName: string; size: number }> {
  try {
    const storageRef = ref(storage, path);
    const snapshot = await uploadBytes(storageRef, file);
    const downloadURL = await getDownloadURL(snapshot.ref);
    
    return {
      url: downloadURL,
      fileName: file.name,
      size: file.size,
    };
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
}

/**
 * Upload analysis file
 */
export async function uploadAnalysisFile(
  file: File,
  tgid: string
): Promise<{ url: string; fileName: string; size: number }> {
  const timestamp = Date.now();
  const path = `analyses/${tgid}/${timestamp}_${file.name}`;
  return uploadFile(file, path);
}

