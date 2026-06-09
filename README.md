<div align="center">

# DMG-KGDU10 — *"No Windows Available for Popping"*
### Forensic Hardware Failure Analysis · Pokémon Gold · Game Boy Color Cartridge

---

![Status](https://img.shields.io/badge/status-concluded-critical?style=flat-square&color=dc2626)
![ROM](https://img.shields.io/badge/ROM-POKEMON__GLD-blue?style=flat-square)
![PCB](https://img.shields.io/badge/PCB-DMGKGDU10--0-blue?style=flat-square)
![Mapper](https://img.shields.io/badge/mapper-MBC3_+_RTC-blue?style=flat-square)
![ROM Size](https://img.shields.io/badge/ROM-2_MiB-blue?style=flat-square)
![Dumps](https://img.shields.io/badge/dumps_analysed-4-yellow?style=flat-square)
![Diffs](https://img.shields.io/badge/differing_bytes-1313-orange?style=flat-square)
![Alignment](https://img.shields.io/badge/0x100_alignment-100%25-red?style=flat-square)
![License](https://img.shields.io/badge/license-CC_BY--NC--SA_4.0-green?style=flat-square)
![Author](https://img.shields.io/badge/author-NostaMods-blueviolet?style=flat-square)

</div>

---

## Abstract

This repository presents a complete forensic hardware analysis of a defective **Pokémon Gold** cartridge (PCB: **DMGKGDU10-0**, mapper: **MBC3 + RTC**) exhibiting the boot-fatal error:

```
No windows available for popping
```

Through systematic component substitution across two independent PCB assemblies, electrical verification, and structured binary analysis of four ROM dumps, the fault was isolated and characterized at the semiconductor level. The initial hypothesis of a floating-bit Mask-ROM cell degradation was **disproved by quantitative dump analysis**, which revealed a structurally distinct failure mode: a **stuck-low address bus fault on lines A0–A7** of the ROM die.

At the time of writing, **no prior technical documentation of this specific failure mode** exists in the public domain beyond a single unresolved thread on Glitch City Laboratories (2010) and isolated Reddit reports with no root-cause analysis. This repository is intended as a reproducible reference for hardware repair technicians and retro hardware researchers.

> **Verdict: The cartridge is irreparable under standard workshop conditions.**  
> The fault originates within the ROM die itself and cannot be resolved through any form of component substitution, reflowing, or PCB-level intervention.

---

## Table of Contents

1. [Hardware Under Test](#1-hardware-under-test)
2. [The Error — Origin and Mechanism](#2-the-error--origin-and-mechanism)
3. [Methodology](#3-methodology)
4. [Component Substitution Matrix](#4-component-substitution-matrix)
5. [ROM Dump Analysis](#5-rom-dump-analysis)
6. [Binary Diff — Key Findings](#6-binary-diff--key-findings)
7. [Root Cause: Stuck Address Lines A0–A7](#7-root-cause-stuck-address-lines-a0a7)
8. [Secondary Boot Symptoms Explained](#8-secondary-boot-symptoms-explained)
9. [Repairability Assessment](#9-repairability-assessment)
10. [Comparison with Prior Art](#10-comparison-with-prior-art)
11. [Repository Structure](#11-repository-structure)
12. [References](#12-references)

---

## 1. Hardware Under Test

| Parameter | Value |
|---|---|
| **Game Title** | Pokémon Gold Version |
| **Internal ROM Title** | `POKEMON_GLD` |
| **PCB Revision** | DMGKGDU10-0 |
| **Memory Bank Controller** | MBC3 (with Real-Time Clock) |
| **ROM Size** | 2 MiB (128 × 16 KiB banks) |
| **SRAM** | 32 KiB |
| **CGB Flag** | `0x80` (GBC compatible, DMG supported) |
| **SGB Flag** | `0x03` (SGB enhanced) |
| **Region / Destination** | EUR (`0x01`) |
| **ROM Version Byte** | `0x00` |
| **Licensee** | Nintendo (`0x3031`) |
| **Header Checksum** | `0x4C` ok |
| **Expected Global Checksum** | `0xDC97` |
| **Measured Global Checksum** | `0xDC97` ok / `0xF004` no (intermittent) |

---

## 2. The Error — Origin and Mechanism

### 2.1 Error String Source

The string `"No windows available for popping"` is **not embedded in the Pokémon Gold game binary**. It is emitted by the **Game Boy Color system firmware** when the memory management layer encounters an inconsistency in its ROM window stack.

The GBC firmware maintains a stack of active MBC3 "windows" — internal records of bank-switch operations performed by the MBC3 controller. When the CPU issues a bank-pop instruction and the stack contains no matching entry, the firmware raises this error and halts execution.

### 2.2 Why This Error Appears

The error is triggered by the following sequence:

```
ROM delivers corrupted/aliased instruction data
         ↓
Z80 CPU executes incoherent instruction stream
         ↓
MBC3 receives malformed bank-switch parameters
         ↓
GBC firmware attempts to pop a non-existent window from empty stack
         ↓
"No windows available for popping"  →  HALT
```

The root cause is not a software bug in the game. It is the hardware delivering **physically corrupted data** to the CPU on every boot.

<div align="center">

![No windows available for popping — captured on boot](docs/NoWindowsAv.png)

*Fig. 1 — The error as it appears on boot. No further execution occurs until hard reset.*

</div>

### 2.3 Why It Is Rarely Documented

The error is cartridge-specific and hardware-generated, not a software state that can be triggered by gameplay. It requires a specific class of ROM fault to manifest — one that corrupts the early boot execution path without triggering the BIOS logo check failure (which would display a different error). This narrow fault window explains why the symptom is virtually absent from repair literature.

---

## 3. Methodology

All diagnostics followed a **single-variable substitution protocol**: one component replaced per session, all others held constant, boot-tested after each change. This ensures each result is attributable to the substituted component alone.

```
Session 1 — Baseline boot test + visual/electrical inspection
Session 2 — MBC3 replacement
Session 3 — SRAM replacement
Session 4 — Full SMD passive replacement
Session 5 — Full PCB swap (ROM chip transferred to donor board)
Session 6 — ROM dump analysis (4 dumps)
Session 7 — Binary diff analysis (invalid vs. reference dump)
```

### Equipment Used

| Tool | Purpose |
|---|---|
| Hot air rework station | Component removal / installation |
| Multimeter | Voltage, continuity, resistance verification |
| GB cartridge flasher | ROM dumping (×4 sessions) |
| Verified GBC reference unit | Boot testing |
| Donor DMGKGDU10-0 board | PCB-swap substitution test |
| Python 3.x + custom script | Binary diff and fault characterization |

---

## 4. Component Substitution Matrix

| Component | Action Taken | Result | Fault Ruled Out |
|---|---|---|---|
| Edge connector | Cleaned (IPA + glass fibre) | Error persists | ok |
| PCB traces | Optical + electrical verification | No faults found | ok |
| SMD capacitors | 100% replaced from verified stock | Error persists | ok |
| SMD resistors | 100% replaced from verified stock | Error persists | ok |
| MBC3 | Replaced from donor stock | Error persists | ok |
| SRAM | Replaced | Error persists | ok |
| Full PCB | Donor board substitution — ROM transferred | **Error migrates with ROM** | ok -- PCB ruled out |
| **ROM chip** | Cannot replace (Mask-ROM) | **Confirmed defect origin** | FAULT SOURCE |

The PCB-swap test (Session 5) is the definitive isolation step. With every component replaced or verified except the ROM chip, and the error following the ROM across two independent PCB assemblies, the ROM is confirmed as the sole fault source.

---

## 5. ROM Dump Analysis

Four dumps were performed under identical conditions with no hardware changes between sessions.

### 5.1 Header Fields (both dumps)

All header fields are **identical** between the invalid and reference dumps — including Nintendo Logo, title string, mapper type, ROM/RAM size, region, version byte, and header checksum. The two dumps are confirmed to be the same ROM version and revision.

| Field | Invalid Dump | Valid Reference | Match |
|---|---|---|---|
| Title | `POKEMON_GLD` | `POKEMON_GLD` | ok |
| CGB Flag | `0x80` | `0x80` | ok |
| Cart Type | `0x10` (MBC3+RAM+TIMER) | `0x10` | ok |
| ROM Size | `0x06` (2 MiB) | `0x06` | ok |
| Version | `0x00` | `0x00` | ok |
| Header Checksum | `0x4C` | `0x4C` | ok |
| **Global Checksum** | **`0xDC97`** (2/4 dumps) | **`0xDC97`** | intermittent (see notes) |
| **Entry Point** | **`F3 C3 C6 05`** | **`00 C3 C6 05`** | DIFFERS |

> **Note on Entry Point:** The first byte of the entry point vector differs — `0xF3` (DI — Disable Interrupts) vs. `0x00` (NOP). This is the first byte fetched by the CPU on boot and its corruption is a direct contributor to the subsequent execution fault chain.

### 5.2 Dump Checksum Results

| Dump # | Global Checksum | Valid | Notes |
|---|---|---|---|
| 1 | `0xF004` | no | Invalid |
| 2 | `0xF004` | no | Invalid — identical to Dump 1 |
| 3 | `0xDC97` | ok | Valid |
| 4 | `0xDC97` | ok | Valid — identical to Dump 3 |

50% valid / 50% invalid under zero-variable conditions. The consistent `0xF004` value (not random variance) and the subsequent binary analysis reframe this as **intermittent address resolution**, not random bit noise.

---

## 6. Binary Diff — Key Findings

Byte-level comparison of the invalid dump against the known-good reference using [`rom_diff_analysis.py`](rom_diff_analysis.py) produced the following findings:

### 6.1 Overview Statistics

| Metric | Value |
|---|---|
| Total differing bytes | **1,313** |
| ROM banks affected | **101 of 128** |
| Addresses aligned to 0x100 boundary | **1,313 / 1,313 (100.0%)** |
| Low byte of every differing address | **`0x00`** (universally) |
| Dominant stride between consecutive diffs | **`0x0200`** (661 occurrences) |
| Secondary stride | **`0x0100`** (652 occurrences) |
| Data bit flip distribution | Uniform across all 8 bits (spread: 125 flips) |

### 6.2 The Critical Observation

**Every single differing byte is located at an address that is an exact multiple of 256 (`0x100`).**

```
0x000100  ← diff
0x000300  ← diff
0x000500  ← diff
...
0x1A8000  ← diff
(never 0x000101, never 0x000202, never any odd address)
```

This is **mathematically impossible through random bit degradation**. A floating-bit failure distributes errors stochastically across the address space. A 100% alignment rate to a power-of-two boundary is the deterministic signature of a **systematic addressing fault**.

### 6.3 Bank Distribution

Diffs are distributed across 101 of 128 ROM banks, with the highest concentration in the low banks (Bank 0–10) which contain the boot code and critical game engine routines:

```
Bank 00  (0x000000–0x003FFF):  41 diffs  ████████████████████████████████████████
Bank 01  (0x004000–0x007FFF):  30 diffs  ██████████████████████████████
Bank 02  (0x008000–0x00BFFF):  31 diffs  ███████████████████████████████
Bank 03  (0x00C000–0x00FFFF):  29 diffs  █████████████████████████████
...
```

The higher bank density in Bank 0 is consistent with a more severe read failure in the fixed bank (always mapped, always read first on boot) vs. switched banks.

### 6.4 Data Line Uniformity

Bit flip frequency is uniform across all 8 data lines (D0–D7), with a spread of only 125 flips between the most and least affected line. This **rules out a stuck data line** and confirms the fault lies in the address domain, not the data domain.

---

## 7. Root Cause: Stuck Address Lines A0–A7

### 7.1 How ROM Addressing Works

A 2 MiB Mask-ROM requires 21 address inputs (A0–A20) to uniquely address every byte in its 2,097,152-byte space. These are physical pins on the chip package connected to the ROM die via bond wires. The MBC3 drives A13–A20 for bank selection; A0–A12 are driven directly by the CPU address bus.

```
Address line:  A20  A19  ...  A8   A7   A6  ...  A1   A0
Bit weight:    1M   512K ...  256  128   64  ...   2    1
```

### 7.2 The Fault Model

If address lines **A0 through A7** are permanently held at logic `0` — whether through a failed bond wire, a degraded input transistor, or an open address decoder — the chip's lower 8 address inputs are always zero. The chip cannot distinguish between any two addresses that differ only in bits 0–7:

```
Requested address:  0x00_1234  (binary: ...0001 0010 0011 0100)
Chip receives:      0x00_1200  (binary: ...0001 0010 0000 0000)
                                                     ↑↑↑↑↑↑↑↑
                                               A7–A0 always 0
```

Every 256-byte window in the ROM space maps to a single readable byte — the byte at offset `0x??00`. The remaining 255 bytes of each window are invisible to the chip and return aliased or stale data.

### 7.3 Why the Dump Shows This Pattern

A ROM flasher increments the address counter linearly from `0x000000` to `0x1FFFFF`. With A0–A7 stuck:

- Addresses `0x000000`–`0x0000FF` all read the byte at `0x000000`
- Addresses `0x000100`–`0x0001FF` all read the byte at `0x000100`
- etc.

The flasher records a different value at `0x????00` transitions (where A8+ change) and the same repeated value within each 256-byte window. When compared against a correct dump, **every difference appears at a `0x????00` address** — exactly what the analysis shows.

### 7.4 Why the Boot Fails

The Z80 CPU begins execution at the entry point vector (`0x0100`). With A0–A7 stuck low:

1. Fetch at `0x0100` → returns `0xF3` (DI) — **confirmed differs from valid `0x00`**
2. Subsequent fetches at `0x0101`, `0x0102` ... `0x01FF` → all return **the aliased byte from `0x0100`**
3. The CPU executes 255 copies of the same (incorrect) opcode
4. When the PC crosses into `0x0200`, A9 changes state — chip delivers the byte from `0x0200`
5. This process produces an incoherent instruction stream with no valid bank-switch sequence
6. MBC3 receives malformed parameters → GBC firmware stack underflow → **`"No windows available for popping"`**

### 7.5 Why Dumps Are Intermittently Valid

The intermittent nature — 2 valid, 2 invalid dumps — indicates the stuck condition is **not a complete open circuit** but a **high-impedance / intermittent fault**. Under certain conditions (contact pressure during insertion, die temperature, supply voltage marginal state), the address lines may briefly resolve correctly, producing a valid dump. Under other conditions, the lines float to ground and the fault manifests.

This same intermittency explains the partial boot sequences observed after valid dumps: the chip was in a temporarily functional state during those sessions.

### 7.6 Physical Fault Location Candidates

| Location | Mechanism | Likelihood |
|---|---|---|
| Bond wire fracture (A0–A7 common bus) | Mechanical fatigue, 25-year thermal cycling | High |
| Input transistor oxide breakdown (address decoder) | Gate oxide degradation, ESD history | Medium |
| Solder joint on ROM package pin | Cold joint, vibration fracture | Low (migrated with chip across boards) |
| Address line short to GND inside package | Internal contamination or delamination | Low |

> A solder joint fault on the PCB pad is effectively ruled out by the board-swap test — the fault migrated with the ROM chip to a fresh PCB with verified pads.

---

## 8. Secondary Boot Symptoms Explained

Following sessions where valid checksums were obtained, the cartridge was tested in-system. The resulting symptoms are fully explained by the intermittent addressing fault producing a partially coherent execution state:

<div align="center">

| | |
|:---:|:---:|
| ![Correct color title screen](docs/correct_color.png) | ![No windows error](docs/NoWindowsAv.png) |
| *Fig. 2 — Normal title screen (reference, functional state)* | *Fig. 3 — Boot failure state, consistent across resets* |
| ![Black professor sprite](docs/ProfessorSprite_Broken.png) | ![Inverted colors crash](docs/Restart_INV_Color.png) |
| *Fig. 4 — Professor Elm intro with null tile pointer (black sprite)* | *Fig. 5 — Full palette inversion mid-session before crash* |
| ![Select name crash](docs/SelectName_Crash.png) | |
| *Fig. 6 — Name selection screen crash state* | |

</div>

| Symptom | Mechanism |
|---|---|
| **Save menu without battery** | SRAM validity check reads aliased ROM reference byte → false-positive match → save menu rendered |
| **Autonomous A-button input** | Joypad polling subroutine reads aliased opcode → always-pressed loop |
| **Black professor sprite** | Tile pointer resolves to `0x0000` or out-of-range address → null tile rendered |
| **Full palette inversion** | Rogue write to GBC palette registers `BGP`/`OBP0`/`OBP1` from corrupted code path |
| **Music pitch degradation** | Timer registers `DIV`/`TIMA`/`TAC` overwritten → audio engine timing base corrupted |
| **Crash to title screen** | Stack overflow / illegal instruction → CPU reset, registers cleared |

All symptoms resolved on soft reset, confirming they are runtime state corruptions rather than hardware damage to the console or SRAM.

---

## 9. Repairability Assessment

### Option A — Standard Component Replacement
> Not applicable. All standard-replaceable components verified or substituted. None affect the fault.

### Option B — ROM Chip Donor Transplant
> Theoretically possible, but practically destructive.  
> Requires sourcing an identical functional Pokémon Gold (EUR, DMGKGDU10-0) cartridge as a donor. The ROM transplant requires hot-air removal of the donor chip, precision re-balling, and reflow onto the target board — a destructive operation on a functional cartridge. Only warranted for exceptional sentimental or collector value cases.

### Option C — Flash Replacement Module
> Niche -- no verified off-the-shelf solution for this footprint.  
> Custom adapter PCBs replacing Mask-ROM with compatible Flash exist in the modding community for some Game Boy cartridge types. No confirmed solution for the specific DMGKGDU10-0 ROM footprint was identified. Would require custom PCB design and a compatible Flash IC with matching bus timing.

### Option D — Documentation and Return
> Recommended.  
> The cartridge is beyond economical repair. The fault is a natural wear-out failure mode of a 25-year-old semiconductor component, attributable to material degradation over service life. No prior repair attempts by the owner contributed to the fault.

### Summary Verdict

```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: IRREPARABLE                                        ║
║                                                              ║
║  Fault: Stuck address lines A0–A7, ROM die                   ║
║  Cause: Internal semiconductor degradation (25-year wear)    ║
║  Fix:   ROM chip replacement only                            ║
║  Availability: No off-the-shelf solution                     ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 10. Comparison with Prior Art

### Known Public References

| Source | Year | Content | Root Cause Identified |
|---|---|---|---|
| Glitch City Laboratories forum | 2010 | Single thread, error string reported | none |
| Reddit r/Gameboy | Various | Anecdotal mentions, no analysis | none |
| Reddit r/GameboyRepair | Various | Isolated reports, unresolved | none |
| GameBoy Forum communities | Various | Rare mentions | none |
| **This repository** | **2025** | **Full forensic analysis** | **Stuck A0–A7** |

### Why This Error Is Under-Documented

The error requires a specific and uncommon fault class to manifest: the ROM must fail in a way that corrupts the execution path *after* the BIOS Nintendo logo check but *before* a stable bank mapping is established. A ROM that fails the logo check produces a different system error. A ROM with a different fault location may produce a blank screen or hang without a text error. The narrow fault window that produces `"No windows available for popping"` is rare enough that repair technicians rarely encounter it, and those who do typically lack the tooling for binary dump analysis.

---

## 11. Repository Structure

```
DMG-KGDU10-NoWindowsAvailableForPopping-Analysis/
│
├── README.md                  ← This document (full analysis)
├── DIAGNOSIS_LOG.md           ← Chronological repair sessions (Entry 001–010)
├── ROM_DUMP_ANALYSIS.md       ← Raw dump metadata and checksum results
├── FINDINGS.md                ← Consolidated verdict and repairability statement
├── rom_diff_analysis.py       ← Forensic binary diff tool (Python 3, no deps)
└── docs/
    ├── correct_color.png      ← Reference: normal title screen
    ├── NoWindowsAv.png        ← Primary failure: boot error screen
    ├── ProfessorSprite_Broken.png  ← Null tile / black sprite anomaly
    ├── Restart_INV_Color.png  ← Full palette inversion before crash
    └── SelectName_Crash.png   ← Name selection crash state
```

### Using `rom_diff_analysis.py`

```bash
# Basic usage — compare any two GBC/GB ROM dumps
python3 rom_diff_analysis.py <invalid_dump.bin> <valid_reference.bin>

# Example with this cartridge's dumps
python3 rom_diff_analysis.py invalid_POKEMON_GLD.bin valid_reference.bin
```

The script produces a full structured report including header comparison, bank-level diff distribution, address bit analysis, data line bit-flip statistics, stride pattern analysis, and an automated diagnosis conclusion.

**No external dependencies required — standard Python 3 only.**

---

## 12. References

### Technical Specifications
- **Pan Docs — MBC3:** https://gbdev.io/pandocs/MBC3.html
- **Pan Docs — Power Up Sequence:** https://gbdev.io/pandocs/Power_Up_Sequence.html
- **Pan Docs — Memory Map:** https://gbdev.io/pandocs/Memory_Map.html
- **Game Boy Hardware Database (DMGKGDU10 PCB):** https://gbhwdb.gekkio.fi
- **Game Boy CPU Manual (Z80 variant):** https://archive.org/details/GameBoyProgManVer1.1

### Prior Art (Unresolved)
- Glitch City Laboratories — "No windows available for popping" (2010): https://glitchcity.wiki
- Reddit r/Gameboy: https://www.reddit.com/r/Gameboy
- Reddit r/GameboyRepair: https://www.reddit.com/r/GameboyRepair

### ROM Verification
- **No-Intro ROM Database (GBC):** https://www.no-intro.org  
  Expected SHA-1 for Pokémon Gold (EUR): `D8B8A3600A465308C9953B46BC16CBBF4B79F9AC`

---

<div align="center">

---

*Research, hardware analysis, and tooling by **Jannik Weyrich / NostaMods***  
*[github.com/jw0710](https://github.com/jw0710)*

*Published under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)*  
*Attribution required · Non-commercial use only · Share-alike*

*If this analysis helped you diagnose a similar fault, consider opening an Issue or Discussion with your findings — every documented case strengthens the collective knowledge base.*

</div>
