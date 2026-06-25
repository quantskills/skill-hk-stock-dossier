"""Markdown renderer — 将数据渲染为结构化中文研报."""

import logging
from typing import Any

from hk_dossier.utils import (
    fmt_date,
    fmt_market_cap,
    fmt_number,
    fmt_pct,
    fmt_shares,
)

logger = logging.getLogger(__name__)


def render_dossier(
    symbol: str,
    profile: dict,
    market: dict,
    financials: dict,
    dividends: dict,
    shareholders: dict,
    insider: dict,
    consensus: dict,
    events: dict,
) -> str:
    """Render all collected data into a complete Markdown dossier."""
    lines: list[str] = []

    name = profile.get("cn_name") or profile.get("name", symbol)
    _add(lines, f"# {name}（{symbol}）港股尽职调查报告")
    _add(lines, f"> 报告生成时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
    _add(lines, "> **免责声明：** 本报告仅供参考，不构成投资建议。数据来源为 Pandadata。")
    _add(lines, "")

    # ── Section 1: Company Profile ──
    _render_profile(lines, profile)

    # ── Section 2: Market & Valuation ──
    _render_market(lines, market)

    # ── Section 3: Financial Analysis ──
    _render_financials(lines, financials, market)

    # ── Section 4: Dividends & Capital Actions ──
    _render_dividends(lines, dividends)

    # ── Section 5: Shareholder Structure ──
    _render_shareholders(lines, shareholders)

    # ── Section 6: Insider Trading ──
    _render_insider(lines, insider)

    # ── Section 7: Analyst Consensus ──
    _render_consensus(lines, consensus, market)

    # ── Section 8: Corporate Events ──
    _render_events(lines, events)

    # ── Section 9: Risk Notes ──
    _render_risks(lines, profile, market, financials, shareholders)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------


def _render_profile(lines: list[str], p: dict):
    _add(lines, "## 一、公司概览")
    _add(lines, "")
    _add(lines, f"- **股票代码：** {p.get('symbol', '')}")
    _add(lines, f"- **公司名称：** {p.get('name', '')}")
    _add(lines, f"- **中文名称：** {p.get('cn_name', '')}")
    _add(lines, f"- **上市日期：** {fmt_date(p.get('listed_date'))}")
    _add(lines, f"- **成立日期：** {fmt_date(p.get('incorp_date'))}")
    _add(lines, f"- **上市板块：** {p.get('board_type', '—')}")
    _add(lines, f"- **经济 sector：** {p.get('economic_sector', '—')}")
    _add(lines, f"- **业务 sector：** {p.get('business_sector', '—')}")
    _add(lines, f"- **行业组：** {p.get('industry_group', '—')}")
    _add(lines, f"- **ISIN：** {p.get('isin_code', '—')}")
    _add(lines, f"- **交易代码：** {p.get('trading_code', '—')}")
    _add(lines, f"- **每手股数：** {p.get('min_order_amount', '—')}")
    _add(lines, f"- **交易状态：** {'在交易' if p.get('asset_state') == 'AC' else p.get('asset_state', '—')}")
    _add(lines, f"- **总部地址：** {p.get('office_address', '')}，{p.get('office_city', '')}，{p.get('office_country', '')}")
    if p.get("website"):
        _add(lines, f"- **公司网站：** [{p['website']}]({p['website']})")
    if "error" in p:
        _add(lines, f"\n> ⚠️ 数据获取异常：{p['error']}")
    _add(lines, "")


def _render_market(lines: list[str], m: dict):
    _add(lines, "## 二、行情与估值")
    _add(lines, "")

    pv = m.get("pv_indicators", {}) or {}
    summary = m.get("summary", {}) or {}

    # Price stats
    _add(lines, "### 最新行情")
    _add(lines, "")
    close = summary.get("latest_close") or pv.get("close")
    close_date = summary.get("latest_date") or pv.get("close_date")
    _add(lines, f"- **最新收盘价：** {fmt_number(close)} {pv.get('close_currency', '')}（{fmt_date(close_date)}）")
    _add(lines, f"- **开盘价：** {fmt_number(summary.get('open'))}")
    _add(lines, f"- **最高价：** {fmt_number(summary.get('high'))}")
    _add(lines, f"- **最低价：** {fmt_number(summary.get('low'))}")
    _add(lines, f"- **成交量：** {fmt_shares(summary.get('volume'))}")
    _add(lines, f"- **VWAP：** {fmt_number(summary.get('vwap'))}")
    _add(lines, "")

    # Market cap & 52-week range
    _add(lines, "### 市值与价量指标")
    _add(lines, "")
    _add(lines, f"- **总市值：** {fmt_market_cap(pv.get('market_cap'), pv.get('market_cap_currency', 'HKD'))}")
    _add(lines, f"- **5年 Beta：** {fmt_number(pv.get('beta_5y'), 4)}")
    _add(lines, f"- **52周最高：** {fmt_number(pv.get('high_52w'))}（{fmt_date(pv.get('high_52w_date'))}）")
    _add(lines, f"- **52周最低：** {fmt_number(pv.get('low_52w'))}（{fmt_date(pv.get('low_52w_date'))}）")
    _add(lines, "")

    # Returns
    _add(lines, "### 阶段涨跌幅")
    _add(lines, "")
    _add(lines, "| 区间 | 涨幅 | 相对基准涨幅 |")
    _add(lines, "|------|------|------------|")
    _add(lines, f"| 1日 | {fmt_pct(pv.get('return_1d'))} | — |")
    _add(lines, f"| 5日 | {fmt_pct(pv.get('return_5d'))} | — |")
    _add(lines, f"| 年初至今 | {fmt_pct(pv.get('return_ytd'))} | {fmt_pct(pv.get('rel_return_ytd'))} |")
    _add(lines, f"| 13周 | {fmt_pct(pv.get('return_13w'))} | {fmt_pct(pv.get('rel_return_13w'))} |")
    _add(lines, f"| 26周 | {fmt_pct(pv.get('return_26w'))} | {fmt_pct(pv.get('rel_return_26w'))} |")
    _add(lines, f"| 52周 | {fmt_pct(pv.get('return_52w'))} | {fmt_pct(pv.get('rel_return_52w'))} |")
    _add(lines, "")

    # Volume
    _add(lines, "### 成交量")
    _add(lines, "")
    _add(lines, f"- **日均成交量（10日）：** {fmt_shares(summary.get('avg_volume_10d') or pv.get('avg_vol_10d'))}")
    _add(lines, f"- **日均成交量（90日）：** {fmt_shares(summary.get('avg_volume_90d') or pv.get('avg_vol_90d'))}")
    _add(lines, f"- **日均成交额（3月）：** {fmt_number(pv.get('avg_val_3m'))}")
    _add(lines, "")


def _render_financials(lines: list[str], fin: dict, market: dict):
    _add(lines, "## 三、财务分析")
    _add(lines, "")

    mkt = fin.get("mktfin", {}) or {}
    ind = fin.get("industry_median", {}) or {}
    stmt = fin.get("statement")

    _add(lines, "### 关键估值指标")
    _add(lines, "")
    _add(lines, "| 指标 | 公司 | 行业中位数 |")
    _add(lines, "|------|------|-----------|")

    def row(label: str, co_val: Any, ind_val: Any = None) -> str:
        co = fmt_number(co_val) if co_val is not None else "—"
        iv = fmt_number(ind_val) if ind_val is not None else "—"
        return f"| {label} | {co} | {iv} |"

    _add(lines, row("PE (TTM)", mkt.get("pe_ttm"), ind.get("imed_pe_ttm")))
    _add(lines, row("PB", mkt.get("pb"), ind.get("imed_pb_ttm")))
    _add(lines, row("EV/EBITDA (TTM)", mkt.get("ev_to_ebitda"), None))
    _add(lines, row("股息率", mkt.get("dividend_yield"), ind.get("imed_gross_div_yield_ttm")))
    _add(lines, "")

    # EV
    if mkt.get("ev"):
        _add(lines, f"- **企业价值 (EV)：** {fmt_market_cap(mkt.get('ev'), mkt.get('ev_currency', 'HKD'))}")
        _add(lines, "")

    # Per-share / employee metrics (HK mktfin limited)
    _add(lines, "### 人均效能")
    _add(lines, "")
    _add(lines, f"- **人均销售额 (TTM)：** {fmt_number(mkt.get('sales_per_emp'))}")
    _add(lines, f"- **人均净利润 (TTM)：** {fmt_number(mkt.get('net_inc_per_emp'))}")
    _add(lines, "")

    # Industry context
    if ind.get("industry_name"):
        _add(lines, f"> 📊 行业对比基准：**{ind['industry_name']}** 行业中位数")
        _add(lines, "")

    # Financial statement summary
    if stmt is not None and not stmt.empty:
        _add(lines, "### 财务报表摘要（最新季度）")
        _add(lines, "")
        _add(lines, "```")
        _add(lines, f"报告期：{stmt.iloc[0].get('fy_period', '—')}")
        _add(lines, f"总资产：{fmt_market_cap(stmt.iloc[0].get('bs_asset_accruals'))}")
        _add(lines, f"总负债：{fmt_market_cap(stmt.iloc[0].get('bs_liab_accruals'))}")
        _add(lines, f"营业收入：{fmt_market_cap(stmt.iloc[0].get('is_oper_rev_accruals'))}")
        _add(lines, f"营业利润：{fmt_market_cap(stmt.iloc[0].get('is_oper_pl_accruals'))}")
        _add(lines, f"净利润（归母）：{fmt_market_cap(stmt.iloc[0].get('is_net_pl_cont_op_parent_comp_accruals'))}")
        _add(lines, f"经营现金流：{fmt_market_cap(stmt.iloc[0].get('cf_oper_net_cash_flow_accruals'))}")
        _add(lines, "```")
        _add(lines, "")


def _render_dividends(lines: list[str], d: dict):
    _add(lines, "## 四、分红与股本动作")
    _add(lines, "")

    divs = d.get("dividend_events", [])
    mkt_events = d.get("market_events", [])

    if divs:
        _add(lines, "### 分红历史")
        _add(lines, "")
        _add(lines, "| 公告日期 | 除权日 | 类型 | 每股金额 | 币种 | 事件 |")
        _add(lines, "|----------|--------|------|---------|------|------|")
        for ev in divs[:10]:
            _add(
                lines,
                "| {} | {} | {} | {} | {} | {} |".format(
                    fmt_date(ev.get("publish_date")),
                    fmt_date(ev.get("excute_date")),
                    ev.get("event_type", ""),
                    fmt_number(ev.get("number")),
                    ev.get("currency", ""),
                    str(ev.get("event", ""))[:60],
                ),
            )
        _add(lines, "")
    else:
        _add(lines, "_暂无分红数据。_")
        _add(lines, "")

    if mkt_events:
        _add(lines, "### 市场活动（配售/增发/锁定期等）")
        _add(lines, "")
        _add(lines, "| 公告日期 | 事件 |")
        _add(lines, "|----------|------|")
        for ev in mkt_events[:10]:
            _add(
                lines,
                "| {} | {} |".format(
                    fmt_date(ev.get("info_date")),
                    str(ev.get("event", ""))[:80],
                ),
            )
        _add(lines, "")


def _render_shareholders(lines: list[str], sh: dict):
    _add(lines, "## 五、股东结构")
    _add(lines, "")

    conc = sh.get("concentration", {}) or {}
    top20 = sh.get("top20", {}) or {}
    holdings = sh.get("holdings", []) or []

    if conc:
        _add(lines, "### 投资者集中度")
        _add(lines, "")
        _add(lines, f"- **投资者总数：** {fmt_number(conc.get('total_investors'), 0)}")
        _add(lines, f"- **机构持仓占流通比：** {fmt_pct(conc.get('investor_outstanding_ratio'))}")
        _add(lines, f"- **机构总持股：** {fmt_shares(conc.get('total_sharehold'))}")
        _add(lines, f"- **机构持股市值：** {fmt_market_cap(conc.get('total_holdings_value'), conc.get('currency', 'HKD'))}")
        _add(lines, "")

    if top20:
        _add(lines, "### 前20大投资者")
        _add(lines, "")
        _add(lines, f"- **前 {fmt_number(top20.get('top_investors_num', 0), 0)} 大投资者持股占流通比：** {fmt_pct(top20.get('investor_outstanding_ratio'))}")
        _add(lines, f"- **持股合计：** {fmt_shares(top20.get('sharehold'))}")
        _add(lines, f"- **持股市值：** {fmt_market_cap(top20.get('holdings_value'), top20.get('currency', 'HKD'))}")
        _add(lines, "")

    if holdings:
        _add(lines, "### 主要股东持股报告")
        _add(lines, "")
        _add(lines, "| 报告日期 | 股东名称 | 类别 | 持股数 | 占流通比 | 变动 | 变动比例 |")
        _add(lines, "|----------|----------|------|--------|---------|------|---------|")
        for h in holdings[:10]:
            _add(
                lines,
                "| {} | {} | {} | {} | {} | {} | {} |".format(
                    fmt_date(h.get("holding_date")),
                    str(h.get("investor_name", ""))[:25],
                    h.get("investor_category", ""),
                    fmt_shares(h.get("sharehold")),
                    fmt_pct(h.get("outstanding_ratio")),
                    fmt_shares(h.get("sharehold_change")),
                    fmt_pct(h.get("sharehold_change_ratio")),
                ),
            )
        _add(lines, "")


def _render_insider(lines: list[str], ins: dict):
    _add(lines, "## 六、内部人交易")
    _add(lines, "")

    trades = ins.get("trades", [])
    summary = ins.get("summary", {}) or {}

    if summary:
        _add(lines, f"- **交易总次数：** {fmt_number(summary.get('total_transactions', 0), 0)}")
        _add(lines, f"- **买入次数：** {summary.get('buy_count', 0)}")
        _add(lines, f"- **卖出次数：** {summary.get('sell_count', 0)}")
        _add(lines, f"- **净成交量：** {fmt_shares(summary.get('net_volume'))}")
        _add(lines, "")

    if trades:
        _add(lines, "### 近期交易记录")
        _add(lines, "")
        _add(lines, "| 消息日期 | 交易日期 | 内部人 | 类型 | 调整后股数 | 交易价格 | 占流通比 |")
        _add(lines, "|----------|----------|--------|------|-----------|---------|---------|")
        for t in trades[:10]:
            _add(
                lines,
                "| {} | {} | {} | {} | {} | {} | {} |".format(
                    fmt_date(t.get("info_date")),
                    fmt_date(t.get("transaction_date")),
                    str(t.get("investor_name", ""))[:20],
                    t.get("transaction_type", ""),
                    fmt_shares(t.get("adjusted_trade_shares")),
                    fmt_number(t.get("transaction_price")),
                    fmt_pct(t.get("trade_outstanding_ratio")),
                ),
            )
        _add(lines, "")
    else:
        _add(lines, "_暂无内部人交易数据。_")
        _add(lines, "")


def _render_consensus(lines: list[str], con: dict, market: dict):
    _add(lines, "## 七、市场机构观点")
    _add(lines, "")

    nc = con.get("ncycl_consensus", {}) or {}
    rec = con.get("recommendation", {}) or {}

    if nc:
        _add(lines, "### 一致预期（目标价）")
        _add(lines, "")
        _add(lines, f"- **机构覆盖数：** {int(nc.get('num_estimates', 0) or 0)}")
        _add(lines, f"- **目标均价：** {fmt_number(nc.get('mean_target_price'))} {nc.get('currency', '')}")
        _add(lines, f"- **目标中位数：** {fmt_number(nc.get('median_target_price'))} {nc.get('currency', '')}")
        _add(lines, f"- **目标最高：** {fmt_number(nc.get('high_target_price'))} {nc.get('currency', '')}")
        _add(lines, f"- **目标最低：** {fmt_number(nc.get('low_target_price'))} {nc.get('currency', '')}")

        # Upside/downside
        close = market.get("pv_indicators", {}).get("close") or market.get("summary", {}).get("latest_close")
        if close and nc.get("mean_target_price"):
            try:
                upside = (float(nc["mean_target_price"]) / float(close) - 1) * 100
                _add(lines, f"- **潜在涨跌幅：** {fmt_pct(upside)}（相对目标均价）")
            except (ValueError, TypeError):
                pass
        _add(lines, "")

    if rec:
        _add(lines, "### 买卖建议分布")
        _add(lines, "")
        total = rec.get("total_recommendations", 0) or 0
        _add(lines, f"- **总建议数：** {int(total)}")
        buy = int(rec.get("strong_buy_count", 0) or 0)
        buy += int(rec.get("buy_count", 0) or 0)
        _add(lines, f"- **买入（含强力买入）：** {buy}")
        _add(lines, f"- **持有：** {int(rec.get('hold_count', 0) or 0)}")
        sell = int(rec.get("strong_sell_count", 0) or 0)
        sell += int(rec.get("sell_count", 0) or 0)
        _add(lines, f"- **卖出（含强力卖出）：** {sell}")

        if total:
            buy_pct = buy / total * 100
            _add(lines, f"- **买入占比：** {fmt_pct(buy_pct)}")
        _add(lines, "")

    if not nc and not rec:
        _add(lines, "_暂无机构覆盖数据。_")
        _add(lines, "")


def _render_events(lines: list[str], ev: dict):
    _add(lines, "## 八、公司事件日历")
    _add(lines, "")

    meetings = ev.get("meeting_events", [])
    fin_events = ev.get("financial_events", [])
    ir_events = ev.get("ir_events", [])

    if meetings:
        _add(lines, "### 公司会议")
        _add(lines, "")
        _add(lines, "| 公告日期 | 会议日期 | 会议类型 | 事件 |")
        _add(lines, "|----------|----------|----------|------|")
        for m in meetings[:5]:
            _add(
                lines,
                "| {} | {} | {} | {} |".format(
                    fmt_date(m.get("info_date")),
                    fmt_date(m.get("start_date")),
                    m.get("event_type", ""),
                    str(m.get("event", ""))[:60],
                ),
            )
        _add(lines, "")

    if fin_events:
        _add(lines, "### 财务披露")
        _add(lines, "")
        _add(lines, "| 公告日期 | 事件 |")
        _add(lines, "|----------|------|")
        for f in fin_events[:5]:
            _add(
                lines,
                "| {} | {} |".format(
                    fmt_date(f.get("info_date")),
                    str(f.get("event", ""))[:80],
                ),
            )
        _add(lines, "")

    if ir_events:
        _add(lines, "### 投资者关系活动")
        _add(lines, "")
        _add(lines, "| 公告日期 | 事件 |")
        _add(lines, "|----------|------|")
        for ir in ir_events[:5]:
            _add(
                lines,
                "| {} | {} |".format(
                    fmt_date(ir.get("info_date")),
                    str(ir.get("event", ""))[:80],
                ),
            )
        _add(lines, "")

    if not meetings and not fin_events and not ir_events:
        _add(lines, "_暂无公司事件数据。_")
        _add(lines, "")


def _render_risks(lines: list[str], profile: dict, market: dict, financials: dict, shareholders: dict):
    _add(lines, "## 九、风险提示")
    _add(lines, "")
    risks: list[str] = []

    # Market risk
    pv = market.get("pv_indicators", {}) or {}
    if pv.get("beta_5y") is not None:
        try:
            beta = float(pv["beta_5y"])
            if beta > 1.2:
                risks.append(f"- **高 Beta 风险：** 股票 Beta 为 {fmt_number(beta, 4)}，波动性显著高于市场，市场下行时跌幅可能更大。")
            elif beta > 0.8:
                risks.append(f"- **中等 Beta 风险：** 股票 Beta 为 {fmt_number(beta, 4)}，波动性与市场基本同步。")
        except (ValueError, TypeError):
            pass

    # Valuation risk
    mkt = financials.get("mktfin", {}) or {}
    pe = mkt.get("pe_ttm")
    ind = financials.get("industry_median", {}) or {}
    if pe is not None and ind.get("imed_pe_ttm") is not None:
        try:
            if float(pe) > float(ind["imed_pe_ttm"]) * 2:
                risks.append(f"- **估值偏高风险：** PE（TTM）为 {fmt_number(pe)}，显著高于行业中位数 {fmt_number(ind['imed_pe_ttm'])}。")
        except (ValueError, TypeError):
            pass

    # EV/EBITDA based risk (proxy for leverage)
    if mkt.get("ev_to_ebitda") is not None:
        try:
            ev_ebitda = float(mkt["ev_to_ebitda"])
            if ev_ebitda > 30:
                risks.append(f"- **估值偏高风险：** EV/EBITDA 为 {fmt_number(ev_ebitda)}，估值水平较高。")
        except (ValueError, TypeError):
            pass

    # Liquidity risk
    summary = market.get("summary", {}) or {}
    if summary.get("avg_volume_90d") is not None:
        try:
            if float(summary["avg_volume_90d"]) < 100000:
                risks.append("- **流动性风险：** 近90日日均成交量较低，可能存在流动性不足的风险。")
        except (ValueError, TypeError):
            pass

    # Shareholder concentration risk
    conc = shareholders.get("concentration", {}) or {}
    if conc.get("investor_outstanding_ratio") is not None:
        try:
            ratio = float(conc["investor_outstanding_ratio"])
            if ratio > 80:
                risks.append(
                    f"- **持股集中度风险：** 机构持仓占流通股 {fmt_pct(ratio)}，筹码高度集中，需关注大额减持风险。"
                )
        except (ValueError, TypeError):
            pass

    if not risks:
        risks.append("_基于当前数据未识别出显著风险。_")
    _add(lines, "\n".join(risks))
    _add(lines, "")

    # Disclaimer
    _add(lines, "---")
    _add(lines, "")
    _add(lines, "> **免责声明：** 本报告由自动化工具生成，所有数据来源于 Pandadata 接口。")
    _add(lines, "> 报告中的分析和判断仅供参考，不构成任何投资建议。投资者应独立判断并承担投资风险。")
    _add(lines, "> 报告生成时间：" + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"))


def _add(lines: list[str], text: str = ""):
    lines.append(text)
