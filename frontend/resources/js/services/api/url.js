const trimTrailingSlash = (value = "") => String(value || "").replace(/\/+$/, "");

const normalizeApiBase = (value) => {
    const fallback = "/api";
    const candidate = String(value || fallback).trim();
    if (!candidate) return fallback;
    return trimTrailingSlash(candidate);
};

export const API_BASE_URL = normalizeApiBase(import.meta.env.VITE_API_BASE_URL);

export const BACKEND_BASE_URL = (() => {
    const apiBase = API_BASE_URL;
    if (apiBase === "/api") {
        return "";
    }

    return trimTrailingSlash(apiBase.replace(/\/api$/i, ""));
})();

export const FRONTEND_BASE_URL = (() => {
    const explicit = trimTrailingSlash(import.meta.env.VITE_FRONTEND_BASE_URL || "");
    if (explicit) {
        return explicit;
    }

    if (typeof window !== "undefined" && window.location?.origin) {
        return trimTrailingSlash(window.location.origin);
    }

    return "";
})();

export const buildApiUrl = (path = "") => {
    const cleanPath = String(path || "").replace(/^\/+/, "");
    if (!cleanPath) {
        return API_BASE_URL;
    }

    return `${API_BASE_URL}/${cleanPath}`;
};

const isAbsoluteUrl = (value) => /^(?:[a-z]+:)?\/\//i.test(String(value || ""));

export const toAbsoluteBackendUrl = (value) => {
    const raw = String(value || "").trim();
    if (!raw) return raw;

    if (raw.startsWith("data:")) return raw;
    if (isAbsoluteUrl(raw)) return raw;

    const normalizedPath = raw.startsWith("/") ? raw : `/${raw}`;

    if (!BACKEND_BASE_URL) {
        return normalizedPath;
    }

    return `${BACKEND_BASE_URL}${normalizedPath}`;
};

const extractShareToken = (value = "") => {
    const raw = String(value || "").trim();
    if (!raw) return "";

    const tokenMatch = raw.match(/\/s\/([^/?#]+)/i);
    if (tokenMatch?.[1]) {
        return tokenMatch[1];
    }

    return raw;
};

export const buildPublicShareUrl = (tokenOrUrl = "") => {
    const token = extractShareToken(tokenOrUrl);
    if (!token) return "";

    if (!FRONTEND_BASE_URL) {
        return `/s/${token}`;
    }

    return `${FRONTEND_BASE_URL}/s/${token}`;
};

const shouldNormalizeKey = (key = "") => {
    const normalized = String(key || "").toLowerCase();
    return /(url|uri|path|avatar|image|logo|icon|file)/.test(normalized);
};

const shouldNormalizeValue = (value = "") => {
    const candidate = String(value || "").trim();
    if (!candidate) return false;
    if (candidate.startsWith("data:")) return false;
    if (isAbsoluteUrl(candidate)) return false;

    return (
        candidate.startsWith("/") ||
        candidate.startsWith("storage/") ||
        candidate.startsWith("uploads/")
    );
};

const isPlainObject = (value) => {
    if (!value || typeof value !== "object") return false;
    return Object.prototype.toString.call(value) === "[object Object]";
};

export const normalizeBackendUrlsInData = (input, parentKey = "") => {
    if (Array.isArray(input)) {
        return input.map((item) => normalizeBackendUrlsInData(item, parentKey));
    }

    if (isPlainObject(input)) {
        const output = {};
        Object.entries(input).forEach(([key, value]) => {
            output[key] = normalizeBackendUrlsInData(value, key);
        });
        return output;
    }

    if (typeof input === "string" && shouldNormalizeKey(parentKey) && shouldNormalizeValue(input)) {
        return toAbsoluteBackendUrl(input);
    }

    return input;
};
