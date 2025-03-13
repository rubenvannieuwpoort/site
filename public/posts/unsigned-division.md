---
title: Division by constant unsigned integers
description: Most modern processors have an integer divide instruction which is relatively slow compared to the other arithmetic operations. When the divisor is known at compile-time or the same divisor is used for many divisions, it is possible to transform the single division to a series of instructions which execute faster. Most compilers will optimize divisions in this way. In this article, I give an overview of the existing techniques for unsigned integers.
date: 2020-08-28
template: post
show: false
---

The integer division operation, which calculates $\lfloor \frac{n}{d} \rfloor$ for integers $n$ and $d$, is one of the slowest operations in modern processors. While the [M1 made significant improvements](https://ridiculousfish.com/blog/posts/benchmarking-libdivide-m1-avx512.html), it is still possible to implement division by a constant integer divisor more efficiently.

The basic idea is that instead of using the division instruction to calculate $\lfloor \frac{n}{d} \rfloor$, you multiply by $\lfloor \frac{2^k}{d} \rfloor$ and shift right by $k$ bits, for some appropriate value of $k$. This essentially approximates the division by $d$ by a multiplication by $x \approx \frac{1}{d}$.


## A decimal example

To make the technique concrete, let's look at an example using decimal instead of binary. Let's say we want to divide a lot of integers by three. Instead of calculating this as $\frac{n}{3}$, which needs a division, we calculate the integer $\lfloor \frac{10^5}{3} \rfloor = 33333$. Then we can approximately divide by three by multiplying by this constant and discarding the 5 least significant digits (which is equivalent to dividing by $10^5$ and rounding down). For example, for $n = 11$ we get $11 \cdot 33333 = 366663$, and discarding the five least significant digits we get $3$. Indeed, this is correct, since $\lfloor \frac{11}{3} \rfloor = 3$.

However, taking $n = 12$ we get $12 \cdot 33333 = 399996$, which gives $4$ after discarding the 5 least significant digits. This is obviously wrong. More generally, we can see that we'll always have this problem when $d$ is not a divisor of $10^5$ and $n$ is a multiple of $d$: If $n = kd$ then
$$ \lfloor \frac{n \cdot \lfloor \frac{10^5}{d} \rfloor}{10^5} \rfloor < \frac{kd \cdot \frac{10^5}{d}}{10^5} = k$$

So in this case, *we will never get the right answer*.

The problem is that the product $n \cdot \lfloor \frac{10^5}{d} \rfloor$ is slightly too low. A naive way to increase the value of the product is to increase either $n$ or $\lfloor \frac{10^5}{d} \rfloor$. Indeed, for the example with $n = 12$ both work, since $13 \cdot 33333 = 433329$ and $12 \cdot 33334 = 400008$, and both give $4$ after discarding the 5 least significant digits.

Doing the same thing in binary, instead of using the division operation, we set $m = \lfloor \frac{2^k}{d} \rfloor$ and use one of the expressions
$$ \lfloor \frac{(m + 1)n}{2^k} \rfloor, \lfloor \frac{m(n + 1)}{2^k} \rfloor $$

to calculate $\lfloor \frac{n}{d} \rfloor$.

The remainder of this post answers the following questions:
  1. How do we pick $k$, and under what conditions do the previously mentioned expressions give the correct result?
  2. How can we efficiently implement this method?


## Conditions for correctness

Suppose we are implementing the technique for an $N$-bit processor. The constant $m = \lfloor \frac{2^k}{d} \rfloor$ contains the fractional bits of $\frac{1}{d}$, so it makes sense to maximize the number of bits in $m$ while still making sure that $m$ fits in an $N$-bit word. That means that we set $k = N + \ell$ with $\ell = \lceil \log_2(d) \rceil - 1$: If we set $k$ any larger we get $m \geq 2^N$ and $m$ will not fit in an $N$-bit unsigned integer.

We will now consider the conditions under which we have
$$ \lfloor \frac{(m + 1)n}{2^k} \rfloor = \lfloor \frac{n}{d} \rfloor $$

and the conditions under which we have
$$ \lfloor \frac{m(n + 1)}{2^k} \rfloor = \lfloor \frac{n}{d} \rfloor $$

for all $N$-bit unsigned integers. Signed integers are slightly more involved and I will cover them in a separate post.

The following lemma will come in handy.

**Lemma 1**: *Suppose that $n \in \mathbb{Z}$, $d \in \mathbb{N}_+$. If $\frac{n}{d} \leq x < \frac{n + 1}{d}$ then $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.*

**Proof**: We have $\frac{n + 1}{d} = \lfloor \frac{n}{d} \rfloor + \frac{k}{d}$ for some nonnegative integer $k \leq d$. So $\frac{n + 1}{d} = \lfloor \frac{n}{d} \rfloor + \frac{k}{d} \leq \lfloor \frac{n}{d} \rfloor + 1$. It follows that $x \in [ \lfloor \frac{n}{d} \rfloor, \lfloor \frac{n}{d} \rfloor + 1)$, so that $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.
$\square$

From now on, I will denote the set of $N$-bit unsigned integers by $\mathbb{U}_N$. The following lemma tells us when $\lfloor \frac{(m + 1)n}{2^k} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$.

**Lemma 2**: *Let $c, d, N \in \mathbb{N}_+$ and $\ell \in \mathbb{N}_0$. If*
$$ 2^{N + \ell} \leq c \cdot d \leq 2^{N + \ell} + 2^\ell $$

*then $\lfloor \frac{(m + 1) \cdot n}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$*.

**Proof**: Multiplying the inequality by $\frac{n}{d \cdot 2^{N + \ell}}$ we get
$$ \frac{n}{d} \leq \frac{c \cdot n}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d} \cdot \frac{n}{2^N} $$

For all $n \in \mathbb{U}_N$ we have $n < 2^N$, so that $\frac{n}{2^N} < 1$. It follows that we have
$$ \frac{n}{d} \leq \frac{c \cdot n}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d} $$

for all $n \in \mathbb{U}_N$. By lemma 1, it follows that $\lfloor \frac{c \cdot n}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$.
$\square$

We have a similar lemma to tell us when $\lfloor \frac{m(n + 1)}{2^k} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$.

**Lemma 3**: *Let $c, d, N \in \mathbb{N}_+$ and $\ell \in \mathbb{N}_0$. If*
$$ 2^{N + \ell} - 2^\ell \leq c \cdot d < 2^{N + \ell}$$

*then $\lfloor \frac{c \cdot (n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$*.

**Proof**: Multiply the inequality by $\frac{n + 1}{d \cdot 2^{N + \ell}}$ to get
$$ \frac{n}{d} + \frac{1}{d} \cdot \left( 1 - \frac{n + 1}{2^N} \right) \leq \frac{c \cdot (n + 1)}{2^{N + \ell}} < \frac{n + 1}{d} $$

Looking at the expression on the left side, we have $1 \leq n + 1 \leq 2^N$, so that $0 \leq 1 - \frac{n + 1}{2^N} < 1$. It follows that $\frac{n}{d} \leq \frac{n}{d} + \frac{1}{d} \cdot (1 - \frac{n + 1}{2^N})$, so
$$ \frac{n}{d} \leq \frac{c \cdot (n + 1)}{2^{N + \ell}} < \frac{n + 1}{d} $$

for all $n \in \mathbb{U}_N$. So lemma 1 applies and we have $\lfloor \frac{c \cdot (n + 1)}{2^{N + \ell}} \rfloor$ for all $n \in \mathbb{U}_N$.
$\square$

So, lemma 2 tells us that if there is a multiple $cd$ of $d$ in the interval $[2^{N + \ell}, 2^{N + \ell} + 2^\ell]$, then  we have $\lfloor \frac{c n}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$. The first multiple of $d$ in this interval is $\lceil \frac{2^{N + \ell}}{d} \rceil d$.

Lemma 3 tells us that if there is a multiple $cd$ of $d$ in the interval $[2^{N + \ell} - 2^\ell, 2^{N + \ell})$, then  we have $\lfloor \frac{c n}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$. When $d$ is not a power of two, the first multiple of $d$ in this interval is $\lfloor \frac{2^{N + \ell}}{d} \rfloor d$.

If we set $\ell = \lceil \log_2(d) \rceil - 1$, then $[2^{N + \ell} - 2^\ell, 2^{N + \ell} + 2^\ell]$ is an interval of size $2 \cdot 2^\ell + 1 > 2^{\lceil \log_2(d) \rceil} \geq d$, which contains exactly one multiple of $d$. So that means that either the conditions of lemma 2 or the conditions of lemma 3 are satisfied.

**Theorem 4**: Let $N \in \mathbb{N}_+$. For every $d \in \mathbb{U}_N$ with $\ell = \lceil \log_2(d) \rceil - 1$, precisely one of the following applies:
  - $2^{N + \ell} - 2^\ell \leq c d < 2^{N + \ell}$ and $\lfloor \frac{c (n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$, with $c = \lfloor \frac{2^{N + \ell}}{d} \rfloor$.
  - $2^{N + \ell} \leq c d \leq 2^{N + \ell} + 2^\ell$ and $\lfloor \frac{c n}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$, with $c = \lceil \frac{2^{N + \ell}}{d} \rceil$.

When $d$ is not a power of two we have $\ell = \lfloor \log_2(d) \rfloor$ and $\lceil \frac{2^{N + \ell}}{d} \rceil = \lfloor \frac{2^{N + \ell}}{d} \rfloor + 1$, and we can simplify the result a bit.

**Corollary 5**: Let $N \in \mathbb{N}_+$. Let $d \in \mathbb{U}_N$ not be a power of two, $\ell = \lfloor \log_2(d) \rfloor$, and $m = \lfloor \frac{2^{N + \ell}}{d} \rfloor$. Precisely one of the following applies:
  - $2^{N + \ell} - 2^\ell \leq m d < 2^{N + \ell}$ and $\lfloor \frac{m (n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$.
  - $2^{N + \ell} \leq (m + 1) d \leq 2^{N + \ell} + 2^\ell$ and $\lfloor \frac{(m + 1) n}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all $n \in \mathbb{U}_N$.


## Efficient implementation

To find out what method to use, we can use the following test, which can be efficiently implemented.

**Lemma**: *Let $N \in \mathbb{N}_+$, $d \in \mathbb{U}_N$, and define $\ell = \lceil \log_2(d) \rceil - 1$. Define $c = \lceil \frac{2^{N + \ell}}{d} \rceil$. If $\text{mod}_{2^N}(c \cdot d) \leq 2^\ell$, then $2^{N + \ell} \leq c d \leq 2^{N + \ell} + 2^\ell$, so the second case of theorem 4 applies.*

Again, when $d$ is not a power of two, we can set $\ell = \lfloor \log_2(d) \rfloor$, $c = $ which is usually more convenient.

There are some special cases that have special implementations which are even more efficient than the multiplicate method of the previous section. When possible, these methods should be preferred:
  1. A division by one can be implemented as a no-op.
  2. A division by $2^p$ can be implemented by right bit shift by $p$ bits.
  3. If we divide $n \in \mathbb{U}_N$ by a sufficiently large divisor $d > \frac{2^N - 1}{2}$, the result will always be 0 or 1. Specifically, the result will be one when $n \geq d$, which can be efficiently implemented in some architectures.
  4. When we know $n$ is a multiple of $d$, dividing $n$ by $d$ is the same as multiplying $n$ by the multiplicative inverse of $d$ modulo $2^N$ (where $N$ is the word size of the machine), which can be efficiently implemented.



## Worked examples

- fast test
- powers of two
- large divisors
- even divisors
- outline

## Worked examples
