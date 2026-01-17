# 🔒 BEZPEČNOSTNÍ PRŮVODCE - NovaSandbox

## Přehled hrozeb a mitigace

### 1. **Host Breakout** (Únik z VM)
Útočník se snaží uniknout z VM a přistoupit k hostitelskému systému.

**Implementovaná ochrana:**
- ✅ **Kernel namespacing** - Oddělit network, PID, IPC namespace
- ✅ **TAP interface izolace** - Network je oddělena od hostitele
- ✅ **Readonly rootfs** (PARANOID) - Zákaz zápisu do kritických souborů
- ✅ **Seccomp filtering** - Blokování nebezpečných syscalls
  - `ptrace`, `clone`, `fork`, `vfork` - Debug/escape prevence
  - `mount`, `umount2` - Zákaz mountování dalších FS
  - `module_load` - Zákaz kernel modulů
- ✅ **File access control** - Blokování cest `/../`, `/host`, atd.

**Použití (maximální ochrana):**
```python
from novasandbox.core import SandboxConfig, SecurityLevel

config = SandboxConfig(
    security_level=SecurityLevel.PARANOID,
    # Výsledek:
    # - Maximální seccomp filtrování
    # - 512MB RAM limit
    # - 1 vCPU limit
    # - Readonly rootfs
)
```

---

### 2. **Denial of Service (DOS)** 
Útočník vyčerpá resursy a zhroutí sandbox/host.

**Implementovaná ochrana:**
- ✅ **Memory limits** - cgroups memory.limit_in_bytes
  - BASIC: Bez limitu
  - STANDARD: 2048MB
  - STRICT: 1024MB
  - PARANOID: 512MB

- ✅ **CPU limits** - cpuset.cpus omezení
  - BASIC: Bez limitu
  - STANDARD: 4 vCPU max
  - STRICT: 2 vCPU max
  - PARANOID: 1 vCPU max

- ✅ **Process limits** - pids.max
  - STANDARD: 1000 procesů max
  - STRICT: Nižší limit
  
- ✅ **Rate limiting** - Síťové requesty
  ```python
  # Automaticky limituje 1000 requestů/sec per sandbox
  # Lze konfigurovat: rate_limit_mbps
  ```

- ✅ **File descriptor limits**
  - max_open_files: 1024 (nastavitelné)

**Testování DOS odolnosti:**
```bash
# Stress test v sandboxu
stress-ng --vm 1 --vm-bytes 100M --timeout 10s

# Host zůstane stabilní díky cgroups limitům
```

---

### 3. **Network Exploitation**
Útočník získá přístup k síti/porům mimo sandbox.

**Implementovaná ochrana:**
- ✅ **IP whitelist/blacklist**
  ```python
  policy = SecurityPolicy(
      blocked_ips={"192.168.1.1", "10.0.0.0/8"}
  )
  ```

- ✅ **Port whitelist**
  ```python
  policy = SecurityPolicy(
      allowed_ports={80, 443, 8080}  # Pouze tyto porty
  )
  ```

- ✅ **Rate limiting per connection**
  ```python
  policy = SecurityPolicy(
      max_network_connections=10,
      rate_limit_mbps=100  # 100 Mbps max
  )
  ```

- ✅ **Raw socket blokace**
  ```python
  policy = SecurityPolicy(
      allow_raw_sockets=False  # Zákaz raw socketu
  )
  ```

- ✅ **Network namespace izolace**
  - Sandbox má vlastní network namespace
  - Přístup jen přes NAT překlad

---

### 4. **Privilege Escalation**
Útočník se pokusí získat root přístup v sandboxu nebo na hostiteli.

**Implementovaná ochrana:**
- ✅ **Setuid bit blokace**
  ```python
  policy = SecurityPolicy(
      allow_setuid=False  # Zákaz setuid binaries
  )
  ```

- ✅ **Capabilities dropping** - Linux capabilities omezeny
  - CAP_NET_ADMIN
  - CAP_SYS_ADMIN
  - CAP_SYS_PTRACE

- ✅ **Syscall filtering** - Blokování escalation syscalls

---

### 5. **Information Disclosure**
Útočník se snaží číst citlivé informace.

**Implementovaná ochrana:**
- ✅ **Audit logging**
  ```python
  policy = SecurityPolicy(
      log_syscalls=True,    # Log všech syscalls
      log_network=True      # Log síťového provozu
  )
  
  # Potom:
  summary = security_manager.get_violations_summary()
  # Contains 'syscall_log', 'violations'
  ```

- ✅ **Proc filesystem restricce** - /proc/sys hidden
- ✅ **Device whitelist** - Jen `/dev/null`, `/dev/zero`, `/dev/urandom`

---

### 6. **Supply Chain / Code Injection**
Útočník podstrčí malicious kód do image nebo šablony.

**Implementovaná ochrana:**
- ✅ **Image signing** (manuální, doporučeno)
  ```bash
  # Vytvoření SHA256 hashe image
  sha256sum alpine-python.img > alpine-python.img.sha256
  
  # Ověření:
  sha256sum -c alpine-python.img.sha256
  ```

- ✅ **Immutable templates**
  ```python
  # Templates jsou read-only, nelze měnit za běhu
  # Verze je v názvu: alpine-python-v1.2.3.json
  ```

- ✅ **Signed kernels** (volitelně)

---

## Úrovně Bezpečnosti - Detailní Porovnání

| Funkce | BASIC | STANDARD | STRICT | PARANOID |
|--------|-------|----------|--------|----------|
| **Seccomp** | ❌ | ✅ | ✅ | ✅ |
| **AppArmor** | ❌ | ✅ | ✅ | ✅ |
| **Cgroups** | ❌ | ✅ | ✅ | ✅ |
| **Memory limit** | ∞ | 2GB | 1GB | 512MB |
| **CPU limit** | ∞ | 4 | 2 | 1 |
| **Network connections** | ∞ | 500 | 10 | 5 |
| **Raw sockets** | ✅ | ✅ | ❌ | ❌ |
| **Ptrace/Debug** | ✅ | ✅ | ❌ | ❌ |
| **Setuid** | ✅ | ✅ | ❌ | ❌ |
| **Host mount** | ✅ | ❌ | ❌ | ❌ |
| **Readonly rootfs** | ❌ | ❌ | ❌ | ✅ |
| **Kill on violation** | ❌ | ❌ | ✅ | ✅ |
| **Syscall logging** | ❌ | ❌ | ✅ | ✅ |
| **Network logging** | ❌ | ❌ | ❌ | ✅ |

---

## Praktické Příklady

### Příklad 1: Bezpečný AI Agent Sandbox
```python
from novasandbox.core import SandboxConfig, SecurityLevel
from novasandbox.providers import FirecrackerHypervisor

# Konfigurace pro untrusted kód
config = SandboxConfig(
    template_id="alpine-python",
    security_level=SecurityLevel.STRICT,
    memory_mb=1024,
    vcpus=2
)

# Sandbox bude:
# - Seccomp filtrovaný
# - Cgroups limitovaný
# - Kill on violation
```

### Příklad 2: Custom Bezpečnostní Politika
```python
from novasandbox.core.security import SecurityPolicy

policy = SecurityPolicy(
    max_memory_mb=512,
    max_vcpus=1,
    max_processes=100,
    
    # Network omezení
    allowed_ports={443, 8080},  # Jen HTTPS a 8080
    blocked_ips={"192.168.0.0/16"},  # Blokovat LAN
    rate_limit_mbps=10,  # Max 10 Mbps
    
    # Execution omezení
    allow_setuid=False,
    allow_ptrace=False,
    allow_kernel_modules=False,
    
    # Monitoring
    enable_seccomp=True,
    log_syscalls=True,
    kill_on_violation=True
)

config = SandboxConfig(
    custom_security_policy=policy
)
```

### Příklad 3: Monitoring a Audit
```python
sandbox = await hypervisor.create_sandbox(config)

# ... sandbox běží a potenciálně porušuje pravidla ...

# Pak kontrolujeme:
summary = sandbox.security_manager.get_violations_summary()
print(f"Violations: {summary['total_violations']}")
print(f"Lifetime: {summary['lifetime_seconds']}s")

for violation in summary['violations']:
    print(f"  - {violation['type']}: {violation.get('message')}")
```

### Příklad 4: Testování Breakoutu
```bash
# V sandboxu se pokusit o breakout:
cd /host  # ❌ Zablokováno - "host_breakout_attempt"
cat /../../../etc/passwd  # ❌ Zablokováno
strace -p 1  # ❌ Zablokováno (ptrace) - SecurityLevel=STRICT

# Pokud kill_on_violation=True:
# Sandbox je automaticky zabitý
```

---

## Best Practices

### 1. **Vyberte správnou úroveň bezpečnosti**
```
AI Agent (untrusted)     → STRICT nebo PARANOID
Internal tool (semi-trusted) → STANDARD
Testing environment      → BASIC (jen pro dev)
Production untrusted     → PARANOID
```

### 2. **Pravidelný Audit**
```python
# Cron job každou hodinu
async def audit_sandboxes():
    for sandbox in hypervisor._sandboxes.values():
        summary = sandbox.security_manager.get_violations_summary()
        if summary['total_violations'] > 10:
            logger.alert(f"Suspicious activity: {sandbox.sandbox_id}")
            await sandbox.stop()  # Kill it
```

### 3. **Firewalling**
```bash
# Hypervisor host - zákaz přístupu z internetu
sudo ufw default deny incoming
sudo ufw allow from 127.0.0.1  # Jen localhost
```

### 4. **Kernel Hardening**
```bash
# Disable unprivileged user namespaces (Linux)
echo 0 | sudo tee /proc/sys/kernel/unprivileged_userns_clone

# Disable kernel module loading
echo 1 | sudo tee /proc/sys/kernel/modules_disabled
```

### 5. **Monitoring & Alerting**
```python
# Prometheus metrics
sandbox_violations_total.labels(sandbox_id=sid, type=vtype).inc()
sandbox_memory_usage.labels(sandbox_id=sid).set(memory_mb)
sandbox_syscalls_blocked.labels(sandbox_id=sid).inc()
```

---

## Conhecidos Omezení

1. **Spectre/Meltdown**: microcode update na CPU potřeba
2. **Side-channels**: L1TF, L1D flush vyžaduje kernel 5.1+
3. **Firecracker boot**: Není pod 100ms bez custom kernelu
4. **AppArmor**: Vyžaduje AppArmor SELinux kernel modul

---

## Reporting Security Issues

Pokud najdete bezpečnostní problém:
1. ❌ Neposílejte na GitHub Issues (public)
2. ✅ Pošlete na: security@novasandbox.dev (private)
3. ✅ Tým má 48 hodin na odpověď

---

## Reference

- **Firecracker Security**: https://github.com/firecracker-microvm/firecracker/blob/master/docs/design.md#threat-containment
- **Seccomp Syscalls**: https://man7.org/linux/man-pages/man2/seccomp.2.html
- **Cgroups v2**: https://kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
- **Linux Capabilities**: https://man7.org/linux/man-pages/man7/capabilities.7.html
