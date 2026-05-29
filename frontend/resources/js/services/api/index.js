import auth from "./endpoints/auth";
import system from "./endpoints/system";
import vault from "./endpoints/vault";
import dynamicRoutes from "./endpoints/dynamic-routes";
import users from "./endpoints/users";
import icons from "./endpoints/icons";
import cusAlliance from "./endpoints/cus-alliance-complaints";
import portfolios from "./endpoints/portfolios";
import files from "./endpoints/files";
import folders from "./endpoints/folders";
import { finanzasApi as finanzas } from "./endpoints/finanzas";

/**
 * API Service Registry
 * Centralizes all API endpoints for easy access throughout the app.
 */
export const api = {
    auth,
    system,
    vault,
    dynamicRoutes,
    users,
    icons,
    cusAlliance,
    portfolios,
    files,
    folders,
    finanzas,
};

export default api;
