---
title: Revamped blog
description: I revamped my blog.
date: 2024-10-12
template: post
show: true
---

My blog has been in a bit of a rut lately. Well, for the last two-and-a-half years, that is. I wrote a bunch of things, but never really *finished* things to such an extent that I feel comfortable uploading them.

What I have done, however, is revamp my blog. Besides a few cosmetic issues that are yet to be solved (some missing fonts, mostly), this should not affect the site or the content on it too much. However, on the backend there have been quite a few changes:
  - I wrote a simple static site generator in Go that now powers my blog.
  - I also wrote a simple utility that compiles a standalone server. That is, I can copy the bare binary between systems (assuming they have the right OS and architecture).
  - I now self-host my site, instead of having it hosted on github pages it is now hosted on a single-board computer I have at home.
  - I have *finally* set up proper CI/CD for my site.

The content of my posts now exists of a bunch of markdown files with a YAML front matter that contains some metadata. This should at least make it a bit easier to update my site. This post serves as a bit of a test, or maybe a benchmark.

Update: I pressed that start timere on my stopwatch and enter on my keyboard at the same time, and it takes about a minute to deploy. The server service (in the sense of systemd service) is restarted, but I didn't notice any downtime. Not bad!
