{
    "title": "Solving \"Modular Search\"",
    "date": "2026-02-15",
    "show": true
}

In Russ Cox' ["Floating-Point Printing and Parsing Can Be Simple And Fast"](https://research.swtch.com/fp) (which is both a tough and an enjoyable read, the guy's a genius!), the following problem is introduced under the name "modular search":

> For given positive integers $c$, $m$, find the value of $x$ such that $\text{mod}_m(c \cdot x)$ is minimal and in the range $[\text{min}, \text{max}]$.

I didn't quite like the solution that was presented there. It works, but I think there is a more elegant solution that is is the obvious one for people with some knowledge of modular arithmetic. I'll present this solution here.

It is well-known that the expression $\text{mod}_m(c \cdot x)$ can only assume values that are multiples of $\gcd(c, m)$. So, it is easy to check if the condition can be satisfied: We round $\text{min}$ up to a multiple of $gcd(c, m)$ to obtain a "candidate" value. If this candidate value is more than $\text{max}$, we know the problem has no solution for the given $c$ and $m$.

If the candidate is less than or equal to $\text{max}$, we know the problem has a solution and we want to find the $x$ such that $c \cdot x$ equals our candidate value $n \cdot \gcd(c, m)$ modulo $m$.

It is also well-known that by using the extended Euclidean algorithm we can efficiently find a $d$ such that $c \cdot d \equiv \gcd(c, m)$ modulo $m$. So we have
$$ n \cdot c \cdot d \equiv n \cdot \gcd(c, m) \pmod{m}$$

So we find that $x = \text{mod}_m(n \cdot d)$.

All in all, we get the following:

```
def minmax_euclid(c, m, min, max):
    gcd, _, d = extended_euclid(m, c % m)
    n = (min + gcd - 1) // gcd
    candidate = n * gcd

    if candidate > max:
        return None
    
    return (n * d) % m
```

The function `extended_euclid(a, b)` assumes that `a` and `b` are positive integers with `a > b`. It returns a triple `(gcd, p, q)`, where `gcd = p * a + q * b`. So if we call it as `gcd, _, d = extended_euclid(m, c % m)` (the modulo operator is just to handle the case where `c > m`), we'll have `gcd == (c * d) % m`.

I have written about how the extended Euclidean algorithm works before so I won't repeat myself here, but here is an implementation:
```
def extended_euclid(a, b,
        p_a = 1, q_a = 0, p_b = 0, q_b = 1):
    if b == 0:
        return a, p_a, q_a

    n = a // b
    return extended_euclid(b, a - n * b,
        p_b, q_b, p_a - n * p_b, q_a - n * q_b)
```

Or, alternatively, a version that uses iteration instead of recursion:
```
def extended_euclid(a, b,
        p_a = 1, q_a = 0, p_b = 0, q_b = 1):
    while b > 0:
        n = a // b
        a, b, p_a, q_a, p_b, q_b = (b, a - n * b,
            p_b, q_b, p_a - n * p_b, q_a - n * q_b)

    return a, p_a, q_a
```
