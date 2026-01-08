# What This System Will Never Do

## Core Guarantees (Locked)

This system encodes refusal as a first-class behavior.  
These invariants cannot change without breaking the contract.

---

## 1. Never Act On Incomplete Truth

observe → {missing, unknown, running, stopped}
plan → refuse "unknown" state
safety → refuse partial observations

- `missing` ≠ `stopped` (existence truth)
- `unknown` → empty plan (refusal to guess)
- Partial API response → `unknown` status

---

## 2. Never Stop Production Workloads

```python
if step.name.startswith("prod-") and step.action == "stop":
    raise PolicyViolation("never stop prod VM")

3. Never Mutate During Observation
textobserve() → read-only, no retries, no discovery
audit/plan modes → zero side effects
apply mode → explicit confirmation required
Adapters swap at observe(). Core logic is invariant.

4. Never Couple Intent To Implementation
textreplay.json ≡ live observation
VMState contract is the seam:
text┌─────────────┐
│ Proxmox │ JSON │ DFIR │ Tests │ Cloud
└──┬──────────┘ └─────┼──────┼──────┼──────┘
   │                  │
   └────── observe() ──────┐
                           │
                    ┌──────▼──────┐
                    │ plan() safety() │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ audit │ apply │
                    └──────────────┘

5. Never Leak Coupling Into The Spine
× No Proxmox types in plan()/safety()
× No retry logic in observe()
× No discovery (desired-list only)
× No defaults (explicit failure)
× No side effects in audit/plan modes

6. Never Violate Time Travel
textreplay.json ≡ live observation
deterministic plan() given VMState input
audit_mode(states) produces identical output

7. Never Hide Decisions
All artifacts are structured JSON:

current.json - raw observation
plan.json - diff logic
result.json - apply outcomes

No log parsing required.

Pipeline Guarantees
textdesired.yaml → observe → VMState → plan → PlanStep → safety → [audit|apply]
                     ↓                ↓                   ↓
                  missing           refuse unknown     prod- protection
                  unknown               skip           zero side effects
Every step is pure, total, and predictable.

Proof Strategy
Negative testing proves what it CANNOT do:
Pythontest_cannot_stop_prod()        # → PolicyViolation
test_cannot_act_on_unknown()   # → empty plan
test_cannot_discover_vms()     # → desired-list only
test_replay_equivalence()      # → identical plan()


