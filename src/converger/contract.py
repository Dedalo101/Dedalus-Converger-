import hashlib
import sys
from pathlib import Path

# THIS HASH LOCKS DESIGN.md - change requires major version + unanimous review
EXPECTED_DESIGN_HASH = "7021488b8418c146bd1d82c289ed403ba07acabb2eadf0fa10989d2e1b66f956"  # ← current valid hash

DESIGN_PATH = Path(__file__).parent.parent.parent.parent / "DESIGN.md"


def compute_file_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_contract():
    if not DESIGN_PATH.exists():
        print(f"ERROR: DESIGN.md missing at {DESIGN_PATH}", file=sys.stderr)
        sys.exit(1)

    current_hash = compute_file_sha256(DESIGN_PATH)

    if current_hash != EXPECTED_DESIGN_HASH:
        print("╔════════════════════════════════════════════════════════════╗", file=sys.stderr)
        print("║               CONTRACT INTEGRITY VIOLATION                 ║", file=sys.stderr)
        print("║                                                            ║", file=sys.stderr)
        print(f"║  DESIGN.md changed unexpectedly!                           ║", file=sys.stderr)
        print(f"║  Expected hash: {EXPECTED_DESIGN_HASH} ║", file=sys.stderr)
        print(f"║  Current hash:  {current_hash} ║", file=sys.stderr)
        print("║                                                            ║", file=sys.stderr)
        print("║  The spine is LOCKED. Any change requires:                 ║", file=sys.stderr)
        print("║  • Major version bump                                      ║", file=sys.stderr)
        print("║  • Unanimous review                                        ║", file=sys.stderr)
        print("║  • Updated hash in contract.py                             ║", file=sys.stderr)
        print("╚════════════════════════════════════════════════════════════╝", file=sys.stderr)
        sys.exit(1)

    print("Contract integrity: OK (DESIGN.md unchanged)")


if __name__ == "__main__":
    verify_contract()
    from pathlib import Path
import os
import sys

# Find the repository root (works in editable install, direct run, CI)
def find_repo_root():
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists():
            return parent
    # Fallback: assume 3-4 levels up from src/converger/contract.py
    return current.parent.parent.parent.parent

REPO_ROOT = find_repo_root()
DESIGN_PATH = REPO_ROOT / "DESIGN.md"