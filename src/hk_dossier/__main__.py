"""CLI entry point — python -m hk_dossier <SYMBOL>"""

import argparse
import logging
import sys

from hk_dossier.client import PandadataClient
from hk_dossier.core import generate_dossier


def main():
    parser = argparse.ArgumentParser(
        description="港股尽职调查研报生成工具 (HK Stock Dossier)"
    )
    parser.add_argument(
        "symbol",
        type=str,
        help="港股代码，如 0700.HK 或 0700（自动补齐 .HK 后缀）",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出文件路径（默认输出到 stdout）",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细日志输出",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    symbol = args.symbol.upper().strip()
    if not symbol.endswith(".HK"):
        symbol = symbol + ".HK"
        print(f"ℹ️  自动补齐后缀: {args.symbol} → {symbol}", file=sys.stderr)

    try:
        client = PandadataClient()
        report = generate_dossier(symbol, client=client)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        print("\n请按以下方式配置 Pandadata 凭证：", file=sys.stderr)
        print("  export DEFAULT_USERNAME='your_username'", file=sys.stderr)
        print("  export DEFAULT_PASSWORD='your_password'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 生成研报失败: {e}", file=sys.stderr)
        logger = logging.getLogger(__name__)
        logger.debug("Detail", exc_info=True)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ 研报已保存到: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
