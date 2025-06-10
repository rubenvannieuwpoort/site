---
title: Notes on iterators
date: 2025-06-10
template: post
show: true
---

There are two common ways to implement iteration in imperative programming languages: internal or push iterators, and external or pull iterators. In this article I discuss the details and tradeoffs between them.

As an example, I will use a simple list with names, implemented in Java.
```
var names = List.of("Alice", "Bob", "Charlie");
```

< Java is far from my favourite programming language, but it does have a relatively clean version of both kind of iterators.

**Internal** or **push** iterators implement a method that takes a lambda function that is applied ("pushed") to every element in the iterable. This way, the iteration stays internal to the iterable:
```
names.forEach(name -> System.out.println(name));
```

This is wonderfully simple, but without special support you do not have a way to exit the iteration early.

**External** or **pull** iterators implement an iterator object that allows you to "pull" out elements of the container. This way the iteration is controlled from code external to the iterator.

This is probably the more familiar way of iteration. Conceptually, something that can be iterated over is called an **iterable**. It can be iterated over by using an **iterator**.

This is often implemented as some kind of "iterator protocol" that iterables and iterators have to implement. In practice this often means that iterables have to implement a method (e.g. `iterator`) to get an iterator from an iterable. In turn, iterators have to implement a `next` method that returns the next element (or an exception if there is none), and (optionally) some way to check if there are more elements in the iteration (e.g. a `hasNext` method that indicates if there are more elements).

The idiomatic `for` loop is then just syntatic sugar for directly using the iterator protocol. For example, in Java, we can write
```
for (var name : names) {
	System.out.println(name);
}
```

which is just syntactic sugar for
```
for (Iterator iter = names.iterator(); iter.hasNext(); ) {
	var name = iter.next();
	System.out.println(name);
}
```

External iterators allow you to "bail out" of loops early. For example, with external iterators it is trivial to write a `contains` method that returns if an iterable contains a specific element:
```
static <T> boolean contains(Iterable<T> haystack, T needle) {
	for (T elem : haystack) {
		if (elem == needle) {
			return true;
		}
		return false;
	}
}
```

Again, doing this with internal iterators requires special support.

External iterators not all rainbows and sunshine. They require you to implement a `next` method that returns an element. The hard part is to make sure that the next call to `next` will return the right element. For this, you need keep track of all the necessary state in the iterator.

For some iterables, like linked lists, this is relatively straightforward. But for other iterables, like trees, this becomes much more complex.

All of this raises the question: How do other programming languages handle this?

The three conceptual approaches I have seen are:
- Use generators like in Python.
- Implement special support for internal iterators, so that they can exit early and return a value. This is done in Go and Ruby.
- Completely avoid the problem by not being an imperative programming language that relies on call stacks. Lazy functional programming languages like Haskell fall in this category.

Let's look at this in more detail for a toy example. I want to make an iterator that returns the positive squares 1, 4, 9, 16...


### Python: Generators

Python has support for *generators*. Generators can be thought of functions that do not return a single value. Instead they "yield" a value. After yielding a value, the function pauses and can be called again to yield a next value. When there are no more values to be yield, the generator will raise a `StopIteration` exception.

```
def squares():
   n = 1
   k = 1
   while True:
      yield n
	  k += 2
      n += k
```

Now, the `squares` function returns a generator, which implements the iterator protocol. So we can do `it = squares()` and repeatedly call `next(it)` to get the values, but we can now simply use a `for` loop:
```
count = 0
for s in squares():
   print(s)

   count += 1
   if count == 10:
      break
```

This provides a very nice developer experience.


### Go: Push iterator protocol with compiler transform

Go uses a rather unusual iterator protocol, in which push iterators are the default.

In Go, an iterator for type `V` is a function that returns a function that takes a function as a parameter. The parameter function is named `yield` by convention, and has signature `yield func(V) bool`. A convenient type alias for this is `iter.Seq[V]`:
```
type Seq[V any] func(yield func(V) bool)
```

< Don't feel bad if you are confused by this definition. It is known to break the brains of mere mortals.

The idea is that the iterator pushes the values by calling `yield`. The `yield` function then has the code that handles the elements returned by the iterator, and returns `true` if it wants another element, and `false` if it wants to terminate the iteration.

The implementation for `Squares` looks as follows:
```
func Squares() iter.Seq[int] {
	return func(yield func(int) bool) {
		n := 1
		k := 1
		for {
			if !yield(n) {
				return
			}
			k += 2
			n += k
		}
	}
}
```

If there were no compiler support, we would need to do something like this to get the first 10 values of the iteration:
```
count := 0
yield := func(v int) bool {
	fmt.Println(v)
	count += 1
	if count == 10 {
		return false
	}
	return true
}

seq := allIntegers()
seq(yield)
```

However, through a compiler transform, the normal range loops are transformed to this form. So we can simply write a normal range loop:
```
count := 0
for n := range allIntegers() {
	fmt.Println(n)
	count += 1
	if count == 10 {
		break
	}
}
```

More importantly, the compiler transform *has full support for `break`, `continue`, `defer`, `goto`, and `return`*. I find this quite impressive! More details can be found in [this discussion on GitHub](https://github.com/golang/go/discussions/56413).


### Haskell: lazyness

In Haskell, things are more abstract and we don't have to worry about petty things such as iterators.
```
diffs = [1,3..]
squares = tail . scanl (+) 0 $ diffs
```

> Of course, we have other things to worry about, such as writing Haskell code.

Now, `take 10 squares` takes the first 10 squares from this infinite list.
