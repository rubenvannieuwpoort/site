{
    "title": "Some identities involving integer division",
    "description": "Writing other articles, I have worked out quite some identities involving integer division, and I decided to write them down.",
    "date": "2025-04-12",
    "show": true
}


I have worked out quite some identities involving integer division while writing other articles, and I decided to write them down for reference.

The variables $m$, $n$, $d$ are assumed to be integers (with $d \neq 0$) throughout this article, whereas $x$ is a real variable.


### Rounding up and down

When we divide unsigned integers `n` and `d`, the result gets rounded down. That is, `n / d` evaluates to $\lfloor \frac{n}{d} \rfloor$. If we want to round up the quotient, we can do it as `(n + d - 1) / d`. Here, we are using the following identity:
$$ \lfloor \frac{n + d - 1}{d} \rfloor = \lceil \frac{n}{d} \rceil $$

The relation between the floor and the ceil function is that
$$ \lfloor - x \rfloor = - \lceil x \rceil $$


### Rounding to multiples of $d$

To round down an integer $n$ to the nearest multiple of $d$, we can use the expression $d \lfloor \frac{n}{d} \rfloor$. Alternatively, we can use modular arithmetic to write this expression as
$$ n - \text{mod}_d(n) $$

Likewise, we can round up an integer $n$ to the nearest multiple of $d$ with the expression $d \lceil \frac{n}{d} \rceil$. With modular arithmetic we can write this as
$$ n + \text{mod}_d(-n) $$


### Getting rid of floor/ceil

Sometimes, it is useful to get rid of the floor or ceiling function from an expression. From the results in the last section we can derive the following identities which allow you to do this.

For the floor function, we have:
$$ \lfloor \frac{n}{d} \rfloor = \frac{n - \text{mod}_d(n)}{d} $$

And for the ceil function:
$$ \lceil \frac{n}{d} \rceil = \frac{n + \text{mod}_d(-n)}{d} $$


### Sum identity

I write $q_n = \lfloor \frac{n}{d} \rfloor$, $p_n = \text{mod}_d(n)$, so that we have $n = d q_n + p_n$.

By working out $\lfloor \frac{m + n}{d} \rfloor = \lfloor \frac{(dq_m + p_m) + (dq_n + p_n)}{d} \rfloor$ we can prove that
$$ q_{n + m} = q_n + q_m + \lfloor \frac{p_n + p_m}{d} \rfloor $$

Likewise, we can write $s_n = \lceil \frac{n}{d} \rceil$, $r_n = \text{mod}_d(-n)$, so that $n = d s_n - r_{-n}$.

Then, we can work out $\lceil \frac{m + n}{d} \rceil = \lceil \frac{(d s_m - r_m) + (d s_n - r_n)}{d} \rceil$ and get the identity
$$ s_{n + m} = s_n + s_m - \lfloor \frac{r_n + r_m}{d} \rfloor $$

### Product identity

Again, I write $q_n = \lfloor \frac{n}{d} \rfloor$, $p_n = \text{mod}_d(n)$, so that we have $n = d q_n + p_n$.

By working out and simplifying the expression $\lfloor \frac{mn}{d} \rfloor = \lfloor \frac{(dq_m + p_m)(dq_n + p_n)}{d} \rfloor$ we can prove that
$$ q_{nm} = d q_m q_n + p_m q_n + q_m p_n + \lfloor \frac{p_n p_m}{d} \rfloor $$

Again writing $s_n = \lceil \frac{n}{d} \rceil$, $r_n = \text{mod}_d(-n)$, we have $n = d s_n - r_{-n}$.

Now we can work out $\lceil \frac{mn}{d} \rceil = \lceil \frac{(d s_m + r_m)(d s_n + r_n)}{d} \rceil$ and get the identity
$$ s_{nm} = d s_m s_n - (r_m s_n + s_m r_n) + \lceil \frac{r_n r_m}{d} \rceil $$
