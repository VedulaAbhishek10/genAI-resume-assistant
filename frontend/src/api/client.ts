import axios, { type AxiosError } from "axios";
import type { ApiError } from "@/types/api";

const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * The backend returns errors as `{"error": {"code", "message"}}` (docs/API.md).
 * Unwrap that envelope so callers can catch a plain `ApiError` instead of reaching
 * into the Axios response shape themselves.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error: ApiError }>) => {
    const apiError = error.response?.data?.error;
    if (apiError) {
      return Promise.reject(apiError satisfies ApiError);
    }
    return Promise.reject(error);
  },
);
