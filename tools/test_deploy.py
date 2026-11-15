from pathlib import Path

from deploy import build_command


def test_build_command_with_reset() -> None:
    command = build_command("COM3", [Path("main.py"), Path("lib")], reset=True)
    assert command[command.index("connect") + 1] == "COM3"
    assert command[-3:] == [":", "+", "reset"]


def test_build_command_without_reset() -> None:
    command = build_command("auto", [Path("main.py")], reset=False)
    assert command[-1] == ":"
    assert "reset" not in command