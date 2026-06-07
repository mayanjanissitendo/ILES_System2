import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/",
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("iles_token");
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("iles_token");
      localStorage.removeItem("iles_user");
    }
    return Promise.reject(error);
  }
);

export default api;
