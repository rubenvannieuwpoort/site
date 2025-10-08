{
    "title": "Better approximate atavising",
    "date": "2025-03-24",
    "show": true
}


As I learned from [this article](https://hardmath123.github.io/conways-gradient.html), atavising is the art of "reversing" [Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) configurations. In the article, "differentiable automata" are used to atavise an image of Conway.

Nice! However, it seemed to me that a much simpler method would also work. For a Game of Life configuration $C$, let $N(C)$ be the next configuration, $T$ be the target image, and $d$ be a distance function so that $d(C, T)$ is small when $C$ and $T$ are visually similar (here, $T$ can be an image with non-binary values). We can now do this:

0. Start with some Game of Life configuration $C$.
1. Flip a random pixel in $C$ and call the result $C'$.
2. If $d(S(C'), T) < d(S(C), T)$, set $C \leftarrow C'$.
3. Go to step 1.

The distance function applies a simple blurring kernel, gamma encoding, and takes the sum of the squares of the difference for each pixel. Because both the blurring kernel and computing the next Game of Life configuration only depend on pixels that are near the flipped pixel, we can get away with only computing the distance over a small section around the flipped pixel, and the whole process is reasonably efficient even without optimizations.

I wrote a simple C program that does this and displays the result using SDL. The code can be found on [GitHub](https://github.com/rubenvannieuwpoort/conlife). If I run the program for this target image:

![Small image of Conway](images/conway_small.png)

The result converges to this within 10 seconds:

![Small atavised image of Conway](images/conway_small_atavised.png)

Which arguably is of higher quality than the atavised image obtained by using the differentiable automata:

![Original small atavised image of Conway](images/conway_small_atavised_original.png)

Using a higher resolution image is entirely feasible. This is a 707 by 900 picture of Conway:

![Large atavised image of Conway](images/conway_large_atavised.png)

Even atavising multiple generations is feasible, although the quality degrades quickly with the number of generations. This is the same image, atavised 3 generations:

![Large image of Conway atavised over multiple generations](images/conway_large_atavised_multigen.png)
