#!/usr/bin/env python3
"""
🚀 STARTER KIT - Nejjednoduší Příklad Použití NovaSandbox

Tento script ukazuje jak prakticky používat NovaSandbox
v reálné aplikaci.
"""

import asyncio
from novasandbox.core import SandboxConfig, SecurityLevel
from novasandbox.providers import AppleVZHypervisor

# Vyber podle OS:
# - macOS: AppleVZHypervisor
# - Linux: FirecrackerHypervisor

async def example_1_basic_usage():
    """Příklad 1: Základní spuštění kódu"""
    print("\n" + "="*60)
    print("📋 PŘÍKLAD 1: Základní Spuštění Kódu")
    print("="*60)
    
    # Konfigurace sandboxu
    config = SandboxConfig(
        template_id="alpine-python",
        security_level=SecurityLevel.STANDARD,  # Doporučeno
        memory_mb=512,
        vcpus=2
    )
    
    # Vytvoř hypervisor
    hypervisor = AppleVZHypervisor()
    
    # Vytvoř sandbox
    sandbox = await hypervisor.create_sandbox(config)
    print(f"✅ Sandbox {sandbox.sandbox_id} vytvořen")
    
    # Spustí příkaz
    try:
        result = await sandbox.execute_command("echo 'Hello from NovaSandbox!'")
        print(f"Output: {result}")
    except Exception as e:
        print(f"Chyba: {e}")
    
    # Zastavení
    await sandbox.stop()
    print(f"✅ Sandbox zastavený")


async def example_2_untrusted_code():
    """Příklad 2: Bezpečné spuštění Untrusted Kódu"""
    print("\n" + "="*60)
    print("🔒 PŘÍKLAD 2: Untrusted Kód - Bezpečně")
    print("="*60)
    
    # Nebezpečný kód - pokusit se číst hesla
    untrusted_code = """
import sys
print("Pokusím se číst /etc/passwd...")
try:
    with open("/etc/passwd") as f:
        print(f.read())
except PermissionError as e:
    print(f"❌ Blokováno: {e}")
except Exception as e:
    print(f"❌ Systém chyba: {e}")
"""
    
    # Přísná konfigurace pro untrusted kód
    config = SandboxConfig(
        security_level=SecurityLevel.STRICT,  # 🔒 PŘÍSNÉ
        memory_mb=256,  # Malá paměť
        vcpus=1
    )
    
    hypervisor = AppleVZHypervisor()
    sandbox = await hypervisor.create_sandbox(config)
    
    # Spustit untrusted kód
    try:
        # Uložit kód do sandboxu
        cmd = f"""cat > /tmp/untrusted.py << 'PYEOF'
{untrusted_code}
PYEOF
python /tmp/untrusted.py"""
        result = await sandbox.execute_command(cmd)
        print(f"Output:\n{result}")
    except Exception as e:
        print(f"Sandbox zastavil: {e}")
    
    # Kontrola porušení
    summary = sandbox.security_manager.get_violations_summary()
    print(f"\n📊 Porušení bezpečnosti: {summary['total_violations']}")
    if summary['total_violations'] > 0:
        print(f"   Detaily: {summary['violations'][:3]}")
    
    await sandbox.stop()


async def example_3_resource_limits():
    """Příklad 3: Testování Resource Limitů"""
    print("\n" + "="*60)
    print("⚙️  PŘÍKLAD 3: Resource Limity (DOS Ochrana)")
    print("="*60)
    
    config = SandboxConfig(
        security_level=SecurityLevel.STANDARD,
        memory_mb=512,  # Max 512MB RAM
        vcpus=1         # Max 1 CPU
    )
    
    hypervisor = AppleVZHypervisor()
    sandbox = await hypervisor.create_sandbox(config)
    
    # Test 1: Memory limit
    print("\n🧠 Test paměti (512MB limit):")
    try:
        result = await sandbox.execute_command(
            "python -c \"import os; a = os.urandom(1024*1024*100); print('Alokováno 100MB')\""
        )
        print(f"   ✅ {result}")
    except Exception as e:
        print(f"   ❌ Sandbox zabil (OOM): {str(e)[:50]}")
    
    await sandbox.stop()
    
    # Test 2: CPU limit
    print("\n⚡ Test CPU (1 core limit):")
    hypervisor = AppleVZHypervisor()
    sandbox = await hypervisor.create_sandbox(config)
    
    try:
        result = await sandbox.execute_command(
            "nproc"  # Počet dostupných CPU
        )
        print(f"   CPU dostupných v sandboxu: {result}")
    except Exception as e:
        print(f"   Chyba: {e}")
    
    await sandbox.stop()


async def example_4_monitoring():
    """Příklad 4: Monitorování Sandboxu"""
    print("\n" + "="*60)
    print("📈 PŘÍKLAD 4: Monitorování")
    print("="*60)
    
    config = SandboxConfig(
        security_level=SecurityLevel.STRICT,
        memory_mb=512,
        vcpus=2
    )
    
    hypervisor = AppleVZHypervisor()
    sandbox = await hypervisor.create_sandbox(config)
    
    # Spustit něco v sandboxu
    try:
        await sandbox.execute_command("python -c \"print('Hello')\"; sleep 2")
    except:
        pass
    
    # Kontrola statistik
    stats = await sandbox.get_stats()
    print(f"\n📊 Statistika Sandboxu:")
    print(f"   ID: {sandbox.sandbox_id}")
    print(f"   Stav: {sandbox.state.value}")
    print(f"   Uptime: {sandbox.get_uptime_ms():.1f}ms")
    
    # Kontrola porušení
    summary = sandbox.security_manager.get_violations_summary()
    print(f"\n🔒 Bezpečnost:")
    print(f"   Celkem porušení: {summary['total_violations']}")
    print(f"   Průběh (sec): {summary['lifetime_seconds']:.1f}")
    
    await sandbox.stop()


async def example_5_paranoid_mode():
    """Příklad 5: Maximum Bezpečnosti (PARANOID)"""
    print("\n" + "="*60)
    print("🔐 PŘÍKLAD 5: PARANOID Režim - Maximum Ochrany")
    print("="*60)
    
    config = SandboxConfig(
        security_level=SecurityLevel.PARANOID,  # 🔐 MAXIMUM
        memory_mb=256,  # Jen 256MB
        vcpus=1         # Jen 1 CPU
    )
    
    hypervisor = AppleVZHypervisor()
    sandbox = await hypervisor.create_sandbox(config)
    print(f"✅ Sandbox vytvořen (PARANOID mode)")
    print(f"   Memory: 256MB max")
    print(f"   CPU: 1 core max")
    print(f"   Readonly rootfs: YES")
    print(f"   Kill on violation: YES")
    print(f"   Syscall logging: YES")
    
    # Pokusit se změnit /bin
    try:
        result = await sandbox.execute_command("touch /bin/test 2>&1 || echo 'Readonly'")
        print(f"\n📝 Pokus zápis do /bin: {result}")
    except:
        pass
    
    await sandbox.stop()


async def main():
    """Spustit všechny příklady"""
    print("\n" + "="*60)
    print("🚀 NOVASANDBOX STARTER KIT")
    print("="*60)
    print("Tento script ukazuje 5 praktických příkladů")
    
    try:
        await example_1_basic_usage()
    except Exception as e:
        print(f"⚠️  Příklad 1 error: {e}")
    
    try:
        await example_2_untrusted_code()
    except Exception as e:
        print(f"⚠️  Příklad 2 error: {e}")
    
    try:
        await example_3_resource_limits()
    except Exception as e:
        print(f"⚠️  Příklad 3 error: {e}")
    
    try:
        await example_4_monitoring()
    except Exception as e:
        print(f"⚠️  Příklad 4 error: {e}")
    
    try:
        await example_5_paranoid_mode()
    except Exception as e:
        print(f"⚠️  Příklad 5 error: {e}")
    
    print("\n" + "="*60)
    print("✅ STARTER KIT HOTOV")
    print("="*60)
    print("\n💡 Dalších příklady najdete v:")
    print("   - examples/basic_usage.py")
    print("   - examples/api_server.py")
    print("   - examples/performance_test.py")
    print("   - DEPLOYMENT.md (Detailný průvodce)")


if __name__ == "__main__":
    asyncio.run(main())
