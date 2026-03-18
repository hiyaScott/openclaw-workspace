#!/bin/bash
# ASCII Art Generator - 简单封装figlet

TEXT="${1:-HELLO}"
FONT="${2:-slant}"

echo "$TEXT" | figlet -f "$FONT"