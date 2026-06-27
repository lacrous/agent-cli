#!/usr/bin/env bash
# Advanced installer for mika CLI.
# Installs Python dependencies, sets up the `mika` command globally,
# configures bash completion, and prepares the config directory.

set -euo pipefail

APP_NAME="mika"
REPO_URL="https://github.com/lacrous/agent-cli.git"
INSTALL_DIR="/usr/local"
BIN_DIR="${INSTALL_DIR}/bin"
REQUIRED_PYTHON="3.8"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_success() { echo -e "${GREEN}[OK]${NC}    $*"; }

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

python_version_ok() {
    local version
    version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_info "Detected Python ${version}"
    if [ "$(printf '%s\n' "$REQUIRED_PYTHON" "$version" | sort -V | head -n1)" != "$REQUIRED_PYTHON" ]; then
        log_error "Python ${REQUIRED_PYTHON}+ is required."
        return 1
    fi
}

detect_os() {
    case "$(uname -s)" in
        Linux*)  echo "linux";;
        Darwin*) echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)       echo "unknown";;
    esac
}

install_system_deps() {
    local os=$1
    log_info "Installing system dependencies for ${os}..."
    case "$os" in
        linux)
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv curl git
            elif command_exists dnf; then
                sudo dnf install -y python3 python3-pip curl git
            elif command_exists pacman; then
                sudo pacman -Sy --noconfirm python python-pip curl git
            else
                log_warn "Unsupported package manager. Please install python3, pip, curl, and git manually."
            fi
            ;;
        macos)
            if command_exists brew; then
                brew install python curl git
            else
                log_warn "Homebrew not found. Please install python3, curl, and git manually."
            fi
            ;;
        windows)
            log_warn "Windows detected. Please ensure Python 3.8+, git, and curl are installed."
            ;;
        *)
            log_warn "Unknown OS. Please install python3, pip, curl, and git manually."
            ;;
    esac
}

setup_virtualenv() {
    local venv_dir="${HOME}/.local/share/mika/venv"
    log_info "Setting up virtual environment at ${venv_dir}..."
    mkdir -p "$(dirname "$venv_dir")"
    local recreate=false
    if [ -d "$venv_dir" ]; then
        if [ ! -x "$venv_dir/bin/python" ]; then
            log_warn "Existing virtual environment is missing python binary. Recreating."
            recreate=true
        else
            log_warn "Existing virtual environment found. Reusing."
        fi
    fi
    if [ "$recreate" = true ]; then
        rm -rf "$venv_dir"
        python3 -m venv "$venv_dir"
    elif [ ! -d "$venv_dir" ]; then
        python3 -m venv "$venv_dir"
    fi
    echo "$venv_dir"
}

install_python_package() {
    local python_bin=$1
    log_info "Installing mika and Python dependencies..."
    "$python_bin" -m pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        "$python_bin" -m pip install -r requirements.txt
    fi
    "$python_bin" -m pip install .
}

ensure_symlink() {
    local python_bin=$1
    local target="${BIN_DIR}/${APP_NAME}"
    local source_bin
    source_bin=$("$python_bin" -c 'import sys, os; print(os.path.join(sys.prefix, "bin", "mika"))')

    log_info "Ensuring ${APP_NAME} is available in ${BIN_DIR}..."
    if [ -L "$target" ]; then
        log_warn "Existing symlink ${target} found. Replacing."
        sudo rm -f "$target"
    elif [ -e "$target" ]; then
        log_warn "Existing file ${target} found. Backing up to ${target}.bak"
        sudo mv "$target" "${target}.bak"
    fi
    sudo ln -s "$source_bin" "$target"
    sudo chmod +x "$target"
}

install_completion() {
    local python_bin=$1
    log_info "Installing bash completion..."
    "$python_bin" -m mika completion
    local completion_file
    completion_file=$("$python_bin" -m mika completion 2>/dev/null | tail -n1 | awk '{print $NF}')
    if [ -n "$completion_file" ] && [ -f "$completion_file" ]; then
        local shell_rc="${HOME}/.bashrc"
        [ "$(uname -s)" = "Darwin" ] && shell_rc="${HOME}/.bash_profile"
        if ! grep -q "source ${completion_file}" "$shell_rc" 2>/dev/null; then
            echo "source ${completion_file}" >> "$shell_rc"
            log_success "Added completion source to ${shell_rc}."
        else
            log_warn "Completion already sourced in ${shell_rc}."
        fi
    fi
}

print_final_instructions() {
    echo
    log_success "Installation complete!"
    echo
    log_info "Next steps:"
    echo "  1. Reload your shell or run: source ~/.bashrc"
    echo "  2. Run the interactive setup wizard: mika config -i"
    echo "  3. Start chatting: mika chat"
    echo
    log_info "For help: mika --help"
}

main() {
    local os
    os=$(detect_os)
    log_info "Detected OS: ${os}"

    if ! command_exists python3; then
        install_system_deps "$os"
    fi

    python_version_ok

    if ! command_exists git; then
        install_system_deps "$os"
    fi

    if ! command_exists pip3 && ! python3 -m pip --version >/dev/null 2>&1; then
        log_error "pip is not available. Please install python3-pip."
        exit 1
    fi

    local python_bin
    if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        local venv_dir
        venv_dir=$(setup_virtualenv)
        python_bin="${venv_dir}/bin/python"
        install_python_package "$python_bin"
    else
        log_error "No setup.py or pyproject.toml found. Are you running install.sh from the repo root?"
        exit 1
    fi

    ensure_symlink "$python_bin"
    install_completion "$python_bin"

    print_final_instructions
}

main "$@"
