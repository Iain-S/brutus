#!/bin/bash

cd debug && find . -name '*.gcda' -exec rm '{}' \; && make && make test && cd .. && ./coverage.sh 
