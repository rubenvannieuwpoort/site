---
title: The Fowler–Noll–Vo hash
description: A fast, simple, and effective hash function.
date: 2022-03-11
template: post
show: true
---

The Fowler–Noll–Vo hash function is a simple but effective hash function. If you ever need to implement one from scratch, it is an excellent choice.

Note that this is not a cryptographic hash. It is intended to be used in hash tables and checksums.

The algorithm (or more precisely, the FNV-1a variant of the algorithm) is as follows:
```
#define FNV_OFFSET_BASIS 14695981039346656037
#define FNV_PRIME 1099511628211

uint64_t fnv_hash(uint8_t *data, size_t length) {
	uint64_t hash = FNV_OFFSET_BASIS;

	for (size_t i = 0; i < length; i++) {
		hash = hash ^ data[i];
		hash *= FNV_PRIME;
	}

	return hash;
}
```

This is the 64-bit variant. For other bit sizes, the size of the `hash` variable needs to be adapted and different constants need to be used for `FNV_PRIME` and `FNV_OFFSET_BASIS`:

| Bits         | FNV prime                                                                                                                                                                                                           | FNV offset basis                                                                                                                                                                                                                                                                                              |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 32           | 16777619                                                                                                                                                                                                            | 2166136261                                                                                                                                                                                                                                                                                             |
| 64           | 1099511628211                                                                                                                                                                                                       | 14695981039346656037                                                                                                                                                                                                                                                                                   |
| 128          | 309485009821345068724781371                                                                                                                                                                                         | 144066263297769815596495629667062367629                                                                                                                                                                                                                                                                |
| 256          | 374144419156711147060143317 175368453031918731002211                                                                                                                                                                | 100029257958052580907070968620625704837 092796014241193945225284501741471925557                                                                                                                                                                                                                        |
| 512          | 358359158748448673689190764 890951084499463279557543925 583998256154206699388825751 26094039892345713852759                                                                                                         | 965930312949666949800943540071631046609 041874567263789610837432943446265799458 293219771643844981305189220653980578449 5328239340083876191928701583869517785                                                                                                                                          |
| 1024         | 501645651011311865543459881103 527895503076534540479074430301 752383111205510814745150915769 222029538271616265187852689524 938529229181652437508374669137 180409427187316048473796672026 0389217684476157468082573 | 14197795064947621068722070641403218320 88062279544193396087847491461758272325 22967323037177221508640965212023555493 65628174669108571814760471015076148029 75596980407732015769245856300321530495 71501574036444603635505054127112859663 61610267868082893823963790439336411086 884584107735010676915 |


## References

[FNV Hash](http://www.isthe.com/chongo/tech/comp/fnv) by Landon Curt Noll, one of the authors of the FNV hash function.

