"""GIN-EXP-014  AArch64 and RISC-V division, executed under emulation.

Hypotheses: GIN-H-038 (the specification models of ginsdk.machine for AArch64
SDIV/UDIV and RISC-V DIV/DIVU/REM/REMU agree with the instructions as executed by
an independent implementation of those ISAs), GIN-H-039 (tininess detection is
ISA-dependent: an operation whose exact result lies just below the smallest normal
number and rounds up to it raises underflow under before-rounding detection only).

Method.  `machine/isa_div.c` is compiled freestanding (no libc) with
`clang --target={aarch64,riscv64}-linux-gnu -O1 -nostdlib -static -fuse-ld=lld`
and executed with QEMU user-mode emulation.  Operands are volatile, so the
division instructions are emitted.  The program reads the floating-point status
register directly (AArch64 FPSR, RISC-V fflags).  The x86-64 tininess probe runs
natively (gcc, fenv.h).

Status of the evidence.  These are EMULATOR measurements: they test the SDK's
models against QEMU's implementation of the two ISAs, which is independent of
this repository but is not hardware.  They do not replace measurements on
physical AArch64 or RISC-V processors (GIN-OPEN-009).  Skipped cleanly when clang,
lld or qemu are missing.
"""
import os
import shutil
import subprocess

from common import HERE, tool_version, write
from ginsdk import machine as M

SRC = os.path.join(HERE, "machine", "isa_div.c")
BUILD = os.path.join(HERE, "machine", "build")
os.makedirs(BUILD, exist_ok=True)

AARCH64_FPSR = {0: "invalid", 1: "divideByZero", 2: "overflow", 3: "underflow", 4: "inexact"}
RISCV_FFLAGS = {4: "invalid", 3: "divideByZero", 2: "overflow", 1: "underflow", 0: "inexact"}
FDIV_CASES = ["1/0", "0/0", "-1/0", "1e308/1e-10", "2.2250738585072014e-308/0.5", "0/1"]


def flags(bits: int, table: dict) -> list[str]:
    return sorted(name for b, name in table.items() if bits >> b & 1)


def run_isa(isa: str) -> dict:
    exe = os.path.join(BUILD, f"isa_div_{isa}")
    cc = subprocess.run(["clang", f"--target={isa}-linux-gnu", "-O1", "-nostdlib", "-static", "-ffreestanding", "-fno-builtin",
                         "-fuse-ld=lld", "-o", exe, SRC], capture_output=True, text=True)
    if cc.returncode:
        return {"skipped": "compile failed: " + cc.stderr.strip()[:200]}
    p = subprocess.run([f"qemu-{isa}", exe], capture_output=True, text=True, timeout=60)
    out = {"int": [], "fdiv64": [], "tiny": None, "exit": p.returncode}
    table = AARCH64_FPSR if isa == "aarch64" else RISCV_FFLAGS
    model = M.div_aarch64 if isa == "aarch64" else M.div_riscv
    fi = 0
    for line in p.stdout.splitlines():
        w = line.split()
        if w[0] == "sdiv32":
            a, b, q, r, uq, ur = int(w[1]), int(w[2]), int(w[3]), int(w[4]), int(w[6]), int(w[7])
            mo = model(a, b, 32)
            # AArch64 has no remainder instruction: C's % compiles to SDIV then MSUB (a − q·b), computed mod 2^32
            m_r = mo.remainder if mo.remainder is not None else M.wrap(a - b * mo.value, 32)
            row = {"a": a, "b": b, "quotient": q, "remainder": r, "udiv": uq, "urem": ur, "model_quotient": mo.value, "model_remainder": m_r}
            if isa == "riscv64":
                mu = M.divu_riscv(a, b, 32)
                row.update(model_udiv=mu.value, model_urem=mu.remainder)
            else:
                ua, ub = a & 0xFFFFFFFF, b & 0xFFFFFFFF
                row.update(model_udiv=0 if ub == 0 else ua // ub, model_urem=ua if ub == 0 else ua % ub)
            row["agree"] = q == mo.value and r == m_r and uq == row["model_udiv"] and ur == row["model_urem"]
            out["int"].append(row)
        elif w[0] == "fdiv64":
            out["fdiv64"].append({"case": FDIV_CASES[fi], "bits": w[1], "flags": flags(int(w[3], 16), table)})
            fi += 1
        elif w[0] == "fmul32-tiny":
            out["tiny"] = {"bits": w[1], "flags": flags(int(w[3], 16), table)}
    out["model_agreement"] = f"{sum(r['agree'] for r in out['int'])}/{len(out['int'])}"
    out["tininess"] = ("before rounding" if out["tiny"] and "underflow" in out["tiny"]["flags"] else "after rounding") if out["tiny"] else None
    return out


def x86_tiny() -> dict:
    src = os.path.join(BUILD, "tiny_x86.c")
    with open(src, "w") as f:
        f.write('#include <stdio.h>\n#include <fenv.h>\nint main(void){volatile unsigned ta=0x3f7ffffe,tb=0x00800001;float a,b;'
                '__builtin_memcpy(&a,(void*)&ta,4);__builtin_memcpy(&b,(void*)&tb,4);feclearexcept(FE_ALL_EXCEPT);volatile float z=a*b;'
                'unsigned u;__builtin_memcpy(&u,(void*)&z,4);printf("%08x %d %d\\n",u,!!fetestexcept(FE_UNDERFLOW),!!fetestexcept(FE_INEXACT));return 0;}\n')
    exe = os.path.join(BUILD, "tiny_x86")
    subprocess.run(["gcc", "-O1", src, "-o", exe, "-lm"], check=True)
    bits, uf, ix = subprocess.run([exe], capture_output=True, text=True).stdout.split()
    return {"bits": "0x" + bits, "flags": [f for f, on in (("underflow", uf), ("inexact", ix)) if on == "1"],
            "tininess": "before rounding" if uf == "1" else "after rounding"}


def main():
    need = ["clang", "ld.lld", "qemu-aarch64", "qemu-riscv64"]
    missing = [t for t in need if not shutil.which(t)]
    data = {"versions": {"clang": tool_version(["clang", "--version"]), "qemu-aarch64": tool_version(["qemu-aarch64", "--version"]),
                         "qemu-riscv64": tool_version(["qemu-riscv64", "--version"]), "gcc": tool_version(["gcc", "--version"])},
            "evidence": "emulator (QEMU user mode) for AArch64 and RISC-V; native hardware for x86-64"}
    if missing:
        data["skipped"] = f"missing tools: {', '.join(missing)}"
        print("EXP-014 skipped:", data["skipped"])
    else:
        data["aarch64"] = run_isa("aarch64")
        data["riscv64"] = run_isa("riscv64")
    data["x86_64_tiny"] = x86_tiny()
    write("GIN-EXP-014", ["GIN-H-038", "GIN-H-039"], None, data)
    if not missing:
        print("EXP-014", "aarch64", data["aarch64"]["model_agreement"], data["aarch64"]["tininess"],
              "| riscv64", data["riscv64"]["model_agreement"], data["riscv64"]["tininess"], "| x86-64", data["x86_64_tiny"]["tininess"])
        for isa in ("aarch64", "riscv64"):
            print(" ", isa, "1/0 ->", [(r["quotient"], r["remainder"]) for r in data[isa]["int"] if r["b"] == 0],
                  "fdiv flags", [(c["case"], c["flags"]) for c in data[isa]["fdiv64"]])


if __name__ == "__main__":
    main()
