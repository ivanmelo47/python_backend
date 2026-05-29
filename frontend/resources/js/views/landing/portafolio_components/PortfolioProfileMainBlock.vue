<template>
    <section class="profile-main-block reveal">
        <div class="profile-main-content">
            <figure class="avatar-wrap">
                <img
                    id="portfolio-avatar-img"
                    :src="avatarUrl"
                    :alt="`Foto de perfil de ${profile.name}`"
                    loading="lazy"
                    decoding="async"
                />
            </figure>

            <div class="profile-main-text">
                <p class="eyebrow">Perfil principal</p>
                <h1>{{ profile.name }}</h1>
                <h2>{{ profile.role }}</h2>
                <p>{{ profile.summary }}</p>

                <div class="profile-main-actions">
                    <button type="button" class="landing-cta" @click="scrollTo('proyectos')">Ver proyectos</button>
                    <button type="button" class="outline-btn" @click="scrollTo('contacto')">Contactar</button>
                    <button type="button" class="btn-cv" @click="$emit('download-cv')">Descargar CV</button>
                </div>
            </div>
        </div>
    </section>
</template>

<script setup>
const emit = defineEmits(['download-cv']);
defineProps({
    profile: {
        type: Object,
        required: true
    },
    avatarUrl: {
        type: String,
        required: true
    }
});

function scrollTo(id) {
    const el = document.getElementById(id);
    if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
    }
}
</script>

<style scoped>
.profile-main-block {
    position: relative;
    padding: 32px;
    margin-bottom: 24px;
    border-radius: 28px;
    background: var(--bg-primary);
    backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--border-color);
    box-shadow: 
        0 44px 80px var(--shadow-color),
        inset 0 0 20px rgba(255, 255, 255, 0.02);
    overflow: hidden;
}

.profile-main-block::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at top left, color-mix(in srgb, var(--primary), transparent 90%), transparent 60%);
    pointer-events: none;
}

.profile-main-content {
    display: grid;
    grid-template-columns: 240px 1fr;
    gap: 40px;
    align-items: center;
}

.avatar-wrap {
    position: relative;
    margin: 0;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    padding: 8px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    box-shadow: 0 20px 40px var(--shadow-color);
}

.avatar-wrap img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
    display: block;
    border: 4px solid var(--bg-primary);
}

.eyebrow {
    margin: 0;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--primary);
    opacity: 0.9;
}

h1 {
    margin: 8px 0 0;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text-primary);
}

h2 {
    margin: 4px 0 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--primary);
}

.profile-main-text > p {
    margin: 20px 0 0;
    font-size: 1.1rem;
    line-height: 1.6;
    color: var(--text-secondary);
    max-width: 600px;
    white-space: pre-wrap;
}

.profile-main-actions {
    margin-top: 32px;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.landing-cta {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 12px 24px;
    border-radius: 12px;
    font-weight: 700;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: all 0.3s;
}

.landing-cta:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px color-mix(in srgb, var(--primary), transparent 80%);
}

.outline-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    font-weight: 600;
    color: var(--text-primary);
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: 0.8rem;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: all 0.25s ease;
}

.outline-btn:hover {
    transform: translateY(-2px);
    border-color: var(--primary);
    color: var(--primary-dark);
}

.btn-cv {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    font-weight: 700;
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid var(--primary);
    border-radius: 0.8rem;
    padding: 0.75rem 1.25rem;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
}

.btn-cv:hover {
    background: var(--primary);
    color: white;
    transform: translateY(-3px);
    box-shadow: 0 10px 25px color-mix(in srgb, var(--primary), transparent 70%);
}

@media (max-width: 780px) {
    .profile-main-content {
        grid-template-columns: 1fr;
        justify-items: center;
        text-align: center;
    }

    .profile-main-text > p {
        max-width: 48ch;
    }

    .profile-main-actions {
        justify-content: center;
    }
}
</style>
