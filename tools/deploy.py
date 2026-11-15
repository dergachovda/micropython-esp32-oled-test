"""Заливає каталог device/ на плату з MicroPython через mpremote."""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEVICE_DIR = ROOT / "device"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def build_command(port: str, sources: list[Path], *, reset: bool) -> list[str]:
    """Збирає команду mpremote для копіювання файлів на плату.

    Args:
        port: Послідовний порт (`COM3`, `/dev/ttyACM0`) або `auto`.
        sources: Файли й каталоги, які копіюються в корінь файлової системи плати.
        reset: Чи перезавантажити плату після копіювання.

    Returns:
        Список аргументів для `subprocess.run`.
    """
    command = [sys.executable, "-m", "mpremote", "connect", port, "fs", "cp", "-r"]
    command += [str(source) for source in sources]
    command.append(":")
    if reset:
        command += ["+", "reset"]
    return command


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Розбирає аргументи командного рядка.

    Args:
        argv: Аргументи; `None` означає `sys.argv`.

    Returns:
        Розібрані аргументи.
    """
    parser = argparse.ArgumentParser(description="Залити device/ на плату.")
    parser.add_argument(
        "-p",
        "--port",
        default="auto",
        help="порт, напр. COM3 або /dev/ttyACM0 (за замовчуванням auto)",
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="не перезавантажувати плату після заливки",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Копіює device/ на плату без `__pycache__` і перезавантажує її.

    Args:
        argv: Аргументи; `None` означає `sys.argv`.

    Returns:
        Код завершення mpremote або 1, якщо каталог device/ не знайдено.
    """
    args = parse_args(argv)
    if not DEVICE_DIR.is_dir():
        print(f"Каталог не знайдено: {DEVICE_DIR}", file=sys.stderr)
        return 1

    # Копія без __pycache__: pytest на ПК створює його в device/lib.
    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "device"
        shutil.copytree(DEVICE_DIR, staging, ignore=IGNORE)
        sources = sorted(staging.iterdir())
        if not sources:
            print("Каталог device/ порожній.", file=sys.stderr)
            return 1
        command = build_command(args.port, sources, reset=not args.no_reset)
        print("Заливаю:", ", ".join(source.name for source in sources))
        return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
