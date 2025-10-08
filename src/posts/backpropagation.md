{
    "title": "Notes on backpropagation",
    "description": "My notes on backpropagation.",
    "date": "2025-07-07",
    "show": true
}


These are my notes on using backpropagation for training neural networks.

If you are using a machine learning library that implements automatic differentiation ("autograd"), you don't necessarily need knowledge about backpropagation. However, if for some reason you cannot use a library with autograd, want to implement your own library, or just want to understand the fundamentals of artificial neural networks, you do need an understanding of backpropagation.

## Context

Mathematically, an artificial neural network can be seen as a function $f_P$ that depends on a (usually large) set of parameters $P$. During training the parameters $P$ get adjusted such that
$$ f_P(x) \approx y $$

for tuples $(x, y)$ in a *training set* $D_\text{train}$. We can think of $y$ as the "right" output for input $x$. The hope is that the trained neural network "generalizes", that is, provides a good output for inputs $x$ that are not in the training set.

This is usually done by defining a *loss function* $\ell : \mathbb{R}^M \times \mathbb{R}^M \rightarrow \mathbb{R}_{\geq 0}$, which maps two vectors in the output space of the neural network to a non-negative number. The loss function can be thought of as a measure of how "distant" two output functions are. That is, the smaller $\ell(f_P(x), y)$ is, the closer the output $f_P$ of the neural network is to desired output $y$ for input $x$.

Then, the parameters $P$ are adjusted to minimize $\sum_{(x, y) \in D_\text{train}} \ell(f(x), y)$ using some variant of [gradient descent](https://en.wikipedia.org/wiki/Gradient_descent).

>! During training, the performance of the neural network is usually measured on a *test set* $D_\text{test}$ which does not share input/output tuples with the training set. This is to make sure the neural network doesn't "overfit", which means improving performance on the training set in a way that does not generalize to inputs that are outside of the training set. In general, larger networks suffer less from overfitting, but are slower, need more resources, and need to train for a longer time.

To use gradient descent, the gradient of the loss function $\ell$ with respect to the parameters $P$ has to be computed. The most common algorithm to do this is called "backpropagation", and, depending on who you ask, it's either the pinnacle of modern science and technology, or a straightforward application of the [chain rule](https://en.wikipedia.org/wiki/Chain_rule), known since 1676.


## Structure of neural networks

Most artificial neural networks are structured in layers. We can think of each of these layers as function with its own parameters. The layers then have vectors as input and output.

>! In practice, inputs are often batched, and the different input vectors are concatenated to an input matrix. Likewise, the inputs and outputs of the layers become matrices instead of vectors.

The evaluation of $f_P(x)$ is called *forward propagation* or *inference*, and it's done by evaluating the layers from first to last. Every layer takes an input $x$, the parameters $P$, and returns an output $y$.

![Schematic representation of inference in a single layer in a artifical neural network.](./images/inference.svg)

During backpropagation, we go the other way: From the last layer (which has output the final output during inference), to the first layer.

![Schematic representation of inference in a single layer in a artifical neural network.](./images/backprop.svg)

To do this, the chain rule for multivariate functions can be used, so that we get $\frac{\partial \ell}{\partial x} = \frac{\partial \ell}{\partial y} \frac{\partial y}{\partial x}$ and $\frac{\partial \ell}{\partial P} = \frac{\partial \ell}{\partial y} \frac{\partial y}{\partial P}$. However, in many situations it works better to look at a single element of $\frac{\partial \ell}{\partial P}$, which is the partial derivative of $\ell$ with respect to a single parameter $p$:
$$ \frac{\partial \ell}{\partial p} = \sum_j \frac{\partial \ell}{\partial y_j} \frac{\partial y_j}{\partial p} $$

Then, the expression for $\frac{\partial y_j}{\partial p}$ can be worked out using the definition of the layer and substituted into this equation. The result can often be simplified to something more efficient to evaluate than the expression you get from explicitly evaluating the product $\frac{\partial \ell}{\partial y} \frac{\partial y}{\partial P}$.


## Examples

In the following, $x$ and $y$ are *row* vectors. In mathematics, it is more common to use column vectors, but row vectors have couple of attractive properties. For one, they are more easily written because of their horizontal layout. Many programming languages implement row vectors as an array, and a column vector as an array of arrays. Further, it is convenient that the partial derivative $\frac{\partial \ell}{\partial x}$ and $x$ are both row vectors and have the same shape.


### Linear layer

A linear (or "fully connected") layer simply maps the input row vector $x \in \mathbb{R}^m$ to an output $y \in \mathbb{R}^n$ defined by
$$ y = Wx + b $$

The parameters are $W \in \mathbb{R}^{m \times n}$, which is the matrix of *weights*, and $b \in \mathbb{R}^n$ which is the *bias*.

For a single component of the output $y_j$ we have
$$ y_j = b_j + \sum_{i = 0}^{m - 1} w_{i, j} x_i \tag{1} $$


#### Gradient of the input

We have $\frac{\partial y_j}{\partial x_i} = w_{i, j}$, so that $\frac{\partial y}{\partial x} = W^\top$ and

$$ \frac{\partial \ell}{\partial x} = \frac{\partial \ell}{\partial y} W^\top $$


#### Gradient of the weights

By the multivariate chain rule, we have
$$ \frac{\partial \ell}{\partial w_{i, j}} = \sum_{k = 0}^{n - 1} \frac{\partial \ell}{\partial y_k} \frac{\partial y_k}{\partial w_{i, j}} \tag{2} $$

Taking the derivative of $(1)$ with respect to $w_{i, j}$, we get
$$
\frac{\partial y_k}{\partial w_{i, j}} =
\begin{cases}
x_i & \text{if $k=j$} \\
0 & \text{otherwise}
\end{cases}
$$

And substituting this in $(2)$ yields $\frac{\partial \ell}{\partial w_{i, j}} = \frac{\partial \ell}{\partial y_i} x_i$, so that
$$ \frac{\partial \ell}{\partial W} = x^\top \frac{\partial \ell}{\partial y} $$


#### Gradient of the bias

We can do something similar for the bias. Again we use the multivariate chain rule to get 
$$ \frac{\partial \ell}{\partial b_j} = \sum_{k = 0}^{n - 1} \frac{\partial \ell}{\partial y_k} \frac{\partial y_k}{\partial b_j} \tag{3} $$

By taking the derivative of $(1)$ with respect to $b_j$ we see that
$$
\frac{\partial y_k}{\partial b_j} =
\begin{cases}
1 & \text{if $k=j$} \\
0 & \text{otherwise}
\end{cases}
$$

Substituting this in $(3)$ gives $\frac{\partial \ell}{\partial b_j} = \frac{\partial \ell}{\partial b}$ so that
$$ \frac{\partial \ell}{\partial b} = \frac{\partial \ell}{\partial y} $$


### Activation layer

An activation layer applies a function $f$ to every element of $x$ elementwise. So, $x, y \in \mathbb{R}^m$ and
$$ y_i = f(x_i) $$

Activation layers have no parameters.


#### Gradient of the input

We have
$$ \frac{\partial \ell}{\partial x_i} = \sum_{k = 0}^{m - 1} \frac{\partial \ell}{\partial y_k} \frac{\partial y_k}{\partial x_i} $$

and
$$
\frac{\partial y_k}{\partial x_i} =
\begin{cases}
f'(x_i) & \text{if $k=i$} \\
0 & \text{otherwise}
\end{cases}
$$

So that
$$ \left(\frac{\partial \ell}{\partial x} \right)_i = \frac{\partial \ell}{\partial y_i} f'(x) $$


#### Mean squared error loss function

For an input $x \in \mathbb{R}^m$, the mean squared error loss function $\ell : \mathbb{R}^m \rightarrow \mathbb{R}$ is defined as
$$ \ell(x) = \frac{1}{2m} \sum_{k = 0}^{m - 1} (x_k - c_k)^2 $$

The factor of 2 in the denominator makes the gradient slightly nicer. The loss function depends on the input as well as on a vector $c \in \mathbb{R}^m$, but we consider $c$ a constant instead of a parameter, so we will not compute its gradient.

Considering the derivative with respect to a single element $x_i$, we see $\frac{\partial \ell}{\partial x_i} = x_i - c_i$, so that
$$ \frac{\partial \ell}{\partial x} = x - c $$
