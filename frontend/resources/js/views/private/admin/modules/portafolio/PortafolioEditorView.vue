<template>
    <section class="portfolio-editor-page dashboard-module">
        <div class="editor-sticky-shell">
            <nav v-if="portfolioItem" class="editor-tabs" aria-label="Bloques del portafolio">
                <div class="tabs-group">
                    <button v-for="tab in editorTabs" :key="tab.id" type="button" class="tab-btn"
                        :class="{ active: activeTab === tab.id }" :title="tab.label" @click="setActiveTab(tab.id)">
                        <Icon :name="tab.icon" :size="16" />
                        <span>{{ tab.label }}</span>
                    </button>
                </div>

                <div class="tabs-actions">
                    <button type="button" class="btn btn--compact" @click="openInfoModal">Informacion</button>
                    <button type="button" class="btn btn--compact" @click="goBack">Volver</button>
                </div>
            </nav>
        </div>

        <div v-if="!portfolioItem" class="editor-empty">
            <h2>Portafolio no encontrado</h2>
            <p>El identificador no existe o no hay datos guardados en este navegador.</p>
            <button type="button" class="btn btn--primary" @click="goBack">Regresar a la lista</button>
        </div>

        <div v-else class="editor-layout">
            <div class="editor-main">
                <ProfileTab v-if="activeTab === 'profile'" :profile="localBlocks.profile"
                    v-model:avatar-url="localBlocks.avatarUrl" :portfolio-item="portfolioItem"
                    @avatar-updated="handleAvatarUpdated" />

                <MetricsTab v-if="activeTab === 'metrics'" :metrics="localBlocks.metrics" />

                <SkillsTab v-if="activeTab === 'skills'" :skills="localBlocks.skills" />

                <TechnologiesTab v-if="activeTab === 'technologies'" :technologies="localBlocks.technologies" />

                <ProjectsTab v-if="activeTab === 'projects'" :projects="localBlocks.projects"
                    :portfolio-item="portfolioItem" :all-blocks="localBlocks" @request-save="saveChanges"
                    @portfolio-synced="handleJobsSynced" />

                <JobsTab v-if="activeTab === 'jobs'" :jobs="localBlocks.jobs" :portfolio-item="portfolioItem"
                    :all-blocks="localBlocks" @request-save="saveChanges" @portfolio-synced="handleJobsSynced" />

                <EducationTab v-if="activeTab === 'education'" :education="localBlocks.education"
                    :portfolio-item="portfolioItem" :all-blocks="localBlocks" @request-save="saveChanges"
                    @portfolio-synced="handleJobsSynced" />

                <CoursesTab v-if="activeTab === 'courses'" :courses="localBlocks.courses"
                    :portfolio-item="portfolioItem" :all-blocks="localBlocks" @request-save="saveChanges"
                    @portfolio-synced="handleJobsSynced" />

                <ContactTab v-if="activeTab === 'contact'" :contact="localBlocks.contact"
                    :social="localBlocks.social" />
            </div>
        </div>

        <div v-if="isInfoModalOpen" class="info-modal-overlay" @click="closeInfoModal">
            <article class="info-modal" role="dialog" aria-modal="true" @click.stop>
                <header class="info-modal-header">
                    <div>
                        <h3>Resumen base</h3>
                        <p>Informacion general y conteo de bloques del portafolio.</p>
                    </div>
                    <button type="button" class="btn" @click="closeInfoModal">Cerrar</button>
                </header>

                <div class="info-modal-body" v-if="portfolioItem">
                    <p><strong>Portafolio:</strong> {{ portfolioItem.name || 'Sin nombre' }}</p>
                    <p><strong>Usuario:</strong> {{ portfolioItem.ownerName || 'Sin usuario' }}</p>
                    <p><strong>Token:</strong> {{ portfolioItem.token || '------' }}</p>
                    <p><strong>Estado:</strong> {{ portfolioItem.status === 'published' ? 'Publicado' : 'Borrador' }}
                    </p>

                    <hr />

                    <h4>Contenido configurado</h4>
                    <p><strong>Metricas:</strong> {{ localBlocks.metrics.length }}</p>
                    <p><strong>Skills:</strong> {{ localBlocks.skills.length }}</p>
                    <p><strong>Tecnologias:</strong> {{ localBlocks.technologies.length }}</p>
                    <p><strong>Proyectos:</strong> {{ localBlocks.projects.length }}</p>
                    <p><strong>Trabajos:</strong> {{ localBlocks.jobs.length }}</p>
                    <p><strong>Educacion:</strong> {{ localBlocks.education.length }}</p>
                    <p><strong>Cursos:</strong> {{ localBlocks.courses.length }}</p>
                    <p v-if="isDirty" class="unsaved-warning">Tienes cambios sin guardar.</p>

                    <a class="public-link preview-link" :href="buildPublicUrl(portfolioItem.token || '______')"
                        target="_blank" rel="noopener noreferrer">
                        Abrir vista publica
                    </a>
                </div>
            </article>
        </div>
    </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import { FRONTEND_BASE_URL } from '@/services/api/url';

// Components
import ProfileTab from './components/ProfileTab.vue';
import MetricsTab from './components/MetricsTab.vue';
import SkillsTab from './components/SkillsTab.vue';
import TechnologiesTab from './components/TechnologiesTab.vue';
import ProjectsTab from './components/ProjectsTab.vue';
import JobsTab from './components/JobsTab.vue';
import EducationTab from './components/EducationTab.vue';
import CoursesTab from './components/CoursesTab.vue';
import ContactTab from './components/ContactTab.vue';
import Icon from '@/components/Icon.vue';

const TAB_STORAGE_KEY = 'portfolio_editor_active_tab';

const route = useRoute();
const router = useRouter();
const alert = useAlert();

const portfolioItem = ref(null);
const initialSnapshot = ref('');
const isInfoModalOpen = ref(false);
const saveStatus = ref(null); // { text, type: 'loading' | 'success' | 'error' }
let saveTimeout = null;
const activeTab = ref('profile');
const editorTabs = [
    { id: 'profile', label: 'Perfil', icon: 'user' },
    { id: 'metrics', label: 'Metricas', icon: 'activity' },
    { id: 'skills', label: 'Habilidades', icon: 'star' },
    { id: 'technologies', label: 'Tecnologias', icon: 'code' },
    { id: 'projects', label: 'Proyectos', icon: 'folder' },
    { id: 'jobs', label: 'Trabajos', icon: 'maletin' },
    { id: 'education', label: 'Educacion', icon: 'graduation-cap' },
    { id: 'courses', label: 'Cursos', icon: 'collectionPlayFill' },
    { id: 'contact', label: 'Contacto', icon: 'send' }
];

const localBlocks = reactive(defaultLandingBlocks());

const isDirty = computed(() => JSON.stringify(localBlocks) !== initialSnapshot.value);

function sanitizeTab(tabId) {
    const allowedTabs = editorTabs.map(item => item.id);
    return allowedTabs.includes(tabId) ? tabId : 'profile';
}

function setActiveTab(tabId) {
    const safeTab = sanitizeTab(tabId);
    activeTab.value = safeTab;
    localStorage.setItem(TAB_STORAGE_KEY, safeTab);
}

function restoreActiveTab() {
    const storedTab = localStorage.getItem(TAB_STORAGE_KEY);
    const safeStoredTab = sanitizeTab(storedTab);
    activeTab.value = safeStoredTab;
    localStorage.setItem(TAB_STORAGE_KEY, safeStoredTab);
}

function defaultLandingBlocks() {
    return {
        profile: {
            name: 'Tu Nombre Apellido',
            role: 'Desarrollador Full Stack',
            summary: 'Desarrollador orientado a producto, enfocado en crear soluciones robustas.',
            aboutText: 'Desarrollador orientado a producto, enfocado en crear soluciones robustas que combinan rendimiento, claridad visual y buena experiencia de usuario.'
        },
        avatarUrl: 'https://i.pravatar.cc/420?img=68',
        metrics: [
            { value: '6+', label: 'anos de experiencia', icon_uuid: null, icon_data: null, is_active: true },
            { value: '25+', label: 'proyectos entregados', icon_uuid: null, icon_data: null, is_active: true },
            { value: '100%', label: 'enfoque en calidad', icon_uuid: null, icon_data: null, is_active: true }
        ],
        skills: [
            { label: 'Arquitectura modular', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Resolucion de problemas', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Comunicacion con negocio', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Liderazgo tecnico', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Testing y mejora continua', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Optimizacion de rendimiento', icon_uuid: null, icon_data: null, is_active: true }
        ],
        technologies: [
            { label: 'Laravel', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'PHP 8.4', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Vue 3', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Vite', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Sass', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'MySQL', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Docker', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Nginx', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'JWT', icon_uuid: null, icon_data: null, is_active: true },
            { label: 'Git', icon_uuid: null, icon_data: null, is_active: true }
        ],
        projects: [
            {
                id: 1,
                title: 'Gestor inteligente de archivos',
                description: 'Control de documentos, permisos por roles y flujo de trabajo para equipos internos.',
                detailedDescription:
                    'Sistema documental con control de permisos por rol, versionado, auditoria y busquedas rapidas para equipos con alto volumen de informacion.',
                type: 'Web Platform',
                repoUrl: 'https://github.com/tu-usuario/gestor-archivos',
                liveUrl: 'https://gestor-archivos.tu-dominio.com',
                images: [
                    'https://picsum.photos/seed/gestor-1/960/620',
                    'https://picsum.photos/seed/gestor-2/960/620',
                    'https://picsum.photos/seed/gestor-3/960/620'
                ],
                imagesText:
                    'https://picsum.photos/seed/gestor-1/960/620\nhttps://picsum.photos/seed/gestor-2/960/620\nhttps://picsum.photos/seed/gestor-3/960/620'
            }
        ],
        jobs: [
            {
                id: 1,
                role: 'Senior Software Developer',
                company: 'Tech Studio',
                period: '2023 - Actualidad',
                startDate: '2023-01',
                endDate: '',
                isCurrent: true,
                companyUrl: 'https://www.empresa.com',
                imageUrl: '',
                imageUrls: [],
                description: 'Lideré el desarrollo de microservicios con Laravel y Vue 3.',
                tags: ['Laravel', 'Vue 3', 'Microservicios']
            },
            {
                id: 2,
                role: 'Full Stack Developer',
                company: 'Digital Factory',
                period: '2020 - 2023',
                startDate: '2020-05',
                endDate: '2023-01',
                isCurrent: false,
                companyUrl: '',
                imageUrl: '',
                imageUrls: [],
                description: 'Desarrollo de landing pages y e-commerce.',
                tags: ['E-commerce', 'UI', 'Integraciones']
            }
        ],
        education: [
            { id: 1, title: 'Ingenieria en Sistemas', institution: 'Universidad Tecnologica', period: '2014 - 2018' },
            { id: 2, title: 'Diplomado en Arquitectura de Software', institution: 'Academia Tech', period: '2019' }
        ],
        courses: [
            { id: 1, title: 'Escalabilidad y performance web', provider: 'Plataforma Online Pro', year: '2024', courseUrl: '', description: '', tags: ['Backend', 'Performance'], imageUrl: '', imageUrls: [], certificateUrl: '', certificateUrls: [] },
            { id: 2, title: 'Clean Architecture aplicada', provider: 'Code Academy', year: '2023', courseUrl: '', description: '', tags: ['Arquitectura', 'PHP'], imageUrl: '', imageUrls: [], certificateUrl: '', certificateUrls: [] },
            { id: 3, title: 'Diseno UX para desarrolladores', provider: 'UX Institute', year: '2022', courseUrl: '', description: '', tags: ['UX', 'Frontend'], imageUrl: '', imageUrls: [], certificateUrl: '', certificateUrls: [] }
        ],
        contact: {
            email: 'tuemail@dominio.com',
            phone: '',
            whatsapp: ''
        },
        social: []
    };
}

function splitLines(value) {
    return String(value || '')
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean);
}

function normalizeLegacyList(lines, mapFn) {
    return splitLines(lines).map((line, index) => mapFn(line, index));
}

function normalizeLabeledItems(source, fallbackLines) {
    if (!Array.isArray(source)) {
        return normalizeLegacyList(fallbackLines, line => ({
            label: line,
            icon_uuid: null,
            icon_data: null
        }));
    }

    return source
        .map(item => {
            if (typeof item === 'string') {
                return {
                    label: item,
                    icon_uuid: null,
                    icon_data: null,
                    is_active: true
                };
            }

            return {
                label: item.label || item.name || '',
                icon_uuid: item.icon_uuid || item.iconUuid || null,
                icon_data: item.icon_data || item.iconData || null,
                is_active: item.is_active !== false
            };
        })
        .filter(item => item.label || item.icon_uuid);
}

function normalizeBlocks(sourceBlocks = {}, baseData = {}) {
    const defaults = defaultLandingBlocks();

    const blocks = {
        ...defaults,
        ...sourceBlocks,
        profile: {
            ...defaults.profile,
            ...(sourceBlocks.profile || {})
        },
        contact: {
            ...defaults.contact,
            ...(sourceBlocks.contact || {})
        },
        social: (Array.isArray(sourceBlocks.social) ? sourceBlocks.social : defaults.social).map(s => ({
            name: s.name || '',
            handle: s.handle || '',
            url: s.url || '',
            icon: s.icon || 'external-link',
            icon_uuid: s.icon_uuid || s.iconUuid || null,
            icon_data: s.icon_data || s.iconData || null,
            is_active: s.is_active !== false
        })),
        aboutText: sourceBlocks.profile?.aboutText || sourceBlocks.aboutText || defaults.profile.aboutText
    };

    if (!sourceBlocks.profile) {
        blocks.profile.name = baseData.name || defaults.profile.name;
        blocks.profile.summary = sourceBlocks.aboutText || defaults.profile.summary;
        blocks.profile.aboutText = sourceBlocks.aboutText || defaults.profile.aboutText;
    }

    if (!Array.isArray(sourceBlocks.metrics) || sourceBlocks.metrics.length === 0) {
        blocks.metrics = defaults.metrics;
    } else {
        blocks.metrics = sourceBlocks.metrics.map(m => ({
            value: m.value || '',
            label: m.label || '',
            icon_uuid: m.icon_uuid || m.iconUuid || null,
            icon_data: m.icon_data || m.iconData || null,
            is_active: m.is_active !== false
        }));
    }

    blocks.skills = normalizeLabeledItems(sourceBlocks.skills, sourceBlocks.skillsText);
    if (blocks.skills.length === 0) {
        blocks.skills = defaults.skills;
    }

    blocks.technologies = normalizeLabeledItems(sourceBlocks.technologies, sourceBlocks.technologiesText);
    if (blocks.technologies.length === 0) {
        blocks.technologies = defaults.technologies;
    }

    if (!Array.isArray(sourceBlocks.projects)) {
        blocks.projects = normalizeLegacyList(sourceBlocks.projectsText, (line, index) => {
            const [titlePart, descriptionPart] = line.split(':');
            return {
                id: Date.now() + index,
                title: (titlePart || `Proyecto ${index + 1}`).trim(),
                description: (descriptionPart || line).trim(),
                detailedDescription: (descriptionPart || line).trim(),
                type: 'Proyecto',
                repoUrl: '',
                liveUrl: '',
                images: [],
                imagesText: ''
            };
        });

        if (blocks.projects.length === 0) {
            blocks.projects = defaults.projects;
        }
    }

    if (!Array.isArray(sourceBlocks.jobs)) {
        blocks.jobs = normalizeLegacyList(sourceBlocks.workHistoryText, (line, index) => {
            const [company, role] = line.split('-');
            return {
                id: Date.now() + index,
                role: (role || 'Rol').trim(),
                company: (company || line).trim(),
                startDate: '',
                endDate: '',
                isCurrent: false,
                companyUrl: '',
                imageUrl: '',
                imageUrls: []
            };
        });

        if (blocks.jobs.length === 0) {
            blocks.jobs = defaults.jobs;
        }
    } else {
        // Preserve all specific fields for existing array-based jobs
        blocks.jobs = sourceBlocks.jobs.map(job => ({
            ...(() => {
                const imageUrls = Array.isArray(job.imageUrls)
                    ? job.imageUrls.filter(Boolean)
                    : Array.isArray(job.image_urls)
                        ? job.image_urls.filter(Boolean)
                        : job.imageUrl || job.image_url
                            ? [job.imageUrl || job.image_url]
                            : [];

                return {
                    imageUrls,
                    imageUrl: imageUrls[0] || ''
                };
            })(),
            id: job.id || Date.now() + Math.random(),
            role: job.role || '',
            company: job.company || '',
            period: job.period || '',
            startDate: job.startDate || job.start_date || '',
            endDate: job.endDate || job.end_date || '',
            isCurrent: !!(job.isCurrent || job.is_current),
            companyUrl: job.companyUrl || job.company_url || '',
            description: job.description || '',
            tags: Array.isArray(job.tags)
                ? job.tags.map(tag => String(tag || '').trim()).filter(Boolean)
                : typeof job.tags === 'string'
                    ? job.tags.split(',').map(tag => tag.trim()).filter(Boolean)
                    : []
        }));
    }

    if (!Array.isArray(sourceBlocks.education)) {
        blocks.education = normalizeLegacyList(sourceBlocks.educationText, (line, index) => ({
            id: Date.now() + index,
            title: line,
            institution: '',
            period: ''
        }));

        if (blocks.education.length === 0) {
            blocks.education = defaults.education;
        }
    }

    if (!Array.isArray(sourceBlocks.courses)) {
        blocks.courses = normalizeLegacyList(sourceBlocks.coursesText, (line, index) => ({
            id: Date.now() + index,
            title: line,
            provider: '',
            year: '',
            courseUrl: '',
            description: '',
            tags: [],
            imageUrl: '',
            imageUrls: [],
            certificateUrl: '',
            certificateUrls: []
        }));

        if (blocks.courses.length === 0) {
            blocks.courses = defaults.courses;
        }
    } else {
        blocks.courses = sourceBlocks.courses.map((course, index) => {
            const imageUrls = Array.isArray(course.imageUrls)
                ? course.imageUrls.filter(Boolean)
                : Array.isArray(course.image_urls)
                    ? course.image_urls.filter(Boolean)
                    : course.imageUrl || course.image_url
                        ? [course.imageUrl || course.image_url]
                        : [];

            const certificateUrls = Array.isArray(course.certificateUrls)
                ? course.certificateUrls.filter(Boolean)
                : Array.isArray(course.certificate_urls)
                    ? course.certificate_urls.filter(Boolean)
                    : course.certificateUrl || course.certificate_url
                        ? [course.certificateUrl || course.certificate_url]
                        : [];

            const tags = Array.isArray(course.tags)
                ? course.tags.map(tag => String(tag || '').trim()).filter(Boolean)
                : typeof course.tags === 'string'
                    ? course.tags.split(',').map(tag => tag.trim()).filter(Boolean)
                    : [];

            return {
                id: course.id || Date.now() + index,
                title: course.title || `Curso ${index + 1}`,
                provider: course.provider || '',
                year: course.year || course.period || '',
                courseUrl: course.courseUrl || course.course_url || '',
                description: course.description || '',
                tags,
                imageUrls,
                imageUrl: imageUrls[0] || '',
                certificateUrls,
                certificateUrl: certificateUrls[0] || ''
            };
        });
    }

    if (!sourceBlocks.contact) {
        blocks.contact.email = sourceBlocks.contactEmail || defaults.contact.email;
    }

    blocks.projects = blocks.projects.map((project, index) => {
        const images = Array.isArray(project.images) ? project.images : splitLines(project.imagesText);
        const tags = Array.isArray(project.tags)
            ? project.tags.map(tag => String(tag || '').trim()).filter(Boolean)
            : typeof project.tags === 'string'
                ? project.tags.split(',').map(tag => tag.trim()).filter(Boolean)
                : typeof project.tagsText === 'string'
                    ? project.tagsText.split(',').map(tag => tag.trim()).filter(Boolean)
                    : [];

        return {
            id: project.id || Date.now() + index,
            title: project.title || `Proyecto ${index + 1}`,
            description: project.description || '',
            detailedDescription: project.detailedDescription || project.description || '',
            type: project.type || 'Proyecto',
            repoUrl: project.repoUrl || '',
            liveUrl: project.liveUrl || '',
            tags,
            tagsText: project.tagsText || tags.join(', '),
            images,
            imagesText: project.imagesText || images.join('\n')
        };
    });

    return blocks;
}

function fillBlocks(blocks = {}) {
    const normalized = normalizeBlocks(blocks, portfolioItem.value || {});

    localBlocks.profile.name = normalized.profile.name;
    localBlocks.profile.role = normalized.profile.role;
    localBlocks.profile.summary = normalized.profile.summary;
    localBlocks.profile.aboutText = normalized.profile.aboutText || normalized.profile.summary;
    localBlocks.profile.phone = normalized.profile.phone || '';
    localBlocks.avatarUrl = normalized.avatarUrl;
    localBlocks.metrics = normalized.metrics.map(item => ({ ...item }));
    localBlocks.skills = [...normalized.skills];
    localBlocks.technologies = [...normalized.technologies];
    localBlocks.projects = normalized.projects.map(item => ({ ...item }));
    localBlocks.jobs = normalized.jobs.map(item => ({ ...item }));
    localBlocks.education = normalized.education.map(item => ({ ...item }));
    localBlocks.courses = normalized.courses.map(item => ({ ...item }));
    localBlocks.contact.email = normalized.contact.email;
    localBlocks.contact.phone = normalized.contact.phone || '';
    localBlocks.contact.whatsapp = normalized.contact.whatsapp || '';
    localBlocks.social = Array.isArray(normalized.social) ? normalized.social.map(item => ({ ...item })) : [];

    initialSnapshot.value = JSON.stringify(localBlocks);
}

function mapApiPortfolio(item) {
    return {
        id: item.id,
        name: item.name,
        ownerName: item.owner_name,
        summary: item.summary,
        token: item.token,
        status: item.status,
        blocks: item.blocks || {}
    };
}

async function loadCurrentPortfolio() {
    const id = String(route.params.id || '');

    try {
        const response = await api.portfolios.getPortfolio(id);
        const found = mapApiPortfolio(response.data.data);
        portfolioItem.value = found;
        fillBlocks(found.blocks || {});
    } catch (error) {
        portfolioItem.value = null;
        fillBlocks(defaultLandingBlocks());
        if (error.response?.status !== 404) {
            alert.toast.error('Error', 'No se pudo cargar el portafolio.');
        }
    }
}

async function saveChanges() {
    if (!portfolioItem.value) {
        return;
    }

    saveStatus.value = { text: 'Sincronizando...', type: 'loading' };

    localBlocks.projects = localBlocks.projects.map((project, index) => {
        const images = Array.isArray(project.images) && project.images.length > 0
            ? project.images
            : splitLines(project.imagesText);

        return {
            ...project,
            id: project.id || Date.now() + index,
            images,
            imagesText: project.imagesText || images.join('\n')
        };
    });

    localBlocks.courses = localBlocks.courses.map((course, index) => {
        const images = Array.isArray(course.images) && course.images.length > 0
            ? course.images
            : Array.isArray(course.imageUrls) && course.imageUrls.length > 0
                ? course.imageUrls
                : splitLines(course.imagesText);

        return {
            ...course,
            id: course.id || Date.now() + index,
            images,
            imageUrls: images
        };
    });

    localBlocks.jobs = localBlocks.jobs.map((job, index) => {
        const imageUrls = Array.isArray(job.imageUrls) && job.imageUrls.length > 0
            ? job.imageUrls
            : Array.isArray(job.image_urls) && job.image_urls.length > 0
                ? job.image_urls
                : job.imageUrl
                    ? [job.imageUrl]
                    : [];

        return {
            ...job,
            id: job.id || Date.now() + index,
            imageUrls,
            imageUrl: imageUrls[0] || ''
        };
    });

    const id = String(portfolioItem.value.id);

    try {
        const response = await api.portfolios.updatePortfolio(id, {
            blocks: JSON.parse(JSON.stringify(localBlocks))
        });
        const updated = mapApiPortfolio(response.data.data);
        portfolioItem.value = updated;

        // Very important: update the initial snapshot to avoid "dirty" state
        initialSnapshot.value = JSON.stringify(localBlocks);

        // Also ensure localBlocks is synced if server modified anything (e.g. IDs)
        if (updated.blocks) {
            fillBlocks(updated.blocks);
        }
        saveStatus.value = { text: 'Cambios sincronizados', type: 'success' };
        alert.toast.success('Sincronizado', 'Cambios guardados correctamente.');
    } catch (error) {
        saveStatus.value = { text: 'Error al sincronizar', type: 'error' };
        alert.toast.error('Error', 'No se pudieron guardar los cambios.');
    }
}

// Auto-save logic
watch(localBlocks, () => {
    if (!portfolioItem.value) return;

    // Clear existing timeout
    if (saveTimeout) clearTimeout(saveTimeout);

    // Check if truly dirty (ignore during initial load)
    if (!isDirty.value) return;

    // Set status to pending
    saveStatus.value = { text: 'Pendiente de guardado...', type: 'pending' };

    // Debounce 2 seconds
    saveTimeout = setTimeout(() => {
        saveChanges();
    }, 2000);
}, { deep: true });

function handleAvatarUpdated(updatedData) {
    const updated = mapApiPortfolio(updatedData);
    portfolioItem.value = updated;
    fillBlocks(updated.blocks || {});
}

function handleJobsSynced(updatedData) {
    const updated = mapApiPortfolio(updatedData);
    portfolioItem.value = updated;
    fillBlocks(updated.blocks || {});
}

function goBack() {
    router.push('/dashboard/gestion-portafolios');
}

function openInfoModal() {
    isInfoModalOpen.value = true;
}

function closeInfoModal() {
    isInfoModalOpen.value = false;
}

function buildPublicUrl(token) {
    const origin = FRONTEND_BASE_URL || (typeof window !== 'undefined' ? window.location.origin : 'https://tu-dominio.com');
    return `${origin}/portafolio-usuario/${String(token || '______').toUpperCase()}`;
}

function handleBeforeUnload(event) {
    if (!portfolioItem.value || !isDirty.value) {
        return;
    }

    event.preventDefault();
    event.returnValue = '';
}

onMounted(() => {
    restoreActiveTab();
    loadCurrentPortfolio();
    window.addEventListener('beforeunload', handleBeforeUnload);
});

onBeforeRouteLeave(() => {
    localStorage.removeItem(TAB_STORAGE_KEY);
});

onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload);
});
</script>
