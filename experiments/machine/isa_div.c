/* Freestanding probe of integer division and IEEE flags on AArch64 and RISC-V
 * (GIN-EXP-014).  Built with clang --target=<isa>-linux-gnu -nostdlib -static
 * and run under qemu-user.  No libc: results are written with a raw write(2).
 * Operands are volatile so the compiler must emit the division instructions.
 * Output lines:  name a b quotient remainder   and   fp name result-bits flags
 */
typedef unsigned long u64; typedef long i64; typedef int i32; typedef unsigned int u32;

static long sys3(long n, long a, long b, long c) {
#if defined(__aarch64__)
  register long x8 __asm__("x8") = n, x0 __asm__("x0") = a, x1 __asm__("x1") = b, x2 __asm__("x2") = c;
  __asm__ volatile("svc 0" : "+r"(x0) : "r"(x8), "r"(x1), "r"(x2) : "memory");
  return x0;
#elif defined(__riscv)
  register long a7 __asm__("a7") = n, a0 __asm__("a0") = a, a1 __asm__("a1") = b, a2 __asm__("a2") = c;
  __asm__ volatile("ecall" : "+r"(a0) : "r"(a7), "r"(a1), "r"(a2) : "memory");
  return a0;
#endif
}
#define SYS_WRITE 64
#define SYS_EXIT 93
static char buf[8192]; static int pos;
static void puts_(const char *s) { while (*s) buf[pos++] = *s++; }
static void puti(i64 v) { char t[24]; int n = 0; u64 u = v < 0 ? -(u64)v : (u64)v; if (v < 0) buf[pos++] = '-'; do { t[n++] = '0' + u % 10; u /= 10; } while (u); while (n) buf[pos++] = t[--n]; }
static void putx(u64 v) { const char *h = "0123456789abcdef"; puts_("0x"); for (int i = 60; i >= 0; i -= 4) buf[pos++] = h[(v >> i) & 15]; }

static volatile i32 A[] = {1, 0, -7, -2147483647 - 1, -7, 7, 7, 2147483647};
static volatile i32 B[] = {0, 0, 0, -1, 2, -2, 2, 1};

static u64 fpflags_read_clear(void) {
#if defined(__aarch64__)
  u64 v; __asm__ volatile("mrs %0, fpsr" : "=r"(v) :: "memory"); __asm__ volatile("msr fpsr, xzr"); return v & 0x9f; /* IDC|IXC|UFC|OFC|DZC|IOC */
#elif defined(__riscv)
  u64 v; __asm__ volatile("csrrw %0, fflags, zero" : "=r"(v) :: "memory"); return v & 0x1f; /* NV DZ OF UF NX */
#endif
}
static volatile double D[] = {1.0, 0.0, -1.0, 1e308, 2.2250738585072014e-308, 0.0};
static volatile double E[] = {0.0, 0.0, 0.0, 1e-10, 0.5, 1.0};
static volatile double SINK; static volatile float SINKF;
/* FA = 1 − 2^-23 (0x3f7ffffe), FB = 2^-126·(1 + 2^-23) (0x00800001): the exact product 2^-126·(1 − 2^-46) lies just
   below the smallest normal and rounds UP to it.  Underflow is flagged iff tininess is detected BEFORE rounding. */
static volatile u32 FAB = 0x3f7ffffe, FBB = 0x00800001;

void _start(void) {
  for (int i = 0; i < 8; i++) {
    i32 a = A[i], b = B[i];
    i32 q = a / b, r = a % b;           /* UB in ISO C for b == 0 or overflow: we observe the instruction */
    u32 uq = (u32)a / (u32)b, ur = (u32)a % (u32)b;
    puts_("sdiv32 "); puti(a); puts_(" "); puti(b); puts_(" "); puti(q); puts_(" "); puti(r);
    puts_(" udiv32 "); puti(uq); puts_(" "); puti(ur); puts_("\n");
  }
  fpflags_read_clear();
  for (int i = 0; i < 6; i++) {
    double x = D[i], y = E[i]; SINK = x / y; __asm__ volatile("" ::: "memory"); double z = SINK; u64 bits; __builtin_memcpy(&bits, &z, 8);
    u64 f = fpflags_read_clear();
    puts_("fdiv64 "); putx(bits); puts_(" flags "); putx(f); puts_("\n");
  }
  { float fa, fb; u32 ta = FAB, tb = FBB; __builtin_memcpy(&fa, &ta, 4); __builtin_memcpy(&fb, &tb, 4); SINKF = fa * fb; __asm__ volatile("" ::: "memory"); float z = SINKF; u32 bits; __builtin_memcpy(&bits, &z, 4); u64 f = fpflags_read_clear(); puts_("fmul32-tiny "); putx(bits); puts_(" flags "); putx(f); puts_("\n"); }
  sys3(SYS_WRITE, 1, (long)buf, pos);
  sys3(SYS_EXIT, 0, 0, 0);
  for (;;) {}
}
