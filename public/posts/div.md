---
title: Division by constant unsigned integers
description: Most modern processors have an integer divide instruction which is relatively slow compared to the other arithmetic operations. When the divisor is known at compile-time or the same divisor is used for many divisions, it is possible to transform the single division to a series of instructions which execute faster. Most compilers will optimize divisions in this way. In this article, I give an overview of the existing techniques for unsigned integers.
date: 2020-08-28
template: post
show: false
---

This post is a survey of the methods to optimize unsigned integer division. It largely follows the approach and terminology in the excellent articles [TODO] by ridiculous_fish, but aims to be slighly more rigorous and concise.

< These articles were written by ridiculous_fish, the author of the [libdivide](https://libdivide.com) library, a C++ header-only library which uses various methods to speed up division, including the methods described in this post.

First, the round-up method is presented, which shows that for every $N$-bit divisor $d > 0$ there is a constant $m$ so that the upper bits of $mn$ equal $\lfloor \frac{n}{d} \rfloor$ for every $N$-bit unsigned $n$. For certain "uncooperative" divisors the constant $m$ will not fit in $N$ bits, in which case the method is feasible but less efficient. To improve the efficiency, the round-down method is presented, which is similar to the round-up method but more efficient for uncooperative divisors.


## Intuition

To understand why these multiplicative methods work, let’s build some intuition. The idea is to choose an integer constant, $m$, that approximates $\frac{2^k}{d}$. This way, $m$ effectively represents $\frac{1}{d}$ in binary form. Multiplying by $2^k$ shifts the fractional bits to more significant positions, allowing them to be captured as an integer.

Simply put, since we have $m \approx \frac{2^k}{d}$, we expect that $\frac{mn}{2^k} \approx \frac{n}{d}$. So, it isn't to far-fetched to expect that $\lfloor \frac{mn}{2^k} \rfloor = \lfloor \frac{n}{d} \rfloor$. In the next section we'll see under which conditions this equality holds.

If this doesn't click yet, consider an example in base 10 instead. Pick $d = 3$ and instead of $2^k$, we'll pick $10^4$ and $m = 3334 \approx \frac{10^4}{3}$. Picking $n = 492$ we see that $\frac{mn}{10^4} = \frac{1640328}{10^4}$. This equals $164.0328$, so indeed we have $\lfloor \frac{mn}{10^4} \rfloor = \lfloor \frac{492}{3} \rfloor = 164$.

< Note that we didn't round $\frac{10^4}{3}$ to the closest integer here, and we would get an incorrect result if we did.


## Round-up method

We start with deriving a theorem that shows the method is correct. To prove this theorem, we'll need the following lemma.

**Lemma 1**: *Suppose that $n$ and $d$ are integers with $d > 0$, and $x$ is a real number. If $\frac{n}{d} \leq x < \frac{n + 1}{d}$ then $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.*

**Proof**: We have $\frac{n}{d} \leq x < \frac{n + 1}{d} \leq \lfloor \frac{n}{d} \rfloor + 1$. After taking the floor of all terms and considering that the right-hand side is an integer, we get $\lfloor \frac{n}{d} \rfloor \leq \lfloor x \rfloor < \lfloor \frac{n}{d} \rfloor + 1$, which implies $\lfloor x \rfloor = \lfloor \frac{n}{d} \rfloor$.

$\square$

Now, we are ready to prove the result that justifies the round-up method.

**Theorem 2**: *Let $d$, $m$, $\ell$ be nonnegative integers with $d \neq 0$ and*
$$ 2^{N + \ell} \leq d \cdot m \leq 2^{N + \ell} + 2^\ell \tag{1} $$

*then $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n < 2^N$*.

**Proof**: Multiplying the inequality by $\frac{n}{d \cdot 2^{N + \ell}}$ we get $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d} \cdot \frac{n}{2^N}$. We have $n < 2^N$, so that $\frac{n}{2^N} < 1$. It follows that $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d}$. By lemma 1, it follows that $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all integers $n$ with $0 \leq n < 2^N$.

$\square$

So if we can find $\ell$, $m$ satisfying $(1)$, we can compute $\lfloor \frac{n}{d} \rfloor$ as $\lfloor \frac{mn}{2^{N + \ell}} \rfloor$. An $m$ that satisfies $(1)$ exists only if and only if the interval $[2^{N + \ell}, 2^{N + \ell} + 2^\ell]$ contains a multiple of $d$.

< If we know that $m$ is not a power of two, we have $\lceil \frac{2^{N + \ell}}{d} \rceil = \lfloor \frac{2^{N + \ell}}{d} \rfloor + 1$, where the latter might be easier to evaluate.

If $\ell > \log_2(d)$, the interval will contain $d$ or more successive integers and we can be certain that the interval contains a multiple of $d$. Since $d \cdot \lceil \frac{2^{N + \ell}}{d} \rceil$ is just the first multiple of $d$ that is at least as large as $2^{N + \ell}$, we can always set $m = \lceil \frac{2^{N + \ell}}{d} \rceil$; if there an $m$ exists that satisfies $(1)$, this $m$ will do so too.

On the other hand, we would like to have $m < 2^N$ so that $m$ fits in an $N$-bit word, but this requires $\ell < \log_2(d)$. So, this we can't guarantee this, and indeed we see that for some divisors $d$ there only exist $m$, $\ell$ with $m > 2^N$.

So, concretely, how can we find $m$ and $\ell$? First we pick $\ell = \lfloor \log_2(d) \rfloor$ and set $m = \lceil \frac{2^{N + \ell}}{d} \rceil$. For $m$ calculating this way we have $m < 2^N$, so we have to check that it satisfies $(1)$.

< An efficient way to test if $(1)$ is satisfied is work modulo $2^N$ (i.e. ignore overflow). The test can then simply be implemented as `d * m < (1 << l)`.

We can also see that if $m$ is even, we can divide we can divide all terms in $(1)$ by two and get the valid equation $2^{N + \ell - 1} \leq d \cdot \frac{m}{2} \leq 2^{N + \ell - 1} + 2^{\ell - 1}$. So if $m$ is even we can replace $m$ by $\frac{m}{2}$ and $\ell$ by $\ell - 1$, and $(1)$ will still hold. In some cases, this allows us to find a smaller constant $m$ that still satisfies $(1)$.

We will call a divisor $d$ for which an $m < 2^N$, $\ell$ satisfying $(1)$ exists **cooperative**, because they allow us to easily compute the product $mn$ for $N$-bit unsigned integers $N$. Divisors that are not cooperative are called **uncooperative**; for them it is more tricky and less efficient to calculate the product $mn$. We will consider both cases in the following subsections.


### Cooperative divisors

To make the last section more concrete, let's optimize the following function.
```
uint32_t div9(uint32_t n) {
	return n / 9;
}
```

Using the strategy outlined in the previous section, we set $\ell = \lfloor \log_2(9) \rfloor = 3$ and compute $m = \lceil \frac{2^{32 + 3}}{9} \rceil = 3817748708$. Working modulo $2^{32}$ we see that $\text{mod}_{2^{32}}(d \cdot m)$ equals $\text{mod}_{2^{32}}(34359738372) = 4$. We have $4 < 2^3$, so the test succeeds and $3$ is a cooperative divisor.

However, we see that $m$ is even. We can divide it by two to get $3817748708$, which is also even. Dividing by two once more gives $954437177$. Adjusting for this, we only need to shift right by $33$ bits, instead of $35$.

So the optimized version of the function is

< The constant `954437177` is a 32-bit number, but it needs to be converted to a `uint64_t` to get the full 64-bit product.

```
uint32_t div9(uint32_t n) {
	return (uint64_t(954437177) * n) >> 33;
}
```

Indeed, GCC compiles `div9` and `div9_opt` to the same assembly. For example in `x86_64` we get:
```
div9:
	mov eax, edi
	mul rax, rax, 954437177
	shr rax, 33
	ret
```

For 32-bit instruction sets, the shift is usually implemented by taking the high 32-bit word of the full 64-bit and performing a right shift by one on that. For example, in 32-bit RISC-V:
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

Doing the same, we compute $\ell = \lfloor \log_2(7) \rfloor = 2$, $m = \lceil \frac{2^{32 + 2}}{7} \rceil = 2454267027$. Now, we compute $\text{mod}_{2^{32}}(d \cdot m)$ to be $\text{mod}_{2^{32}}(17179869189) = 5 > 4$. So the test fails and $7$ and we see that $7$ is an uncooperative divisor.

This means we can't use the value we just calculated for $m$ and instead we have to set $\ell = \lceil \log_2(7) \rceil = 3$. We get $m = \lceil \frac{2^{32 + 3}}{7} \rceil = 4908534053$. This is a 33-bit value and we have to resort to some tricks to evaluate $\lfloor \frac{mn}{2^{N + \ell}} \rfloor$ without overflow.

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

Suppose we have an even uncooperative divisor $d$ of the form $d = 2^pc$, so that $p \geq 1$. We can implement a division by $d$ as a division by $2^p$ -- which can be implemented efficiently with a bit shift -- followed by a division by $c$. Now, $c$ will be a uncooperative divisor too, but since the dividend $n$ will only be an $(N - p)$-bit number, the constant $m$ will fit in $N$ bits. This only costs us a single bit shift, which is more efficient than implementing the overflow-avoiding product from last section.

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

The following theorem powers the **round-down method**. I present the result in a forum analogous to theorem 2.

**Theorem 3**: *Let $d$, $m$, $\ell$ be nonnegative integers with $d \neq 0$ and*
$$ 2^{N + \ell} -2^\ell \leq d \cdot m \leq 2^{N + \ell} \tag{2} $$

*then $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n < 2^N$*.

**Proof**: Multiplying the inequality by $\frac{n + 1}{d \cdot 2^{N + \ell}}$ we get $\frac{n}{d} + \frac{1}{d} \cdot (1 - \frac{n + 1}{2^N}) \leq \frac{m(n + 1)}{2^{N + \ell}} \leq \frac{n + 1}{d}$. Since $n < 2^N$ we have $\frac{n}{d} \leq \frac{n}{d} + \frac{1}{d} \cdot (1 - \frac{n + 1}{2^N})$ and the condition of lemma 1 is satisfied. So we have $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all integers $n$ with $0 \leq n < 2^N$.

$\square$

The result is fairly straightforward to use. However, we need to take care of overflows again. There are multiple strategies to avoid overflow:
  1. Compute the full $2N$-bit product $mn$ (not just the high $N$-bit word), and add $m$ to that.
  2. If the target architecture has a fused-multiply-add instruction, use that to evaluate $m(n + 1)$ as $mn + m$.
  3. Use a saturating increment on $n$. This can usually be done with an increment, followed by a single instruction that subtracts the overflow bit.

The first approach is the most obvious one. The second approach was suggested in TODO, and the third one in TODO. I suggest going with the third approach, since it seems to be reasonably portable between instruction sets, and slightly more efficient than the other approaches.


### Correctness of the saturating-increment approach

When we use saturating-increment approach, we calculate $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every $n < 2^N - 1$. For $n = 2^N - 1$, we don't increment, so we effectively calculate $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{2^N - 2}{d} \rfloor$. This seems wrong, but it's correct as long as $d$ is an uncooperative divisor. This is OK, since if $d$ is a cooperative divisor, we would like to use the round-up method anyway.

We only have $\lfloor \frac{2^N - 2}{d} \rfloor \neq \lfloor \frac{2^N - 1}{d} \rfloor$ when $d$ is a divisor of $2^N - 1$. But in this case, we have $2^N \equiv 1 (\text{mod}\ d)$, which means that $2^{N + \ell} + 2^\ell$ equals $-2^\ell + 2^\ell$ modulo $d$. So $d$ divides $2^{N + \ell} + 2^\ell$, and the condition for theorem 2 holds.
