// GIN-EXP-013 oracle: Go int32 arithmetic.
package main

import ("bufio"; "fmt"; "os"; "strconv"; "strings")

func apply(a, b int32, op string) (r int32, err string) {
	defer func() { if e := recover(); e != nil { err = fmt.Sprint(e) } }()
	switch op { case "+": r = a + b; case "-": r = a - b; case "*": r = a * b; case "/": r = a / b; default: r = a % b }
	return
}
func main() {
	sc := bufio.NewScanner(os.Stdin)
	for sc.Scan() {
		t := strings.Fields(sc.Text()); A, _ := strconv.ParseInt(t[0], 10, 64); B, _ := strconv.ParseInt(t[2], 10, 64)
		r, err := apply(int32(A), int32(B), t[1])
		if err != "" { fmt.Println("exception panic:", err) } else { fmt.Println("value", r) }
	}
}
