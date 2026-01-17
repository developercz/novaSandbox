#!/bin/bash
# 🚀 SETUP SCRIPT - Automatizovaná instalace NovaSandbox

set -e  # Zastavit na chybě

echo "==============================================="
echo "🚀 NovaSandbox - Automatický Setup"
echo "==============================================="

# Barvy pro výstup
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funkce pro tisky
success() { echo -e "${GREEN}✅  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

# Zjistit OS
OS=$(uname -s)
info "Detekovaný OS: $OS"

# Zjistit Python verzi
if ! command -v python3 &> /dev/null; then
    error "Python3 není nainstalován. Instalujte prosím Python 3.9+"
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
info "Python verze: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.9" | bc) -eq 1 ]]; then
    error "Potřebný Python 3.9+, máte $PYTHON_VERSION"
fi

success "Python checks prošel"

# Krok 1: Vytvoření virtual environment
echo ""
info "Krok 1: Vytvoření virtual environment..."

if [ -d "venv" ]; then
    info "venv již existuje, přeskakuji"
else
    python3 -m venv venv
    success "Virtual environment vytvořen"
fi

# Aktivace venv
source venv/bin/activate
success "Virtual environment aktivován"

# Krok 2: Instalace závislostí
echo ""
info "Krok 2: Instalace Python závislostí..."

if [ ! -f "requirements.txt" ]; then
    error "requirements.txt nenalezen!"
fi

pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

success "Závislosti nainstalovány"

# Krok 3: Ověření instalace
echo ""
info "Krok 3: Ověření instalace..."

python3 -c "from novasandbox.core import SandboxConfig; print('✓ Core')" || error "Core import error"
python3 -c "from novasandbox.providers import AppleVZHypervisor, FirecrackerHypervisor; print('✓ Providers')" || error "Providers import error"

success "Import checks prošel"

# Krok 4: OS-specifické nastavení
echo ""
info "Krok 4: OS-specifické nastavení..."

if [ "$OS" = "Darwin" ]; then
    info "macOS detekován - AppleVZ bude dostupný"
    success "macOS setup hotov"
elif [ "$OS" = "Linux" ]; then
    info "Linux detekován - Firecracker bude dostupný"
    
    # Ověřit KVM
    if [ ! -e "/dev/kvm" ]; then
        error "KVM není dostupný. Potřebný pro Firecracker na Linuxu"
    fi
    
    # Ověřit Firecracker
    if ! command -v firecracker &> /dev/null; then
        error "Firecracker není nainstalován. Instalujte: sudo apt-get install firecracker"
    fi
    
    success "Linux setup hotov"
else
    error "Nepodporovaný OS: $OS"
fi

# Krok 5: Performance test (optional)
echo ""
read -p "🧪 Spustit Performance test? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "Spouštím performance test..."
    python3 examples/performance_test.py | tail -20
    success "Performance test hotov"
fi

# Finální zpráva
echo ""
echo "==============================================="
echo "✅ SETUP HOTOV!"
echo "==============================================="
echo ""
echo "🚀 Další kroky:"
echo ""
echo "1. Aktivovat virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Spustit starter kit:"
echo "   python3 examples/starter_kit.py"
echo ""
echo "3. Nebo spustit API server:"
echo "   python3 examples/api_server.py"
echo ""
echo "4. Podrobnosti:"
echo "   cat DEPLOYMENT.md"
echo ""
echo "==============================================="
