import { storage } from '../firebase/config';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';

/**
 * Upload file to Firebase Storage
 */
export async function uploadFile(
  file: File,
  path: string
): Promise<{ url: string; fileName: string; size: number }> {
  try {
    console.log('Firebase: Uploading file to path:', path);
    const storageRef = ref(storage, path);
    console.log('Firebase: Starting upload bytes...');
    const snapshot = await uploadBytes(storageRef, file);
    console.log('Firebase: Upload complete, getting download URL...');
    const downloadURL = await getDownloadURL(snapshot.ref);
    console.log('Firebase: Download URL received:', downloadURL);
    
    return {
      url: downloadURL,
      fileName: file.name,
      size: file.size,
    };
  } catch (error) {
    console.error('Firebase upload error:', error);
    throw new Error(`Ошибка загрузки в Firebase: ${error instanceof Error ? error.message : String(error)}`);
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

