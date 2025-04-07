---
title: Division by constant integers
description: Most modern processors have an integer divide instruction which is relatively slow compared to the other arithmetic operations. When the divisor is known at compile-time or the same divisor is used for many divisions, it is possible to transform the single division to a series of instructions which execute faster. Most compilers will optimize divisions in this way. In this article, I give an overview of the existing techniques for unsigned integers.
date: 2025-04-07
template: post
show: true
---

This post is a survey of the methods to optimize integer division.

The methods in this post originate from the classic 1991 paper ["Division by Invariant Integers using Multiplication" by Torbjörn Granlund and Peter L. Montgomery](https://gmplib.org/~tege/divcnst-pldi94.pdf). In particular, the paper presents what in this post is called the "round-up method". This method was further popularized by Henry S. Warren in his 2002 book "Hacker's Delight". In the 2005 paper ["N-Bit Unsigned Division Via N-Bit Multiply-Add" by Arch D. Robinson](https://www.computer.org/csdl/proceedings-article/arith/2005/23660131/12OmNyQYt7U) presents what in this post is called the "round-down method". In [episode I](https://ridiculousfish.com/blog/posts/labor-of-division-episode-i.html) and [episode III](https://ridiculousfish.com/blog/posts/labor-of-division-episode-iii.html) of the series of articles cleverly named "The Labor of Division", ridiculous_fish both independently discovers the round-down method, and clearly describes both methods.

< ridiculous_fish is the author of the [libdivide](https://libdivide.com) library, a C++ header-only library which uses various methods to speed up division, including the methods described in this post.

What does this post add to the already existing literature? For one, it serves as a reference, combining the results in a rigorous and structured way. I am presenting the results that power the different methods (theorem 2 and 3) in a slightly simpler and more unified way that is consistent with the original presentation in the paper "Division by Invariant Integers using Multiplication".


### Overview

First, the round-up method is presented, which shows that for every $N$-bit divisor $d > 0$ there is a constant $m$ so that the upper bits of $mn$ equal $\lfloor \frac{n}{d} \rfloor$ for every $N$-bit unsigned $n$. For certain "uncooperative" divisors the constant $m$ will not fit in $N$ bits, in which case the method is feasible but less efficient. To improve the efficiency, the round-down method is presented, which is similar to the round-up method but more efficient for uncooperative divisors. Then, we will discuss how the method can be applied to signed integers.


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

**Proof**: Multiplying the inequality by $\frac{n}{d \cdot 2^{N + \ell}}$ we get $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} \leq \frac{n}{d} + \frac{1}{d} \cdot \frac{n}{2^N}$. We have $n < 2^N$, so that $\frac{n}{2^N} < 1$. It follows that $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} < \frac{n}{d} + \frac{1}{d}$. By lemma 1, it follows that $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all integers $n$ with $0 \leq n < 2^N$.

$\square$

So if we can find $\ell$, $m$ satisfying $(1)$, we can compute $\lfloor \frac{n}{d} \rfloor$ as $\lfloor \frac{mn}{2^{N + \ell}} \rfloor$. An $m$ that satisfies $(1)$ exists only if and only if the interval $[2^{N + \ell}, 2^{N + \ell} + 2^\ell]$ contains a multiple of $d$.

< If we know that $m$ is not a power of two, we have $\lceil \frac{2^{N + \ell}}{d} \rceil = \lfloor \frac{2^{N + \ell}}{d} \rfloor + 1$, where the latter might be easier to evaluate.

If $\ell \geq \log_2(d)$, the interval will contain $d$ or more successive integers and we can be certain that the interval contains a multiple of $d$. Since $d \cdot \lceil \frac{2^{N + \ell}}{d} \rceil$ is just the first multiple of $d$ that is at least as large as $2^{N + \ell}$, we can always set $m = \lceil \frac{2^{N + \ell}}{d} \rceil$; if there an $m$ exists that satisfies $(1)$, this $m$ will do so too.

**Corollary 3**: *If $\ell \geq \log_2(d)$ and $m = \lceil \frac{2^{N + \ell}}{d} \rceil$, then $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n < 2^N$*.

However, we would like to have $m < 2^N$ so that $m$ fits in an $N$-bit word, but this requires $\ell < \log_2(d)$. So, this we can't guarantee this, and indeed we see that for some divisors $d$ there only exist $m$, $\ell$ with $m > 2^N$.

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
	return (((uint64_t)954437177) * n) >> 33;
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

Note that $m$ is even, so we can use $\frac{m}{2}$ instead and decrease $\ell$. We get $m = 613566757$, $N = 30$, $\ell = 2$. The optimized version of the function is as follows:
```
uint32_t div28(uint32_t n) {
	n = n >> 2;
	return (((uint64_t)613566757) * n) >> 32;
}
```

TODO: add godbolt links

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

The following theorem powers the **round-down method**. I present the result in a form analogous to theorem 2.

**Theorem 3**: *Let $d$, $m$, $\ell$ be nonnegative integers with $d \neq 0$ and*
$$ 2^{N + \ell} -2^\ell \leq d \cdot m \leq 2^{N + \ell} \tag{2} $$

*then $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n < 2^N$*.

**Proof**: Multiplying the inequality by $\frac{n + 1}{d \cdot 2^{N + \ell}}$ we get $\frac{n}{d} + \frac{1}{d} \cdot (1 - \frac{n + 1}{2^N}) \leq \frac{m(n + 1)}{2^{N + \ell}} \leq \frac{n + 1}{d}$. Since $n < 2^N$ we have $\frac{n}{d} \leq \frac{n}{d} + \frac{1}{d} \cdot (1 - \frac{n + 1}{2^N})$ and the condition of lemma 1 is satisfied. So we have $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all integers $n$ with $0 \leq n < 2^N$.

$\square$

The computation of $m$ is very similar to the round-up method: We take $\ell = \lfloor \log_2(d) \rfloor$ and compute $m = \lfloor \frac{2^{N + \ell}}{d} \rfloor$. The difference is of course that we round $m$ *down* instead of up (which can hardly be a surprise, given the name of the method). So it's only the increment that can overflow.

For the evaluation of the expression $m(n + 1)$ we do need to be careful to avoid overflows again. It can happen that $n = 2^N - 1$, and in this case naively computing $n + 1$ will overflow. The product $m(n + 1)$ needs to be computed with a "widening" multiplication as before (sometimes you can get away with a "compute high word of product" instruction, if the target architecture has one).

Possible strategies to avoid overflow include:
  1. Compute the full $2N$-bit product $mn$ (not just the high $N$-bit word), and add $m$ to that.
  2. Use a saturating increment on $n$. The implementation is architecture-dependent, but it can usually be done with an increment, followed by a single instruction that subtracts the overflow bit.

< In the paper "N-Bit Unsigned Division Via N-Bit Multiply-Add", it is suggested to implement the first method with a fused-multiply-add operation. This works fine if there is such an instruction on the target architecture, like on the Itanium architecture which is used in the article. However, most architectures do not have such an instruction, so I will not go into this approach any further.

In most cases the second approach seems better. The exception is when the division is done on $N$-bit integers but the target architecture is $2N$-bit (typically this happens when dividing 32-bit integers on a 64-bit procesors). In this case, we can just use a $2N$-bit word to store $n + 1$ without worrying about overflow.


### Correctness of the saturating-increment approach

When we use the saturating-increment approach, we calculate $\lfloor \frac{m(n + 1)}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every $n < 2^N - 1$. For $n = 2^N - 1$, incrementing $n$ would lead to an overflow, and we don't increment. This means that instead of $\lfloor \frac{m(n+1)}{2^{N+\ell}} \rfloor = \lfloor \frac{2^N - 1}{d} \rfloor$ we calculate $\lfloor \frac{mn}{2^{N+\ell}} \rfloor = lfloor \frac{2^N-2}{d} \rfloor$. I claim that $\lfloor \frac{2^N - 2}{d} \rfloor = \lfloor \frac{2^N - 1}{d} \rfloor$ when $d$ is an uncooperative divisor.

We only have $\lfloor \frac{2^N - 2}{d} \rfloor \neq \lfloor \frac{2^N - 1}{d} \rfloor$ when $d$ is a divisor of $2^N - 1$. But in this case, we have $2^N \equiv 1 (\text{mod}\ d)$, which means that $2^{N + \ell} + 2^\ell$ equals $-2^\ell + 2^\ell$ modulo $d$. So $d$ divides $2^{N + \ell} + 2^\ell$, and the condition for theorem 2 holds.


### Example

Checking for overflow is a bit messy in pure C. I'll assume we use GCC and use the `__builtin_uadd_overflow` builtin for this. Details can be found [here](https://gcc.gnu.org/onlinedocs/gcc/Integer-Overflow-Builtins.html). To check for overflow, we use it like this:
```
// add unsigned integers x and y
if (__builtin_uadd_overflow(x, y, &result)) {
	// there was an overflow, result equals the low 32 bits of x + y
} else {
	// there was no overflow, result equals x + y
}
```

We'll now implement an optimized version of the following function.
```
uint32_t div7(uint32_t n) {
	return n / 7;
}
```

With $N = 32$ we compute $\ell = \lfloor \log_2(7) \rfloor = 2$. We test if $d = 7$ is a cooperative divisor by checking if $\text{mod}_{2^{32}}(d \cdot m) < 2^\ell$ with $m = \lceil \frac{2^{34}}{7} \rceil$. The left-hand side is 5 and the right-hand side is 4, so $d = 7$ is an uncooperative divisor.

So we use the round-down method and set $m = \lfloor \frac{2^{34}}{7} \rfloor$ so that $\lfloor \frac{m(n + 1)}{2^{34}} \rfloor = \lfloor \frac{n}{7} \rfloor$.

Now, as discussed in the previous section, when $n = 2^N - 1$ we have $\lfloor \frac{mn}{2^{34}} \rfloor = \lfloor \frac{m(n + 1)}{2^{34}} \rfloor = \lfloor \frac{n}{7} \rfloor$ so that we can use a saturating increment to compute $mn$ when $n = 2^N - 1$ and $m(n + 1)$ otherwise.

So we can write an optimized version:
```
uint32_t div7(uint32_t n) {
	if (__builtin_uadd_overflow(n, 1, &n)) {
		n--;
	}
	return (((uint64_t)2454267026) * n) >> 34;
}
```

RISC-V:
```
div7:
	# saturating increment a0
	sltiu   a5,a0,-1
	add     a0,a5,a0

	# get high word of m * (n + 1)
	# (or m * n when n = 2^32 - 1)
	li a4, 2454267026
	mulhu   a0,a0,a4

	# shift right
	srli    a0,a0,2

	ret
```

In x86_64 we get
```
div7:
	# move first arg (n) to eax
	mov eax, edi

	# saturating increment on n
	add eax, 1
	sbb eax, 0

	# get high word of m * (n + 1)
	# (or m * n when n = 2^32 - 1)
	mov edx, 2454267026
	mul rax, rdx

	# shift right
	shr rax, 34

	ret
```

Since `x64_64` is a 64-bit architecture, we can use a 64-bit word for `n + 1` without having to worry about overflow. 
```
uint32_t div7(uint32_t n32) {
	uint64_t n = n32;
	return (((uint64_t)2454267026) * (n + 1)) >> 34;
}
```

This makes the resulting assembly ever so slightly more elegant (and I suspect more efficient as well, although I haven't benchmarked it):
```
div7:
	# move first arg (n) to eax/rax
	mov eax, edi

	# increment rax/n
	add rax, 1

	# load m * (n + 1) into rax
	mov edx, 2454267026
	mul rax, rdx

	# shift rax right
	shr rax, 34

	ret
```


## Signed integers

For nonnegative signed integers, we can use the same expression as we did for the round-up method. In fact, since the maximum magnitude of signed integers is smaller than the maximum magnitude of unsigned integers, it is the case that for every divisor $d > 0$ we can find an $N$-bit magic number $m$ such that
$$ \lfloor \frac{mn}{2^{N - 1 + \ell}}\rfloor = \lfloor \frac{n}{d} \rfloor $$

for all integers $n$ with $0 \leq n \leq 2^N$. Proving this is straightforward using a variation of the proof of theorem 2.

**Theorem 4**: *Let $d$, $m$, $\ell$ be nonnegative integers with $d \neq 0$ and*
$$ 2^{N - 1 + \ell} \leq d \cdot m < 2^{N - 1 + \ell} + 2^\ell $$

*then $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for every integer $n$ with $0 \leq n \leq 2^{N-1}$*.

**Proof**: When $n = 0$ the result is trivial. When $n > 0$, we can multiply the inequality by $\frac{n}{d \cdot 2^{N + \ell}}$ to get $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} < \frac{n}{d} + \frac{1}{d} \cdot \frac{n}{2^N}$. We have $n \leq 2^{N-1}$, so that $\frac{n}{2^N} \leq 1$. It follows that $\frac{n}{d} \leq \frac{mn}{2^{N + \ell}} < \frac{n}{d} + \frac{1}{d}$. By lemma 1, it follows that $\lfloor \frac{mn}{2^{N + \ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ for all integers $n$ with $0 \leq n \leq 2^{N-1}$.

$\square$

But how we do handle the case where the quotient is negative? In most programming languages, integer division rounds *towards zero*. That means that when the quotient is negative, the expression should be rounded up instead of down.

Another subtlety that we have to handle, is that $m$ is an unsigned number while $n$ is a signed number. Processors generally have instructions to multiply unsigned integers or signed integers, but not to multiply a signed integer by an unsigned one. So we have to figure out how we can evaluate this product.

For now, I will assume that the divisor $d$ is positive. I will address the case where $d$ is negative later -- it will turn out to be quite simple to handle.


### Rounding up instead of down

We have the identity $\lfloor \frac{n + d - 1}{d} \rfloor = \lceil \frac{n}{d} \rceil$ when $n$ and $d$ are integers. Using this, we can evaluate $\lceil \frac{mn}{2^{N - 1 + \ell}} \rceil$ as $\lfloor \frac{m(n + d - 1)}{2^{N - 1 + \ell}} \rfloor$.

If $mn$ is not a power of two we have
$$ 2^{N-1+\ell} < md < 2^{N-1+\ell} + 2^\ell $$

Since $2^{N-1+\ell}$ and $2^{N-1+\ell} + 2^\ell$ are consecutive multiples of $2^\ell$, $md$ cannot be one. So $m$ also cannot be a multiple of $2^\ell$, and for an $N$-bit signed integers $n$, $mn$ can not be a multiple of $2^{N-1+\ell}$, given that $n = -2^{N-1}$ has the highest number of two's in its factorization.

So $\frac{mn}{2^{N-1+\ell}}$ is not an integer and we have
$$ \lceil \frac{mn}{2^{N - 1 + \ell}} \rceil = \lfloor \frac{mn}{2^{N - 1 + \ell}} \rfloor + 1 $$

when $d$ is not a power of two. This last expression is potentially more efficient to evaluate.

So in practice we want to compute
$$ \lfloor \frac{mn}{2^{N - 1 + \ell}} \rfloor + 1_{n < 0} $$

when $d$ is not a power of two. An efficient way of adding $1_{n < 0}$ is by subtracting `n >> (N - 1)`. This expression will be $-1$ when $n$ is negative, and $0$ otherwise. By swapping the operands of the subtraction, we can negate the result "for free".

When $d$ is a power of two this will not work, and we need to explicitly negate the result. This can be done in a single instruction on most architectures.

### Computing the product of a signed and an unsigned integer

If we set $\ell = \lceil \log_2(d) \rceil$, the value $m = \lceil \frac{2^{N-1+\ell}}{d} \rceil$ with  is an $N$-bit unsigned integer with the most significant bit set. When $m$ is even, we can use $m' = \frac{m}{2}$ and use
$$ \frac{mn}{2^{N-1+\ell}} = \frac{m'n}{2^{N-2+\ell}} $$

This is easier to evaluate since we can now simply compute $m'n$ as a signed product.

When $m$ is odd, we do not have this option. Let $m_s$ be the value obtained by interpreting the bits of $m$ (represented as an unsigned integer) as a signed integer. That is, if $m = \sum_{k=0} 2^k m_k$, then
$$ m_s = -2^{N-1}m_{N-1} + \sum_{k = 0}^{N-2} 2^k m_k $$

So we have $m = m_s + 2^k$ so that
$$ mn = (m_s + 2^k)n = m_s n + 2^k n$$

That is, we can use a signed product to evaluate $m_s n$, and add $n$ to the high word of the product. The result will be $mn$.


### Examples

#### Example 1: Dividing by 7

For a simple example, consider the following function:
```
int32_t div7(int32_t n) {
	return n / 7;
}
```

With $N = 32$ we find $\ell = \lceil \log_2(7) \rceil = 3$, $m = \lceil \frac{2^{N - 1 + \ell}}{d} \rceil = 245426702$. This is an odd number, so we can't simplify. Since $m$ is a 32-bit number, we'll have to evaluate the high word of the product `mn_hi` as `mn_signed_hi + n`. Here, `mn_signed_hi` is the product of $n$ and $m'$, and $m'$ is the interpretation of $m$ as a signed word. When we interpret $m$ as a signed number, we get $245426702 - 2^{32} = -1840700269$, so this is what we use in the multiplication, instead of the unsigned value of $m$.

We proceed by shifting right the rest of the bits. We have already shifted the product by $32$ bits, so we need to shift right by $2$ additional bits. Finally, we correct the rounding by adding `n >> 31`.

All in all, we get
```
int32_t div7(int32_t n) {
	int32_t m = -1840700269;

	// evaluate the high word of m * n
	int32_t mn_signed_hi = ((int64_t)m * n) >> 32;
	int32_t mn_hi = mn_signed_hi + n;

	// shift remaining bits and correct rounding
	return (mn_hi >> 2) - (n >> 31);
}
```

This results in the following assembly:
```
div7:
	# move n to ecx
	mov ecx, DWORD PTR [esp+4]

	# move m to eax
	mov eax, -1840700269

	# move m*n to edx:eax
	imul ecx

	# add n and store in eax
	add eax, [edx+ecx]

	# shift right by two and add (n << 31)
	sar     ecx, 31
	sar     eax, 2
	sub     eax, ecx
	ret
```

Also, GCC sometimes prefers to use a `lea` instruction instead of a simple addition. This is the only difference between the assembly generated by the two C functions above.

To divide by -7 we can now simply swap the operands of the subtraction in the `return` statement. However, GCC seems to have difficulties generating efficient assembly for this, and the resulting assembly is definitely not equivalent to the assembly that results from compiling `int32_t div7(int32_t n) { return n / -7; }`.


#### Example 2: Dividing by 9

Now, consider the following function:
```
int32_t div9(int32_t n) {
	return n / 9;
}
```

Setting $\ell = \lceil \log_2(9) \rceil = 4$, we get $m = \lceil \frac{2^{N-1+\ell}}{9} \rceil = 3817748708$. This is even so we can decrease $\ell$ to $3$ and get $m = 1908874354$. This is again even so we can decrease $\ell$ once more to get $2$ and we get $m = 954437177$.

This fits in a signed 32-bit integer and we can proceed as before, except that we can use a simple signed product to evaluate $mn$.
```
int32_t div9(int32_t n) {
	int32_t m = 954437177;

	// evaluate the high word of m * n
	int32_t mn_hi = ((int64_t)m * n) >> 32;

	// shift remaining bits and correct rounding
	return (mn_hi >> 2) - (n >> 31);
}
```


#### Example 3: Dividing by 4096

Consider the following function:
```
int32_t div4096(int32_t n) {
	return n / 4096;
}
```

If we divide by a power of two we simply need to add `d - 1` to `n` to fix the rounding. Otherwise, the division is a simple shift:
```
int32_t div4096(int32_t) {
	if (n < 0) {
		n += 4095;
	}
	return n >> 12;
}
```

In practice, GCC compiles both versions to the same assembly which uses a `cmovs` instruction (conditional move when the sign bit is not set):
```
div4096:
	# move n to eax
	mov eax, DWORD PTR [esp+4]

	# add 4095 to eax if it is negative
	test eax, eax
	lea edx, [eax+4095]
	cmovs eax, edx

	# arithmetic shift right by 12 bits
	# (i.e. signed divide by 4096)
	sar eax, 12
	ret
```

## Addendum

(This section is a work-in-progress.)

During the writing of this last section, I noticed that for some computation (e.g. $d = 3$ for 32-bit signed integers), GCC can simplify the computation while the constant $m$ is odd. That is, the test in this article is too strict. Doing the computations by hand, I came to the conclusion that
- Let $p$ be $d \cdot (\lceil \frac{2^N}{d} \rceil - 1) + 1$. That is, take the largest number $p$ smaller than $2^N$ that has $\text{mod}_d(p) = d - 1$. For signed integers, this should be the largest number $p$ smaller than or equal to $2^{N - 1}$.
- Let $m = \lceil \frac{2^{N+\ell}}{d} \rceil$ and $k = dm - 2^{N+\ell}$

Now, if $kp < 2^N$, then $\lfloor \frac{mn}{2^{N+\ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$.

I realize this is highly cryptic and need to spend some effort to explain this and bring it into a more digestable form. The basic idea is to realize that the equality $\lfloor \frac{mn}{2^{N+\ell}} \rfloor = \lfloor \frac{n}{d} \rfloor$ will first fail when $\text{mod}_d(n) = d - 1$, and that if the equality holds for the largest possible $n$ of this form, the equality will hold for all $n$ in the range.
