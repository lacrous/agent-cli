"""Shell completion support for mika CLI."""

from pathlib import Path

from mika.config import get_completion_dir


BASH_COMPLETION = r"""_mika_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="chat config history providers --help --verbose --debug --provider --model --session --new"

    case "${prev}" in
        --provider)
            COMPREPLY=( $(compgen -W "qwen openai anthropic ollama" -- "${cur}") )
            return 0
            ;;
        --model)
            COMPREPLY=()
            return 0
            ;;
    esac

    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        return 0
    fi

    COMPREPLY=( $(compgen -W "chat config history providers" -- "${cur}") )
    return 0
}
complete -F _mika_completion mika
"""


def get_completion_path() -> Path:
    """Return the path where the bash completion script is stored."""
    return get_completion_dir() / "mika.bash"


def install_completion() -> Path:
    """Write the bash completion script to the config directory."""
    path = get_completion_path()
    with path.open("w", encoding="utf-8") as f:
        f.write(BASH_COMPLETION)
    return path


def get_source_command() -> str:
    """Return the shell command users should add to their profile."""
    path = get_completion_path()
    return f"source {path}"
