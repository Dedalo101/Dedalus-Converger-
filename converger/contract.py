import hashlib
from pathlib import Path

# SHA256 of docs/DESIGN.md as of 2026-01-08 (locked contract)
DESIGN_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # placeholder — we will compute real one

def verify_contract() -> None:
    """Verify that DESIGN.md has not changed without version bump."""
    design_path = Path(__file__).parent.parent / "docs" / "DESIGN.md"
    if not design_path.exists():
        raise RuntimeError("docs/DESIGN.md missing — contract cannot be verified")

    actual_hash = hashlib.sha256(design_path.read_bytes()).hexdigest()
    if actual_hash != DESIGN_HASH:
        raise RuntimeError(
            "DESIGN.md has changed without updating DESIGN_HASH.\n"
            "This violates the locked contract. Requires major version bump and unanimous review."
        )
