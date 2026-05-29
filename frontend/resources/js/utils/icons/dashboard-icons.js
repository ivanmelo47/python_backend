/**
 * Dashboard Icons - SVG Icons for Admin Interface
 * Usage: Automatically registered via index.js
 */

export const dashboardIcons = {
    // Activity / Pulse
    activity: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        `,
    },

    // Menu (Hamburger)
    menu: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
        `,
    },

    // Refresh / Reload
    refresh: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                <path d="M3 3v5h5"/>
                <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
                <path d="M16 16h5v5"/>
            </g>
        `,
    },

    // List View
    list: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
        `,
    },

    // Grid View
    grid: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M4 11h5V5H4v6zm0 7h5v-6H4v6zm6 0h5v-6h-5v6zm6 0h5v-6h-5v6zm-6-7h5V5h-5v6zm6-6v6h5V5h-5z"/>
        `,
    },

    // Dashboard/Home
    dashboard: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
        `,
    },

    // Search
    search: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        `,
    },

    // Close/X
    x: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        `,
    },

    check: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        `,
    },

    // Files/Folder
    folder: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
        `,
    },

    // Users / Group
    users: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        `,
    },

    // User (Single)
    user: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
        `,
    },

    // Settings/Cog
    settings: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.58 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
        `,
    },

    // Logout/Exit
    logout: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
        `,
    },

    // Clock / History
    clock: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
        `,
    },

    // File Text / Report
    "file-text": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        `,
    },

    // Eye / View / Audit
    eye: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
        `,
    },

    // Moon / Dark Mode
    moon: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/>
        `,
    },

    // Sun / Light Mode
    sun: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M6.76 4.84l-1.8-1.79-1.41 1.41 1.79 1.79 1.42-1.41zM4 10.5H1v2h3v-2zm9-9.95h-2V3.5h2V.55zm7.45 3.91l-1.41-1.41-1.79 1.79 1.41 1.41 1.79-1.79zm-3.21 13.7l1.79 1.8 1.41-1.41-1.8-1.79-1.4 1.4zM20 10.5v2h3v-2h-3zm-8-5c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm-1 16.95h2V19.5h-2v2.95zm-7.45-3.91l1.41 1.41 1.79-1.8-1.41-1.41-1.79 1.8z"/>
        `,
    },

    // Star / Favorite / Skills
    star: {
        viewBox: "0 0 24 24",
        path: `
             <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        `,
    },

    // Check / Tick
    check: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        `,
    },

    // Chevron Down
    chevronDown: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
        `,
    },
    "chevron-down": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
        `,
    },

    chevronUp: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z"/>
        `,
    },
    "chevron-up": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z"/>
        `,
    },

    // Chevron Left
    chevronLeft: {
        viewBox: "0 0 24 24",
        path: `
             <path fill="currentColor" d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        `,
    },
    "chevron-left": {
        viewBox: "0 0 24 24",
        path: `
             <path fill="currentColor" d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        `,
    },

    // Chevron Right
    chevronRight: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M10 6L8.5 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        `,
    },
    "chevron-right": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M10 6L8.5 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        `,
    },

    // --- Financial Icons ---
    
    // Wallet / Accounts
    wallet: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/>
                <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/>
                <path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/>
            </g>
        `,
    },

    // Credit Card
    creditCard: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
                <line x1="1" y1="10" x2="23" y2="10"/>
            </g>
        `,
    },

    // Landmark / Bank
    landmark: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="3" y1="21" x2="21" y2="21"/>
                <line x1="9" y1="21" x2="9" y2="11"/>
                <line x1="15" y1="21" x2="15" y2="11"/>
                <path d="m2 11 10-9 10 9"/>
                <path d="M7 11V7l5-3 5 3v4"/>
            </g>
        `,
    },

    // Money / Dollar
    dollarSign: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </g>
        `,
    },

    // Trending Up / Income
    trendingUp: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                <polyline points="17 6 23 6 23 12"/>
            </g>
        `,
    },

    // Trending Down / Expenses
    trendingDown: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
                <polyline points="17 18 23 18 23 12"/>
            </g>
        `,
    },

    // Calendar / Planned
    calendar: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
            </g>
        `,
    },

    // Palette/Colors
    palette: {
        viewBox: "0 0 16 16",
        path: `
            <path fill="currentColor" d="M8 5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm4 3a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM5.5 7a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm.5 6a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/>
            <path fill="currentColor" d="M16 8c0 4.418-3.582 8-8 8s-8-3.582-8-8 3.582-8 8-8 8 3.582 8 8zM8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1z"/>
        `,
    },

    // Image/Photo
    image: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2m0 16H5V5h14zm-5.04-6.71l-2.75 3.54l-1.96-2.36L6.5 17h11z"/>
        `,
    },
    photo: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2m0 16H5V5h14zm-5.04-6.71l-2.75 3.54l-1.96-2.36L6.5 17h11z"/>
        `,
    },

    // Tools
    tools: {
        viewBox: "0 0 16 16",
        path: `
            <path fill="currentColor" d="M1 0 0 1l2.2 3.081a1 1 0 0 0 .815.419h.07a1 1 0 0 1 .708.293l2.675 2.675-2.617 2.654A3.003 3.003 0 0 0 0 13a3 3 0 1 0 5.878-.851l2.654-2.617.968.968-.305.914a1 1 0 0 0 .242 1.023l3.27 3.27a.997.997 0 0 0 1.414 0l1.586-1.586a.997.997 0 0 0 0-1.414l-3.27-3.27a1 1 0 0 0-1.023-.242L10.5 9.5l-.96-.96 2.68-2.643A3.005 3.005 0 0 0 16 3q0-.405-.102-.777l-2.14 2.141L12 4l-.364-1.757L13.777.102a3 3 0 0 0-3.675 3.68L7.462 6.46 4.793 3.793a1 1 0 0 1-.293-.707v-.071a1 1 0 0 0-.419-.814zm9.646 10.646a.5.5 0 0 1 .708 0l2.914 2.915a.5.5 0 0 1-.707.707l-2.915-2.914a.5.5 0 0 1 0-.708M3 11l.471.242.529.026.287.445.445.287.026.529L5 13l-.242.471-.026.529-.445.287-.287.445-.529.026L3 15l-.471-.242L2 14.732l-.287-.445L1.268 14l-.026-.529L1 13l.242-.471.026-.529.445-.287.287-.445.529-.026z"/>
        `,
    },

    // Actions: Edit/Pencil
    pencil: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a.9959.9959 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
        `,
    },

    // Code / Technologies
    code: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m18 16 4-4-4-4M6 8l-4 4 4 4m8.5-12-5 16"/>
        `,
    },

    // Actions: Delete/Trash
    trash: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        `,
    },

    // Actions: Add/Plus
    plus: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        `,
    },

    // Actions: Minus
    minus: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 13H5v-2h14v2z"/>
        `,
    },

    // Exchange / Swap / Accesos (Two arrows)
    exchange: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M6.99 11L3 15l3.99 4v-3H14v-2H6.99v-3zM21 9l-3.99-4v3H10v2h7.01v3L21 9z"/>
        `,
    },

    // More Vertical (Kebab)
    moreVertical: {
        viewBox: "0 0 24 24",
        path: `
             <path fill="currentColor" d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
        `,
    },

    // Bot / Robot
    bot: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7V5.73A2 2 0 0 1 12 2zM4 12a1 1 0 0 0-1 1v3a1 1 0 0 0 1 1h1v-5H4zm16 0h-1v5h1a1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1zM6 9a5 5 0 0 0-5 5v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5a5 5 0 0 0-5-5H6zm3 6a1 1 0 1 1 0-2 1 1 0 0 1 0 2zm6 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
        `,
    },

    boot_2: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M21.928 11.607c-.202-.488-.635-.605-.928-.633V8c0-1.103-.897-2-2-2h-6V4.61c.305-.274.5-.668.5-1.11a1.5 1.5 0 0 0-3 0c0 .442.195.836.5 1.11V6H5c-1.103 0-2 .897-2 2v2.997l-.082.006A1 1 0 0 0 1.99 12v2a1 1 0 0 0 1 1H3v5c0 1.103.897 2 2 2h14c1.103 0 2-.897 2-2v-5a1 1 0 0 0 1-1v-1.938a1.006 1.006 0 0 0-.072-.455zM5 20V8h14l.001 3.996L19 12v2l.001.005.001 5.995H5z"/>
            <ellipse fill="currentColor" cx="8.5" cy="12" rx="1.5" ry="2"/>
            <ellipse fill="currentColor" cx="15.5" cy="12" rx="1.5" ry="2"/>
            <path fill="currentColor" d="M8 16h8v2H8z"/>
        `,
    },

    // Trash 2 (Simple)
    "trash-2": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M3 6h18v2H3V6zm2 3h14v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V9zm3 2v9h2V11H8zm4 0v9h2V11h-2zm4 0v9h2V11h-2zM9 4V2h6v2h5v2H4V4h5z"/>
        `,
    },

    // Send / Paper Plane
    send: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        `,
    },

    // Map & Location
    map: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/>
        `,
    },

    "map-pin": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        `,
    },

    // External Link
    "external-link": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
        `,
    },

    // External Link
    "link": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
        `,
    },

    // Maletin / Briefcase
    maletin: {
        viewBox: "0 0 512 512",
        path: `
            <path fill="currentColor" d="M0,149.3V448c0,23.5,19.1,42.7,42.7,42.7H64v-384H42.7C19.1,106.7,0,125.8,0,149.3z M469.3,106.7H448v384h21.3 c23.5,0,42.7-19.1,42.7-42.7V149.3C512,125.8,492.9,106.7,469.3,106.7z M106.7,490.7h298.7v-384H106.7V490.7z M213.3,64h85.3v21.3 h42.7V64c0-23.5-19.1-42.7-42.7-42.7h-85.3c-23.5,0-42.7,19.1-42.7,42.7v21.3h42.7V64z"/>
        `,
    },

    "folder-plus": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M20 6h-8l-2-2H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-1 8h-3v3h-2v-3h-3v-2h3V9h2v3h3v2z"/>
        `,
    },

    "folder-open": {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M20 18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-8l-2-2H4c-1.1 0-2 .9-2 2v12l2 2h16zM4 4h5.17l2 2H20v10H4V4z"/>
        `,
    },

    file: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M13 11h-2v3H8v2h3v3h2v-3h3v-2h-3v-3zm1-9H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        `,
    },

    shield: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
        `,
    },

    lock: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1s3.1 1.39 3.1 3.1v2z"/>
        `,
    },

    unlock: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M12 17c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm6-9h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6h1.9c0-1.71 1.39-3.1 3.1-3.1s3.1 1.39 3.1 3.1v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm0 12H6V10h12v10z"/>
        `,
    },

    userShare: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
        `,
    },

    "key-share": {
        viewBox: "0 0 16 16",
        path: `
        <path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd"
        d="M16 5.5C16 8.53757 13.5376 11 10.5 11H7V13H5V15L4 16H0V12L5.16351 6.83649C5.0567 6.40863 5 5.96094 5 5.5C5 2.46243 7.46243 0 10.5 0C13.5376 0 16 2.46243 16 5.5ZM13 4C13 4.55228 12.5523 5 12 5C11.4477 5 11 4.55228 11 4C11 3.44772 11.4477 3 12 3C12.5523 3 13 3.44772 13 4Z"/>
    `,
    },

    "system-mails": {
        viewBox: "414 257 32 32",
        path: `
        <path fill="currentColor" d="M430,275.916 L426.684,273.167 L415.115,285.01 L444.591,285.01 L433.235,273.147 L430,275.916 Z 
        M434.89,271.89 L445.892,283.329 C445.955,283.107 446,282.877 446,282.634 L446,262.862 L434.89,271.89 Z 
        M414,262.816 L414,282.634 C414,282.877 414.045,283.107 414.108,283.329 L425.147,271.927 L414,262.816 Z 
        M445,261 L415,261 L430,273.019 L445,261 Z"/>
    `,
    },

    "correos-entrada": {
        viewBox: "0 0 512 512",
        path: `
        <path fill="currentColor" fill-rule="evenodd"
        d="M480,224a31.991,31.991,0,0,0-32,32V448H64V256a32,32,0,0,0-64,0V480a31.991,31.991,0,0,0,32,32H480a31.991,31.991,0,0,0,32-32V256A31.991,31.991,0,0,0,480,224Z"/>
        <path fill="currentColor" fill-rule="evenodd"
        d="M288,224V28.091C288,12.578,273.688,0,256,0s-32,12.578-32,28.091V224H128L256,352,384,224Z"/>
    `,
    },

    branchs: {
        viewBox: "0 0 48 48",
        path: `
        <g stroke="currentColor" stroke-width="4" fill="none" stroke-linejoin="round" stroke-linecap="round">
            <circle cx="40" cy="24" r="4" fill="currentColor"/>
            <circle cx="9" cy="8" r="4" fill="currentColor"/>
            <circle cx="9" cy="40" r="4" fill="currentColor"/>
            <polyline points="9 12 9 36 9 24 36 24"/>
        </g>
    `,
    },

    collectionPlayFill: {
        viewBox: "0 0 16 16",
        path: `
        <path fill="currentColor" d="M2.5 3.5a.5.5 0 0 1 0-1h11a.5.5 0 0 1 0 1zm2-2a.5.5 0 0 1 0-1h7a.5.5 0 0 1 0 1zM0 13a1.5 1.5 0 0 0 1.5 1.5h13A1.5 1.5 0 0 0 16 13V6a1.5 1.5 0 0 0-1.5-1.5h-13A1.5 1.5 0 0 0 0 6zm6.258-6.437a.5.5 0 0 1 .507.013l4 2.5a.5.5 0 0 1 0 .848l-4 2.5A.5.5 0 0 1 6 12V7a.5.5 0 0 1 .258-.437"/>
    `,
    },

    archiveFill: {
        viewBox: "0 0 16 16",
        path: `
        <path fill="currentColor" d="M12.643 15C13.979 15 15 13.845 15 12.5V5H1v7.5C1 13.845 2.021 15 3.357 15zM5.5 7h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1 0-1M.8 1a.8.8 0 0 0-.8.8V3a.8.8 0 0 0 .8.8h14.4A.8.8 0 0 0 16 3V1.8a.8.8 0 0 0-.8-.8z"/>
    `,
    },

    download: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
        `,
    },

    upload: {
        viewBox: "0 0 24 24",
        path: `
            <path fill="currentColor" d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
        `,
    },

    excel: {
        viewBox: "0 0 32 32",
        path: `
            <path d="M28.781,4.405H18.651V2.018L2,4.588V27.115l16.651,2.868V26.445H28.781A1.162,1.162,0,0,0,30,25.349V5.5A1.162,1.162,0,0,0,28.781,4.405Zm.16,21.126H18.617L18.6,23.642h2.487v-2.2H18.581l-.012-1.3h2.518v-2.2H18.55l-.012-1.3h2.549v-2.2H18.53v-1.3h2.557v-2.2H18.53v-1.3h2.557v-2.2H18.53v-2H28.941Z" style="fill:#20744a;fill-rule:evenodd"/>
            <rect x="22.487" y="7.439" width="4.323" height="2.2" style="fill:#20744a"/>
            <rect x="22.487" y="10.94" width="4.323" height="2.2" style="fill:#20744a"/>
            <rect x="22.487" y="14.441" width="4.323" height="2.2" style="fill:#20744a"/>
            <rect x="22.487" y="17.942" width="4.323" height="2.2" style="fill:#20744a"/>
            <rect x="22.487" y="21.443" width="4.323" height="2.2" style="fill:#20744a"/>
            <polygon points="6.347 10.673 8.493 10.55 9.842 14.259 11.436 10.397 13.582 10.274 10.976 15.54 13.582 20.819 11.313 20.666 9.781 16.642 8.248 20.513 6.163 20.329 8.585 15.666 6.347 10.673" style="fill:#ffffff;fill-rule:evenodd"/>
        `,
    },
    // Graduation Cap / Education
    "graduation-cap": {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5-10-5z"/>
                <path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </g>
        `,
    },

    // Image / Logo
    image: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
            </g>
        `,
    },

    // Book Open / Courses
    "book-open": {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
            </g>
        `,
    },

    // Briefcase / Jobs
    briefcase: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </g>
        `,
    },

    // Folder Git 2 / Projects
    "folder-git2": {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H20a2 2 0 0 1 2 2v5"/>
                <circle cx="18" cy="18" r="3"/>
                <path d="M18 15v3"/>
                <path d="M18 18h3"/>
            </g>
        `,
    },
    // Database / Backups
    database: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="5" rx="9" ry="3"/>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
                <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>
            </g>
        `,
    },

    // Refresh CCW / History
    "refresh-ccw": {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                <path d="M3 3v5h5"/>
                <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
                <path d="M16 16h5v5"/>
            </g>
        `,
    },

    // Info / Help
    info: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
            </g>
        `,
    },

    // Mail / Email Settings
    mail: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                <path d="M22 7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7Z"/>
            </g>
        `,
    },

    // Tool / Maintenance
    tool: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
            </g>
        `,
    },

    // Check Circle
    "check-circle": {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
            </g>
        `,
    },

    // Sort Arrows
    arrowUp: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="19" x2="12" y2="5"/>
                <polyline points="5 12 12 5 19 12"/>
            </g>
        `,
    },
    arrowDown: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <polyline points="19 12 12 19 5 12"/>
            </g>
        `,
    },

    // Wand / Magic / Yield
    wand: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 21 9-9"/>
                <path d="m12.2 6.2 1.2 1.2"/>
                <path d="m19 5-1.2 1.2"/>
                <path d="m19 13-1.2-1.2"/>
                <path d="m7.2 6.2 1.2 1.2"/>
                <path d="M15 4V2"/>
                <path d="M15 16v-2"/>
                <path d="M8 9h2"/>
                <path d="M20 9h2"/>
            </g>
        `,
    },

    // Zap / Yield / Energy
    zap: {
        viewBox: "0 0 24 24",
        path: `
            <g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </g>
        `,
    },
};

export default dashboardIcons;
