import { toAbsoluteBackendUrl } from '@/services/api/url';

/**
 * Robust helper to load an image and return a base64 string.
 * This version tries to bypass CORS by using relative paths.
 */
async function loadImgData(url, bgColor = null) {
    if (!url) return null;

    let absoluteUrl = toAbsoluteBackendUrl(url);
    
    // In development, we use the Vite proxy for /storage to avoid CORS
    if (import.meta.env.DEV && absoluteUrl.includes('/storage/')) {
        const parts = absoluteUrl.split('/storage/');
        absoluteUrl = '/storage/' + parts[1];
    }
    
    const targetUrl = absoluteUrl.startsWith('data:') ? absoluteUrl : `${absoluteUrl}${absoluteUrl.includes('?') ? '&' : '?'}t=${Date.now()}`;

    // Helper to render any image (including SVGs) to a PNG base64 via canvas
    const renderToPng = (src) => {
        return new Promise((resolve) => {
            const img = new Image();
            if (!src.startsWith('data:')) img.crossOrigin = 'anonymous';
            img.onload = () => {
                try {
                    const canvas = document.createElement('canvas');
                    const size = 512;
                    canvas.width = size;
                    canvas.height = size;
                    const ctx = canvas.getContext('2d');

                    // 1. Limpiar todo para asegurar transparencia en las esquinas
                    ctx.clearRect(0, 0, size, size);

                    // 2. Dibujar el fondo de cuadrado redondeado si se proporciona bgColor
                    if (bgColor) {
                        ctx.fillStyle = `rgb(${bgColor.join(',')})`;
                        const r = size * 0.22; // Radio de curvatura para un estilo moderno
                        ctx.beginPath();
                        if (ctx.roundRect) {
                            ctx.roundRect(0, 0, size, size, r);
                        } else {
                            // Fallback para navegadores antiguos
                            ctx.moveTo(r, 0);
                            ctx.arcTo(size, 0, size, size, r);
                            ctx.arcTo(size, size, 0, size, r);
                            ctx.arcTo(0, size, 0, 0, r);
                            ctx.arcTo(0, 0, size, 0, r);
                        }
                        ctx.fill();
                    }

                    // 3. Dibujar la imagen centrada con margen (evitando artefactos de clip)
                    // Como tenemos un margen del 15%, el logo no se sale del círculo aunque sea cuadrado.
                    const margin = size * 0.15;
                    const drawSize = size - (margin * 2);
                    ctx.drawImage(img, margin, margin, drawSize, drawSize);

                    resolve(canvas.toDataURL('image/png'));
                } catch (err) { resolve(null); }
            };
            img.onerror = () => resolve(null);
            img.src = src;
        });
    };

    // For icons, we ALWAYS want to go through renderToPng to ensure:
    // 1. Transparency is handled via canvas (avoids jsPDF black square bugs)
    // 2. We can apply circular clipping and background color
    return await renderToPng(targetUrl);
}

/**
 * Helper to load an image and return a circular base64 string.
 */
async function loadCircularImage(url) {
    if (!url) return null;

    let absoluteUrl = toAbsoluteBackendUrl(url);
    
    // In development, we use the Vite proxy for /storage to avoid CORS
    if (import.meta.env.DEV && absoluteUrl.includes('/storage/')) {
        const parts = absoluteUrl.split('/storage/');
        absoluteUrl = '/storage/' + parts[1];
    }
    
    const targetUrl = absoluteUrl.startsWith('data:') ? absoluteUrl : `${absoluteUrl}${absoluteUrl.includes('?') ? '&' : '?'}t=${Date.now()}`;

    return new Promise((resolve) => {
        const img = new Image();
        if (!targetUrl.startsWith('data:')) img.crossOrigin = 'anonymous';
        img.onload = () => {
            try {
                const sw = img.width;
                const sh = img.height;
                const size = Math.min(sw, sh);

                const canvas = document.createElement('canvas');
                canvas.width = size;
                canvas.height = size;
                const ctx = canvas.getContext('2d');

                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'high';

                ctx.clearRect(0, 0, size, size);
                ctx.beginPath();
                ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
                ctx.clip();

                const sx = (sw - size) / 2;
                const sy = (sh - size) / 2;
                ctx.drawImage(img, sx, sy, size, size, 0, 0, size, size);

                resolve(canvas.toDataURL('image/png'));
            } catch (e) { resolve(null); }
        };
        img.onerror = () => resolve(null);
        img.src = targetUrl;
    });
}

/**
 * Normal image loader for QRs
 */
async function loadQRData(url) {
    if (!url) return null;
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(url)}`;
    return new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
            try {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                canvas.getContext('2d').drawImage(img, 0, 0);
                resolve(canvas.toDataURL('image/jpeg', 0.8));
            } catch (e) { resolve(null); }
        };
        img.onerror = () => resolve(null);
        img.src = qrUrl;
    });
}

const paletteThemes = {
    default: { primary: [15, 23, 42], accent: [66, 185, 131] },
    blue: { primary: [15, 23, 42], accent: [59, 130, 246] },
    purple: { primary: [31, 20, 60], accent: [139, 92, 246] },
    orange: { primary: [40, 20, 10], accent: [249, 115, 22] },
    red: { primary: [45, 10, 10], accent: [239, 68, 68] },
    gold: { primary: [35, 25, 10], accent: [245, 158, 11] }
};


export async function generateResumePDF(data) {
    const { jsPDF } = await import('jspdf');
    const { profile, jobs, education, skills, technologies, projects, courses, contactEmail, avatarUrl, palette } = data;

    const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const sidebarWidth = 75;
    const margin = 15;
    const contentMargin = sidebarWidth + 12;
    const contentWidth = pageWidth - contentMargin - margin;

    const theme = paletteThemes[palette] || paletteThemes.default;
    const primaryColor = theme.primary;
    const accentColor = theme.accent;
    const sidebarTextColor = [241, 245, 249];
    const mainTextColor = [51, 65, 85];
    const headerTextColor = [15, 23, 42];

    // Sidebar
    doc.setFillColor(...primaryColor);
    doc.rect(0, 0, sidebarWidth, pageHeight, 'F');

    let sy = 20;

    // --- CIRCULAR AVATAR ---
    if (avatarUrl) {
        try {
            const imgData = await loadCircularImage(avatarUrl);
            if (imgData) {
                const imgSize = 48;
                const ix = (sidebarWidth - imgSize) / 2;
                doc.setDrawColor(...accentColor);
                doc.setLineWidth(0.8);
                doc.circle(ix + imgSize / 2, sy + imgSize / 2, (imgSize / 2) + 1, 'D');
                doc.addImage(imgData, 'PNG', ix, sy, imgSize, imgSize);
                sy += imgSize + 15;
            } else {
                // Last ditch effort: try to use the DOM image directly without canvas if possible
                // (though jsPDF still needs it, it might work if we just use a placeholder)
                sy += 10;
            }
        } catch (e) {
            sy += 10;
        }
    } else {
        sy += 20;
    }

    const drawSidebarTitle = (text, y) => {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.setTextColor(255, 255, 255);
        doc.text(text.toUpperCase(), 12, y);
        doc.setDrawColor(...accentColor);
        doc.setLineWidth(0.8);
        doc.line(12, y + 2, 25, y + 2);
        return y + 10;
    };

    sy = drawSidebarTitle('Contacto', sy);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(...sidebarTextColor);

    const drawContactItem = (label, value, y) => {
        if (!value) return y;
        doc.setFont('helvetica', 'bold');
        doc.text(label, 12, y);
        doc.setFont('helvetica', 'normal');
        const lines = doc.splitTextToSize(value, sidebarWidth - 24);
        doc.text(lines, 12, y + 4);
        return y + 6 + (lines.length * 4);
    };

    sy = drawContactItem('Email', contactEmail, sy);
    sy = drawContactItem('Ubicación', profile.location, sy);
    sy = drawContactItem('Teléfono', data.phone || profile.phone, sy);
    sy += 8;

    // Helper for Sidebar Icon Lists (Habilidades, Tecnologías)
    const drawSidebarIconList = async (title, items, y) => {
        if (!items || items.length === 0) return y;
        y = drawSidebarTitle(title, y);
        doc.setFontSize(9);

        for (const item of items) {
            const label = typeof item === 'string' ? item : (item.label || '');
            const iconData = item.icon_data;
            let iconSource = null;
            const rowStartX = 12;

            if (iconData) {
                if (iconData.svg_raw) {
                    const svgBase64 = btoa(unescape(encodeURIComponent(iconData.svg_raw)));
                    iconSource = `data:image/svg+xml;base64,${svgBase64}`;
                } else if (iconData.file_path) {
                    iconSource = iconData.file_path;
                }
            }

            // Draw border box for the whole item row
            doc.setDrawColor(...accentColor);
            doc.setLineWidth(0.2);
            doc.roundedRect(rowStartX, y - 6, sidebarWidth - 22, 10, 1.5, 1.5, 'S');

            if (iconSource) {
                const imgData = await loadImgData(iconSource, accentColor);
                if (imgData) {
                    // Dibujamos la imagen directamente - ya trae el círculo y fondo de loadImgData
                    doc.addImage(imgData, 'PNG', rowStartX + 1.5, y - 4.5, 7, 7);

                    doc.setTextColor(...sidebarTextColor);
                    doc.text(label, rowStartX + 10, y + 0.5);
                } else {
                    doc.setTextColor(...sidebarTextColor);
                    doc.text(label, rowStartX + 3, y + 0.5);
                }
            } else {
                doc.setTextColor(...sidebarTextColor);
                doc.text(`• ${label}`, rowStartX + 3, y + 0.5);
            }

            y += 13; // Increased spacing for boxed items
            if (y > pageHeight - 15) break;
        }
        return y + 5;
    };

    sy = await drawSidebarIconList('Habilidades', skills, sy);
    sy = await drawSidebarIconList('Tecnologías', technologies, sy);

    // Main Content
    let my = 15;

    // --- SOCIAL BANNER ABOVE NAME ---
    if (data.social && data.social.length > 0) {
        let bx = contentMargin + 2; // Initial offset for the first box
        for (const link of data.social) {
            const pairStartX = bx;
            const iconData = link.icon_data;
            let iconSource = null;

            if (iconData) {
                if (iconData.svg_raw) {
                    const svgBase64 = btoa(unescape(encodeURIComponent(iconData.svg_raw)));
                    iconSource = `data:image/svg+xml;base64,${svgBase64}`;
                } else if (iconData.file_path) {
                    iconSource = iconData.file_path;
                }
            }

            // Draw Icon
            if (iconSource) {
                const imgData = await loadImgData(iconSource, accentColor);
                if (imgData) {
                    // Dibujamos la imagen directamente - ya es circular y tiene fondo
                    doc.addImage(imgData, 'PNG', bx, my - 8, 10, 10);
                    bx += 12;
                }
            }

            // Draw QR
            if (link.url) {
                const qr = await loadQRData(link.url);
                if (qr) {
                    doc.addImage(qr, 'JPEG', bx, my - 8, 10, 10);
                    bx += 12;
                }
            }

            // Draw border around the pair (Icon + QR)
            const pairWidth = bx - pairStartX;
            if (pairWidth > 0) {
                doc.setDrawColor(...accentColor);
                doc.setLineWidth(0.3);
                doc.roundedRect(pairStartX - 2, my - 10, pairWidth + 2, 14, 2, 2, 'S');
            }

            bx += 12; // Space to next boxed pair
            if (bx > pageWidth - margin - 20) break;
        }
        my += 18;
    }

    // Dynamically adjust font size for the name to fit the available space
    let nameFontSize = 28;
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(nameFontSize);
    const nameStr = profile.name.toUpperCase();
    while (doc.getTextWidth(nameStr) > contentWidth && nameFontSize > 14) {
        nameFontSize -= 1;
        doc.setFontSize(nameFontSize);
    }

    doc.setTextColor(...headerTextColor);
    doc.text(nameStr, contentMargin, my);
    my += 10;

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(...accentColor);
    doc.text(profile.role, contentMargin, my);
    my += 15;

    const drawMainTitle = (text, y) => {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(12);
        doc.setTextColor(...headerTextColor);
        doc.text(text.toUpperCase(), contentMargin, y);
        doc.setDrawColor(...accentColor);
        doc.setLineWidth(0.5);
        doc.line(contentMargin, y + 2, contentMargin + 15, y + 2);
        return y + 10;
    };

    if (profile.summary) {
        my = drawMainTitle('Perfil Profesional', my);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        doc.setTextColor(...mainTextColor);
        const summaryLines = doc.splitTextToSize(profile.summary, contentWidth);
        doc.text(summaryLines, contentMargin, my);
        my += (summaryLines.length * 5.5) + 12;
    }

    if (jobs && jobs.length > 0) {
        my = drawMainTitle('Experiencia Laboral', my);
        for (const job of jobs) {
            if (my > 260) { doc.addPage(); my = 20; doc.setFillColor(...primaryColor); doc.rect(0, 0, sidebarWidth, pageHeight, 'F'); }
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.setTextColor(...headerTextColor);
            
            // Wrap role to avoid overlap with period
            const period = job.period || `${job.startDate} - ${job.isCurrent ? 'Actual' : job.endDate}`;
            const periodWidth = doc.getTextWidth(period);
            const maxRoleWidth = contentWidth - periodWidth - 5;
            const roleLines = doc.splitTextToSize(job.role, maxRoleWidth);
            doc.text(roleLines, contentMargin, my);

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(9);
            doc.setTextColor(...accentColor);
            doc.text(period, pageWidth - margin - periodWidth, my);
            
            my += (roleLines.length * 5);
            doc.setFont('helvetica', 'italic');
            doc.setFontSize(10);
            doc.setTextColor(...mainTextColor);
            doc.text(job.company, contentMargin, my);
            my += 2;
            const companyUrl = job.companyUrl || job.company_url;
            if (companyUrl) {
                const qr = await loadQRData(companyUrl);
                if (qr) {
                    // QR más abajo y con espacio extra
                    doc.addImage(qr, 'JPEG', pageWidth - margin - 12, my + 2, 12, 12);
                    my += 5;
                }
            }
            my += 4;
            if (job.description) {
                doc.setFont('helvetica', 'normal');
                doc.setFontSize(9.5);
                doc.setTextColor(...mainTextColor);
                const descLines = doc.splitTextToSize(job.description, contentWidth - 15);
                doc.text(descLines, contentMargin, my);
                my += (descLines.length * 5) + 8;
            } else { my += 6; }
        }
        my += 4;
    }

    if (education && education.length > 0) {
        // Ordenar educación de más viejo a más nuevo para consistencia
        const sortedEducation = [...education].sort((a, b) => {
            const dateA = a.startDate || '';
            const dateB = b.startDate || '';
            return dateA.localeCompare(dateB);
        });

        if (my > 240) { doc.addPage(); my = 20; doc.setFillColor(...primaryColor); doc.rect(0, 0, sidebarWidth, pageHeight, 'F'); }
        my = drawMainTitle('Educación', my);
        for (const edu of sortedEducation) {
            if (my > 260) { doc.addPage(); my = 20; doc.setFillColor(...primaryColor); doc.rect(0, 0, sidebarWidth, pageHeight, 'F'); }
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(11);
            doc.setTextColor(...headerTextColor);
            
            // Wrap title to avoid overlap with period
            const period = edu.period || `${edu.startDate} - ${edu.isCurrent ? 'Actual' : edu.endDate}`;
            const periodWidth = doc.getTextWidth(period);
            const maxEduTitleWidth = contentWidth - periodWidth - 5;
            const eduTitleLines = doc.splitTextToSize(edu.title, maxEduTitleWidth);
            doc.text(eduTitleLines, contentMargin, my);

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(...accentColor);
            doc.text(period, pageWidth - margin - periodWidth, my);
            
            my += (eduTitleLines.length * 5);
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(10);
            doc.setTextColor(...mainTextColor);
            doc.text(edu.institution, contentMargin, my);
            const instUrl = edu.institutionUrl || edu.institution_url;
            if (instUrl) {
                const qr = await loadQRData(instUrl);
                if (qr) {
                    // Posicionamos el QR debajo de la fecha para evitar colisión
                    doc.addImage(qr, 'JPEG', pageWidth - margin - 12, my + 2, 12, 12);
                    my += 8; // Espacio extra si hay QR
                }
            }
            my += 10;
        }
    }

    if (projects && projects.length > 0) {
        if (my > 240) { doc.addPage(); my = 20; doc.setFillColor(...primaryColor); doc.rect(0, 0, sidebarWidth, pageHeight, 'F'); }
        my = drawMainTitle('Proyectos Destacados', my);
        for (const proj of projects.slice(0, 3)) {
            if (my > 260) { doc.addPage(); my = 20; doc.setFillColor(...primaryColor); doc.rect(0, 0, sidebarWidth, pageHeight, 'F'); }
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(10);
            doc.setTextColor(...headerTextColor);
            doc.text(proj.title, contentMargin, my);
            const pUrl = proj.liveUrl || proj.live_url || proj.repoUrl || proj.repo_url;
            if (pUrl) {
                const qr = await loadQRData(pUrl);
                if (qr) {
                    // Bajamos el QR para que no choque con el título
                    doc.addImage(qr, 'JPEG', pageWidth - margin - 12, my + 2, 12, 12);
                    my += 4;
                }
            }
            my += 5;
            const desc = proj.description || proj.detailedDescription;
            if (desc) {
                doc.setFont('helvetica', 'normal');
                doc.setFontSize(9);
                const descLines = doc.splitTextToSize(desc, contentWidth - 15);
                doc.text(descLines, contentMargin, my);
                my += (descLines.length * 4.5) + 6;
            }
        }
    }
    if (courses && courses.length > 0) {
        if (my > 240) { doc.addPage(); my = 20; doc.setFillColor(...primaryColor); doc.rect(0, 0, sidebarWidth, pageHeight, 'F'); }
        my = drawMainTitle('Cursos y Certificaciones', my);
        
        // Ordenar de más reciente a más viejo (o según prefiera el usuario, usualmente los cursos van por año)
        const sortedCourses = [...courses].sort((a, b) => {
            const yearA = String(a.year || '');
            const yearB = String(b.year || '');
            return yearB.localeCompare(yearA);
        });

        for (const course of sortedCourses) {
            if (my > 260) { doc.addPage(); my = 20; doc.setFillColor(...primaryColor); doc.rect(0, 0, sidebarWidth, pageHeight, 'F'); }
            
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(10);
            doc.setTextColor(...headerTextColor);
            
            // Wrap title to avoid overlap with year
            const yearText = String(course.year || '');
            const yearWidth = doc.getTextWidth(yearText);
            const maxCourseTitleWidth = contentWidth - yearWidth - 5;
            const courseTitleLines = doc.splitTextToSize(course.title, maxCourseTitleWidth);
            doc.text(courseTitleLines, contentMargin, my);

            doc.setFont('helvetica', 'normal');
            doc.setFontSize(9);
            doc.setTextColor(...accentColor);
            doc.text(yearText, pageWidth - margin - yearWidth, my);
            
            my += (courseTitleLines.length * 5);
            doc.setFont('helvetica', 'italic');
            doc.setFontSize(9);
            doc.setTextColor(...mainTextColor);
            doc.text(course.provider, contentMargin, my);

            const cUrl = course.courseUrl || (course.certificateUrls && course.certificateUrls[0]) || course.certificateUrl;
            if (cUrl) {
                const qr = await loadQRData(cUrl);
                if (qr) {
                    // Bajamos el QR para no chocar con el año (que está arriba a la derecha)
                    doc.addImage(qr, 'JPEG', pageWidth - margin - 12, my + 2, 12, 12);
                    my += 8; 
                }
            }
            my += 10;
        }
    }

    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.text(`Curriculum Vitae  -  ${profile.name}  -  Página ${i} de ${pageCount}`, pageWidth / 2, 287, { align: 'center' });
    }

    doc.save(`CV_${profile.name.replace(/\s+/g, '_')}.pdf`);
}
