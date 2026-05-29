<template>
    <div id="app" class="portfolio-page" :data-theme="theme" :data-color-theme="palette">
        <LandingNav />

        <main class="portfolio-wrapper">
            <PortfolioProfileMainBlock 
                :profile="profile" 
                :avatar-url="avatarUrl" 
                @download-cv="downloadResume"
            />
            <!-- <PortfolioHeroBlock /> -->

            <section class="masonry-grid">
                <PortfolioAboutBlock :profile="profile" :metrics="metrics" />
                <PortfolioSkillsBlock :skills="skills" />
                <PortfolioTechnologiesBlock :technologies="technologies" />
                <PortfolioProjectsBlock :projects="projects" />
                <PortfolioJobsBlock :jobs="jobs" />
                <PortfolioEducationBlock :education="education" />
                <PortfolioCoursesBlock :courses="courses" />
                <PortfolioSocialBlock :links="socialLinks" />
                <PortfolioContactBlock 
                    :email="contactEmail" 
                    :phone="contactPhone"
                    :whatsapp="contactWhatsApp"
                    @open-contact="openContactModal" 
                    @download-cv="downloadResume"
                />
            </section>
        </main>

        <ModalForm
            :isVisible="isContactModalOpen"
            title="Enviar mensaje"
            :loading="isSendingContact"
            size="md"
            :columns="4"
            submitLabel="Enviar mensaje"
            :fields="contactFields"
            :modelValue="contactForm"
            :errors="contactErrors"
            @close="closeContactModal"
            @submit="submitContactForm"
        >
            <template #header-icon>
                <Icon name="mail" :size="18" />
            </template>

            <template #default>
                <div class="contact-modal-intro col-span-full">
                    Completa tus datos y enviaremos una copia de este mensaje a tu correo.
                </div>

                <ModalField
                    label="Mensaje"
                    :required="true"
                    :span="4"
                    :error="contactErrors.message?.[0]"
                >
                    <textarea
                        v-model.trim="contactForm.message"
                        rows="5"
                        maxlength="3000"
                        class="contact-modal-message"
                        placeholder="Escribe tu mensaje"
                        required
                    ></textarea>
                </ModalField>
            </template>
        </ModalForm>

        <FloatingAppearanceControls />

        <!-- Premium CV Generation Loading Overlay -->
        <Transition name="fade-overlay">
            <div v-if="isGeneratingCV" class="cv-loading-overlay">
                <div class="cv-loading-content">
                    <div class="cv-loading-visual">
                        <div class="cv-loading-circle"></div>
                        <Icon name="file-text" :size="32" class="cv-loading-icon" />
                    </div>
                    <div class="cv-loading-text">
                        <h3>Generando CV Premium</h3>
                        <p>Estamos procesando tus datos, iconos y QRs...</p>
                    </div>
                    <div class="cv-loading-progress-container">
                        <div class="cv-loading-progress-bar"></div>
                    </div>
                </div>
            </div>
        </Transition>
    </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { api } from '@/services/api';
import { useAlert } from '@/composables/useAlert';
import PortfolioAboutBlock from './portafolio_components/PortfolioAboutBlock.vue';
import PortfolioContactBlock from './portafolio_components/PortfolioContactBlock.vue';
import PortfolioSocialBlock from './portafolio_components/PortfolioSocialBlock.vue';
import PortfolioCoursesBlock from './portafolio_components/PortfolioCoursesBlock.vue';
import PortfolioEducationBlock from './portafolio_components/PortfolioEducationBlock.vue';
import PortfolioHeroBlock from './portafolio_components/PortfolioHeroBlock.vue';
import PortfolioJobsBlock from './portafolio_components/PortfolioJobsBlock.vue';
import PortfolioProjectsBlock from './portafolio_components/PortfolioProjectsBlock.vue';
import PortfolioProfileMainBlock from './portafolio_components/PortfolioProfileMainBlock.vue';
import PortfolioSkillsBlock from './portafolio_components/PortfolioSkillsBlock.vue';
import PortfolioTechnologiesBlock from './portafolio_components/PortfolioTechnologiesBlock.vue';
import LandingNav from './components/LandingNav.vue';
import FloatingAppearanceControls from './components/FloatingAppearanceControls.vue';
import Icon from '@/components/Icon.vue';
import ModalForm from '@/views/private/admin/components/ModalForm.vue';
import ModalField from '@/views/private/admin/components/ModalField.vue';
import { useTheme } from '@/composables/useTheme';
import { useColorPalette } from '@/composables/useColorPalette';
import { generateResumePDF } from './services/PortfolioResumeService';

const { theme } = useTheme();
const { palette } = useColorPalette();

const route = useRoute();
const alert = useAlert();
const selectedPortfolio = ref(null);
const isContactModalOpen = ref(false);
const isSendingContact = ref(false);
const isGeneratingCV = ref(false);
const contactErrors = reactive({});
const contactForm = reactive({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
});
const contactFields = [
    {
        key: 'name',
        label: 'Nombre completo',
        type: 'text',
        placeholder: 'Ej. Juan Perez',
        required: true,
        span: 4,
    },
    {
        key: 'email',
        label: 'Correo Electronico',
        type: 'email',
        placeholder: 'ejemplo@correo.com',
        required: true,
        span: 4,
    },
    {
        key: 'phone',
        label: 'Telefono',
        type: 'text',
        placeholder: 'Opcional',
        required: false,
        span: 2,
    },
    {
        key: 'subject',
        label: 'Asunto',
        type: 'text',
        placeholder: 'Motivo del contacto',
        required: true,
        span: 2,
    }
];

const fallbackBlocks = {
    profile: {
        name: 'Tu Nombre Apellido',
        role: 'Desarrollador Full Stack',
        summary: 'Desarrollador orientado a producto, enfocado en crear soluciones robustas que combinan rendimiento, claridad visual y buena experiencia de usuario.'
    },
    avatarUrl: 'https://i.pravatar.cc/420?img=68',
    metrics: [
        { value: '6+', label: 'anos de experiencia', icon_uuid: null, icon_data: null },
        { value: '25+', label: 'proyectos entregados', icon_uuid: null, icon_data: null },
        { value: '100%', label: 'enfoque en calidad', icon_uuid: null, icon_data: null }
    ],
    skills: [
        { label: 'Arquitectura modular' },
        { label: 'Resolucion de problemas' },
        { label: 'Comunicacion con negocio' },
        { label: 'Liderazgo tecnico' },
        { label: 'Testing y mejora continua' },
        { label: 'Optimizacion de rendimiento' }
    ],
    technologies: [
        { label: 'Laravel' },
        { label: 'PHP 8.4' },
        { label: 'Vue 3' },
        { label: 'Vite' },
        { label: 'Sass' },
        { label: 'MySQL' },
        { label: 'Docker' },
        { label: 'Nginx' },
        { label: 'JWT' },
        { label: 'Git' }
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
            ]
        }
    ],
    jobs: [
        { id: 1, role: 'Senior Software Developer', company: 'Tech Studio', period: '2023 - Actualidad' },
        { id: 2, role: 'Full Stack Developer', company: 'Digital Factory', period: '2020 - 2023' },
        { id: 3, role: 'Backend Developer', company: 'Solutions Lab', period: '2018 - 2020' }
    ],
    education: [
        { id: 1, title: 'Ingenieria en Sistemas', institution: 'Universidad Tecnologica', period: '2014 - 2018' },
        { id: 2, title: 'Diplomado en Arquitectura de Software', institution: 'Academia Tech', period: '2019' }
    ],
    courses: [
        { id: 1, title: 'Escalabilidad y performance web', provider: 'Plataforma Online Pro' },
        { id: 2, title: 'Clean Architecture aplicada', provider: 'Code Academy' },
        { id: 3, title: 'Diseno UX para desarrolladores', provider: 'UX Institute' }
    ],
    contact: {
        email: 'tuemail@dominio.com',
        phone: '+52 123 456 7890',
        whatsapp: '+52 123 456 7890',
    },
    social: [
        { name: 'LinkedIn', handle: 'in/tu-perfil', url: 'https://linkedin.com/in/tu-perfil', icon: 'linkedin' },
        { name: 'GitHub', handle: '@tu-usuario', url: 'https://github.com/tu-usuario', icon: 'github' },
        { name: 'WhatsApp', handle: 'Chat directo', url: 'https://wa.me/521234567890', icon: 'whatsapp' }
    ]
};

const currentBlocks = computed(() => {
    const blocks = selectedPortfolio.value?.blocks || {};
    return {
        ...fallbackBlocks,
        ...blocks,
        profile: {
            ...fallbackBlocks.profile,
            ...(blocks.profile || {})
        },
        contact: {
            ...fallbackBlocks.contact,
            ...(blocks.contact || {})
        }
    };
});

const profile = computed(() => currentBlocks.value.profile);
const avatarUrl = computed(() => currentBlocks.value.avatarUrl || fallbackBlocks.avatarUrl);
const metrics = computed(() => {
    const dynamicMetrics = currentBlocks.value.metrics;
    const filtered = Array.isArray(dynamicMetrics)
        ? dynamicMetrics.filter(m => m.is_active !== false)
        : [];
        
    return filtered.length > 0 ? filtered : fallbackBlocks.metrics;
});

const skills = computed(() => {
    const source = Array.isArray(currentBlocks.value.skills) ? currentBlocks.value.skills : [];
    const list = source
        .filter(item => item.is_active !== false);

    return list.length > 0
        ? list
        : fallbackBlocks.skills;
});

const technologies = computed(() => {
    const source = Array.isArray(currentBlocks.value.technologies) ? currentBlocks.value.technologies : [];
    const list = source
        .filter(item => item.is_active !== false);

    return list.length > 0
        ? list
        : fallbackBlocks.technologies;
});

const projects = computed(() => Array.isArray(currentBlocks.value.projects) && currentBlocks.value.projects.length > 0
    ? currentBlocks.value.projects
    : fallbackBlocks.projects);

const jobs = computed(() => Array.isArray(currentBlocks.value.jobs) && currentBlocks.value.jobs.length > 0
    ? currentBlocks.value.jobs
    : fallbackBlocks.jobs);

const education = computed(() => {
    const list = Array.isArray(currentBlocks.value.education) && currentBlocks.value.education.length > 0
        ? [...currentBlocks.value.education]
        : [...fallbackBlocks.education];
    
    return list.sort((a, b) => {
        const dateA = a.startDate || '';
        const dateB = b.startDate || '';
        return dateA.localeCompare(dateB);
    });
});

const courses = computed(() => Array.isArray(currentBlocks.value.courses) && currentBlocks.value.courses.length > 0
    ? currentBlocks.value.courses
    : fallbackBlocks.courses);

const contactEmail = computed(() => currentBlocks.value.contact?.email || fallbackBlocks.contact.email);
const contactPhone = computed(() => currentBlocks.value.contact?.phone || fallbackBlocks.contact.phone);
const contactWhatsApp = computed(() => currentBlocks.value.contact?.whatsapp || fallbackBlocks.contact.whatsapp);
const socialLinks = computed(() => {
    const dynamicSocial = currentBlocks.value.social;
    const filtered = Array.isArray(dynamicSocial) 
        ? dynamicSocial.filter(link => link.is_active !== false)
        : [];
        
    return filtered.length > 0
        ? filtered
        : fallbackBlocks.social;
});

function resetContactErrors() {
    Object.keys(contactErrors).forEach(key => {
        delete contactErrors[key];
    });
}

function resetContactForm() {
    contactForm.name = '';
    contactForm.email = '';
    contactForm.phone = '';
    contactForm.subject = '';
    contactForm.message = '';
    resetContactErrors();
}

function openContactModal() {
    if (!selectedPortfolio.value?.token) {
        alert.toast.error('Error', 'No hay un portafolio activo para enviar mensaje.');
        return;
    }

    isContactModalOpen.value = true;
    resetContactErrors();
}

function closeContactModal() {
    if (isSendingContact.value) {
        return;
    }
    isContactModalOpen.value = false;
}

async function submitContactForm() {
    const token = String(selectedPortfolio.value?.token || '').toUpperCase().trim();
    if (!token) {
        alert.toast.error('Error', 'No se pudo identificar el portafolio.');
        return;
    }

    resetContactErrors();
    isSendingContact.value = true;

    try {
        await api.portfolios.sendPublicContact(token, {
            name: contactForm.name,
            email: contactForm.email,
            phone: contactForm.phone,
            subject: contactForm.subject,
            message: contactForm.message,
        });

        alert.toast.success('Mensaje enviado', 'Se envio el correo al propietario y una copia a tu email.');
        isContactModalOpen.value = false;
        resetContactForm();
    } catch (error) {
        const errors = error?.response?.data?.errors || {};
        Object.entries(errors).forEach(([field, messages]) => {
            const message = Array.isArray(messages) ? messages[0] : String(messages || 'Dato invalido.');
            contactErrors[field] = [message];
        });

        if (Object.keys(errors).length === 0) {
            alert.toast.error('Error', error?.response?.data?.message || 'No se pudo enviar el mensaje.');
        }
    } finally {
        isSendingContact.value = false;
    }
}

async function downloadResume() {
    isGeneratingCV.value = true;
    try {
        await generateResumePDF({
            profile: profile.value,
            jobs: jobs.value,
            education: education.value,
            skills: skills.value,
            technologies: technologies.value,
            projects: projects.value,
            courses: courses.value,
            contactEmail: contactEmail.value,
            phone: contactPhone.value,
            whatsapp: contactWhatsApp.value,
            social: socialLinks.value,
            avatarUrl: avatarUrl.value,
            palette: palette.value
        });
    } catch (error) {
        console.error('Error al generar el PDF:', error);
        alert.toast.error('Error', 'No se pudo generar el CV. Por favor intenta de nuevo.');
    } finally {
        setTimeout(() => {
            isGeneratingCV.value = false;
        }, 500); // Pequeño delay para suavizar la salida
    }
}

async function loadPortfolio() {
    const tokenParam = String(route.params.token || '').toUpperCase().trim();

    try {
        const response = tokenParam
            ? await api.portfolios.getPublicPortfolio(tokenParam)
            : await api.portfolios.getDefaultPublicPortfolio();

        selectedPortfolio.value = response?.data?.data || null;
    } catch {
        selectedPortfolio.value = null;
    }
}

watch(() => route.params.token, async () => {
    await loadPortfolio();
});

onMounted(async () => {
    await loadPortfolio();
});
</script>

<style scoped>
.portfolio-page {
    min-height: 100vh;
    color: var(--text-primary);
    background: var(--bg-secondary);
    position: relative;
    overflow-x: hidden;
    transition: background 0.5s ease, color 0.5s ease;
}

/* Aero Plasma Background */
.portfolio-page::before,
.portfolio-page::after {
    content: '';
    position: fixed;
    width: 60vw;
    height: 60vw;
    border-radius: 50%;
    filter: blur(120px);
    z-index: 0;
    pointer-events: none;
    opacity: 0.15;
    animation: aero-plasma 25s infinite alternate ease-in-out;
}

.portfolio-page::before {
    top: -10%;
    left: -10%;
    background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
}

.portfolio-page::after {
    bottom: -10%;
    right: -10%;
    background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
    animation-delay: -5s;
}

.portfolio-wrapper {
    position: relative;
    z-index: 1;
    width: min(1200px, 92%);
    margin: 0 auto;
    padding: 3rem 0 6rem;
}

.contact-modal-intro {
    margin-bottom: 0.5rem;
    color: var(--text-muted);
    font-size: 0.88rem;
}

.list-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    list-style: none;
    padding: 0;
}

.list-grid li {
    padding: 8px 16px;
    border-radius: 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 0.88rem;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    gap: 8px;
}

.skill-icon {
    opacity: 0.8;
}

.contact-modal-message {
    min-height: 140px;
    resize: vertical;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 12px;
    color: var(--text-primary);
    transition: all 0.3s;

    &:focus {
        border-color: var(--primary);
        outline: none;
        box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary), transparent 90%);
    }
}

:deep(.modal-overlay) {
    z-index: 3200;
    background: rgba(8, 9, 12, 0.7);
    backdrop-filter: blur(12px);
}

:deep(.modal-container) {
    background: color-mix(in srgb, var(--bg-secondary), transparent 4%) !important;
    backdrop-filter: blur(24px);
    border: 1px solid var(--border-color) !important;
    box-shadow: 
        0 40px 100px var(--shadow-color),
        inset 0 0 40px rgba(255, 255, 255, 0.02) !important;
}

:deep(.modal-header) {
    border-bottom: 1px solid var(--border-color) !important;
    background: rgba(255, 255, 255, 0.02);
}

:deep(.modal-title) {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
}

:deep(.close-btn) {
    color: var(--text-secondary) !important;
    &:hover {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
    }
}

.masonry-grid {
    display: grid;
    grid-template-columns: repeat(12, minmax(0, 1fr));
    gap: 1.25rem;
}

:deep(.about-block) { grid-column: span 7; }
:deep(.skills-block) { grid-column: span 5; }
:deep(.tech-block) { grid-column: span 4; }
:deep(.projects-block) { grid-column: span 8; }
:deep(.social-block) { grid-column: span 6; }
:deep(.jobs-block),
:deep(.education-block) { grid-column: span 6; }
:deep(.courses-block) { grid-column: span 6; }
:deep(.contact-block) { grid-column: span 6; }

:deep(.reveal) {
    animation: aero-reveal 0.85s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}

:deep(.reveal-delay-1) { animation-delay: 0.1s; }
:deep(.reveal-delay-2) { animation-delay: 0.2s; }
:deep(.reveal-delay-3) { animation-delay: 0.3s; }
:deep(.reveal-delay-4) { animation-delay: 0.4s; }

/* Modal Cards Detail Styles */
:deep(.card-main) {
    flex: 1;
    padding: 1.5rem 2rem;
    overflow-y: auto;
    max-height: 520px;
    scrollbar-width: thin;
    scrollbar-color: var(--primary) rgba(255, 255, 255, 0.05);

    &::-webkit-scrollbar {
        width: 6px;
    }
    &::-webkit-scrollbar-track {
        background: transparent;
    }
    &::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 10px;
    }
}

:deep(.card-description-scroll) {
    margin-top: 10px;
}

:deep(.info-panel) {
    margin-top: 1.5rem;
}

:deep(.panel-label) {
    display: block;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

:deep(.card-tags) {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

:deep(.card-tag) {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 4px 12px;
    background: color-mix(in srgb, var(--primary), transparent 92%);
    color: var(--text-secondary);
    border: 1px solid color-mix(in srgb, var(--primary), transparent 80%);
    border-radius: 8px;
    transition: all 0.2s;

    &:hover {
        background: var(--primary);
        color: var(--bg-primary);
        border-color: var(--primary);
        transform: translateY(-1px);
    }
}

@media (max-width: 1024px) {
    :deep(.about-block),
    :deep(.skills-block),
    :deep(.tech-block),
    :deep(.projects-block),
    :deep(.jobs-block),
    :deep(.education-block),
    :deep(.courses-block),
    :deep(.social-block),
    :deep(.contact-block) {
        grid-column: span 12;
    }
}

/* --- CV Loading Overlay Styles --- */
.cv-loading-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: color-mix(in srgb, var(--bg-primary), transparent 20%);
    backdrop-filter: blur(16px) saturate(180%);
    display: flex;
    align-items: center;
    justify-content: center;
}

.cv-loading-content {
    background: var(--bg-secondary);
    padding: 3rem;
    border-radius: 32px;
    border: 1px solid var(--border-color);
    box-shadow: 
        0 40px 100px var(--shadow-color),
        inset 0 0 40px rgba(255, 255, 255, 0.02);
    text-align: center;
    max-width: 440px;
    width: 90%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
}

.cv-loading-visual {
    position: relative;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.cv-loading-circle {
    position: absolute;
    inset: 0;
    border: 3px solid color-mix(in srgb, var(--primary), transparent 85%);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: cv-spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.cv-loading-icon {
    color: var(--primary);
    filter: drop-shadow(0 0 10px color-mix(in srgb, var(--primary), transparent 60%));
}

.cv-loading-text h3 {
    font-size: 1.5rem;
    font-weight: 850;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.cv-loading-text p {
    color: var(--text-muted);
    font-size: 0.95rem;
    line-height: 1.5;
}

.cv-loading-progress-container {
    width: 100%;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 10px;
    overflow: hidden;
    margin-top: 0.5rem;
}

.cv-loading-progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    width: 40%;
    border-radius: 10px;
    animation: cv-progress 2s infinite ease-in-out;
}

@keyframes cv-spin {
    to { transform: rotate(360deg); }
}

@keyframes cv-progress {
    0% { transform: translateX(-100%); width: 30%; }
    50% { transform: translateX(100%); width: 60%; }
    100% { transform: translateX(300%); width: 30%; }
}

.fade-overlay-enter-active,
.fade-overlay-leave-active {
    transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.fade-overlay-enter-from,
.fade-overlay-leave-to {
    opacity: 0;
    transform: scale(0.95);
    backdrop-filter: blur(0px);
}

@media (max-width: 768px) {
    .portfolio-wrapper {
        padding-top: 1.5rem;
    }
}
</style>
