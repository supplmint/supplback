import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyD61o4cjhjVbSUercj2ifXAoOujlOpLuHQ",
  authDomain: "suppl-f09d8.firebaseapp.com",
  projectId: "suppl-f09d8",
  storageBucket: "suppl-f09d8.firebasestorage.app",
  messagingSenderId: "957710320009",
  appId: "1:957710320009:web:66d85c153e481d4c2d2158"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const storage = getStorage(app);

export default app;

