/* GIN-EXP-013 oracle: int32 arithmetic in C (gcc -O0, x86-64).  Reads "a op b" lines;
   prints "value V" or "trap SIGFPE".  Signed overflow is undefined in ISO C; what -O0
   code happens to do is recorded as observed behaviour, not as a guarantee. */
#include <setjmp.h>
#include <signal.h>
#include <stdio.h>
static sigjmp_buf env;
static void on_fpe(int s) { (void)s; siglongjmp(env, 1); }
int main(void) {
  struct sigaction sa = {0}; sa.sa_handler = on_fpe; sigemptyset(&sa.sa_mask); sa.sa_flags = SA_NODEFER; sigaction(SIGFPE, &sa, 0);
  long long A, B; char op;
  while (scanf("%lld %c %lld", &A, &op, &B) == 3) {
    volatile int a = (int)A, b = (int)B; volatile int r = 0;
    if (sigsetjmp(env, 1)) { printf("trap SIGFPE\n"); fflush(stdout); continue; }
    switch (op) { case '+': r = a + b; break; case '-': r = a - b; break; case '*': r = a * b; break; case '/': r = a / b; break; case '%': r = a % b; break; }
    printf("value %d\n", r); fflush(stdout);
  }
  return 0;
}
