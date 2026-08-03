"""
Alert manager for Telegram, Discord, and Slack notifications.
"""

from typing import Optional
import asyncio

import aiohttp

from config.settings import Config
from monitoring.logger import log


class AlertManager:
    """Sends alerts to configured channels."""

    def __init__(
        self,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        discord_webhook: Optional[str] = None,
        slack_webhook: Optional[str] = None,
    ):
        self.telegram_token = telegram_token or Config.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = telegram_chat_id or Config.TELEGRAM_CHAT_ID
        self.discord_webhook = discord_webhook or Config.DISCORD_WEBHOOK_URL
        self.slack_webhook = slack_webhook or Config.SLACK_WEBHOOK_URL
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self._session

    async def send_alert(self, title: str, message: str, level: str = "INFO"):
        """Send alert to all configured channels."""
        full_message = f"[{level}] {title}\n{message}"

        tasks = []
        if self.telegram_token and self.telegram_chat_id:
            tasks.append(self._send_telegram(full_message))
        if self.discord_webhook:
            tasks.append(self._send_discord(title, message, level))
        if self.slack_webhook:
            tasks.append(self._send_slack(full_message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        log.info(f"Alert sent: {title} - {message}")

    async def _send_telegram(self, message: str):
        """Send Telegram message."""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML",
            }
            session = await self._get_session()
            async with session.post(url, json=payload) as resp:
                resp.raise_for_status()
        except Exception as e:
            log.warning(f"Telegram alert failed: {e}")

    async def _send_discord(self, title: str, message: str, level: str):
        """Send Discord webhook message."""
        try:
            color_map = {"INFO": 3447003, "WARNING": 16776960, "ERROR": 15158332, "CRITICAL": 10038562}
            payload = {
                "embeds": [
                    {
                        "title": title,
                        "description": message,
                        "color": color_map.get(level, 3447003),
                    }
                ]
            }
            session = await self._get_session()
            async with session.post(self.discord_webhook, json=payload) as resp:
                resp.raise_for_status()
        except Exception as e:
            log.warning(f"Discord alert failed: {e}")

    async def _send_slack(self, message: str):
        """Send Slack webhook message."""
        try:
            payload = {"text": message}
            session = await self._get_session()
            async with session.post(self.slack_webhook, json=payload) as resp:
                resp.raise_for_status()
        except Exception as e:
            log.warning(f"Slack alert failed: {e}")

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
