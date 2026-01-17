"""
Instrukce pro vytvoření Firecracker templates
"""

INSTRUCTIONS = """
# Vytvoření Alpine Linux šablony pro Firecracker

## 1. Instalace Firecracker

```bash
# Na Linux
curl -s https://raw.githubusercontent.com/firecracker-microvm/firecracker/master/tools/devtool | bash
# Nebo:
wget https://github.com/firecracker-microvm/firecracker/releases/download/v1.4.0/firecracker-v1.4.0-x86_64.tgz
tar xzf firecracker-v1.4.0-x86_64.tgz
sudo mv release-v1.4.0-x86_64/firecracker-v1.4.0-x86_64 /usr/bin/firecracker
sudo chmod +x /usr/bin/firecracker
```

## 2. Vytvoření Alpine rootfs

```bash
mkdir -p templates/alpine-python
cd templates/alpine-python

# Stažení Alpine rootfs
ALPINE_VERSION=3.18
ALPINE_ARCH=x86_64
wget https://dl-cdn.alpinelinux.org/alpine/v${ALPINE_VERSION}/releases/${ALPINE_ARCH}/alpine-minirootfs-${ALPINE_VERSION}.0-${ALPINE_ARCH}.tar.gz

# Vytvoření rootfs image
dd if=/dev/zero of=rootfs.ext4 bs=1M count=500
mkfs.ext4 -F rootfs.ext4

# Připojení a naplnění
mkdir -p mnt
sudo mount rootfs.ext4 mnt
sudo tar xzf alpine-minirootfs-${ALPINE_VERSION}.0-${ALPINE_ARCH}.tar.gz -C mnt

# Instalace Python
sudo chroot mnt apk update
sudo chroot mnt apk add python3 python3-pip curl wget bash
sudo chroot mnt apk add musl-dev gcc g++  # Pro pip balíčky

# Odpojení
sudo umount mnt
rmdir mnt
```

## 3. Bootování Firecracker kernelu

```bash
# Stažení jádra
KERNEL_VERSION=6.1.0
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KERNEL_VERSION}.tar.xz
tar xJf linux-${KERNEL_VERSION}.tar.xz
cd linux-${KERNEL_VERSION}

# Konfigurace pro Firecracker
make defconfig
# Úprava pro Firecracker specifika:
# - Vypnout nepotřebné moduly pro rychlejší boot
echo "CONFIG_VIRTIO_NET=y" >> .config
echo "CONFIG_SERIAL_8250=y" >> .config
echo "CONFIG_SERIAL_8250_CONSOLE=y" >> .config

make vmlinux
cp vmlinux ../templates/alpine-python/
```

Nebo stažení precompiled:

```bash
# Firecracker projekt poskytuje precompiled kernely
wget https://github.com/firecracker-microvm/firecracker/releases/download/v1.4.0/vmlinux-5.10.217
mv vmlinux-5.10.217 templates/alpine-python/vmlinux
```

## 4. Test šablony

```bash
python -c "
from core.template_manager import TemplateManager
tm = TemplateManager('templates')
print(f'Dostupné šablony: {tm.list_templates()}')

template = tm.get_template('alpine-python')
if template:
    print(f'Šablona: {template.name}')
    print(f'Paměť: {template.memory_mb}MB')
    print(f'vCPU: {template.vcpus}')
    print(f'Boot čas: {template.boot_time_ms}ms')
"
```

## 5. Spuštění VM

```bash
python examples/basic_usage.py
```

## Optimalizace pro rychlejší boot

1. **Kernel** - minimální kernely s vypnutými nepotřebnými moduly
2. **Initrd** - místo init=/sbin/init použít init=/sbin/busybox
3. **Filesystem** - ext4 bez journalu
4. **CPU** - ht_enabled=False v machine-config
5. **Tahy k síťi** - vynechat pokud není potřeba

Očekávané boot časy:
- S minimálním kernelem a Alpine: <100ms
- S Python: 120-150ms
- S extra aplikacemi: 150-300ms

"""

if __name__ == "__main__":
    print(INSTRUCTIONS)
