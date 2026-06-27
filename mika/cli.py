"""Command-line interface for mika."""

import argparse
import logging
import sys
from typing import Optional

from mika import __app_name__, __version__
from mika.chat import run_chat
from mika.completion import get_source_command, install_completion
from mika.config import (
    get_active_model,
    get_active_provider,
    get_api_key,
    load_config,
    save_config,
    set_api_key,
    set_model,
    set_provider,
    set_system_prompt,
)
from mika.history import add_message, create_session, delete_session, list_sessions, load_session
from mika.logger import setup_logging
from mika.providers import list_providers
from mika.ui import (
    confirm,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
    prompt_choice,
    prompt_input,
)

logger = logging.getLogger("mika")


def _setup_logging_from_args(args: argparse.Namespace) -> None:
    level = logging.WARNING
    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    setup_logging(level=level)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description="A terminal-based open-source AI agent CLI with streaming and thinking display.",
    )
    parser.add_argument("--version", action="version", version=f"{__app_name__} {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging.")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    chat_parser = subparsers.add_parser("chat", help="Start an interactive chat session")
    chat_parser.add_argument("--provider", help="Override provider")
    chat_parser.add_argument("--model", help="Override model")
    chat_parser.add_argument("--session", help="Resume a session by ID")
    chat_parser.add_argument("--new", action="store_true", help="Start a new session")

    config_parser = subparsers.add_parser("config", help="Configure mika")
    config_parser.add_argument("--provider", help="Set active provider")
    config_parser.add_argument("--model", help="Set active model")
    config_parser.add_argument("--api-key", help="Set API key for active provider")
    config_parser.add_argument("--system-prompt", help="Set system prompt")
    config_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive setup wizard")

    history_parser = subparsers.add_parser("history", help="Manage chat history")
    history_parser.add_argument("--list", "-l", action="store_true", help="List recent sessions")
    history_parser.add_argument("--resume", metavar="ID", help="Resume a session")
    history_parser.add_argument("--delete", metavar="ID", help="Delete a session")

    providers_parser = subparsers.add_parser("providers", help="List supported providers and models")
    providers_parser.add_argument("--show-keys", action="store_true", help="Show whether API key is set (masked)")

    subparsers.add_parser("completion", help="Install shell completion")

    return parser


def cmd_chat(args: argparse.Namespace) -> int:
    run_chat(
        provider_name=args.provider,
        model=args.model,
        session_id=args.session,
        new_session=args.new,
    )
    return 0


def _interactive_config() -> int:
    print_header("mika configuration")
    providers = list_providers()
    choices = [f"{cls.CONFIG.display_name}" for cls in providers.values()]
    selected = prompt_choice("Select a provider:", choices)
    provider_name = list(providers.keys())[selected]
    provider_cls = providers[provider_name]

    print_info(f"\nSelected: {provider_cls.CONFIG.display_name}")

    # API key
    if provider_cls.CONFIG.requires_api_key:
        existing = get_api_key(provider_name)
        if existing:
            print_success(f"API key already configured for {provider_cls.CONFIG.display_name}.")
            if not confirm("Change it?"):
                api_key = existing
            else:
                api_key = prompt_input(f"Enter {provider_cls.CONFIG.display_name} API key", password=True)
        else:
            api_key = prompt_input(f"Enter {provider_cls.CONFIG.display_name} API key", password=True)
        if api_key:
            set_api_key(provider_name, api_key)

    # Model
    models = provider_cls.get_models()
    default_idx = models.index(provider_cls.get_default_model()) if provider_cls.get_default_model() in models else 0
    model_choice = prompt_choice("Select default model:", models, default=default_idx)
    model = models[model_choice]

    # System prompt
    current_prompt = load_config().get("system_prompt", "")
    system_prompt = prompt_input("System prompt", default=current_prompt)

    set_provider(provider_name, model=model)
    set_system_prompt(system_prompt)

    print_success("\nConfiguration saved!")
    print_info(f"Provider: {provider_name}")
    print_info(f"Model:    {model}")
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    if args.interactive:
        return _interactive_config()

    updated = False
    if args.provider:
        set_provider(args.provider)
        updated = True
        print_success(f"Provider set to: {args.provider}")
    if args.model:
        set_model(args.model)
        updated = True
        print_success(f"Model set to: {args.model}")
    if args.api_key:
        provider = args.provider or get_active_provider()
        if not provider:
            print_error("No provider specified. Use --provider or run interactive config.")
            return 1
        set_api_key(provider, args.api_key)
        updated = True
        print_success(f"API key saved for: {provider}")
    if args.system_prompt:
        set_system_prompt(args.system_prompt)
        updated = True
        print_success("System prompt updated.")

    if not updated:
        cfg = load_config()
        print_header("mika configuration")
        print_info(f"Provider:      {cfg.get('provider') or 'Not set'}")
        print_info(f"Model:         {cfg.get('model') or 'Not set'}")
        print_info(f"System prompt: {cfg.get('system_prompt', '')}")
        api_key_status = "set" if get_api_key(cfg.get("provider", "")) else "not set"
        print_info(f"API key:       {api_key_status}")
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    if args.delete:
        if delete_session(args.delete):
            print_success(f"Deleted session: {args.delete}")
        else:
            print_warning(f"Session not found: {args.delete}")
        return 0

    if args.resume:
        session = load_session(args.resume)
        if not session:
            print_error(f"Session not found: {args.resume}")
            return 1
        run_chat(session_id=args.resume)
        return 0

    sessions = list_sessions()
    if not sessions:
        print_info("No chat history found.")
        return 0

    print_header("Recent chat sessions")
    for idx, session in enumerate(sessions, start=1):
        title = session.get("title", "Untitled")
        updated = session.get("updated_at", "unknown")
        sid = session.get("id", "unknown")
        print(f"{idx}. [{sid}] {updated} - {title}")
    return 0


def cmd_providers(args: argparse.Namespace) -> int:
    print_header("Supported providers")
    for name, cls in list_providers().items():
        cfg = cls.CONFIG
        print(f"{cfg.display_name} ({name})")
        print(f"  Base URL:      {cfg.base_url}")
        print(f"  Default model: {cfg.default_model}")
        print(f"  Models:        {', '.join(cfg.models)}")
        if args.show_keys:
            key = get_api_key(name)
            masked = "set" if key else "not set"
            print(f"  API key:       {masked}")
        print()
    return 0


def cmd_completion(args: argparse.Namespace) -> int:
    path = install_completion()
    print_success(f"Bash completion installed to: {path}")
    print_info("Add the following line to your ~/.bashrc or ~/.bash_profile:")
    print(f"  {get_source_command()}")
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging_from_args(args)

    logger.debug("Starting mika CLI with args: %s", args)

    if args.command == "chat" or args.command is None:
        return cmd_chat(args)
    if args.command == "config":
        return cmd_config(args)
    if args.command == "history":
        return cmd_history(args)
    if args.command == "providers":
        return cmd_providers(args)
    if args.command == "completion":
        return cmd_completion(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
