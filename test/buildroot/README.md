# Buildroot

If you are interested in learning about Buildroot, check
https://bootlin.com/doc/training/buildroot/buildroot-slides.pdf

### Binary Image Generation (git option)

```
git clone https://gitlab.com/buildroot.org/buildroot.git
make initiallinkconfig
cd buildroot
make punxa_rv64_defconfig
make
cd ..

```


### Binary Image Generation (Download release option)

Download latest long term support release

```
wget https://buildroot.org/downloads/buildroot-2024.02.10.tar.gz
tar -xvf buildroot-2024.02.10.tar.gz
cd buildroot-2024.02.10
vi configs/punxa_rv64_defconfig
```

Introduce the following content
```
# Architecture
BR2_riscv=y
BR2_RISCV_64=y

# System
BR2_TARGET_GENERIC_GETTY=y

# Filesystem
BR2_TARGET_ROOTFS_EXT2=y

# Image
BR2_ROOTFS_POST_IMAGE_SCRIPT="board/qemu/post-image.sh"
BR2_ROOTFS_POST_SCRIPT_ARGS="$(BR2_DEFCONFIG)"

# Linux headers same as kernel
BR2_PACKAGE_HOST_LINUX_HEADERS_CUSTOM_6_1=y

# Kernel
BR2_LINUX_KERNEL=y
BR2_LINUX_KERNEL_CUSTOM_VERSION=y
BR2_LINUX_KERNEL_CUSTOM_VERSION_VALUE="6.1.44"
#BR2_LINUX_KERNEL_DEFCONFIG="punxa_rv64"
BR2_LINUX_KERNEL_IMAGE=y
BR2_LINUX_KERNEL_CUSTOM_CONFIG_FILE="punxa_rv64_linux_defconfig"

# Bootloader
BR2_TARGET_OPENSBI=y
BR2_TARGET_OPENSBI_CUSTOM_VERSION=y
BR2_TARGET_OPENSBI_CUSTOM_VERSION_VALUE="1.2"
BR2_TARGET_OPENSBI_PLAT="generic"

# host-qemu for gitlab testing
BR2_PACKAGE_HOST_QEMU=y
BR2_PACKAGE_HOST_QEMU_SYSTEM_MODE=y
```

Then compile

```
make punxa_rv64_devconfig
make
```

it will fail

```
cd output/build/linux-6.1.44/arch/riscv/configs/
ln -s defconfig rv64_defconfig
```

It will compile too many things. Do

```
make linux-menuconfig
```

and disable:

- Virtualization
- Enable loadable module support
- Networking Support
- Device Drivers / PCI support
- Device Drivers / Seruak ATA...
- Device Drivers / Multiple devices
- Device Drivers / SPI
- Device Drivers / USB support
- Device Drivers / MMC/SD/SDIO

Select
Kernel hacking / Compile-time ... / Debug Information / Rely on the toolchain...

Select the following kernel command line
console=ttyS0,115200 earlycon=uart8250,mmio32,0x10000000

This should work by linking to the linux defconfig
```
cd output/build/linux-6.1.44/arch/riscv/configs/
ln -s ../../../../../../configs/punxa_rv64_linux_defconfig .
```

```
cd output/build/linux-6.1.44/arch/riscv/boot/dts/punxa
ln -s ../../../../../../../../../punxa_rv64.dts  .
```

then

```
make
```

to validate that the dtb is valid 


Then we need the Kernel Symbols
```
cd ..
buildroot-2024.02.10/output/host/bin/riscv64-linux-objdump  -t buildroot-2024.02.10/output/build/linux-6.1.44/vmlinux > vmlinux.sym
```




