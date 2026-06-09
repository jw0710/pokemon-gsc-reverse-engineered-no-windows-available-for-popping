# DIAGNOSIS_LOG.md — Chronological Repair & Fault Isolation Log

> **Cartridge:** Pokémon Gold — DMGKGDU10-0  
> **Technician:** Jannik Weyrich / NostaMods  
> **Status:** Fault isolated — ROM defect confirmed, cartridge irreparable

---

## Entry 001 — Initial Inspection & Symptom Capture

**Condition received:** Cartridge non-functional. Owner reports game has not booted for an extended period.

**Initial boot test on verified GBC unit:**
- Nintendo logo animation: ✅ Completes (BIOS ROM logo check passes)
- Expected behavior: Game Freak splash → Title screen
- Actual behavior: Black screen with text output:

```
No windows available for popping
```

- System halts. No further execution. Hard reset required.

**Initial hypothesis:** MBC3 fault, cold solder joint, or SRAM initialization failure.

---

## Entry 002 — Visual Inspection

- PCB inspected under magnification (10×)
- All SMD pads: ✅ No visible cold joints, lifted pads, or oxidation
- PCB traces: ✅ No visible cracking, delamination, or corrosion
- Edge connector: Cleaned with IPA + fiberglass eraser, re-tested — error unchanged
- Battery: Not installed (owner-removed prior to handover)

---

## Entry 003 — Electrical Verification

- Supply voltage at VCC rail: **3.3 V** ✅ (nominal for GBC)
- MBC3 VCC/GND pins: Verified with multimeter — within spec
- SRAM VCC/GND: Verified — within spec
- ROM VCC/GND: Verified — within spec
- All passive component values verified against reference schematic:
  - Decoupling capacitors: ✅ In-spec
  - Pull-up/pull-down resistors: ✅ In-spec
- Data bus continuity (ROM → MBC3 → CPU edge connector): ✅ No open circuits detected

**No electrical fault found at this stage.**

---

## Entry 004 — MBC3 Replacement

**Action:** Removed original MBC3 via hot air. Installed known-good MBC3 pulled from donor stock. Reflowed all pads.

**Result:** Boot test — **Error unchanged.**

`No windows available for popping`

MBC3 ruled out as defect source.

---

## Entry 005 — SRAM Replacement

**Action:** Removed original SRAM. Installed replacement SRAM of matching specification.

**Result:** Boot test — **Error unchanged.**

SRAM ruled out as defect source.

---

## Entry 006 — Full SMD Passive Replacement

**Action:** All SMD components replaced (capacitors, resistors) from verified reel stock. Board re-cleaned with IPA flux remover post-reflow.

**Result:** Boot test — **Error unchanged.**

Passive components ruled out as defect source.

---

## Entry 007 — Full PCB Swap (Donor Board)

**Action:** Sourced donor DMGKGDU10-0 PCB from parts inventory. Transferred ROM chip from defective board to verified donor PCB. All other donor components (MBC3, SRAM, passives) are known-good.

**Rationale:** This test establishes whether the fault is PCB-layer (traces, vias, substrate) or component-level (ROM die).

**Result:** Boot test — **Error unchanged. Error migrates with ROM chip.**

This is the critical finding. The ROM chip is confirmed as the only variable that produced fault migration across two independent PCB assemblies.

**PCB substrate and all other components ruled out. ROM identified as sole remaining fault candidate.**

---

## Entry 008 — First ROM Dump Session

**Action:** ROM dumped ×4 using GB cartridge flasher. No changes to hardware between dumps.

| Dump | Checksum | Valid |
|---|---|---|
| 1 | `0xF004` | ❌ |
| 2 | `0xF004` | ❌ |
| 3 | `0xDC97` | ✅ |
| 4 | `0xDC97` | ✅ |

**Observation:** 50% invalid dump rate under identical conditions. This is not consistent with a contact fault (which would produce consistently invalid results) but is consistent with **intermittent floating-bit behavior** — one or more ROM cells resolving to different logic levels on successive read operations.

---

## Entry 009 — Post-Valid-Dump Cartridge Re-Test

Following dumps 3 and 4 (valid checksum), cartridge re-inserted into GBC for functional test.

**Observed sequence:**

1. Title screen displayed **save file menu** despite no battery or SRAM state — false-positive save detection
2. Selected "New Game" — Professor Elm introduction initiated
3. **Game progressed autonomously** without user input — A-button polling loop stuck in pressed state
4. Professor Elm sprite rendered as **solid black rectangle** — null tile pointer
5. **All display colors inverted** mid-sequence
6. **Background music slowed and dropped in pitch**
7. System crashed to title screen
8. All anomalies cleared on soft reset

These symptoms are consistent with CPU execution of bit-corrupted ROM data in the executable code region. See [README.md — Secondary Symptoms](README.md#secondary-symptoms--behavioral-anomalies) for technical explanation of each anomaly.

---

## Entry 010 — Final Assessment

All diagnostic pathways exhausted:

| Variable | Tested | Status |
|---|---|---|
| Edge connector contact | Cleaned, re-tested | ✅ Ruled out |
| PCB traces & substrate | Electrical + optical | ✅ Ruled out |
| Passive components | 100% replaced | ✅ Ruled out |
| MBC3 | Replaced | ✅ Ruled out |
| SRAM | Replaced | ✅ Ruled out |
| Full PCB | Swapped (ROM transferred) | ✅ Ruled out |
| **ROM chip** | Cannot replace (Mask-ROM) | ❌ **Defect confirmed** |

**Diagnosis:** Partial Mask-ROM die degradation with floating-bit behavior. Irreparable under standard workshop conditions.

See [`FINDINGS.md`](FINDINGS.md) for consolidated conclusions and repairability statement.
