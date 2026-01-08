# Architecture

Dedalus Converger is built around a single immutable reconciliation spine.

Adapters may differ.  
The spine will never change.

## The Reconciliation Spine

desired.yaml → observe → plan → safety → [audit|apply]

Every operation flows through this locked sequence:

1. **observe()** - Read-only observation
   - Adapters swap here (Proxmox, replay, cloud)
   - Returns `List[VMState]`
   - Never mutates, never retries, never discovers

2. **plan()** - Deterministic planning
   - Pure function: same inputs → same outputs
   - Refuses `unknown` status (no guessing)
   - Only acts on explicit desired list
   - Returns `List[PlanStep]`

3. **safety()** - Policy enforcement
   - Enforces explicit invariants
   - Production write-protection (`prod-*` prefix)
   - Raises `PolicyViolation` on refusal
   - Returns `List[PlanStep]`

4. **[audit|apply]** - Execution modes
   - **audit**: Zero side effects, shows plan
   - **plan**: Same as audit, writes `plan.json`
   - **apply**: Only mutating phase, requires confirmation

---

## EntityState Contract

All adapters must emit `VMState`:

```python
@dataclass(frozen=True)
class VMState:
    vmid: int
    name: str
    status: Literal["running", "stopped", "unknown"]
    cpus: Optional[int] = None
    maxmem: Optional[int] = None
    source: str = "live"
```

### Status Semantics

- `running` - VM is executing
- `stopped` - VM exists but is not running
- `unknown` - Partial/failed observation (plan refuses)

**Critical**: `missing` (not in observation) ≠ `stopped`

---

## Adapter Seam

Adapters swap **only** at `observe()`. Core logic never sees adapter types

┌───────────────────────────────┐
│ Proxmox │ JSON │ DFIR │ Cloud │
└────┬─────────┬───────┬────────┘
     │         │       │
     └─── observe() ───┘
              │
       ┌──────▼──────┐
       │   VMState   │  (contract boundary)
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │    plan()   │  (adapter-agnostic)
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │   safety()  │  (adapter-agnostic)
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │audit│ apply │
       └─────────────┘

---

## Refusal Semantics

The system refuses to act when:

1. **Incomplete truth**: `unknown` status → empty plan
2. **Out of scope**: VM not in desired list → skip
3. **Policy violation**: `prod-*` stop → `PolicyViolation`

Refusal is encoded, not aspirational.

---

## Time Travel Testing

Replay adapter enables deterministic testing:

```python
# Live observation
states = observe_proxmox(...)

# Replay observation (identical plan)
states = observe_replay("replay.json")

# Same plan() output guaranteed
plan(states, desired) == plan(states, desired)
```

---

## File Structure

converger/         # Immutable spine
├── model.py       # EntityState contract
├── observe.py     # Read-only observation
├── plan.py        # Deterministic planning
├── safety.py      # Policy enforcement
├── apply.py       # Execution phase
└── contract.py    # DESIGN.md hash verification

adapters/          # Swappable sources
├── replay.py      # JSON time-travel
└── proxmox.py     # Live Proxmox API

cli.py             # User-facing commands
tests/             # Negative testing

---

## Artifacts

All decisions emit structured JSON:

- `current.json` - Raw observation snapshot
- `plan.json` - Diff logic and actions
- `result.json` - Apply outcomes

No log parsing required.

---

## Extension Points

To add a new adapter:

1. Implement `observe_*() -> List[VMState]`
2. Map adapter states to `{running, stopped, unknown}`
3. Never leak adapter types into `plan()` or `safety()`

The spine remains unchanged.
