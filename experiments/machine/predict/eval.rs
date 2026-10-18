// GIN-EXP-013 oracle: Rust i32 arithmetic, debug build (overflow checks on).
use std::io::BufRead;
fn main() {
    std::panic::set_hook(Box::new(|_| {}));
    for line in std::io::stdin().lock().lines() {
        let line = line.unwrap(); let t: Vec<&str> = line.split_whitespace().collect();
        let a = t[0].parse::<i64>().unwrap() as i32; let b = t[2].parse::<i64>().unwrap() as i32; let op = t[1].to_string();
        let r = std::panic::catch_unwind(move || match op.as_str() { "+" => a + b, "-" => a - b, "*" => a * b, "/" => a / b, _ => a % b });
        match r { Ok(v) => println!("value {}", v), Err(_) => println!("exception panic") }
    }
}
