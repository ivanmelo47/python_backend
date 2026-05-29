<template>
    <section class="hero-block block-glow reveal">
        <p class="badge">Software Developer</p>
        <h1>
            Portafolio modular con enfoque en
            <span>impacto, diseno y escalabilidad</span>
        </h1>
        <p>
            Estructura pensada para crecer desde el panel de gestion: cada bloque se puede alimentar
            con datos dinamicos de proyectos, skills, experiencia, educacion y cursos.
        </p>
        <div class="hero-actions">
            <a href="#proyectos" class="landing-cta">Explorar proyectos</a>
            <a href="#contacto" class="outline-btn">Contactar</a>
        </div>
    </section>
</template>

<style scoped>
.hero-block {
    position: relative;
    padding: clamp(32px, 5vh, 64px);
    margin-bottom: 24px;
    border-radius: 28px;
    background: var(--bg-primary);
    backdrop-filter: blur(24px);
    border: 1px solid var(--border-color);
    overflow: hidden;
    box-shadow: 0 40px 100px var(--shadow-color);
}

.hero-block::before {
    content: '';
    position: absolute;
    width: 300px;
    height: 300px;
    top: -150px;
    right: -100px;
    background: radial-gradient(circle, color-mix(in srgb, var(--primary), transparent 90%) 0%, transparent 70%);
    pointer-events: none;
}

.badge {
    display: inline-flex;
    padding: 6px 16px;
    border-radius: 99px;
    background: color-mix(in srgb, var(--primary), transparent 90%);
    border: 1px solid color-mix(in srgb, var(--primary), transparent 80%);
    color: var(--primary);
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 24px;
    animation: glow-pulse 3s infinite;
}

@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 10px transparent; }
    50% { box-shadow: 0 0 20px color-mix(in srgb, var(--primary), transparent 80%); }
}

h1 {
    margin: 0;
    font-size: clamp(2rem, 5vw, 4rem);
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-primary);

    span {
        display: block;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
}

p {
    max-width: 600px;
    margin: 24px 0 0;
    font-size: 1.1rem;
    line-height: 1.6;
    color: var(--text-secondary);
}

.hero-actions {
    margin-top: 40px;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.landing-cta {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 14px 28px;
    border-radius: 14px;
    font-weight: 700;
    text-decoration: none;
    transition: all 0.3s;
    box-shadow: 0 10px 20px color-mix(in srgb, var(--primary), transparent 80%);

    &:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 30px color-mix(in srgb, var(--primary), transparent 70%);
    }
}

.outline-btn {
    padding: 14px 28px;
    border-radius: 14px;
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s;
    background: var(--bg-primary);

    &:hover {
        background: var(--bg-secondary);
        border-color: var(--primary);
        transform: translateY(-3px);
    }
}

@media (max-width: 768px) {
    .hero-block {
        padding: 40px 24px;
        text-align: center;
    }

    .hero-actions {
        justify-content: center;
    }

    p {
        margin-inline: auto;
    }
}
</style>
