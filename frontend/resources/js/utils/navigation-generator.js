/**
 * Generates the navigation menu structure from Vue Router routes.
 *
 * @param {Array} routes - The route definitions.
 * @param {Number} userHierarchy - The current user's hierarchy level.
 * @param {String} parentPath - The parent path for recursive calls.
 * @param {Object} options - Options for generation.
 * @param {Boolean} options.ignoreSidebarVisibility - If true, includes items even if meta.sidebar is false.
 * @returns {Array} - The navigation menu structure.
 */
export const generateNavigation = (
    routes,
    userHierarchy = 99,
    parentPath = "",
    options = {},
) => {
    return routes
        .map((route) => {
            // 1. Check if module is enabled for sidebar
            // If ignoreSidebarVisibility is true, we skip this check
            if (
                !options.ignoreSidebarVisibility &&
                route.meta?.sidebar === false
            ) {
                return null;
            }

            // 2. Check for hierarchy restrictions
            // Lower hierarchy number usually means higher privilege (1 > 2 > 3)
            // But logic in app seems to be userHierarchy <= minHierarchy (User 1 <= Required 3 -> OK)
            const minHierarchy = route.meta?.minHierarchy ?? 99;
            if (userHierarchy > minHierarchy) {
                return null;
            }

            // 3. Resolve Path
            let fullPath = route.path;
            if (parentPath) {
                const cleanParent = parentPath.endsWith("/")
                    ? parentPath.slice(0, -1)
                    : parentPath;
                const cleanRoute = route.path.startsWith("/")
                    ? route.path.slice(1)
                    : route.path;
                fullPath = `${cleanParent}/${cleanRoute}`;
            }

            // Handle root children (like DashboardHome with path "")
            if (fullPath.endsWith("/")) {
                fullPath = fullPath.slice(0, -1);
            }

            // 4. Process Children
            let children = null;
            if (route.children) {
                children = generateNavigation(
                    route.children,
                    userHierarchy,
                    fullPath,
                    options,
                );

                // If showDropdown is false (e.g. Tools module), we might want to hide children from the SIDEBAR
                // but if we are ignoring sidebar visibility (e.g. for tabs), we might want to keep them?

                // Logic update:
                // If ignoreSidebarVisibility is true, we likely want ALL children that pass hierarchy,
                // regardless of showDropdown.
                if (!options.ignoreSidebarVisibility) {
                    if (route.meta?.showDropdown === false) {
                        children = null;
                    } else if (children && children.length === 0) {
                        children = null;
                    }
                }
            }

            // 5. Construct Menu Item
            return {
                name: route.meta?.title || route.name,
                path: fullPath,
                icon: route.meta?.icon,
                dbIcon: route.meta?.dbIcon, // Add this
                exact: route.meta?.exact ?? false,
                description: route.meta?.description,
                keywords: route.meta?.keywords, // For search
                order: route.meta?.order ?? 999, // For sorting
                children: children,
            };
        })
        .filter((item) => item !== null)
        .sort((a, b) => {
            // Sort by order first
            if (a.order !== b.order) {
                return a.order - b.order;
            }
            // Then by name (which is title)
            return (a.name || "").localeCompare(b.name || "");
        });
};

/**
 * Flattens the navigation tree into a single list of modules.
 * Useful for the Navbar search.
 */
export const flattenNavigation = (items, parentName = '') => {
    let flat = [];

    items.forEach((item) => {
        const itemWithParent = { ...item, parentName };
        flat.push(itemWithParent);
        if (item.children) {
            flat = flat.concat(flattenNavigation(item.children, item.name));
        }
    });

    return flat;
};
