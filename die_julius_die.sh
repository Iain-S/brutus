#!/usr/bin/env bash
ps | grep 'julius' | head -n 1 | awk '{print $1}' | xargs kill -9
