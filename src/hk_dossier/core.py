"""Core orchestrator — 协调各数据模块，生成完整研报."""

import logging
from typing import Any

from hk_dossier.client import PandadataClient
from hk_dossier.data import (
    profile as mod_profile,
    market as mod_market,
    financials as mod_financials,
    dividends as mod_dividends,
    shareholders as mod_shareholders,
    insider as mod_insider,
    consensus as mod_consensus,
    events as mod_events,
)
from hk_dossier.renderer import render_dossier

logger = logging.getLogger(__name__)


def generate_dossier(
    symbol: str, client: PandadataClient | None = None, **kwargs
) -> str:
    """Generate a complete HK stock dossier for the given symbol.

    Args:
        symbol: HK stock symbol (e.g., "0700.HK")
        client: Optional PandadataClient instance. Creates a new one if not provided.

    Returns:
        Markdown-formatted dossier string.
    """
    if client is None:
        client = PandadataClient()

    logger.info("Generating dossier for %s...", symbol)

    # Normalize symbol
    symbol = symbol.upper().strip()
    if not symbol.endswith(".HK"):
        symbol = symbol + ".HK"
        logger.info("Normalized symbol to %s", symbol)

    # Fetch all data in parallel (sequential calls but logically parallel)
    logger.info("Fetching company profile...")
    profile = mod_profile.get_profile(client, symbol)

    logger.info("Fetching market data...")
    market = mod_market.get_price_data(client, symbol)

    logger.info("Fetching financials...")
    financials = mod_financials.get_financials(client, symbol)

    logger.info("Fetching dividends and market events...")
    dividends = mod_dividends.get_dividends(client, symbol)

    logger.info("Fetching shareholder structure...")
    shareholders = mod_shareholders.get_shareholders(client, symbol)

    logger.info("Fetching insider trades...")
    insider = mod_insider.get_insider_trades(client, symbol)

    logger.info("Fetching analyst consensus...")
    consensus = mod_consensus.get_consensus(client, symbol)

    logger.info("Fetching corporate events...")
    events = mod_events.get_events(client, symbol)

    # Render
    logger.info("Rendering dossier...")
    report = render_dossier(
        symbol=symbol,
        profile=profile,
        market=market,
        financials=financials,
        dividends=dividends,
        shareholders=shareholders,
        insider=insider,
        consensus=consensus,
        events=events,
    )

    logger.info("Dossier generation complete for %s", symbol)
    return report
