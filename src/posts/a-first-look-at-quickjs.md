{
    "title": "A first look at QuickJS",
    "description": "QuickJS is, in the words of its author, a small and embeddable Javascript engine. It provides a C API that can be used to run Javascript from C code and vice versa. Like many of Fabrice Bellard's projects, the project is very impressive. However, there is barely any documentation of the C API. In this post, I show some examples to get you started.",
    "date": "2025-08-25",
    "show": true
}

QuickJS is, in the words of its author, a small and embeddable Javascript engine. It provides a C API that can be used to run Javascript from C code and vice versa. Like many of Fabrice Bellard's projects, the project is very impressive. However, there is barely any documentation of the C API. In this post, I show some examples to get you started.


## Retrieving QuickJS

You can retrieve QuickJS in two ways:
1. Clone the [GitHub repository](https://github.com/bellard/quickjs)
2. Download and extract the source from the [QuickJS page](https://bellard.org/quickjs)


### Cloning the repository

To clone the repository:
```
git clone https://github.com/bellard/quickjs.git
```


### Downloading and extracting a release

To download and extract the source from the QuickJS page:
```
wget https://bellard.org/quickjs/quickjs-2025-04-26.tar.xz
tar -xf quickjs-2025-04-26.tar.xz
```

The rest of the instructions assume that we are running commands from a folder that contains QuickJS in a folder called `quickjs`, so we rename the folder:
```
mv quickjs-2025-04-26.tar.xz quickjs
```

Note that this downloads the 2025-04-26 release, which is the latest release at the time of writing. If you want to have the latest release you should check the [QuickJS page](https://bellard.org/quickjs) for new releases and download and extract it if there is a newer one.


## Building QuickJS

The repository and release only contain the source. Before we can use QuickJS we should still build it. Luckily, this is very easy since QuickJS has no dependencies on external source code or libraries. You just need a C compiler and Make to build it:
```
cd quickjs
make
```


## Introduction to QuickJS

After building, there should be two binaries in the `quickjs`:
- `qjs`, which is the Javascript interpreter that uses the QuickJS library.
- `qjsc`, which is a Javascript compiler. It can either compile Javascript to an executable, or to a C file that uses the QuickJS C API.

The compiler compiles Javascript to bytecode, which can then be executed by the C API. The generated C file contains the bytecode as a binary blob.

We are mostly interested in using the compiler, but I'll briefly show how the interpreter can be used as well.


### Using the interpreter

The interpreter can be used as a REPL, or to run a script or module.

#### Using the REPL

By starting the interpreter without any arguments, it acts as a REPL:
```
$ quickjs/qjs
qjs > console.log("Hello, REPL!")
Hello, REPL!
undefined
```

As you can see, it works like most REPLs: It evaluates the expression, and prints the result. In this case, the call to `console.log` prints `"Hello, REPL!"` to the screen, and returns `undefined`, which is then also printed. You can type `\q` and press `ENTER`, press `Ctrl-D`, or press `Ctrl-C` twice to exit.

Alternatively, you can use the interpreter to execute a script or module. QuickJS supports ES6 scripts and modules and will try to autodetect if the thing you're trying to run is a script or a module, according to the following rules:
- If the extension of the file is `.mjs`, the file is loaded as a module.
- If the first keyword in the source of the file is `import`, the file is loaded as a module.
- Otherwise, the file is loaded as a script.

You can force the interpreter to load the file as a module by providing the `-m` keyword.

I will use the following test files.

`test.js`:
```
// this is a test script
function hello() {
    console.log("Hello, world!");
}

hello();
```

`test.mjs`:
```
// this is a test module
export function hello() {
    console.log("Hello, world!");
}

hello();
```


#### Running a script or module

With the `-i` commandline option, we can start the REPL after interpreting also call any functions that are defined in the script:
```
$ quickjs/qjs -i test.js
qjs > greeting()
Hello, world!
undefined
```


#### Running a function from a script

Running a function from a script is very easy. We can run
```
$ quickjs/qjs hello.js
qjs > hello()
Hello, world!
undefined
```


#### Running a function from a module

For modules, we cannot use a static import (of the form `import { hello } from "./hello/mjs"`) in the interpreter, but we can do a _dynamic import_:
```
$ quickjs/qjs
qjs > const { hello } = await import("./hello.mjs");
undefined
qjs > hello();
Hello, world!
undefined
```


### Using the compiler

The compiler can compile to a binary directly, or to a C file that we can then compile ourselves with a C compiler (I believe only GCC is supported, though). I'll use the same test files as in the previous section.


#### Compiling to a binary

Compiling to a binary again is very easy.

```
$ quickjs/qjsc -o main main.js
$ ./main
Hello, world!
```

It works exactly the same for a module.


#### Compiling to a C file

If we compile to a C file we'll have to use the `-e` flag when invoking the `qjsc` compiler. If we just want the bytecode, we can use the `-c` flag.

```
$ quickjs/qjsc -e -o test.c test.js
$ gcc -Iquickjs -lm test.c quickjs/libquickjs.a -o test
$ ./test
Hello, world!
```

Alternatively, we can compile from source directly:
```
gcc -Iquickjs test.c -lm -DCONFIG_VERSION=\"2025-04-26\" -D_GNU_SOURCE quickjs/quickjs.c quickjs/quickjs-libc.c quickjs/libregexp.c quickjs/libunicode.c quickjs/cutils.c quickjs/dtoa.c
```

The exact command that you need to run depends on the version of QuickJS. I have found this by looking at the `Makefile`, and just trying to compile, reading the error messages to see which references are missing, finding in which source file they are defined, and adding the source file.


#### Calling a Javascript function from the C API

Suppose we have a file `add.js` with the following contents:
```
function add(x, y) {
	return x + y;
}
```

>! This example shows how to call a function defined in a script. Functions in modules are defined in their own namespace, and I have not succeeded in calling a function from a module from the C API directly, although the C API contains functions which seem to hint at support for this. Instead, you can use a wrapper script that imports the function, or you can manually assign the function to export to `globalThis` in a module.

We now compile this file to a C file:
```
quickjs/qjsc -e -o add.c
```

In `add.c`, we can add the following code right after the call to `js_std_loop(ctx);` in the `main` function:
```
JSValue global = JS_GetGlobalObject(ctx);
JSValue add = JS_GetPropertyStr(ctx, global, "add");

JSValue args[2];
args[0] = JS_NewInt32(ctx, 2);
args[1] = JS_NewInt32(ctx, 3);

JSValue js_result = JS_Call(ctx, add, JS_UNDEFINED, 2, args);

uint32_t c_result;
JS_ToInt32(ctx, &c_result, js_result);
printf("%u\n", c_result);

JS_FreeValue(ctx, js_result);
JS_FreeValue(ctx, args[1]);
JS_FreeValue(ctx, args[0]);
JS_FreeValue(ctx, add);
JS_FreeValue(ctx, global);
```

This:
1. Gets the `globalThis` object.
2. Gets the `add` property from it.
3. Sets up an array called `args` with two elements.
4. Initializes the elements to Javascript values of 2 and 3.
5. Calls the `add` method with those arguments.
6. Converts the result back to a C `uint32_t` and prints it.
7. Cleans up all the values

This is quite a lot of boilerplate, and I am not even checking for errors, but it works!

To make the code a bit simpler, you can clean up the initialization in the generated `add.c` a bit. I ended up with the following `main` function:
```
int main(int argc, char **argv)
{
  JSRuntime *rt = JS_NewRuntime();
  js_std_init_handlers(rt);

  JSContext *ctx = JS_NewContextRaw(rt);
  JS_AddIntrinsicBaseObjects(ctx);

  js_std_eval_binary(ctx, qjsc_add, qjsc_add_size, 0);

  JSValue global = JS_GetGlobalObject(ctx);
  JSValue add = JS_GetPropertyStr(ctx, global, "add");

  JSValue args[2];
  args[0] = JS_NewInt32(ctx, 2);
  args[1] = JS_NewInt32(ctx, 3);

  JSValue js_result = JS_Call(ctx, add, JS_UNDEFINED, 2, args);

  uint32_t c_result;
  JS_ToInt32(ctx, &c_result, js_result);
  printf("%u\n", c_result);

  JS_FreeValue(ctx, js_result);
  JS_FreeValue(ctx, args[1]);
  JS_FreeValue(ctx, args[0]);
  JS_FreeValue(ctx, add);
  JS_FreeValue(ctx, global);

  js_std_free_handlers(rt);
  JS_FreeContext(ctx);
  JS_FreeRuntime(rt);
  return 0;
}
```

To see which calls you can remove, you might want to have a look at the source code, and consider what features the Javascript code you're calling is using. I advise to first get it working with all the initialization, then remove it step-by-step, ensuring that everything still works after cleaning up some code.
