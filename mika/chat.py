"""Interactive chat loop for mika CLI."""

import logging
import sys
import time
from typing import List, Optional

from mika.config import (
    get_active_model,
    get_active_provider,
    get_api_key,
    get_system_prompt,
)
from mika.history import add_message, create_session, load_session
from mika.providers import get_provider
from mika.providers.base import BaseProvider, StreamChunk
from mika.ui import (
    ThinkingAnimation,
    confirm,
    print_error,
    print_header,
    print_info,
    print_stream_chunk,
    print_success,
    print_warning,
)

logger = logging.getLogger("mika")


def _build_messages(session_id: Optional[str]) -> List[dict]:
    """Load existing messages from a session, if any."""
    if not session_id:
        return []
    session = load_session(session_id)
    if session:
        return session.get("messages", [])
    return []


def _render_stream(provider: BaseProvider, messages: List[dict], system_prompt: str) -> str:
    """Stream the assistant response and return the full content."""
    animation = ThinkingAnimation("Thinking")
    animation.start()

    reasoning_started = False
    answering_started = False
    full_content = ""
    full_reasoning = ""

    # For providers that don't stream reasoning, show animation until first content.
    first_chunk_seen = False

    try:
        stream = provider.chat(messages, system_prompt=system_prompt)
        for chunk in stream:
            if not first_chunk_seen:
                animation.stop(clear=True)
                first_chunk_seen = True

            if chunk.reasoning_content:
                if not reasoning_started:
                    print_info("\n" + "=" * 20 + " Thinking process " + "=" * 20)
                    reasoning_started = True
                print_stream_chunk(chunk.reasoning_content)
                full_reasoning += chunk.reasoning_content

            if chunk.content:
                if not answering_started:
                    print_info("\n" + "=" * 20 + " Full response " + "=" * 20 + "\n")
                    answering_started = True
                print_stream_chunk(chunk.content)
                full_content += chunk.content
    except Exception as exc:
        animation.stop(clear=True)
        logger.exception("Streaming failed")
        print_error(f"\nError during streaming: {exc}")
        raise
    finally:
        animation.stop(clear=True)

    print()  # newline at end
    return full_content


def run_chat(
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    session_id: Optional[str] = None,
    new_session: bool = False,
) -> None:
    """Run the interactive chat loop."""
    provider_name = provider_name or get_active_provider()
    if not provider_name:
        print_error("No provider configured. Run: mika config")
        sys.exit(1)

    provider_cls = get_provider(provider_name)
    api_key = get_api_key(provider_name)
    model = model or get_active_model() or provider_cls.get_default_model()

    try:
        provider = provider_cls(api_key=api_key, model=model)
        provider.validate()
    except RuntimeError as exc:
        print_error(str(exc))
        sys.exit(1)

    if new_session or not session_id:
        session_id = create_session()
        print_success(f"Started new chat session: {session_id}")
    else:
        print_info(f"Resuming session: {session_id}")

    messages = _build_messages(session_id)
    system_prompt = get_system_prompt()

    print_header(f"mika chat | {provider_cls.CONFIG.display_name} | {model}")
    print_info("Type your message and press Enter. Commands:")
    print("  /help     - show commands")
    print("  /clear    - clear conversation history")
    print("  /save     - save current session")
    print("  /exit     - quit")
    print()

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            command = user_input[1:].lower()
            if command in ("exit", "quit", "q"):
                break
            elif command == "help":
                _print_help()
            elif command == "clear":
                messages = []
                print_success("Conversation history cleared.")
            elif command == "save":
                print_success(f"Session saved: {session_id}")
            else:
                print_warning(f"Unknown command: {user_input}")
            continue

        messages.append({"role": "user", "content": user_input})
        add_message(session_id, "user", user_input)

        try:
            assistant_content = _render_stream(provider, messages, system_prompt)
            if assistant_content:
                messages.append({"role": "assistant", "content": assistant_content})
                add_message(session_id, "assistant", assistant_content)
        except Exception:
            # Remove the last user message so the user can retry without duplicates.
            messages.pop()
            print_error("Failed to get response. You can retry your message.")

    print_info("\nGoodbye!")


def _print_help() -> None:
    print_info("Chat commands:")
    print("  /help   - show this help")
    print("  /clear  - clear current conversation context")
    print("  /save   - confirm current session is saved")
    print("  /exit   - leave the chat")
