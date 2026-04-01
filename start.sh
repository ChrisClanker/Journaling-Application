#!/usr/bin/env bash
# start.sh - Start the Journaling Application development server
#
# This script automates local development setup:
#   1. Checks for a .env file (creates one if missing)
#   2. Creates a virtual environment if it doesn't exist
#   3. Installs Python dependencies
#   4. Runs database migrations
#   5. Starts the Django development server
#
# Usage: ./start.sh [--setup-only] [--runserver]
#   --setup-only   Only perform setup steps, do not start the server
#   --runserver    Start the server after setup (default behavior)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"
MANAGE_PY="journal_project/manage.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()    { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }

# --- Parse arguments ---
SETUP_ONLY=false
RUN_SERVER=true

for arg in "$@"; do
    case "$arg" in
        --setup-only)
            SETUP_ONLY=true
            RUN_SERVER=false
            ;;
        --runserver)
            RUN_SERVER=true
            ;;
        --help|-h)
            echo "Usage: $0 [--setup-only] [--runserver]"
            echo ""
            echo "Options:"
            echo "  --setup-only   Only perform setup steps, do not start the server"
            echo "  --runserver    Start the server after setup (default)"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            error "Unknown argument: $arg"
            echo "Run '$0 --help' for usage information."
            exit 1
            ;;
    esac
done

# --- Step 1: Check for .env file ---
if [ ! -f ".env" ]; then
    warn ".env file not found. Creating one with default values..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || python -c "import secrets; print(secrets.token_hex(32))")
    cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=True
USE_AI=False
WEBAPP_USERNAME=joe
EOF
    info "Created .env file with a generated SECRET_KEY."
    warn "Review .env and update values as needed (especially WEBAPP_USERNAME)."
else
    info ".env file found."
fi

# --- Step 2: Load environment variables from .env ---
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    info "Loaded environment variables from .env"
fi

# --- Step 3: Set up virtual environment ---
if [ ! -d "$VENV_DIR" ]; then
    info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR" 2>/dev/null || python -m venv "$VENV_DIR"
    info "Virtual environment created at ${VENV_DIR}/"
else
    info "Virtual environment already exists."
fi

# --- Step 4: Install dependencies ---
info "Installing dependencies..."
"$PIP" install --quiet --upgrade pip
"$PIP" install --quiet -r requirements.txt
info "Dependencies installed."

# --- Step 5: Run database migrations ---
info "Running database migrations..."
"$PYTHON" "$MANAGE_PY" migrate --noinput
info "Migrations complete."

# --- Step 6: Check if a superuser exists ---
USER_COUNT=$("$PYTHON" "$MANAGE_PY" shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).count())" 2>/dev/null || echo "0")
if [ "$USER_COUNT" -eq 0 ]; then
    warn "No admin user found. Creating one now..."
    "$PYTHON" "$MANAGE_PY" createsuperuser
else
    info "Admin user already exists."
fi

# --- Step 7: Start development server ---
if [ "$SETUP_ONLY" = true ]; then
    info "Setup complete. Run '$0' to start the server."
    exit 0
fi

if [ "$RUN_SERVER" = true ]; then
    info "Starting development server..."
    info "Access the app at: http://localhost:8000/"
    info "Press Ctrl+C to stop the server."
    echo ""
    "$PYTHON" "$MANAGE_PY" runserver
fi
