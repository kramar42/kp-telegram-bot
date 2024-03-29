import argparse
import logging
import os
import sys

from kpbot import create_app


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-t",
            "--token",
            required=not os.environ.get("BOT_TOKEN"),
            default=os.environ.get("BOT_TOKEN"),
            help="Telegram Bot token",
        )
        parser.add_argument(
            "-a",
            "--aliases",
            default=os.environ.get("ALIASES"),
            help="Path to YAML file with user aliases",
        )
        parser.add_argument(
            "-d",
            "--db-uri",
            default=os.environ.get("DB_URI"),
            help="Database URI",
        )
        args = parser.parse_args()

        application = create_app(args.token, args.aliases, args.db_uri)
        application.run_polling()
    except Exception as e:
        logging.getLogger().critical(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
