import axios from "axios";
import { API_BASE_URL, buildApiUrl, normalizeBackendUrlsInData } from "./url";

const apiBaseURL = API_BASE_URL;

/**
 * Central API Client Instance
 */
const apiClient = axios.create({
    baseURL: apiBaseURL,
    headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
    },
    timeout: 30000, // 30s timeout
});

/**
 * Request Interceptor
 * Injects the JWT token if available
 */
apiClient.interceptors.request.use(
    (config) => {
        // Let the browser set multipart boundaries for FormData requests.
        if (typeof FormData !== "undefined" && config.data instanceof FormData) {
            if (config.headers?.delete) {
                config.headers.delete("Content-Type");
            } else if (config.headers) {
                delete config.headers["Content-Type"];
                delete config.headers["content-type"];
            }
        }

        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    },
);

/**
 * Token Refresh Logic State
 */
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

/**
 * Response Interceptor
 * Handles common errors like 401 Unauthorized and implements Silent Refresh
 */
apiClient.interceptors.response.use(
    (response) => {
        if (response?.data) {
            response.data = normalizeBackendUrlsInData(response.data);
        }
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // Skip refresh logic for login endpoint or if explicitly disabled
        if (
            originalRequest.url.includes("/login") ||
            originalRequest.url.includes("/auth/login")
        ) {
            return Promise.reject(error);
        }

        // If error is 401 and not already retrying
        if (error.response?.status === 401 && !originalRequest._retry) {
            // If we are already refreshing, queue this request
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                })
                    .then((token) => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return apiClient(originalRequest);
                    })
                    .catch((err) => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // Call refresh endpoint directly using axios to avoid circular dependency
                const refreshUrl = buildApiUrl("auth/refresh");
                const response = await axios.post(
                    refreshUrl,
                    { refresh_token: localStorage.getItem("refresh_token") }
                );

                const { user, token: tokenData } = response.data.data;
                const { access_token, refresh_token } = tokenData || {};

                // Update local storage
                localStorage.setItem("token", access_token);
                if (refresh_token) localStorage.setItem("refresh_token", refresh_token);
                if (user) localStorage.setItem("user", JSON.stringify(user));

                // Process the queue with the new token
                processQueue(null, access_token);

                // Retry the original request
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return apiClient(originalRequest);
            } catch (refreshError) {
                // If refresh fails, process queue with error and logout
                processQueue(refreshError, null);

                localStorage.removeItem("token");
                localStorage.removeItem("user");

                if (!window.location.pathname.includes("/login")) {
                    window.location.href = "/login";
                }
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        // Handle Maintenance Mode (503)
        if (error.response?.status === 503) {
            // If not already on login page (to avoid infinite loops if login itself 503s which it does)
            // But if login 503s, we want to show the error in the form, NOT redirect.

            // If it's a navigation/background request:
            if (!originalRequest.url.includes("/login")) {
                localStorage.removeItem("token");
                localStorage.removeItem("user");
                window.location.href = "/login?maintenance=true";
                return Promise.reject(error);
            }

            // If it WAS a login request that failed with 503, just reject so the form shows the error
            return Promise.reject(error);
        }

        return Promise.reject(error);
    },
);

export default apiClient;
