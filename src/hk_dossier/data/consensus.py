"""Analyst consensus — 一致预期与买卖建议."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_consensus(client: Any, symbol: str) -> dict[str, Any]:
    """Fetch analyst consensus data.

    Returns:
      - ncycl_consensus: non-cyclical indicator consensus
      - recommendation: analyst recommendation consensus
    """
    result: dict[str, Any] = {}

    # --- Non-cyclical consensus ---
    try:
        nc_df = client.call(
            "get_stock_ncycl_consensus", symbol=[symbol], fields=[]
        )
        if nc_df is not None and not nc_df.empty:
            row = nc_df.iloc[0]
            result["ncycl_consensus"] = {
                "mean_target_price": row.get("mean_target_price"),
                "median_target_price": row.get("median_target_price"),
                "high_target_price": row.get("high_target_price"),
                "low_target_price": row.get("low_target_price"),
                "num_estimates": row.get("num_estimates"),
                "currency": row.get("currency"),
                "standard_deviation": row.get("standard_deviation"),
            }
        else:
            result["ncycl_consensus"] = {}
    except Exception as e:
        logger.warning("Failed to fetch consensus for %s: %s", symbol, e)
        result["ncycl_consensus"] = {}

    # --- Recommendation consensus ---
    try:
        rec_df = client.call(
            "get_stock_recommendation_consensus", symbol=[symbol], fields=[]
        )
        if rec_df is not None and not rec_df.empty:
            row = rec_df.iloc[0]
            result["recommendation"] = {
                "buy_count": row.get("buy_count"),
                "outperform_count": row.get("outperform_count"),
                "hold_count": row.get("hold_count"),
                "underperform_count": row.get("underperform_count"),
                "sell_count": row.get("sell_count"),
                "total_recommendations": row.get("total_recommendations"),
                "mean_recommendation_score": row.get("mean_recommendation_score"),
            }
        else:
            result["recommendation"] = {}
    except Exception as e:
        logger.warning("Failed to fetch recommendation for %s: %s", symbol, e)
        result["recommendation"] = {}

    return result
