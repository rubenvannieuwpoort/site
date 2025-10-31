{
    "title": "Assembling to raw binary",
    "date": "2025-10-31",
    "show": true
}

When developing a CPU, it is convenient to easily assembly to raw binary. This script does exactly that, using the GNU toolchain and `xxd`. In this case, it assembles to `risc-v`.

The basic idea is to use `as` to assemble, then `objcopy` to extract the raw binary, and `xxd` to display it as hex:
```
$ cat test.s
addi x1, x0, 42
add x2, x1, x1
$ riscv-elf-as test.s -o test.o
$ riscv-elf-objcopy -O binary test.o test.bin
$ xxd -p test.bin
9300a00233811000
```

As a script, we get this:
```
#!/bin/env bash

# exit if any command fails
set -e

# make a temporary directory
tmp=$(mktemp -d)

# assemble
riscv-elf-as -o "$tmp/output.o" "$1"

# extract binary
riscv-elf-objcopy -O binary "$tmp/output.o" "$tmp/output.bin"

# show binary
xxd -p "$tmp/output.bin"

# clean up temporary directory
rm -rf "$tmp"
```

Example usage (assuming the script is saved as an executable file named `riscv-elf-rawas`, in some folder that's in the current `PATH`):
```
$ cat test.s
addi x1, x0, 42
add x2, x1, x1
$ riscv-elf-rawas test.s
9300a00233811000
```
