# 🔐 Bezpečnostní Modul NovaSandbox

Tento dokument vysvětluje, jak NovaSandbox chránit váš systém před:
- **Host breakouty** (únik z VM)
- **DOS útoky** (vyčerpání prostředků)
- **Privilege escalation** (zvýšení oprávnění)
- **Network exploitací** (síťové útoky)
- **Code injection** (vložení škodlivého kódu)

## 🚀 Rychlý start - Bezpečné použití

### Varianty bezpečnosti:

```python
from novasandbox.core import SandboxConfig, SecurityLevel

# ❌ NEBEZPEČNÉ - Jen pro testování
config = SandboxConfig(security_level=SecurityLevel.BASIC)

# ✅ DOPORUČENÉ - Standardní aplikace
config = SandboxConfig(security_level=SecurityLevel.STANDARD)

# 🔒 PŘÍSNÉ - Untrusted kód
config = SandboxConfig(security_level=SecurityLevel.STRICT)

# 🔐 PARANOIDNÍ - Maximum ochrany
config = SandboxConfig(security_level=SecurityLevel.PARANOID)
```

## 📊 Srovnění úrovní bezpečnosti

| Vlastnost | BASIC | STANDARD | STRICT | PARANOID |
|-----------|-------|----------|--------|----------|
| Seccomp filtrování | ❌ | ✅ | ✅ | ✅ |
| cgroups limity | ❌ | ✅ | ✅ | ✅ |
| AppArmor | ❌ | ✅ | ✅ | ✅ |
| **RAM limit** | ∞ | 2GB | 1GB | **512MB** |
| **CPU limit** | ∞ | 4x | 2x | **1x** |
| **Max procesy** | ∞ | 1000 | 100 | **50** |
| Readonly rootfs | ❌ | ❌ | ❌ | ✅ |
| Raw sockets | ✅ | ✅ | ❌ | ❌ |
| Ptrace/Debug | ✅ | ✅ | ❌ | ❌ |
| Setuid binary | ✅ | ✅ | ❌ | ❌ |
| Host mount | ✅ | ❌ | ❌ | ❌ |
| Kill on violation | ❌ | ❌ | ✅ | ✅ |

## 🛡️ Implementované Ochraně

### 1️⃣ Seccomp (Syscall Filtering)

Blokuje nebezpečné syscalls na úrovni kernelu:

```python
# Automaticky blokované:
ptrace      # Debugging/escape
clone       # Nové procesy
fork        # Nové procesy
vfork       # Nové procesy
mount       # Filesystem změny
umount2     # Filesystem změny
module_load # Kernel moduly
```

**Výhody:**
- ✅ Nejrychlejší - hardware filtrace
- ✅ Všechny procesy v sandboxu jsou filtrované
- ✅ Nelze obejít bez recompiluování kernelu

### 2️⃣ Cgroups (Resource Control)

Limituje přístup k HW resourcům:

```python
# Memory
memory.limit_in_bytes = 1GB  # Max paměť

# CPU
cpuset.cpus = 0-3  # Jen CPU cores 0-3

# Procesy
pids.max = 1000  # Max 1000 procesů

# Network
net.ipv4.tcp_max_syn_backlog = 100
```

**Výhody:**
- ✅ Host není ohrožen DOS
- ✅ Sandbox se zhroutí, ne celý systém
- ✅ Granulární kontrol na úrovni cgroup

### 3️⃣ Network Namespaces

Každý sandbox má vlastní síť:

```
┌─────────────────────────────────┐
│ SANDBOX (Network Namespace)     │
│                                 │
│  eth0: 172.16.0.2              │
│  ├─ Běžné porty (1024+)         │
│  └─ NAT překlad na host         │
│                                 │
│ [Izolován od ostatních]         │
└─────────────────────────────────┘
      ↓ (NAT překlad)
┌─────────────────────────────────┐
│ HOST NETWORK                    │
│  eth0: 192.168.1.100           │
└─────────────────────────────────┘
```

### 4️⃣ AppArmor (Mandatory Access Control)

Kontroluje přístup k souborům a prostředkům:

```
Sandbox profile:
  /proc/sys/** deny,         # Zakázaný /proc/sys
  /host/** deny,             # Zakázaný /host
  /etc/shadow r,             # Čitelný shadow
  @{HOME}/** rw,             # RW domovský adresář
```

### 5️⃣ File Access Control

Vlastní vrstva ochrany souborů:

```python
# Automaticky blokované:
/host/...           # Breakout
/../../../etc/passwd # Directory traversal
/proc/sys/...       # System config
/proc/mem           # Raw memory
```

## 📋 Praktické Příklady

### Příklad 1: AI Agent s Untrusted Kódem

```python
from novasandbox.core import SandboxConfig, SecurityLevel
from novasandbox.providers import FirecrackerHypervisor

# Konfigurace pro untrusted AI kód
config = SandboxConfig(
    template_id="alpine-python",
    security_level=SecurityLevel.STRICT,
    
    # Extra limity
    memory_mb=512,
    vcpus=1
)

# Výsledná ochrana:
# ✅ Seccomp filtrování
# ✅ cgroups limity (512MB, 1 CPU)
# ✅ AppArmor profil
# ✅ Network izolace
# ✅ Kill on violation
```

### Příklad 2: Custom Politika

```python
from novasandbox.core.security import SecurityPolicy

policy = SecurityPolicy(
    # Přísné limity
    max_memory_mb=256,
    max_vcpus=1,
    max_processes=10,
    
    # Network: Jen HTTPS
    allowed_ports={443},
    blocked_ips={"192.168.0.0/16", "10.0.0.0/8"},
    rate_limit_mbps=5,
    
    # Execution
    allow_setuid=False,
    allow_ptrace=False,
    allow_raw_sockets=False,
    allow_kernel_modules=False,
    
    # Audit
    enable_seccomp=True,
    log_syscalls=True,
    kill_on_violation=True
)

config = SandboxConfig(custom_security_policy=policy)
```

### Příklad 3: Monitoring & Audit

```python
sandbox = await hypervisor.create_sandbox(config)

# ... sandbox běží ...

# Kontrola porušení:
summary = sandbox.security_manager.get_violations_summary()

print(f"Violations: {summary['total_violations']}")
print(f"Lifetime: {summary['lifetime_seconds']}s")

for violation in summary['violations'][-10:]:  # Poslední 10
    print(f"  {violation['type']}: {violation.get('message')}")

# Syscall log (jen STRICT+):
syscall_log = sandbox.security_manager._syscall_log
for entry in syscall_log[-50:]:
    print(f"  {entry['syscall']} -> {entry['allowed']}")
```

## 🔍 Testování Bezpečnosti

### Test 1: Host Breakout

```bash
# V sandboxu se pokusit:
ls -la /host  # ❌ BLOKOVÁNO
cat /../../../etc/passwd  # ❌ BLOKOVÁNO
```

**Výsledek (STANDARD+):**
```
Cannot access '/host': Permission denied
Cannot access '/../../../etc/passwd': No such file
```

### Test 2: DOS Attack

```bash
# Fork bomb:
:(){ :|:& };:  # ❌ BLOKOVÁNO (fork syscall)

# Memory exhaustion:
python -c "a = [1]*1000000000"  # ❌ BLOKOVÁNO (cgroups)
```

**Výsledek:**
```
Out of memory: Kill process (sandbox)
Killed
```

### Test 3: Privilege Escalation

```bash
# Ptrace (STRICT):
strace ls  # ❌ BLOKOVÁNO

# Setuid (STRICT):
sudo -i  # ❌ BLOKOVÁNO

# Kernel module (STRICT):
insmod evil.ko  # ❌ BLOKOVÁNO
```

### Test 4: Network Exploitation

```bash
# Blokovaná IP (se polítikou):
nc -zv 192.168.1.1 22  # ❌ BLOKOVÁNO

# Raw socket (STRICT):
python -c "import socket; socket.socket(socket.AF_INET, socket.SOCK_RAW)"
# ❌ BLOKOVÁNO
```

## ⚙️ Linux Kernel Hardening

Doporučujeme:

```bash
# Zákaz unprivileged user namespaces
echo 0 | sudo tee /proc/sys/kernel/unprivileged_userns_clone

# Zákaz kernel module loading
echo 1 | sudo tee /proc/sys/kernel/modules_disabled

# Spectre/Meltdown mitigation
# (Hardware + microcode update)

# Verbose audit
sudo auditctl -a exit,always -F arch=b64 -S execve
```

## 📈 Performance Impact

Bezpečnost má cenu, ale NovaSandbox je optimalizovaný:

| Feature | Performance Cost |
|---------|------------------|
| Seccomp | ~0.1% (hardware filtrování) |
| Cgroups | ~1% (accounting overhead) |
| AppArmor | ~1-2% (path checks) |
| **Celkem** | **~2-3%** |

**Porovnání:** Docker má ~5-10% overhead.

## 🚨 Co Dělat Při Porušení

```python
try:
    sandbox = await hypervisor.create_sandbox(config)
except SecurityViolation as e:
    logger.error(f"Security violation: {e}")
    # 1. Log incident
    # 2. Stop sandbox
    # 3. Notify administrator
    # 4. Audit trail
    # 5. Možné: Ban user/IP
```

## 📚 Reference

- [Firecracker Security](https://github.com/firecracker-microvm/firecracker/blob/master/docs/design.md)
- [Linux Seccomp](https://man7.org/linux/man-pages/man2/seccomp.2.html)
- [Cgroups v2](https://kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [AppArmor Wiki](https://gitlab.com/apparmor/apparmor/-/wikis/home)
- [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)

---

**Připomínka:** Žádný system není 100% bezpečný. Defense-in-depth je klíč:
1. ✅ Správné zvolení úrovně bezpečnosti
2. ✅ Regular audity a monitoring
3. ✅ Kernel hardening
4. ✅ Network firewalling
5. ✅ Incident response plan
