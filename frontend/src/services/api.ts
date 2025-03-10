import axios from "axios";
import { jwtDecode } from "jwt-decode";  // ✅ Correct Import

const api = axios.create({
  baseURL: "http://localhost:5000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getUserIdFromToken = () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const decoded: any = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    if (decoded.exp < currentTime) {
      localStorage.removeItem("token");
      return null;
    }
    return decoded.sub || decoded.user_id || null;
  } catch (error) {
    console.error("Invalid token", error);
    localStorage.removeItem("token");
    return null;
  }
};

export default api;
