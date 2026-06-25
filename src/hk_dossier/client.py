"""Pandadata client helper — handles authentication and provides a clean API wrapper."""

import os
import logging
from typing import Any

import panda_data

logger = logging.getLogger(__name__)


class PandadataClient:
    """Thin wrapper around panda_data that auto-initializes on first use."""

    def __init__(self, username: str | None = None, password: str | None = None):
        self._username = username or os.environ.get("DEFAULT_USERNAME")
        self._password = password or os.environ.get("DEFAULT_PASSWORD")
        self._base_url = os.environ.get(
            "JAVA_SERVICE_BASE_URL", "http://pandadata.pandaaiquant.com"
        )
        self._initialized = False

    def ensure_init(self):
        """Initialize the Pandadata SDK if not already done."""
        if self._initialized:
            return
        if not self._username or not self._password:
            raise RuntimeError(
                "Pandadata credentials not configured. "
                "Set DEFAULT_USERNAME / DEFAULT_PASSWORD env vars "
                "or pass username/password to PandadataClient()."
            )
        panda_data.init_token(
            username=self._username,
            password=self._password,
            base_url=self._base_url,
        )
        self._initialized = True
        logger.info("Pandadata SDK initialized")

    def call(self, method: str, **kwargs) -> Any:
        """Call a panda_data.get_* method safely.

        Usage:
            client.call("get_hk_detail", symbol=["0700.HK"])
        """
        self.ensure_init()
        func = getattr(panda_data, method, None)
        if func is None:
            raise ValueError(f"Unknown Pandadata method: {method}")
        logger.debug("Calling %s with kwargs=%s", method, kwargs)
        try:
            result = func(**kwargs)
            return result
        except Exception as e:
            logger.error("Pandadata call %s failed: %s", method, e)
            raise
