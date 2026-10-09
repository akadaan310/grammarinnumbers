// GIN-EXP-013 oracle: Java int arithmetic.
import java.io.*;
public class Eval {
  public static void main(String[] x) throws IOException {
    BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
    for (String line; (line = in.readLine()) != null; ) {
      String[] t = line.trim().split(" "); int a = (int) Long.parseLong(t[0]), b = (int) Long.parseLong(t[2]);
      try { int r = switch (t[1]) { case "+" -> a + b; case "-" -> a - b; case "*" -> a * b; case "/" -> a / b; default -> a % b; };
        System.out.println("value " + r); }
      catch (ArithmeticException e) { System.out.println("exception " + e.getClass().getSimpleName()); }
    }
  }
}
