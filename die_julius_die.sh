#!/usr/bin/env bash
ps | grep 'julius' | awk '{print $1}' | xargs kill -9
