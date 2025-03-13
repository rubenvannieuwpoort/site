---
title: Division by constant unsigned integers
description: Most modern processors have an integer divide instruction which is relatively slow compared to the other arithmetic operations. When the divisor is known at compile-time or the same divisor is used for many divisions, it is possible to transform the single division to a series of instructions which execute faster. Most compilers will optimize divisions in this way. In this article, I give an overview of the existing techniques for unsigned integers.
date: 2020-08-28
template: post
show: false
---

This post is a survey of the methods to optimize unsigned integer division. <aside>These articles were written by ridiculous_fish, the author of the [libdivide](https://libdivide.com) library, a C++ header-only library which implements the techniques explained in this post for divisors which are constant at runtime.</aside>It largely follows the approach and terminology in the excellent articles [TODO] by ridiculous_fish, but aims to be slighly more rigorous and concise.

First, the round-up method is presented, which shows that for every $N$-bit divisor $d > 0$ there is a constant $m$ so that the upper bits of $mn$ equal $\lfloor \frac{n}{d} \rfloor$ for every $N$-bit unsigned $n$. For certain "uncooperative" divisors the constant $m$ will not fit in $N$ bits, in which case the method is feasible but less efficient. To improve the efficiency, the round-down method is presented, which is similar to the round-up method but more efficient for uncooperative divisors.


## Intuition

To understand why these multiplicative methods work, let’s build some intuition. The idea is to choose an integer constant, $m$, that approximates $\frac{2^k}{d}$. This way, $m$ effectively represents $\frac{1}{d}$ in binary form. Multiplying by $2^k$ shifts the fractional bits to more significant positions, allowing them to be captured as an integer.

Simply put, since we have $m \approx \frac{2^k}{d}$, we expect that $\frac{mn}{2^k} \approx \frac{n}{d}$. So, it isn't to far-fetched to expect that $\lfloor \frac{mn}{2^k} \rfloor = \lfloor \frac{n}{d} \rfloor$. In the next section we'll see under which conditions this equality holds.

If this doesn't click yet, consider an example in base 10 instead. Pick $d = 3$ and instead of $2^k$, we'll pick $10^4$ and $m = 3334 \approx \frac{10^4}{3}$. <aside>Note that we didn't round $\frac{10^4}{3}$ to the closest integer here, and we would get an incorrect result if we did.</aside>Picking $n = 492$ we see that $\frac{mn}{10^4} = \frac{1640328}{10^4}$. This equals $164.0328$, so indeed we have $\lfloor \frac{mn}{10^4} \rfloor = \lfloor \frac{492}{3} \rfloor = 164$.


## Round-up method

We start with deriving a theorem that shows the method is correct. To prove this theorem, we'll need the following lemma.

**Lemma 1**: *Suppose that $n$ and $d$ are integers with $d > 0$, and $x$ is a real number. If $\frac{n}{d} \leq x < \frac{n + 1}{d}$ then $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.*

**Proof**: We have $\frac{n}{d} \leq x < \frac{n + 1}{d} \leq \lfloor \frac{n}{d} \rfloor + 1$. After taking the floor of all terms and considering that the right-hand side is an integer, we get $\lfloor \frac{n}{d} \rfloor \leq \lfloor x \rfloor < \lfloor \frac{n}{d} \rfloor + 1$, which implies $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.

$\square$

Now, we are ready to prove the result that justifies the round-up method.

**Theorem 2**: *Let $d$, $m$, $\ell$ be nonnegative integers with $d \neq 0$ and*
$$ 2^{N + \ell} \leq d \cdot m \leq 2^{N + \ell} + 2^\ell \tag{1} $$

*then $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n < 2^N$*.

**Proof**: Multiplying the inequality by $\frac{n}{d \cdot 2^{N + \ell}}$ we get $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d} \cdot \frac{n}{2^N}$. We have $n < 2^N$, so that $\frac{n}{2^N} < 1$. It follows that $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d}$. By lemma 1, it follows that $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$.

$\square$

If we can find $\ell$ and $m$ such that $(1)$ is satisfied, the theorem states that we can use the expression $\lfloor \frac{mn}{2^{N + \ell}} \rfloor$ as an efficient way to evaluate $\lfloor \frac{n}{d} \rfloor$, for all $N$-bit unsigned integers $n$.

Let's take a closer look at the condition $(1)$. It is satisfied if and only if there is a multiple of $d$ in the interval $[2^{N + \ell}, 2^{N + \ell} + 2^\ell]$. So the existence of an $m$ that satisfies $(1)$ depends on $\ell$.

Suppose that we have $\ell$, $m$ such that the condition holds and we have $2^{N + \ell} \leq d \cdot m \leq 2^{N + \ell} + 2^\ell$. If we multiply this by $2$ we get $2^{N + \ell + 1} \leq d \cdot 2m \leq 2^{N + \ell + 1} + 2^{\ell + 1}$. In other words, if we take $\ell + 1$ instead of $\ell$ and $2m$ instead of $m$, the condition is also satisfied. This means there is a smallest $\ell$ for which an $m$ satisfying $(1)$ exists. For all larger values of $\ell$ an $m$ satisfying $(1)$ is guaranteed to exist.

Conversely, if $m$ is even and $(1)$ is satisfied, we can just divide everything by two and get $2^{N + \ell - 1} \leq d \cdot \frac{m}{2} \leq 2^{N + \ell - 1} + 2^{\ell - 1}$. So we see that in this case the condition still holds for $\ell - 1$, $\frac{m}{2}$.

Now, given that every $d$th integer is a multiple of $d$, we can guarantee that there exists a multiple of $d$ in $[2^{N + \ell}, 2^{N + \ell} + 2^\ell]$ when $\ell \geq \log_2(d)$. However, this means that we have $m = \lceil \frac{N+\ell}{d} \rceil \geq 2^N$, so that $m$ doesn't fit in $N$ bits. Usually $N$ is the word size of the processor. If $m$ doesn't fit in a single word, the evaluation of the product $mn$ becomes more complicated and expensive.

However, for most divisors $d$ we can find an $\ell < \log_2(d)$ for which $m = \lceil \frac{2^{N + \ell}}{d} \rceil$ satisfies $(1)$, so that we have $m < 2^N$ and $m$ does fit in a single word. If this is the case, we'll call $d$ a **cooperative divisor**. Otherwise, we'll call $d$ an **uncooperative divisor**.

In practice we want to find the smallest $m$, because in many architectures smaller constants can be loaded into registers with fewer instructions. In some architectures, multiplication by smaller values might also be more efficient.

So, we can pick $\ell = \lceil \log_2(d) \rceil$ first. Then we decrease $\ell$ and shift right $m$ to the right while $m$ is even.<aside>The following is equivalent but more efficient:
  1. Count the number of trailing zeroes in the binary representation of $m$.
  2. Decrease $\ell$ by $p$ and shift $m$ to the right by $p$ bits, effectively removing all the trailing zero bits.</aside>


### Cooperative divisors

To make the last section more concrete, let's optimize the following function.
```
uint32_t div9(uint32_t n) {
	return n / 9;
}
```

We can use theorem 2 and try to find an $\ell$ such that $m = \lceil \frac{2^{32 + \ell}}{9} \rceil$ satisfies $(1)$. As we deduced earlier, setting $\ell = 4$ will produce a 33-bit number $m$ that satisfies $(1)$. However, we are now interested in the *smallest* constant $m$ that satisfies $(1)$.

So, we try successively smaller values for $\ell$ and see if $\ell$, $m = \lceil \frac{2^{32+\ell}}{9} \rceil$ satisfy $(1)$. For $\ell = 3$ the conditions are satisfied, for $\ell = 2$, they are too, and for $\ell = 1$ they are as well. For $\ell = 0$ they are not, so we set $\ell = 1$ and find $m = 954437177$.

So the optimized version of the function is
<aside>The constant `954437177` is a 32-bit number, but it needs to be converted to a `uint64_t` to get the full 64-bit product.</aside>

```
uint32_t div9_opt(uint32_t n) {
	uint64_t mn = uint64_t(954437177) * n;
	return mn >> 33;
}
```

Indeed, GCC compiles `div9` and `div9_opt` to the same assembly. For example in `x86_64` we get:
```
mov eax, edi
mul rax, rax, 954437177
shr rax, 33
ret
```

For 32-bit instruction sets, the shift is usually implemented by taking the high 32-bit word of the full 64-bit and performing a right shift by one on that. For example, in 32-bit RISC-V:
```
li a5, 954437177
mulhu a0, a0, a5
srli a0, a0, 1
ret
```



















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
	1. A division by one can be implemented as a no-op
	2. A division by $2^p$ can be implemented by right bit shift by $p$ bits
	3. If we divide $n \in \mathbb{U}_N$ by a sufficiently large divisor $d > \frac{2^N - 1}{2}$, the result will always be 0 or 1. Specifically, the result will be one when $n \geq d$, which can be efficiently implemented in some architectures.
	4. When we know $n$ is a multiple of $d$, dividing $n$ by $d$ is the same as multiplying $n$ by the multiplicative inverse of $d$ modulo $2^N$ (where $N$ is the word size of the machine), which can be efficiently implemented.



## Worked examples

- fast test
- powers of two
- large divisors
- even divisors
- outline

## Worked examples
