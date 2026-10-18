# Mathematical typography tests

This page exercises the mathematical constructs used in the book. The build fails if any of them does not render.

Inline: $\Sol(a, b) = \{ c \in R : b c = a \}$, $\Ann(b)$, $x \mapsto b\cdot x + d$, $\val(w) = \sum_{i=1}^{k} d_i b^{k-i}$, $2^{53}+1$, $\lfloor \log_2 n \rfloor + 1$, $a \monus b$, $\Kk, \Pp, \Gg$, $\NaN$, $\pm\infty$, $\ulp(x)$, $a \equiv b \pmod n$, $\varphi(n)$, $\mu(n)$, $\gcd(a, b)$.

Display:

$$
\Sol(a, b) = \begin{cases} \varnothing & a \notin bR,\\ c_0 + \Ann(b) & \text{otherwise.} \end{cases}
$$

$$
\sem{d_1 d_2 \cdots d_k} = \sem{d_k} \circ \cdots \circ \sem{d_1}, \qquad \sem{d}(x) = b x + d .
$$

$$
\begin{array}{c|ccc} \circ & \Kk & \Pp & \Gg \\ \hline \Kk & \Kk & \Kk & \Gg \\ \Pp & \Kk & \Pp & \Gg \\ \Gg & \Kk & \Gg & \Gg \end{array}
$$

$$
\frac{a}{b} = c \iff b \cdot c = a \quad (b \neq 0), \qquad \lim_{x \to 0^{+}} \frac{1}{x} = +\infty .
$$
