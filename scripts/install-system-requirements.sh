#!/usr/bin/env bash

if hash apt 2>/dev/null; then
  sudo apt install -y make
  return
fi

if hash dnf 2>/dev/null; then
  sudo dnf install -y make
  return
fi

if hash yum 2/dev/null; then
  sudo yum install -y make
  return
fi

if hash brew 2>/dev/null; then
  brew install make
  return
fi
