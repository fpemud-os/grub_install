import enum


class Platform(enum.Enum):
    I386_PC = "i386-pc"
    I386_EFI = "i386-efi"
    I386_QEMU = "i386-qemu"
    I386_COREBOOT = "i386-coreboot"
    I386_MULTIBOOT = "i386-multiboot"
    I386_IEEE1275 = "i386-ieee1275"
    I386_XEN = "i386-xen"
    I386_XEN_PVH = "i386-xen_pvh"
    X86_64_EFI = "x86_64-efi"
    X86_64_XEN = "x86_64_xen"
    ARM_UBOOT = "arm-uboot"
    ARM_COREBOOT = "arm-coreboot"
    ARM_EFI = enum.auto()                                   # FIXME
    ARM64_EFI = "arm64-efi"
    IA64_EFI = enum.auto()                                  # FIXME
    SPARC64_IEEE1275 = enum.auto()                          # FIXME
    POWERPC_IEEE1275 = enum.auto()                          # FIXME
    MIPS_ARC = enum.auto()                                  # FIXME
    MIPS_QEMU_MIPS = enum.auto()                            # FIXME
    MIPSEL_ARC = enum.auto()                                # FIXME
    MIPSEL_LOONGSON = enum.auto()                           # FIXME
    MIPSEL_QEMU_MIPS = enum.auto()                          # FIXME
    RISCV32_EFI = enum.auto()                               # FIXME
    RISCV64_EFI = enum.auto()                               # FIXME
