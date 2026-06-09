# FINDINGS.md — Consolidated Conclusions & Repairability Statement

> **Cartridge:** Pokémon Gold — DMGKGDU10-0  
> **Analysis by:** Jannik Weyrich / NostaMods  
> **Date of Analysis:** June 2025

---

## 1. Summary of Findings

This document consolidates the results of a systematic hardware fault analysis on a defective Pokémon Gold cartridge (PCB revision DMGKGDU10-0) exhibiting the error **"No windows available for popping"** on boot.

Following exhaustive component substitution, electrical verification, PCB-level swap testing, and four independent ROM dumps, the fault has been unambiguously isolated to the **Mask-ROM die**.

### Key Evidence

| Evidence | Implication |
|---|---|
| Error persists after MBC3 replacement | MBC3 is not the fault source |
| Error persists after SRAM replacement | SRAM is not the fault source |
| Error persists after full SMD passive replacement | Passive components are not the fault source |
| Error persists after full PCB swap (ROM transferred) | PCB substrate and traces are not the fault source |
| **Error migrates with ROM chip across two PCBs** | **ROM is confirmed defect source** |
| 50% invalid ROM dump rate (consistent `0xF004` checksum) | Floating-bit behavior in one or more ROM cells |
| Header checksum valid across all dumps | Fault is in ROM data region, not header block |
| Runtime anomalies observed after valid dump | Corrupted bits fall within executable code region |

---

## 2. Failure Classification — Revised After Dump Analysis

**Failure Mode:** Stuck address line — ROM address input A0–A7 permanently low

**Failure Class:** Digital logic fault — address bus fault (not floating-bit / not random bit-rot)

**Severity:** Critical — boot-blocking, execution-corrupting

**Reversibility:** None under standard workshop conditions — requires ROM chip replacement

### Technical Description — What The Dump Analysis Revealed

Initial hypothesis was a floating-bit Mask-ROM cell. Byte-level diff analysis of the four ROM dumps **disproves this** and points to a more specific and structurally distinct fault.

Key findings from `rom_diff_analysis.py`:

| Metric | Value | Significance |
|---|---|---|
| Total differing bytes | 1,313 | Widespread — not an isolated cell |
| Addresses aligned to 0x100 | 1,313/1,313 (100%) | **All diffs at exact 256-byte boundaries** |
| Low byte of all differing addresses | `0x00` (100%) | A0–A7 are always `0` in faulty dump |
| Dominant stride between diffs | `0x100` or `0x200` | Perfectly regular, non-random pattern |
| Bit flip distribution (data lines) | Uniform across all 8 bits | No individual data line stuck |

**The pattern is unmistakably structural, not random.** A genuinely degraded Mask-ROM with floating cells produces irregular diffs scattered across arbitrary addresses. This dump produces diffs *exclusively* at addresses ending in `0x??00`, with a machine-regular stride — the signature of a **stuck address line**.

### Stuck Address Line Mechanism

The ROM chip has 21 address inputs (A0–A20) for a 2 MiB address space. If address lines A0–A7 are permanently held low (stuck at 0), the chip cannot distinguish between consecutive byte addresses within any 256-byte window. Every access to address `0x????XY` resolves to `0x????00` regardless of the value of `XY`.

During a ROM dump, the flasher increments the address counter normally — but the chip ignores the lower 8 bits and delivers the same byte for every 256 consecutive read addresses. This produces the observed pattern: every 0x100th byte is real ROM data, the intervening 255 bytes are either stale buffer data or aliased reads.

During gameplay, the Z80 CPU fetches instructions sequentially. With A0–A7 stuck low, every instruction fetch within a 256-byte window reads from offset `0x??00`. The CPU executes an incoherent instruction stream. The first malformed bank-switch call passes an invalid MBC3 window index to the GBC memory manager, which finds no matching stack frame → **`No windows available for popping`**.

### Differentiating ROM Fault vs. Dump Adapter Fault

The same 0x100-stride pattern would appear if the fault were in the **dump hardware** rather than the ROM chip. The following evidence points toward the ROM chip as the fault source:

1. The error occurs on boot from the Game Boy itself — not only during dumping
2. Two of four dumps yielded a valid checksum, suggesting the chip *can* deliver correct data under some conditions (temperature, contact pressure) — consistent with an intermittent stuck line rather than a fully open address trace on the adapter
3. The fault migrated with the ROM chip across two independent PCBs (see `DIAGNOSIS_LOG.md`, Entry 007)

**Most probable fault location:** One or more address input pins on the ROM die — either a failed internal pull-down, a cracked bond wire, or oxide breakdown on the address decoder input transistor for A0–A7.

---

## 3. Error Message — Known Documentation Status

The error string `"No windows available for popping"` is exceptionally rare in public repair documentation. A literature review conducted as part of this analysis identified the following references:

| Source | Year | Depth |
|---|---|---|
| Glitch City Laboratories forum thread | 2010 | Superficial — no resolution documented |
| Reddit (r/Gameboy, r/GameboyRepair) | Various | Anecdotal — no systematic analysis |
| Game Boy forum communities | Various | Isolated mentions — no root cause identified |

**No prior technical analysis linking this error to Mask-ROM floating-bit degradation was found in publicly available sources.** This repository is believed to be the first systematic hardware-level documentation of this failure mode in the context of DMG-KGDU10 cartridges.

---

## 4. Repairability Assessment

### Option A — Standard Component Replacement

**Status: Not applicable.**

All standard-replaceable components (MBC3, SRAM, passives, PCB) have been verified or substituted. None address the fault.

### Option B — ROM Chip Donor Transplant

**Status: Theoretically possible. Practically destructive and economically unviable.**

A like-for-like Mask-ROM donor from an identical, fully functional Pokémon Gold (EUR, DMGKGDU10-0) cartridge would need to be sourced. The transplant would require:

- Hot-air removal of the donor ROM (risk of die cracking)
- Precision re-balling or re-tinning of the donor chip (non-standard footprint)
- Reflow onto the defective board
- Full re-verification by ROM dump

This approach destroys a functional cartridge to potentially repair a defective one — which is not recommended unless the target cartridge holds exceptional sentimental or collector value and the donor is sourced specifically for this purpose.

### Option C — Flash Replacement Module

**Status: Niche. No commercial off-the-shelf solution confirmed for this footprint.**

Custom adapter PCBs replacing Mask-ROM with compatible Flash memory exist for some Game Boy cartridge types within the modding community. No verified solution for the DMGKGDU10-0 ROM footprint was identified at the time of this analysis. A custom adapter would require:

- Reverse engineering of the ROM pinout and timing requirements
- Design of a custom interposer PCB
- A compatible Flash chip with matching bus width and access timing

This is technically feasible but outside the scope of standard repair practice.

### Option D — Documentation & Return

**Status: Recommended.**

Given the above, the cartridge is considered **beyond economical repair** under standard workshop conditions. The recommended course of action is:

1. Return the cartridge to the owner with this technical documentation
2. Advise that the fault is a natural wear-out failure of a 25-year-old semiconductor component
3. Note that the fault is not attributable to misuse, improper storage, or prior repair attempts

---

## 5. Final Verdict

> **The Pokémon Gold cartridge (DMGKGDU10-0) under analysis has suffered a partial Mask-ROM die failure resulting in irreversible floating-bit behavior. The defect cannot be corrected through component replacement, reflowing, or any standard repair technique. The cartridge is irreparable.**

---

## 6. Recommendations for Future Cases

If a technician encounters `"No windows available for popping"` on a GBC cartridge:

1. **Verify the error is reproducible** across multiple GBC units — rule out console-side fault
2. **Clean edge connector** and re-test before proceeding
3. **Replace MBC3** from verified donor stock — this is the most common cause of MBC-related boot failures on KGDU boards
4. **Perform ≥4 ROM dumps** — if checksum results are inconsistent across dumps, suspect ROM die degradation
5. **Perform a full PCB swap** (transferring only the ROM) — if the error migrates, ROM is confirmed defective
6. **Document and return** if ROM is confirmed — no further repair action is warranted

---

*Analysis conducted by Jannik Weyrich / NostaMods*  
*github.com/jw0710*  
*Published under CC BY-NC-SA 4.0*
