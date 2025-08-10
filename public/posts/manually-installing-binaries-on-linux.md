---
title: Manually installing binaries on Linux
description: 
date: 2025-08-10
template: post
show: true
---

I have often run into situations where I want to manually install a binary on a Linux system. I don't do this often enough to recall the specific details, so I am documenting the process here as a reference for myself.

Suppose you want to install a program or toolchain. Say, the toolchain for the [Go programming language](https://go.dev).

On Linux, it is usually recommended to use your systems package manager to install packages. This has several advantages:
- Using the systems package manager provides a uniform way of installing, updating, and removing packages.
- You install binaries that are built, tested (and possibly modified) specifically for your distro.
- Packages in a distributions package registry are typically signed and are considered more secure than your average "binary from the internet".

< If Linux distributions make changes to the source before building and uploading a package to their registry, this is known as "applying downstream patches". The qualifier "downstream" refers to the fact that the changes are not made in the original source ("upstream").

However, using your system package manager to install packages also has several disadvantages compared to installing a binary:
- The package manager might not always have the latest version.
- The downstream patches applied by the different distributions might be undesirable. In some cases they have introduced bugs.

For these reasons, many projects, including Go, recommend manually installing the binaries. This works like this:

#### 1. Download the binary

The binary usually comes in some sort of a compressed file format, like a tarball (a `.tar.gz` file), or a `.zip` file.


#### 2. Look at the file structure and decide where to extract to

By convention, user-managed binaries for all users should go into `/usr/local/bin` on Linux distributions. Binaries for specific users should go into `/home/<user>/.local/bin` on most modern Linuxes, and into `/home/<user>/bin` on some older or more traditional Unixes.

< The [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec), which most modern Linuxes follow, specifies that you should use `/home/<user>/.local/bin`.

If the compressed archive contains a single binary, you can put it directly in `/usr/local/bin` (or whatever folder you picked to install to).

However, most archives contain multiple files. If the archive contains a single folder that contains all the other files and directories you can extract to `/usr/local/`. For example, the archive for the Go toolchain is structured like this:
```
go/
├╴bin
│ ├  go
│ └╴ gofmt
└╴...
```

If the archive does not have a similar structure and instead has multiple folders and/or files at the root of the archive, you need to create the directory to extract to manually with `sudo mkdir /usr/local/mypackage`.


#### 3. Extract the binary to the desired location

Now that that we know where to extract to, it's time to actually extract the thing. The most popular file formats for compressed archives are `.tar.gz` and `.zip`, I will only consider these.

**Notes**
- Make sure the target folder exists, and you're not extracting into an existing installation.
- If you're installing to `/usr/local/` or `/usr/local/bin/` you will need to use `sudo` to run the commands.

For `tar.gz` files, use
```
tar -C <target folder> -xzf <archive>
```

For `.zip` files use
```
unzip <archive> -d <target folder>
```


#### 3. Add the directory containing the binary to your `PATH` environment variable

While the binaries are now installed to your system you will probably want the containing folder added to your `PATH` environment variable so that you can invoke the binary by name from the terminal. If you installed a bare binary to `/usr/local/bin`, chances are this folder is already in your `PATH`. You can test if can already invoke the binary by name, and if so, you can skip this step.

For `bash`, you want to add a line like this to `/home/<user>/.profile` (when you're installing for a specific user), or to `/etc/profile` (when you're installing for all users):
```
export PATH=$PATH:<folder containing the binary>
```

Since these files are only source at startup, you will need to start a new terminal or run `source <path to profile>` in the current terminal before your `PATH` environment variable will be updated.

For `fish`, you can do
```
fish_add_path <target_folder>
```

That's all!
