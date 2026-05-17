import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from app.core.settings import settings

logger = logging.getLogger("mail_sender")


def get_base_template(title: str, content_html: str) -> str:
    """
    Retorna la plantilla base (Layout) de correo electrónico con un diseño premium y responsivo.
    Envuelve cualquier contenido HTML específico manteniendo la consistencia de marca y diseño.
    """
    current_year = datetime.now().year
    app_name = settings.app_name
    if "${" in app_name:
        app_name = "Python Backend API"

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #f8fafc;
                color: #1e293b;
                -webkit-font-smoothing: antialiased;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background: #ffffff;
                border-radius: 16px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
                overflow: hidden;
                border: 1px solid #e2e8f0;
            }}
            .header {{
                background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
                padding: 40px 20px;
                text-align: center;
            }}
            .header h1 {{
                color: #ffffff;
                margin: 0;
                font-size: 26px;
                font-weight: 700;
                letter-spacing: -0.025em;
            }}
            .content {{
                padding: 40px 30px;
                line-height: 1.6;
            }}
            .footer {{
                background-color: #f8fafc;
                padding: 24px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
                font-size: 13px;
                color: #94a3b8;
            }}
            .footer a {{
                color: #4f46e5;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{app_name}</h1>
            </div>
            <div class="content">
                {content_html}
            </div>
            <div class="footer">
                <p>© {current_year} {app_name}. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_action_email_template(
    *,
    name: str,
    title: str,
    body_text: str,
    button_text: str | None = None,
    button_url: str | None = None,
    secondary_text: str | None = None,
) -> str:
    """
    Genera un correo de llamada a la acción totalmente personalizado e inyectado en la plantilla base.
    Perfecto para confirmaciones de cuenta, restablecimiento de contraseña y notificaciones.
    """
    button_html = ""
    if button_text and button_url:
        button_html = f"""
        <div style="text-align: center; margin: 35px 0;">
            <a href="{button_url}" style="background-color: #4f46e5; color: #ffffff !important; text-decoration: none; padding: 14px 30px; font-size: 16px; font-weight: 600; border-radius: 8px; display: inline-block; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2); transition: all 0.2s ease-in-out;">
                {button_text}
            </a>
        </div>
        <p style="color: #64748b; font-size: 14px; margin-top: 20px;">Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
        <p style="word-break: break-all; font-size: 14px; background-color: #f1f5f9; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; margin-bottom: 25px;">
            <a href="{button_url}" style="color: #4f46e5; text-decoration: none;">{button_url}</a>
        </p>
        """

    secondary_html = ""
    if secondary_text:
        secondary_html = f"""
        <p style="margin-top: 25px; margin-bottom: 0; font-size: 14px; color: #64748b; border-top: 1px dashed #e2e8f0; padding-top: 20px;">
            {secondary_text}
        </p>
        """

    content_html = f"""
    <h2 style="font-size: 20px; margin-top: 0; color: #0f172a; font-weight: 600;">¡Hola, {name}!</h2>
    <p style="color: #475569; font-size: 16px; margin-bottom: 20px;">{body_text}</p>
    {button_html}
    {secondary_html}
    """

    return get_base_template(title, content_html)


def send_email(*, to_email: str, subject: str, html_content: str) -> None:
    """Envía un correo electrónico utilizando la configuración SMTP en Settings."""
    try:
        from_name = settings.mail_from_name
        # Si tiene ${APP_NAME} por el parseo de Laravel de .env, lo limpiamos
        if "${" in from_name:
            from_name = settings.app_name

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{settings.mail_from_address}>"
        msg["To"] = to_email

        part = MIMEText(html_content, "html", "utf-8")
        msg.attach(part)

        logger.info(f"Conectando a servidor SMTP {settings.mail_host}:{settings.mail_port}...")
        
        # Conectar al host SMTP
        if settings.mail_port == 465:
            server = smtplib.SMTP_SSL(settings.mail_host, settings.mail_port, timeout=10)
        else:
            server = smtplib.SMTP(settings.mail_host, settings.mail_port, timeout=10)
            if settings.mail_port == 587:
                server.starttls()

        if settings.mail_username and settings.mail_password:
            logger.info("Autenticando credenciales SMTP...")
            server.login(settings.mail_username, settings.mail_password)

        logger.info(f"Enviando correo a {to_email} con asunto: '{subject}'...")
        server.sendmail(settings.mail_from_address, to_email, msg.as_string())
        server.quit()
        logger.info(f"Correo enviado correctamente a {to_email}")
    except Exception as e:
        logger.error(f"Error al enviar correo SMTP a {to_email}: {e}")
        raise e
