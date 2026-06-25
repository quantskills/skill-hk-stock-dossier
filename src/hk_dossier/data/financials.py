"""Financial data — 财务三表、关键比率与行业中位数."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Key financial statement fields of interest
_FINA_FIELDS = [
    "symbol",
    "bs_asset_accruals",
    "bs_liab_accruals",
    "bs_equity_par_accruals",
    "bs_curr_asset_accruals",
    "bs_curr_liab_accruals",
    "bs_noncurr_asset_accruals",
    "bs_noncurr_liab_accruals",
    "bs_inventory_accruals",
    "bs_accounts_receivable_accruals",
    "bs_accounts_payable_accruals",
    "bs_other_curr_asset_accruals",
    "bs_other_curr_liab_accruals",
    "bs_cash_accruals",
    "bs_ppe_accruals",
    "bs_intang_asset_accruals",
    "bs_shortterm_borrow_accruals",
    "bs_longterm_borrow_accruals",
    "bs_notes_receivable_accruals",
    "bs_notes_payable_accruals",
    "is_oper_rev_accruals",
    "is_oper_cost_accruals",
    "is_gross_profit_accruals",
    "is_selling_dist_exp_accruals",
    "is_admin_exp_accruals",
    "is_oper_pl_accruals",
    "is_net_pl_cont_op_accruals",
    "is_net_pl_cont_op_parent_comp_accruals",
    "is_oper_rev_less_oper_cost_accruals",
    "is_finance_cost_accruals",
    "is_inv_income_accruals",
    "is_non_oper_income_accruals",
    "is_non_oper_exp_accruals",
    "is_income_tax_accruals",
    "cf_oper_net_cash_flow_accruals",
    "cf_inv_net_cash_flow_accruals",
    "cf_fin_net_cash_flow_accruals",
    "cf_net_cash_flow_accruals",
    "cf_oper_net_cash_flow_per_share",
    "cf_free_cash_flow",
]


def get_financials(client: Any, symbol: str) -> dict[str, Any]:
    """Fetch financial statements and market financial indicators.

    Returns dict with:
      - fina_statement: latest financial statement data
      - mktfin: market financial indicator ratios
      - industry_median: industry median ratios for comparison
    """
    result: dict[str, Any] = {}

    # --- Financial statements ---
    try:
        df = client.call(
            "get_fina_statement",
            symbol=symbol,
            start_quarter="2023q1",
            end_quarter="2026q4",
            is_latest=True,
            interimType="cumulative",
            fields=_FINA_FIELDS,
        )
        if df is not None and not df.empty:
            result["statement"] = df
        else:
            result["statement"] = None
    except Exception as e:
        logger.warning("Failed to fetch financial statement for %s: %s", symbol, e)
        result["statement"] = None

    # --- Market financial indicators ---
    try:
        mkt_df = client.call(
            "get_stock_mktfin_indicator", symbol=[symbol], fields=[]
        )
        if mkt_df is not None and not mkt_df.empty:
            row = mkt_df.iloc[0]
            result["mktfin"] = {
                "pe_ttm": row.get("mktfin_pe_ttm"),
                "pb_lf": row.get("mktfin_pb_lf"),
                "ps_ttm": row.get("mktfin_ps_ttm"),
                "pcf_ttm": row.get("mktfin_pcf_ttm"),
                "dividend_yield": row.get("mktfin_dividend_yield"),
                "eps_ttm": row.get("mktfin_eps_ttm"),
                "bps_lf": row.get("mktfin_bps_lf"),
                "roe_ttm": row.get("mktfin_roe_ttm"),
                "roa_ttm": row.get("mktfin_roa_ttm"),
                "gross_margin": row.get("mktfin_gross_margin"),
                "net_margin": row.get("mktfin_net_margin"),
                "ebitda_margin": row.get("mktfin_ebitda_margin"),
                "total_asset_turnover": row.get("mktfin_total_asset_turnover"),
                "debt_to_equity": row.get("mktfin_debt_to_equity"),
                "current_ratio": row.get("mktfin_current_ratio"),
                "free_cash_flow": row.get("mktfin_free_cash_flow"),
                "free_cash_flow_ps": row.get("mktfin_free_cash_flow_ps"),
                "revenue_ttm": row.get("mktfin_revenue_ttm"),
                "net_income_ttm": row.get("mktfin_net_income_ttm"),
                "revenue_growth": row.get("mktfin_revenue_growth"),
                "net_income_growth": row.get("mktfin_net_income_growth"),
                "total_assets": row.get("mktfin_total_assets"),
                "total_liabilities": row.get("mktfin_total_liabilities"),
                "total_equity": row.get("mktfin_total_equity"),
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
                "imed_gross_margin_ratio_fye_mid": row.get("imed_gross_margin_ratio_fye_mid"),
                "imed_net_margin_ratio_fye_mid": row.get("imed_net_margin_ratio_fye_mid"),
                "imed_ebitda_margin_ratio_fye_mid": row.get("imed_ebitda_margin_ratio_fye_mid"),
                "imed_debt_to_equity_ratio_fye_mid": row.get("imed_debt_to_equity_ratio_fye_mid"),
                "imed_curr_ratio_fye_mid": row.get("imed_curr_ratio_fye_mid"),
                "imed_asset_turnover_ttm": row.get("imed_asset_turnover_ttm"),
                "imed_revenue_growth": None,
            }
        else:
            result["industry_median"] = {}
    except Exception as e:
        logger.warning("Failed to fetch industry median for %s: %s", symbol, e)
        result["industry_median"] = {}

    return result
