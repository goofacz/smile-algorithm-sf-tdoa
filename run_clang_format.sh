#!/bin/sh
clang-format -i -style=file `find . -name *.cpp` `find . -name *.h`
