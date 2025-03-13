---
title: Division by constant unsigned integers
description: Most modern processors have an integer divide instruction which is relatively slow compared to the other arithmetic operations. When the divisor is known at compile-time or the same divisor is used for many divisions, it is possible to transform the single division to a series of instructions which execute faster. Most compilers will optimize divisions in this way. In this article, I give an overview of the existing techniques for unsigned integers.
date: 2020-08-28
template: post
show: false
---

This post is a survey of the methods to optimize unsigned integer division.

Formally, it shows how to compute $\text{truncate}(\frac{n}{d})$. Here:
- The function $\text{truncate}$ rounds towards zero
- The numbers $n, d$ are integers with $d \neq 0$
- Either $n$ and $d$ are both unsigned (i.e. $0 \leq d, n < 2^N$), or both signed (i.e. $-2^{N-1} \leq n, d < 2^{N - 1}$)

This post largely follows the approach and terminology in the excellent series of articles "The labor of division" by ridiculous_fish, but aims to be slighly more rigorous and concise.

< ridiculous_fish is the author of the [libdivide](https://libdivide.com) library, a C++ header-only library which uses various methods to speed up division, including the methods described in this post.


## Overview

I will first give a short intuitive argument that explains how these optimizations work.

Then, the *round-up method* is presented, which shows that for every $N$-bit divisor $d > 0$ there is a constant $m$ so that the upper bits of $mn$ equal $\lfloor \frac{n}{d} \rfloor$ for every $N$-bit unsigned $n$. For certain "uncooperative" divisors the constant $m$ will not fit in $N$ bits, in which case the method is feasible but less efficient.

To improve the efficiency, the *round-down method* is presented for uncooperative divisors. It is similar to the round-up method but more efficient.

Finally, I show how to apply the techniques to signed integers.


## Intuition

To understand why these multiplicative methods work, let’s build some intuition. The idea is to choose an integer constant, $m$, that approximates $\frac{2^k}{d}$. The constant $m$ effectively represents $\frac{1}{d}$ in binary form. Multiplying by $2^k$ shifts the fractional bits to more significant positions, allowing them to be captured as an integer.

Since we have $m \approx \frac{2^k}{d}$, we expect that $\frac{mn}{2^k} \approx \frac{n}{d}$. So, it isn't too far-fetched to expect that $\lfloor \frac{mn}{2^k} \rfloor = \lfloor \frac{n}{d} \rfloor$. In the next section we'll see under which conditions this equality holds.

If this doesn't click yet, consider an example in base 10 instead. Pick $d = 3$. Instead of $2^k$, we'll pick $10^4$ and $m = 3334 \approx \frac{10^4}{3}$. Picking $n = 492$ we see that $\frac{mn}{10^4} = \frac{1640328}{10^4}$. This equals $164.0328$, so indeed we have $\lfloor \frac{mn}{10^4} \rfloor = \lfloor \frac{492}{3} \rfloor = 164$.

< Note that we rounded $\frac{10^4}{3}$ *up* instead of rounding it to the closest integer here. The method wouldn't work if we rounded down.


## Round-up method

We want to derive the conditions under which the previously demonstrated method is correct. We'll need the following lemma.

**Lemma 1**: *Suppose that $n$ and $d$ are integers with $d > 0$, and $x$ is a real number. If $\frac{n}{d} \leq x < \frac{n + 1}{d}$ then $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.*

**Proof**: We have $\frac{n}{d} \leq x < \frac{n + 1}{d} \leq \lfloor \frac{n}{d} \rfloor + 1$. After taking the floor of all terms and considering that the right-hand side is an integer but $x$ is not, we get $\lfloor \frac{n}{d} \rfloor \leq \lfloor x \rfloor < \lfloor \frac{n}{d} \rfloor + 1$, which implies $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.

$\square$

Now, we are ready to prove the result that justifies the round-up method.

**Theorem 2**: *Let $d$, $m$, $\ell$ be nonnegative integers with $d \neq 0$ and*
$$ 2^{N + \ell} \leq d \cdot m \leq 2^{N + \ell} + 2^\ell \tag{1} $$

*then $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n < 2^N$*.

**Proof**: Multiplying the inequality by $\frac{n}{d \cdot 2^{N + \ell}}$ we get $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d} \cdot \frac{n}{2^N}$. We have $n < 2^N$, so that $\frac{n}{2^N} < 1$. It follows that $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d}$. By lemma 1, it follows that $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all integers $n$ with $0 \leq n < 2^N$.

$\square$

So if we can find $\ell$, $m$ satisfying $(1)$, we can compute $\lfloor \frac{n}{d} \rfloor$ as $\lfloor \frac{mn}{2^{N + \ell}} \rfloor$. An $m$ that satisfies $(1)$ exists only if and only if the interval $[2^{N + \ell}, 2^{N + \ell} + 2^\ell]$ contains a multiple of $d$.

< If we know that $m$ is not a power of two, we have $\lceil \frac{2^{N + \ell}}{d} \rceil = \lfloor \frac{2^{N + \ell}}{d} \rfloor + 1$, where the latter might be easier to evaluate.

If $\ell > \log_2(d)$, the interval will contain at least $d$ successive integers and we can be certain that the interval contains a multiple of $d$. Since $d \cdot \lceil \frac{2^{N + \ell}}{d} \rceil$ is just the first multiple of $d$ that is at least as large as $2^{N + \ell}$, we can always set $m = \lceil \frac{2^{N + \ell}}{d} \rceil$; if there an $m$ exists that satisfies $(1)$, this $m$ will do so too.

On the other hand, we would like to have $m < 2^N$ so that $m$ fits in an $N$-bit word, but this requires $\ell < \log_2(d)$. So, this we can't guarantee this, and indeed we see that for some divisors $d$ there only exist $m$, $\ell$ with $m > 2^N$.

We can first pick $\ell = \lfloor \log_2(d) \rfloor$ and set $m = \lceil \frac{2^{N + \ell}}{d} \rceil$. We have $m < 2^N$, and we have to check that it satisfies $(1)$.

< An efficient way to test if $(1)$ is satisfied is work modulo $2^N$ (that is, ignore overflow). The conditioon $(1)$ can then be tested simply by testing if `d * m` is smaller than `1 << l`.

If $m$ is even, we can divide all terms in $(1)$ by two and get the valid equation $2^{N + \ell - 1} \leq d \cdot \frac{m}{2} \leq 2^{N + \ell - 1} + 2^{\ell - 1}$. So if $m$ is even we can replace $m$ by $\frac{m}{2}$ and $\ell$ by $\ell - 1$, and $(1)$ will still hold. In some cases, this allows us to find a smaller constant $m$ that still satisfies $(1)$. This will be demonstrated later.

If, for a given $d$ there exist an $m < 2^N$ such that $(1)$ is satisfied, $m$ fits in a single word and the product $mn$ is easily evaluated. For this reason, we'll call such divisors **cooperative**, and the others **uncooperative**. For uncooperative diviors it is more tricky and less efficient to calculate the product $mn$. We will consider both cases in the following subsections.

< Strictly speaking, since the condition $(1)$ depends on $N$, we should be more precise and state something like "$d$ is a cooperative divisor for $N$", but we don't really do this since $N$ is usually fixed anyway.


### Cooperative divisors

To make the last section more concrete, let's optimize the following function.
```
uint32_t div9(uint32_t n) {
	return n / 9;
}
```

Using the strategy outlined in the previous section, we set $\ell = \lfloor \log_2(9) \rfloor = 3$ and compute $m = \lceil \frac{2^{32 + 3}}{9} \rceil = 3817748708$. Working modulo $2^{32}$ we see that $\text{mod}_{2^{32}}(d \cdot m)$ equals $\text{mod}_{2^{32}}(34359738372) = 4$. We have $4 < 2^3$, so the test succeeds and we conclude that $3$ is a cooperative divisor.

We also see that $m$ is even. So we can divide it by two to get $3817748708$, which is also even. Dividing by two once more gives $954437177$. Adjusting for this, we only need to shift right by $33$ bits, instead of $35$.

So the optimized version of the function is

< The constant `954437177` is a 32-bit number, but it needs to be converted to a `uint64_t` to get the full 64-bit product.

```
uint32_t div9(uint32_t n) {
	return ((uint64_t)954437177 * n) >> 33;
}
```

Indeed, we can enter both of these functions on [godbolt.org](godbolt.org) and see that clang compiles them to the same assembly. For `x86_64` we get ([compiler-optimized](https://godbolt.org/z/oh6h6P4aa), [hand-optimized](https://godbolt.org/z/6e11Kzbqv)):
```
div9:
	mov eax, edi
	mul rax, rax, 954437177
	shr rax, 33
	ret
```

For 32-bit instruction sets, the shift is usually implemented by taking the high 32-bit word of the full 64-bit and performing a right shift by one on that. For example, in 32-bit RISC-V ([compiler-optimized](https://godbolt.org/z/86jqna17r), [hand-optimized](https://godbolt.org/z/q9e43EY4e)):
```
div9:
	li a5, 954437177
	mulhu a0, a0, a5
	srli a0, a0, 1
	ret
```

< The `mulhu` instruction computes the product of the second and third operand, and stores it in the first operand.


### Uncooperative divisors

Let's take the function from the last section but instead divide by $7$:
```
uint32_t div7(uint32_t n) {
	return n / 7;
}
```

Doing the same, we compute $\ell = \lfloor \log_2(7) \rfloor = 2$, $m = \lceil \frac{2^{32 + 2}}{7} \rceil = 2454267027$. Now, we compute $\text{mod}_{2^{32}}(d \cdot m)$ to be $\text{mod}_{2^{32}}(17179869189) = 5 > 4$. So condition $(1)$ does not hold and $7$ is an uncooperative divisor.

This means we can't use the value we just calculated for $m$ and instead we have to set $\ell = \lceil \log_2(7) \rceil = 3$. We get $m = \lceil \frac{2^{32 + 3}}{7} \rceil = 4908534053$. This is a 33-bit value and we have to resort to some tricks to evaluate $\lfloor \frac{mn}{2^{N + \ell}} \rfloor$ without overflow.


#### Evaluating the product $mn$

A first idea is to set $m' = m - 2^N$ and compute the product $mn$ in two 32-bit words as $(2^{32} + m')n = m' \cdot n + 2^{32} n$. However, this doesn't work since in general the product of a 32-bit number and a 33-bit number does not fit in 64 bits. So we need to take care that the addition of $2^{32} n$ to $m' n$ does not overflow.

This can be done by evaluating $\lfloor \frac{mn}{2^{N + \ell}} \rfloor$ as `((((mn >> N) - n) >> 1) + n) >> (l - 1)`, where `mn` is the full $2N$-bit product.

So the optimized version of the function is

```
uint32_t div7(uint32_t n) {
	// compute the high word of the product m' * n
	uint32_t mn = (((uint64_t)613566757) * n) >> 32;

	// compute (m * n) >> 1 in an overflow-safe way
	uint32_t mn2 = ((n - mn) >> 1) + mn;

	// shift right by l - 1 bits
	return mn2 >> 2;
}
```

< I've swapped the roles of `mn` and `n` here to match GCC's assembly output. They can be swapped because `mn2` equals `(mn + n) >> 1`.

Indeed, GCC gives the same assembly. In `x86_64`:
```
div7:
	mov eax, edi
	imul rax, rax, 613566757
	shr rax, 32
	sub edi, eax
	shr edi
	add eax, edi
	shr eax, 2
	ret
```

Or in `RISC-V`:
```
div7:
	li a5, 613566757
	mulhu a5, a0, a5
	sub a0, a0, a5
	srli a0, a0, 1
	add a0, a0, a5
	srli a0, a0, 2
	ret
```


### Even uncooperative divisors

Suppose we have an even uncooperative divisor $d$ of the form $d = 2^pc$, so that $p \geq 1$. We can use the round-down method, which will be explained in the next section, but there is also a more efficient way. We can implement a division by $d$ as a division by $2^p$ (which can be implemented efficiently with a bit shift) followed by a division by $c$. Now, $c$ will be an uncooperative divisor too, but since the dividend $n$ will only be an $(N - p)$-bit number, the constant $m$ will fit in $N$ bits. This only costs us a single bit shift, which is more efficient than implementing the overflow-avoiding product from last section.

As an example, consider the following function:
```
uint32_t div28(uint32_t n) {
	return n / 28;
}
```

Following the procedure as before, we set $\ell = \lfloor \log_2(28) \rfloor = 4$ and test $m = \lceil \frac{2^{N + \ell}}{d} \rceil = 2454267027$. We see that $\text{mod}_{2^{32}}(d \cdot m) = 20 > 16 = 2^\ell$ so the test fails and 28 is an uncooperative divisor.

So we note that we have an even uncooperative divisor and set $n' = \lfloor \frac{n}{4} \rfloor$. We now need to divide $n'$, a $30$-bit number, by $7$. If $7$ would be a cooperative divisor, then $2^k \cdot 7$ would be too, so we know that $7$ is an uncooperative divisor. So we set $N' = 30$, $\ell = \lceil \log_2(7) \rceil = 3$ and get $m = \lceil \frac{2^{N' + \ell}}{d} \rceil = 1227133514$.

Note that $m$ is even, so we can use $\frac{m}{2}$ instead and decrease $\ell$. We get $m = 613566757$, $N = 30$, $\ell = 2$. The optimized version of the function is
```
uint32_t div28(uint32_t n) {
	n = n >> 2;
	return (((uint64_t)613566757) * n) >> 32;
}
```

In `x86_64` assembly:
```
div28:
	mov eax, edi
	shr eax, 2
	imul rax, rax, 613566757
	shr rax, 32
	ret
```

In `RISC-V`:
```
div28:
	li a5, 613566757
	srli a0, a0, 2
	mulhu a0, a0, a5
	ret
```


## Round-down method

The following theorem powers the **round-down method**, which was introduced in "Labor of Division (Episode III)" and TODO independently. I present the result in a forum analogous to theorem 2.

**Theorem 3**: *Let $d$, $m$, $\ell$ be nonnegative integers with $d \neq 0$ and*
$$ 2^{N + \ell} -2^\ell \leq d \cdot m \leq 2^{N + \ell} \tag{2} $$

*then $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n < 2^N$*.

**Proof**: Multiplying the inequality by $\frac{n + 1}{d \cdot 2^{N + \ell}}$ we get $\frac{n}{d} + \frac{1}{d} \cdot (1 - \frac{n + 1}{2^N}) \leq \frac{m(n + 1)}{2^{N + \ell}} \leq \frac{n + 1}{d}$. Since $n < 2^N$ we have $\frac{n}{d} \leq \frac{n}{d} + \frac{1}{d} \cdot (1 - \frac{n + 1}{2^N})$ and the condition of lemma 1 is satisfied. So we have $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all integers $n$ with $0 \leq n < 2^N$.

The result is fairly straightforward to use. However, we need to take care to avoid overflows.
- A straightforward way is to calculate the full product, using $2N$ bits. TODO suggests to use a fused-multiply-add instruction for this. However, most instruction set architectures do not have such an instruction.
- In "Labor of Division (Episode III)", it is suggested to use *saturating increment* to increment $n$. This is much more portable.

A saturating increment is a normal increment for most integers. For the value $2^N - 1$, which would overflow when incremented, it "saturates" and does nothing. So the overflow is avoided.

However, it is not obvious that performing a saturating increment on $n$ will give the correct result.


### Correctness of the saturating-increment approach

When we use saturating-increment approach, we calculate $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every $n < 2^N - 1$. For $n = 2^N - 1$, we don't increment, so we effectively calculate $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{2^N - 2}{d} \rfloor$. This seems wrong, but it's correct as long as $d$ is an uncooperative divisor. This is OK, since if $d$ is a cooperative divisor, we would like to use the round-up method anyway.

We only have $\lfloor \frac{2^N - 2}{d} \rfloor \neq \lfloor \frac{2^N - 1}{d} \rfloor$ when $d$ is a divisor of $2^N - 1$. But in this case, we have $2^N \equiv 1 (\text{mod}\ d)$, which means that $2^{N + \ell} + 2^\ell$ equals $-2^\ell + 2^\ell$ modulo $d$. So $d$ divides $2^{N + \ell} + 2^\ell$, and the condition for theorem 2 holds.
