import logging

from bot.bot import run_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    run_bot()


if __name__ == "__main__":
    main()
