#!/bin/sh
# Configure git to use the project's tracked hooks directory.
# Run once after cloning: sh scripts/setup_hooks.sh
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo "Git hooks configured. Pre-commit duplicate-title check is now active."
