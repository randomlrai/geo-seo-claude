#!/usr/bin/env python3
"""
geo-seo-claude: AI-powered GEO (Generative Engine Optimization) toolkit
using Claude as the backbone for content analysis and optimization.

This tool helps optimize content for AI-powered search engines and
generative AI platforms like ChatGPT, Claude, Perplexity, and others.
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.runner import AgentRunner
from utils.config import load_config
from utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="geo-seo-claude",
        description="GEO (Generative Engine Optimization) toolkit powered by Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --agent content --url https://example.com/page
  python main.py --agent schema --file ./content.html
  python main.py --agent platform-analysis --url https://example.com
  python main.py --agent ai-visibility --url https://example.com --output report.json
        """,
    )

    parser.add_argument(
        "--agent",
        type=str,
        choices=["content", "schema", "platform-analysis", "ai-visibility", "all"],
        default="all",
        help="Which GEO agent to run (default: all)",
    )

    parser.add_argument(
        "--url",
        type=str,
        help="Target URL to analyze",
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Path to local HTML/text file to analyze",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="geo_report.json",
        help="Output file for the analysis report (default: geo_report.json)",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="claude-opus-4-5",
        help="Anthropic Claude model to use (default: claude-opus-4-5)",
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments and raise errors for invalid combinations."""
    if not args.url and not args.file:
        raise ValueError("Either --url or --file must be provided")

    if args.url and args.file:
        raise ValueError("Provide either --url or --file, not both")

    if args.file and not Path(args.file).exists():
        raise FileNotFoundError(f"File not found: {args.file}")


def main() -> int:
    """Main entry point for the geo-seo-claude CLI."""
    args = parse_args()

    # Setup logging
    logger = setup_logger(verbose=args.verbose)
    logger.info("Starting geo-seo-claude analysis")

    try:
        validate_args(args)
    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Argument error: {e}")
        return 1

    # Load configuration
    config = load_config(args.config)
    config["model"] = args.model

    # Resolve input source
    input_source = args.url or args.file
    input_type = "url" if args.url else "file"

    logger.info(f"Input: {input_type} -> {input_source}")
    logger.info(f"Agent: {args.agent}")
    logger.info(f"Model: {args.model}")

    # Run the selected agent(s)
    runner = AgentRunner(config=config, logger=logger)

    try:
        report = runner.run(
            agent=args.agent,
            input_source=input_source,
            input_type=input_type,
        )
        runner.save_report(report, args.output)
        logger.info(f"Report saved to: {args.output}")
        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
