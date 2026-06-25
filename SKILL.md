---
name: hk-stock-dossier
description: 生成结构化港股尽职调查研报（Due Diligence Dossier），覆盖公司概览、行情估值、
  财务分析、分红股本、股东结构、内部人交易、机构观点、公司事件、风险提示九大维度。
  数据来源为 Pandadata 接口。TRIGGER when: user asks to generate a HK stock report,
  due diligence, dossier, 港股研报, 尽调报告.
metadata:
  organization: YOUR_USERNAME
  repository: hk-stock-dossier
  project_type: skill
  category: analytics
  tags:
  - hk-stock
  - dossier
  - pandadata
  - hong-kong
  platforms:
  - claude-code
  status: dev
---

# HK Stock Dossier — 港股尽职调查研报生成

生成结构化港股尽职调查研报，数据来源为 Pandadata 接口，输出为中文 Markdown 研报。

## 使用方式

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 Pandadata 凭证
export DEFAULT_USERNAME="your_username"
export DEFAULT_PASSWORD="your_password"

# 命令行生成研报
python -m hk_dossier 0700.HK --output report.md

# 简写代码（自动补齐 .HK）
python -m hk_dossier 0700
```

## 研报模板

```
# ${股票名称}（${股票代码}）港股尽职调查报告
## 一、公司概览
## 二、行情与估值
## 三、财务分析
## 四、分红与股本动作
## 五、股东结构
## 六、内部人交易
## 七、市场机构观点
## 八、公司事件日历
## 九、风险提示
```

## 数据模块映射

| 模块 | 功能 | Pandadata 接口 |
|------|------|----------------|
| `data/profile` | 公司基本信息 | `get_hk_detail` |
| `data/market` | 行情与价量 | `get_hk_daily`, `get_stock_pv_indicator` |
| `data/financials` | 财务三表与比率，行业中位数 | `get_fina_statement`, `get_stock_mktfin_indicator`, `get_stock_industry_median` |
| `data/dividends` | 分红与市场活动 | `get_stock_dividend_event`, `get_stock_market_event` |
| `data/shareholders` | 股东集中度与持股 | `get_stock_investor_concentration`, `get_stock_top20_concentration`, `get_stock_shareholder_holding` |
| `data/insider` | 内部人交易 | `get_stock_insider_trade` |
| `data/consensus` | 一致预期与建议 | `get_stock_ncycl_consensus`, `get_stock_recommendation_consensus` |
| `data/events` | 公司会议与 IR | `get_stock_meeting_event`, `get_stock_financial_event`, `get_stock_ir_event` |
