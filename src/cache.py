import valkey.asyncio as valkey

from src.config import settings

valkey_client = valkey.from_url(settings.VALKEY_URL, decode_responses=True)
