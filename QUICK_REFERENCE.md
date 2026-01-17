# 🚀 NOVASANDBOX - QUICK REFERENCE

## INSTALLATION (one time)

```bash
cd /Users/admin/novaSandbox
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## MOST COMMON COMMANDS

| What you want | Command |
|----------|--------|
| **Demo (5 examples)** | `make starter` |
| **REST API** | `make run-api` |
| **Performance test** | `make perf-test` |
| **Security test** | `make security-test` |
| **All help** | `make help` |

## PYTHON CODE - BASIC USAGE

```python
import asyncio
from novasandbox.core import SandboxConfig, SecurityLevel
from novasandbox.providers import AppleVZHypervisor

async def main():
    config = SandboxConfig(security_level=SecurityLevel.STRICT)
    hypervisor = AppleVZHypervisor()  # FirecrackerHypervisor on Linux
    sandbox = await hypervisor.create_sandbox(config)
    
    result = await sandbox.execute_command("echo 'Hello'")
    print(result)
    
    await sandbox.stop()

asyncio.run(main())
```

## SECURITY LEVEL CHOICE

- **BASIC** → Testing only (no protection)
- **STANDARD** → ✅ Recommended
- **STRICT** → Untrusted code
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

## KEY NUMBERS

| Metric | Value |
|---------|---------|
| Creation | **0.058ms** |
| vs Docker | **200-500ms** (3-8x slower) |
| Memory OV. | ~10MB/sandbox |
| CPU OV. | ~2-3% |

## PRODUCTION DEPLOYMENT

**Linux:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 examples.api_server:app
```

**macOS:**
```bash
python3 examples/api_server.py
```

## TROUBLESHOOTING

| Error | Solution |
|-------|--------|
| ImportError AppleVZ | Normal on Linux, use FirecrackerHypervisor |
| Permission denied | Linux: sudo, or run Firecracker with sudo |
| OOM: Kill process | Choose higher memory_mb |
| API unavailable | Check firewall (localhost:8000) |

## MONITORING

```python
summary = sandbox.security_manager.get_violations_summary()
print(f"Violations: {summary['total_violations']}")
```

## DOKUMENTACE

- **DEPLOYMENT.md** - Detailný průvodce
- **SECURITY_GUIDE.md** - Bezpečnost
- **README.md** - Úplné info
