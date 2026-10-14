#!/usr/bin/env bash
# Build the tinyshop fixture repo used by the skill evals.
# Usage: evals/make_fixture.sh <target-dir>
set -euo pipefail
F="$1"
rm -rf "$F"; mkdir -p "$F"/src/tinyshop "$F"/tests "$F"/docs/adr "$F"/docs/backlog
cd "$F"
cat > pyproject.toml <<'EOF'
[project]
name = "tinyshop"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = ["pytest>=8"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
EOF
cat > README.md <<'EOF'
# tinyshop

Tiny order and pricing library.

Run tests: `uv run pytest`
EOF
cat > CLAUDE.md <<'EOF'
# Instructions
- Work test-first.
- Money is handled in integer cents, never floats (see docs/adr/0001-money-in-cents.md).
EOF
cat > docs/adr/0001-money-in-cents.md <<'EOF'
# 0001 Money in integer cents
Status: accepted
All amounts are int cents to avoid float rounding errors. Public functions take and return cents.
EOF
cat > docs/backlog/csv-export.md <<'EOF'
---
status: open
priority: medium
acceptance: orders can be exported to CSV with columns id,total_cents,created_at
---
# CSV export of orders
EOF
: > src/tinyshop/__init__.py
cat > src/tinyshop/pricing.py <<'EOF'
def apply_discount(total_cents: int, percent: int) -> int:
    """Return the total after a percentage discount."""
    return total_cents - total_cents * percent // 100
EOF
cat > src/tinyshop/orders.py <<'EOF'
from dataclasses import dataclass, field
from datetime import datetime

from tinyshop.pricing import apply_discount


@dataclass
class Order:
    id: int
    items_cents: list[int]
    discount_percent: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def total_cents(self) -> int:
        return apply_discount(sum(self.items_cents), self.discount_percent)
EOF
cat > tests/test_pricing.py <<'EOF'
from tinyshop.pricing import apply_discount


def test_ten_percent():
    assert apply_discount(1000, 10) == 900


def test_no_discount():
    assert apply_discount(1000, 0) == 1000
EOF
printf '.venv/\n__pycache__/\n' > .gitignore
git init -q -b main
# Commit a lock file so `uv run` during evals doesn't leave an untracked one.
uv lock -q
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm "Initial tinyshop"
