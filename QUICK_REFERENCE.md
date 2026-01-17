# 🚀 NOVASANDBOX - QUICK REFERENCE

## INSTALACE (1x)

```bash
cd /Users/admin/novaSandbox
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## NEJČASTĚJŠÍ PŘÍKAZY

| Co chceš | Příkaz |
|----------|--------|
| **Demo (5 příkladů)** | `make starter` |
| **REST API** | `make run-api` |
| **Performance test** | `make perf-test` |
| **Security test** | `make security-test` |
| **All help** | `make help` |

## PYTHON KÓD - BASIC USAGE

```python
import asyncio
from novasandbox.core import SandboxConfig, SecurityLevel
from novasandbox.providers import AppleVZHypervisor

async def main():
    config = SandboxConfig(security_level=SecurityLevel.STRICT)
    hypervisor = AppleVZHypervisor()  # FirecrackerHypervisor na Linux
    sandbox = await hypervisor.create_sandbox(config)
    
    result = await sandbox.execute_command("echo 'Hello'")
    print(result)
    
    await sandbox.stop()

asyncio.run(main())
```

## VOLBA BEZPEČNOSTI

- **BASIC** → Jen test (bez ochrany)
- **STANDARD** → ✅ Doporučeno
- **STRICT** → Untrusted kód
- **PARANOID** → Maximum

## REST API EXAMPLE

Terminal 1:
```bash
python3 examples/api_server.py
```

Terminal 2:
```bash
curl -X POST http://localhost:8000/sandboxes \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "alpine-python",
    "security_level": "STRICT",
    "memory_mb": 512
  }'
```

## KLÍČOVÁ ČÍSLA

| Metrika | Hodnota |
|---------|---------|
| Vytvoření | **0.058ms** |
| vs Docker | **200-500ms** (3-8x pomalejší) |
| Memory OV. | ~10MB/sandbox |
| CPU OV. | ~2-3% |

## PRODUKČNÍ DEPLOYMENT

**Linux:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 examples.api_server:app
```

**macOS:**
```bash
python3 examples/api_server.py
```

## TROUBLESHOOTING

| Chyba | Řešení |
|-------|--------|
| ImportError AppleVZ | Normální na Linuxu, použij FirecrackerHypervisor |
| Permission denied | Linux: sudo, nebo vypúštění Firecrackeru s sudo |
| OOM: Kill process | Zvol vyšší memory_mb |
| API nedostupný | Kontrola firewallu (localhost:8000) |

## MONITORING

```python
summary = sandbox.security_manager.get_violations_summary()
print(f"Violations: {summary['total_violations']}")
```

## DOKUMENTACE

- **DEPLOYMENT.md** - Detailný průvodce
- **SECURITY_GUIDE.md** - Bezpečnost
- **README.md** - Úplné info
