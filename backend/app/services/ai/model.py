"""Optional OpenAI-compatible provider. Credentials only come from the server."""

from app.core.config import settings
import httpx


async def complete(system, message):
    key = settings.ai_api_key
    if not key:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            settings.ai_base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": settings.ai_model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
