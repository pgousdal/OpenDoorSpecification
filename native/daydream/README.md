# Native DayDream adapter

This directory contains the portable C implementation of the ODS Core 0.1
DayDream adapter.

The adapter itself does not include historical SDK headers. Instead, one small
SDK-specific translation unit must populate `ods_dd_bindings`. This isolates
compiler-, SDK-, and library-specific calling conventions from door code and
prevents the specification project from inventing undocumented prototypes.

Host verification:

```sh
make -C native/daydream test
```

Cross compilation:

```sh
make -C native/daydream \
  CC=m68k-amigaos-gcc \
  AR=m68k-amigaos-ar \
  CFLAGS='-std=c90 -Wall -Wextra -O2'
```

This builds `native/daydream/build/libods_daydream.a`. A native door links that
library together with its DreamDoor binding translation unit and the historical
SDK import library or pragmas required by the selected compiler.

`examples/minimal/main.c` demonstrates ODS-facing door code. It intentionally
leaves `make_daydream_bindings()` and `daydream_launch_node()` undefined until a
verified SDK/compiler binding is supplied.
