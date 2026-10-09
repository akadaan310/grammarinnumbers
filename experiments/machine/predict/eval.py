"""GIN-EXP-013 oracle: Python int arithmetic (true division for '/')."""
import sys
for line in sys.stdin:
    a, op, b = line.split()
    a, b = int(a), int(b)
    try:
        r = {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b, "%": lambda: a % b}[op]()
        print("value", repr(r))
    except ZeroDivisionError as e:
        print("exception ZeroDivisionError")
