# mika

A terminal-based, open-source AI agent CLI with streaming responses, thinking/reasoning display, conversation history, and support for multiple providers.

## Features

- **Multiple providers**: Qwen (Alibaba DashScope), OpenAI, Anthropic, Ollama (local).
- **Interactive setup wizard**: `mika config -i` walks you through provider, API key, and model selection.
- **Streaming chat**: watch the model think and respond in real time.
- **Conversation history**: save, list, and resume previous chats.
- **System prompts**: configure a global system prompt or persona.
- **Subcommands & flags**: `chat`, `config`, `history`, `providers`, `completion`.
- **Bash completion**: auto-complete commands and flags.
- **Debug logging**: `--verbose` and `--debug` flags.

## Installation

```bash
git clone https://github.com/lacrous/agent-cli.git
cd agent-cli
bash install.sh
```

The installer will:

1. Install Python 3.8+ and system dependencies (if missing).
2. Create a virtual environment at `~/.local/share/mika/venv`.
3. Install the `mika` Python package and dependencies.
4. Symlink `mika` into `/usr/local/bin`.
5. Install and source bash completion.

After installation, reload your shell:

```bash
source ~/.bashrc
```

## Quick start

Run the interactive configuration wizard:

```bash
mika config -i
```

Start chatting:

```bash
mika chat
```

Use a specific provider or model:

```bash
mika chat --provider qwen --model qwen3.7-max
```

## Commands

| Command | Description |
|---------|-------------|
| `mika chat` | Start interactive chat |
| `mika chat --new` | Start a new session |
| `mika chat --session <id>` | Resume a saved session |
| `mika config` | Show current configuration |
| `mika config -i` | Interactive setup wizard |
| `mika config --provider qwen --model qwen3.7-max` | Set provider/model |
| `mika config --api-key <key>` | Store an API key |
| `mika config --system-prompt "You are a..."` | Set system prompt |
| `mika history` | List recent sessions |
| `mika history --resume <id>` | Resume a session |
| `mika history --delete <id>` | Delete a session |
| `mika providers` | List supported providers/models |
| `mika completion` | Install bash completion |

## Chat commands

While in a chat, you can use:

- `/help` - show available commands
- `/clear` - clear the current conversation context
- `/save` - confirm the session is saved
- `/exit` or `/quit` - leave the chat

## Configuration

Configuration is stored in:

```
~/.config/mika/config.json
```

History is stored in:

```
~/.config/mika/history/
```

## Environment variables

Each provider can also read its API key from an environment variable:

- Qwen: `DASHSCOPE_API_KEY`
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Ollama: `OLLAMA_API_KEY` (optional, local by default)

## Development

Run from source:

```bash
python -m mika --help
pip install -e .
```

## License

MIT
