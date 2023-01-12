import { initializeApp } from "firebase/app";
import { getStorage } from "firebase/storage";

// inserer ici vos propres credentials
const firebaseConfig = {
  apiKey: process.env.REACT_APP_APIKEY,
  authDomain: process.env.REACT_APP_AUTHDOMAIN,
  projectId: process.env.PROJECTID,
  storageBucket: process.env.BUCKET,
  messagingSenderId: process.env.MESSAGING,
  appId: process.env.REACT_APP_APIID
};

// Initialisation de l'app
const app = initializeApp(firebaseConfig);
export const storage = getStorage(app)