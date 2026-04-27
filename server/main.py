from __future__ import annotations

import argparse
import asyncio

from server.game_server import GameServer
from shared.difficulty import DIFFICULTY_KEYS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Neon Outbreak async game server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host/IP to bind.")
    parser.add_argument("--port", default=8765, type=int, help="TCP port to bind.")
    parser.add_argument("--difficulty", default="medium", choices=DIFFICULTY_KEYS, help="World difficulty preset.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(GameServer(args.host, args.port, args.difficulty).start())
    except KeyboardInterrupt:
        print("Server stopped.")


if __name__ == "__main__":
    main()
