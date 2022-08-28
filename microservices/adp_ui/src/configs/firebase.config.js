// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth,GoogleAuthProvider, signInWithPopup } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  // apiKey: "AIzaSyAvHeX4BrtlPgdyaofnTHWAahNxie_qfMI",
  // authDomain: "doc-ai-claim-sample.firebaseapp.com",
  // projectId: "doc-ai-claim-sample",
  // storageBucket: "doc-ai-claim-sample.appspot.com",
  // messagingSenderId: "365702445958",
  // appId: "1:365702445958:web:96b48e56f51aeb531cca07",
  // measurementId: "G-1GM3BPBS15"
  apiKey: "AIzaSyD20ZyIxnCTu5E2BxpfkoBExl76TsbwdCc",
  authDomain: "claims-processing-dev.firebaseapp.com",
  projectId: "claims-processing-dev",
  storageBucket: "claims-processing-dev.appspot.com",
  messagingSenderId: "593784320282",
  appId: "1:593784320282:web:d155e140ec9250feb4fca3",
  measurementId: "G-5B385RL5MS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);

const provider = new GoogleAuthProvider();

export const signInWithGoogle = () => {
  signInWithPopup(auth, provider)
    .then((result) => {
      localStorage.setItem("user", result.user.email);
      localStorage.setItem('login',true);
      window.location="/";
    })
    .catch((error) => {
      console.log(error);
    });
};

export const baseURL ='https://adp-dev.cloudpssolutions.com'
