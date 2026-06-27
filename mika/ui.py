"""Terminal UI helpers for mika CLI."""

import sys
import time
from typing import Optional

import colorama
from colorama import Fore, Style

colorama.init()


def print_info(message: str) -> None:
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")


def print_success(message: str) -> None:
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    print(f"{Fore.RED}{message}{Style.RESET_ALL}", file=sys.stderr)


def print_header(title: str) -> None:
    width = 50
    print(f"\n{Fore.MAGENTA}{'=' * width}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{title.center(width)}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'=' * width}{Style.RESET_ALL}\n")


def prompt_input(message: str, default: Optional[str] = None, password: bool = False) -> str:
    """Prompt the user for input with an optional default value."""
    suffix = f" [{default}]" if default else ""
    full_message = f"{Fore.BLUE}?{Style.RESET_ALL} {message}{suffix}: "
    if password:
        import getpass
        value = getpass.getpass(full_message)
    else:
        value = input(full_message)
    if not value and default:
        return default
    return value


def prompt_choice(message: str, choices: list, default: Optional[int] = None) -> int:
    """Display a numbered list and return the selected index (0-based)."""
    print(f"{Fore.BLUE}?{Style.RESET_ALL} {message}")
    for idx, choice in enumerate(choices, start=1):
        marker = "  "
        if default is not None and idx - 1 == default:
            marker = f"{Fore.GREEN}* "
        print(f"{marker}{idx}. {choice}{Style.RESET_ALL}")
    while True:
        prompt_text = "Select"
        if default is not None:
            prompt_text += f" [{default + 1}]"
        value = input(f"{Fore.BLUE}>{Style.RESET_ALL} {prompt_text}: ").strip()
        if not value and default is not None:
            return default
        try:
            index = int(value) - 1
            if 0 <= index < len(choices):
                return index
        except ValueError:
            pass
        print_warning("Invalid choice. Please try again.")


def confirm(message: str, default: bool = False) -> bool:
    """Ask a yes/no question."""
    suffix = " [Y/n]" if default else " [y/N]"
    value = input(f"{Fore.BLUE}?{Style.RESET_ALL} {message}{suffix}: ").strip().lower()
    if not value:
        return default
    return value in ("y", "yes")


class ThinkingAnimation:
    """Simple terminal thinking animation that can be stopped cleanly."""

    def __init__(self, message: str = "Thinking"):
        self.message = message
        self._running = False
        self._start_time: Optional[float] = None

    def start(self) -> None:
        self._running = True
        self._start_time = time.time()
        self._tick()

    def _tick(self) -> None:
        if not self._running:
            return
        elapsed = time.time() - self._start_time
        dots = "." * (int(elapsed * 2) % 4)
        sys.stdout.write(f"\r{Fore.YELLOW}{self.message}{dots}{Style.RESET_ALL}   ")
        sys.stdout.flush()
        # Use a short blocking loop instead of a background thread to keep the CLI simple.

    def update(self) -> None:
        self._tick()

    def stop(self, clear: bool = True) -> None:
        self._running = False
        if clear:
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()


def print_stream_chunk(text: str) -> None:
    """Print a chunk of streamed text without adding newlines."""
    print(text, end="", flush=True)
