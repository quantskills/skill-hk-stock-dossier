"""Financial data — 财务三表、关键比率与行业中位数.

注意：港股的 get_stock_mktfin_indicator 使用 curr_* 前缀字段名（与 A 股的 mktfin_* 不同）。
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_financials(client: Any, symbol: str) -> dict[str, Any]:
    """Fetch financial statements and market financial indicators.

    Returns dict with:
      - statement: latest financial statement DF (may be None if API unavailable)
      - mktfin: market financial indicator ratios (HK naming: curr_pe_dil_excl_ttm, etc.)
      - industry_median: industry median ratios for comparison
    """
    result: dict[str, Any] = {}

    # --- Financial statements ---
    # Note: HK fina_statement API doesn't support interimType parameter
    try:
        df = client.call(
            "get_fina_statement",
            symbol=symbol,
            start_quarter="2023q1",
            end_quarter="2026q4",
            is_latest=True,
            fields=[],
        )
        if df is not None and not df.empty:
            result["statement"] = df
        else:
            result["statement"] = None
    except Exception as e:
        logger.warning("Failed to fetch financial statement for %s: %s", symbol, e)
        result["statement"] = None

    # --- Market financial indicators (HK naming: curr_* prefix) ---
    try:
        mkt_df = client.call(
            "get_stock_mktfin_indicator", symbol=[symbol], fields=[]
        )
        if mkt_df is not None and not mkt_df.empty:
            row = mkt_df.iloc[0]
            result["mktfin"] = {
                # Valuation
                "pe_ttm": row.get("curr_pe_dil_excl_ttm"),
                "pe_basic": row.get("curr_pe_basic_excl"),
                "pb": row.get("curr_pb"),
                "ps": row.get("curr_price_to_rev_pershr_ttm"),
                "pcf": row.get("curr_price_to_cf_pershr_ttm"),
                "dividend_yield": row.get("curr_div_yld_gross_issue_ratio"),
                # Per share
                "eps": row.get("curr_pe_dil_excl"),
                "bps": row.get("curr_pb"),  # PB proxy
                "fcf_ps": row.get("curr_price_to_fcf_pershr_ttm"),
                "sales_per_emp": row.get("curr_sales_per_emp_ttm"),
                # EV
                "ev": row.get("curr_ev"),
                "ev_currency": row.get("curr_ev_currency"),
                "ev_to_ebitda": row.get("curr_ev_to_ebitda_ttm"),
                # Ratios that may not be in HK mktfin
                "net_inc_per_emp": row.get("curr_net_inc_per_emp_ttm"),
            }
        else:
            result["mktfin"] = {}
    except Exception as e:
        logger.warning("Failed to fetch mktfin indicators for %s: %s", symbol, e)
        result["mktfin"] = {}

    # --- Industry median ---
    try:
        ind_df = client.call(
            "get_stock_industry_median", symbol=[symbol], fields=[]
        )
        if ind_df is not None and not ind_df.empty:
            row = ind_df.iloc[0]
            result["industry_median"] = {
                "industry_name": row.get("industry_name"),
                "imed_pe_ttm": row.get("imed_pe_ttm"),
                "imed_pb_ttm": row.get("imed_pb_ttm"),
                "imed_ps_ttm": row.get("imed_ps_ttm"),
                "imed_roe_avg_common_ttm": row.get("imed_roe_avg_common_ttm"),
                "imed_pretax_roa_ratio_ttm": row.get("imed_pretax_roa_ratio_ttm"),
                "imed_gross_div_yield_ttm": row.get("imed_gross_div_yield_ttm"),
                "imed_gross_margin_ratio_fye_mid": row.get(
                    "imed_gross_margin_ratio_fye_mid"
                ),
                "imed_net_margin_ratio_fye_mid": row.get(
                    "imed_net_margin_ratio_fye_mid"
                ),
                "imed_ebitda_margin_ratio_fye_mid": row.get(
                    "imed_ebitda_margin_ratio_fye_mid"
                ),
                "imed_debt_to_equity_ratio_fye_mid": row.get(
                    "imed_debt_to_equity_ratio_fye_mid"
                ),
                "imed_curr_ratio_fye_mid": row.get("imed_curr_ratio_fye_mid"),
                "imed_asset_turnover_ttm": row.get("imed_asset_turnover_ttm"),
            }
        else:
            result["industry_median"] = {}
    except Exception as e:
        logger.warning("Failed to fetch industry median for %s: %s", symbol, e)
        result["industry_median"] = {}

    return result
