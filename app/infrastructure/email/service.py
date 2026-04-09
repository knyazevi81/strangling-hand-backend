import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.infrastructure.config.config import Settings
from app.infrastructure.logging.adapter import get_logger

logger = get_logger(__name__)


def _build_html(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#F0F4FF;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F0F4FF;padding:40px 16px;">
    <tr><td align="center">
      <table width="100%" style="max-width:520px;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #B5D4F4;">
        <tr>
          <td style="background:#185FA5;padding:24px 32px;">
            <div style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">Savebit</div>
            <div style="font-size:13px;color:#B5D4F4;margin-top:2px;">Управление подключениями</div>
          </td>
        </tr>
        <tr>
          <td style="padding:32px;">
            {body_html}
          </td>
        </tr>
        <tr>
          <td style="padding:16px 32px;background:#F0F4FF;border-top:1px solid #E6F1FB;">
            <div style="font-size:12px;color:#378ADD;">Savebit · admin@savebit.ru</div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


class EmailService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send(self, to: str | list[str], subject: str, html: str) -> None:
        if not self._settings.EMAIL_ENABLED:
            logger.info("email.disabled", to=to, subject=subject)
            return

        recipients = [to] if isinstance(to, str) else to
        if not recipients:
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._settings.EMAIL_FROM
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=self._settings.SMTP_HOST,
                port=self._settings.SMTP_PORT,
                username=self._settings.SMTP_USER,
                password=self._settings.SMTP_PASS.get_secret_value(),
                use_tls=True,
            )
            logger.info("email.sent", to=recipients, subject=subject)
        except Exception as exc:
            logger.error("email.failed", error=str(exc), to=recipients)

    # ── Шаблоны автоотбивок ────────────────────────────────────────────────

    async def send_account_activated(self, to: str) -> None:
        body = """
        <h2 style="margin:0 0 12px;font-size:20px;color:#042C53;">Аккаунт активирован</h2>
        <p style="color:#378ADD;line-height:1.6;margin:0 0 20px;">
          Ваш аккаунт в Savebit был активирован администратором.<br>
          Теперь вы можете войти и просматривать свои подключения.
        </p>
        <a href="https://net.savebit.ru" style="display:inline-block;background:#185FA5;color:#ffffff;text-decoration:none;padding:12px 24px;border-radius:10px;font-size:14px;font-weight:500;">Войти в Savebit</a>
        """
        await self.send(to, "Ваш аккаунт активирован — Savebit", _build_html("Аккаунт активирован", body))

    async def send_connection_added(self, to: str, ip: str, port: str) -> None:
        body = f"""
        <h2 style="margin:0 0 12px;font-size:20px;color:#042C53;">Новое подключение добавлено</h2>
        <p style="color:#378ADD;line-height:1.6;margin:0 0 20px;">
          Администратор добавил вам новое подключение.
        </p>
        <div style="background:#F0F4FF;border:1px solid #B5D4F4;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
          <div style="font-size:13px;color:#185FA5;margin-bottom:6px;font-weight:500;">Данные подключения</div>
          <div style="font-family:monospace;font-size:14px;color:#042C53;">
            IP: {ip}<br>
            Порт: {port}
          </div>
        </div>
        <p style="color:#378ADD;font-size:13px;margin:0;">
          Войдите в Savebit чтобы скопировать ссылку подключения.
        </p>
        """
        await self.send(to, "Новое подключение — Savebit", _build_html("Новое подключение", body))

    async def send_connection_updated(self, to: str, ip: str, port: str) -> None:
        body = f"""
        <h2 style="margin:0 0 12px;font-size:20px;color:#042C53;">Подключение обновлено</h2>
        <p style="color:#378ADD;line-height:1.6;margin:0 0 20px;">
          Данные одного из ваших подключений были обновлены администратором.
        </p>
        <div style="background:#F0F4FF;border:1px solid #B5D4F4;border-radius:12px;padding:16px 20px;margin-bottom:20px;">
          <div style="font-size:13px;color:#185FA5;margin-bottom:6px;font-weight:500;">Новые данные</div>
          <div style="font-family:monospace;font-size:14px;color:#042C53;">
            IP: {ip}<br>
            Порт: {port}
          </div>
        </div>
        <p style="color:#378ADD;font-size:13px;margin:0;">
          Обновите ссылку подключения в приложении.
        </p>
        """
        await self.send(to, "Подключение обновлено — Savebit", _build_html("Подключение обновлено", body))

    async def send_password_changed(self, to: str) -> None:
        body = """
        <h2 style="margin:0 0 12px;font-size:20px;color:#042C53;">Пароль изменён</h2>
        <p style="color:#378ADD;line-height:1.6;margin:0 0 20px;">
          Пароль от вашего аккаунта Savebit был изменён.<br>
          Если это были не вы — немедленно свяжитесь с администратором.
        </p>
        """
        await self.send(to, "Пароль изменён — Savebit", _build_html("Пароль изменён", body))

    async def send_custom(self, to: str | list[str], subject: str, message: str) -> None:
        body = f"""
        <h2 style="margin:0 0 12px;font-size:20px;color:#042C53;">{subject}</h2>
        <div style="color:#185FA5;line-height:1.7;white-space:pre-wrap;">{message}</div>
        """
        await self.send(to, f"{subject} — Savebit", _build_html(subject, body))
