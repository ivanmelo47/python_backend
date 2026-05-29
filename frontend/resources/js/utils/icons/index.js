import { loginIcons } from './login-icons';
import { alertIcons } from './alerts-icons';
import { dashboardIcons } from './dashboard-icons';
import { socialIcons } from './social-icons';

// Combine all icon sets
const allIcons = {
    ...loginIcons,
    ...alertIcons,
    ...dashboardIcons,
    ...socialIcons
};

// Helper to get icon by name with fallback
export const getIcon = (name) => {
    return allIcons[name] || allIcons.info || loginIcons.info;
};

export default allIcons;

