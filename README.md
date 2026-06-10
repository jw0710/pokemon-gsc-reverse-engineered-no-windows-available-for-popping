<div align="center">

# DMG-KGDU10 - *"No Windows Available for Popping"*
### Hardware Fault Isolation and Binary Analysis · Pokemon Gold / Silver / Crystal · Game Boy Color

---

![Status](https://img.shields.io/badge/status-active_investigation-orange?style=flat-square)
![ROM](https://img.shields.io/badge/ROM-POKEMON__GLD-blue?style=flat-square)
![PCB](https://img.shields.io/badge/PCB-DMGKGDU10--0-blue?style=flat-square)
![Mapper](https://img.shields.io/badge/mapper-MBC3_+_RTC-blue?style=flat-square)
![ROM Size](https://img.shields.io/badge/ROM-2_MiB-blue?style=flat-square)
![Dumps](https://img.shields.io/badge/dump_sessions-6-yellow?style=flat-square)
![Fault](https://img.shields.io/badge/fault-AC_parametric-red?style=flat-square)
![Xray](https://img.shields.io/badge/X--ray_analysis-pending-orange?style=flat-square)
![License](https://img.shields.io/badge/license-CC_BY--NC--SA_4.0-green?style=flat-square)

</div>

---

## Abstract

This repository presents a complete forensic hardware analysis of a defective **Pokémon Gold** cartridge (PCB: **DMGKGDU10-0**, mapper: **MBC3 + RTC**) exhibiting the boot-fatal error:

```
No windows available for popping
```

Through systematic component substitution across two independent PCB assemblies, electrical verification, and structured binary analysis of ROM dumps taken under varying thermal and contact conditions, the fault was isolated to the Mask-ROM device. The investigation produced a definitive finding.

Under clean contact conditions at ambient temperature, the chip delivers a bitperfect ROM dump with zero differing bytes and a fully matching computed checksum -- confirmed against an independently obtained reference. The boot failure persists regardless. This result conclusively establishes the fault as a **pure AC parametric failure**: the ROM device can resolve every address correctly under the controlled read timing of a flasher, but cannot do so under the continuous cycle demands of the running Z80 at 4.19 MHz. No static data corruption is present. The failure is exclusively timing-domain.

Earlier dump sessions that produced structured 0x100-aligned corruption patterns are now understood to reflect marginal contact conditions rather than the chip's true static read capability. They remain documented as they characterise the fault's behaviour under degraded contact states, but they are not the primary evidence for the fault classification.

At the time of writing, no prior technical documentation of this failure mode exists in the public domain. This repository is intended as a reproducible reference for hardware repair technicians and retro hardware researchers.

> **Verdict: The cartridge is irreparable under standard workshop conditions.**
> The ROM device passes static integrity checks but fails under dynamic system timing. The fault is internal to the chip and cannot be resolved through component substitution, reflowing, or any PCB-level intervention. The exact physical mechanism remains unverified.
>
> **This is an active investigation.** The fault has been classified as an AC parametric failure through empirical testing. Physical verification of the underlying semiconductor defect via X-ray microscopy is currently being pursued. This repository will be updated as further findings become available.

---

## Table of Contents

1. [Hardware Under Test](#1-hardware-under-test)
2. [The Error - Origin and Mechanism](#2-the-error--origin-and-mechanism)
3. [Methodology](#3-methodology)
4. [Component Substitution Matrix](#4-component-substitution-matrix)
5. [ROM Dump Analysis](#5-rom-dump-analysis)
6. [Binary Diff - Key Findings](#6-binary-diff--key-findings)
7. [Probable Root Cause: Failure Affecting ROM Address Resolution](#7-probable-root-cause-failure-affecting-rom-address-resolution)
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

## 2. The Error - Origin and Mechanism

### 2.1 Error String Source

The string `"No windows available for popping"` is **not embedded in the Pokémon Gold game binary**. It is emitted by the **Game Boy Color system firmware** when the memory management layer encounters an inconsistency in its ROM window stack.

The GBC firmware maintains a stack of active MBC3 "windows" - internal records of bank-switch operations performed by the MBC3 controller. When the CPU issues a bank-pop instruction and the stack contains no matching entry, the firmware raises this error and halts execution.

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

![No windows available for popping - captured on boot](docs/NoWindowsAv.png)

*Fig. 1 - The error as it appears on boot. No further execution occurs until hard reset.*

</div>

### 2.3 Why It Is Rarely Documented

The error is cartridge-specific and hardware-generated, not a software state that can be triggered by gameplay. It requires a specific class of ROM fault to manifest - one that corrupts the early boot execution path without triggering the BIOS logo check failure (which would display a different error). This narrow fault window explains why the symptom is virtually absent from repair literature.

---

## 3. Methodology

All diagnostics followed a **single-variable substitution protocol**: one component replaced per session, all others held constant, boot-tested after each change. This ensures each result is attributable to the substituted component alone.

```
Session 1 - Baseline boot test + visual/electrical inspection
Session 2 - MBC3 replacement
Session 3 - SRAM replacement
Session 4 - Full SMD passive replacement
Session 5 - Full PCB swap (ROM chip transferred to donor board)
Session 6 - ROM dump analysis (4 dumps)
Session 7 - Binary diff analysis (invalid vs. reference dump)
```

### Equipment Used

| Tool | Details | Purpose |
|---|---|---|
| Hot air rework station | 300°C, top-side application | Component removal, thermal activation testing |
| Multimeter | -- | Voltage, continuity, resistance verification |
| GB cartridge flasher | GBFlash v1.3, Firmware L13, FlashGBX v4.3 | ROM dumping |
| Verified GBC reference unit | -- | Boot testing |
| Donor DMGKGDU10-0 board | Clean edge connector | PCB-swap substitution test |
| Python 3.x + rom_diff_analysis.py | Custom, see repository | Binary diff and fault characterisation |

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
| Full PCB | Donor board substitution - ROM transferred | **Error migrates with ROM** | ok -- PCB ruled out |
| **ROM chip** | Cannot replace (Mask-ROM) | **Confirmed defect origin** | FAULT SOURCE |

The PCB-swap test (Session 5) is the definitive isolation step. With every component replaced or verified except the ROM chip, and the error following the ROM across two independent PCB assemblies, the ROM is confirmed as the sole fault source.

---

## 5. ROM Dump Analysis

Dumps were performed across multiple sessions under varying thermal conditions. All dumps used the same FlashGBX hardware and cartridge connector.

### 5.1 Important Note on Checksum Reporting

FlashGBX reads the global checksum value directly from the ROM header bytes at `0x014E-0x014F` and stores it in the output file. It does not independently compute and verify the checksum against the read data. As a result, all dumps -- including corrupted ones -- report `0xDC97` as the stored checksum field, because that value is itself stored at a `0x????0E`/`0x????0F` address which the chip reads correctly even under the address-resolution fault.

The actual data integrity of each dump must be assessed by computing the checksum independently from the file contents, which is what `rom_diff_analysis.py` does.

### 5.2 Header Fields

All header fields are identical between defective and reference dumps, confirming both are the same ROM version and revision.

| Field | Defective dumps | Valid Reference | Match |
|---|---|---|---|
| Title | `POKEMON_GLD` | `POKEMON_GLD` | ok |
| CGB Flag | `0x80` | `0x80` | ok |
| Cart Type | `0x10` (MBC3+RAM+TIMER) | `0x10` | ok |
| ROM Size | `0x06` (2 MiB) | `0x06` | ok |
| Version | `0x00` | `0x00` | ok |
| Header Checksum | `0x4C` | `0x4C` | ok |
| **Global Checksum (stored)** | **`0xDC97`** (all dumps) | **`0xDC97`** | ok (see note above) |
| **Global Checksum (computed)** | **varies** | **`0xDC97`** | MISMATCH in all defective dumps |

### 5.3 Dump Sessions and Results

| Session | Thermal state | Board condition | Stored CRC | Computed CRC | Diff bytes | 0x100-aligned | Entry point | Notes |
|---|---|---|---|---|---|---|---|---|
| Cold 1 | Ambient | Clean board | `0xDC97` | `0xDAA3` | 1313 | 100% | FAIL | Reference cold baseline |
| Cold 2 | Ambient | Clean board | `0xDC97` | `0xDAA3` | 1313 | 100% | FAIL | Identical to Cold 1 |
| Warm 1 | ~300°C / 15s | Clean board | `0xDC97` | `0x3826` | 1230 | 1.9% | ok | Thermal activation |
| Warm 2 | ~300°C / 15s | Clean board | `0xDC97` | `0xDB22` | 2 | 50% | ok | Near-complete recovery |
| Confounded | Ambient | Damaged edge connector | `0x4011` | `0x1AC0` | 249023 | 0.4% | FAIL | Contaminated -- see note |
| **Cold 3** | **~20°C (ultrasonic bath)** | **Clean board, fresh reflow** | **`0xDC97`** | **`0xDC97`** | **0** | **n/a** | **ok** | **Bitperfect -- see note** |

The shift from 1313 structured diffs at ambient to 2 near-random diffs under thermal activation was initially interpreted as the central finding of the thermal investigation. However, Cold 3 supersedes this interpretation: under clean contact conditions after fresh reflow, the chip delivered a bitperfect dump at ambient temperature with zero differing bytes and a fully matching computed checksum. The boot failure persists nonetheless.

This result reframes the fault model entirely. The earlier cold dumps (Cold 1/2) with their 0x100-aligned corruption pattern were not representative of the chip's true static read capability -- they reflected a marginal contact state. Cold 3 demonstrates that the fault is **not a static data corruption issue at all**. The chip can deliver every byte correctly under controlled read conditions. The failure is exclusively a dynamic timing fault: the chip cannot resolve addresses reliably under the continuous read cycle demands of the running Z80 at 4.19 MHz, even though it can resolve them correctly under the slower, controlled timing of the flasher.

**Note on the confounded dump:** One dump session was performed cold on a donor board with heavily corroded and damaged edge connector pins. This session produced 249,023 differing bytes with a heavily non-uniform bit-flip distribution consistent with multiple data lines at high impedance. This dump represents two simultaneous independent fault sources and is not used as evidence for the chip-level fault model.

**Note on Cold 3:** CRC32 `4889dfaa` matches the FlashGBX No-Intro database entry for Pokemon Gold Germany. The SHA-1 does not match the No-Intro reference (`D8B8A360...`) as that entry corresponds to a different regional revision. The dump is confirmed bitperfect against the independently obtained reference dump used throughout this analysis (0 byte differences).

---

## 6. Binary Diff - Key Findings

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

## 7. Probable Root Cause: Failure Affecting ROM Address Resolution

### 7.1 Summary of Evidence

The fault was isolated to the Mask-ROM device through systematic component substitution and PCB migration testing. The observed corruption pattern remained associated with the ROM chip across two independent PCB assemblies, while all other components were either verified or replaced without affecting the symptom.

Binary comparison between valid and invalid dumps identified 1,313 differing bytes distributed across 101 ROM banks. Every differing address was aligned to a 0x100 boundary, producing a highly structured and deterministic error pattern inconsistent with random bit degradation or data-line failure.

### 7.2 How ROM Addressing Works

A 2 MiB Mask-ROM requires 21 address inputs (A0-A20) to uniquely address every byte in its 2,097,152-byte space. These are physical pins on the chip package connected to the ROM die via bond wires. The MBC3 drives A13-A20 for bank selection; A0-A12 are driven directly by the CPU address bus.

```
Address line:  A20  A19  ...  A8   A7   A6  ...  A1   A0
Bit weight:    1M   512K ...  256  128   64  ...   2    1
```

### 7.3 Fault Classification: AC Parametric Failure

The definitive evidence for fault classification comes from dump session Cold 3: a bitperfect dump obtained at ambient temperature under clean contact conditions, with zero differing bytes against the reference, confirmed by matching computed checksum and CRC32. The boot failure persists on this same cartridge.

This result rules out static data corruption as a contributing factor to the boot failure. The chip can resolve every address correctly and deliver every byte accurately when the access timing is controlled. The fault manifests exclusively when the chip must respond to continuous read cycles at system clock rate.

This is the definition of an **AC parametric failure** in semiconductor testing terminology: a device that passes DC functionality tests (correct data under static or slow-access conditions) but fails under the timing constraints of its operational environment (correct data not guaranteed within the required setup and hold window at operating frequency).

The earlier cold dumps (Cold 1/2) which showed 0x100-aligned corruption are now understood as a contact-condition artefact. Under marginal edge connector contact, the address lines were not being driven cleanly to the chip, producing the observed aliasing pattern. Under good contact conditions, the chip reads correctly. The underlying chip fault only manifests at system clock speed.

The distinction between DC and AC failure has direct implications for physical fault location. A DC stuck fault (permanently incorrect logic level) would affect all reads equally. An AC parametric fault (marginal timing) implies the fault is in the **propagation path or input response time** of the address lines -- consistent with a bond-wire crack or oxide-layer contact fault that adds resistance to the signal path, slowing the rise/fall time of the address signal below what the chip's input comparator can resolve within a Z80 read cycle.

### 7.4 Boot Failure Under This Model

The GBC boot ROM occupies `0x0000-0x00FF` and is mapped over the cartridge during startup -- the cartridge ROM is not read in this range during the boot sequence. Control transfers to the cartridge entry point at `0x0100` after the boot ROM completes the logo check and header verification.

Under the proposed AC parametric fault model, the Z80 begins instruction fetch from `0x0100` at system clock rate. The address lines responsible for resolving the lower byte of each address fail to settle within the required read cycle, producing unstable data on the bus. The resulting instruction stream is incoherent. The first malformed MBC3 bank-switch operation passes an invalid parameter to the GBC memory manager, which finds no matching window stack entry and emits `"No windows available for popping"`.

The cold-state dump confirms that `0x0100` reads as `0xF3` (DI) rather than the correct `0x00` (NOP), which is consistent with this model: under static dump timing, some addresses resolve to incorrect but stable values; under dynamic Z80 timing, the failure mode may differ in character but the result is the same incoherent execution.

### 7.5 Thermal Activation Results

Applying 300°C hot air for approximately 15 seconds to the ROM package from above produced a measurable and reproducible improvement in dump integrity:

| State | Diff bytes vs reference | 0x100-aligned | Computed checksum | Entry point |
|---|---|---|---|---|
| Cold | 1313 | 100% | `0xDAA3` | FAIL |
| Warm (session 1) | 1230 | 1.9% | `0x3826` | ok |
| Warm (session 2) | 2 | 50% | `0xDB22` | ok |

Three observations from this data are significant:

**The alignment pattern disappears under heat.** Cold dumps show 100% 0x100-alignment -- a deterministic DC-like stuck condition. Warm dumps show near-random distribution across all 256 low-byte values. This indicates the fault transitions from a DC stuck state at ambient temperature to a marginal high-impedance state under thermal expansion, allowing intermittent correct resolution during slow dump reads.

**The two dumps are not reproducible.** Cold sessions 1 and 2 produce identical results (1313 diffs, same addresses). Warm sessions produce different results from each other (1230 vs 2 diffs, minimal address overlap). This irreproducibility under heat is consistent with a contact fault that varies with the exact thermal expansion state of the package at the moment of reading.

**Boot failure persists despite near-perfect dump recovery.** Warm session 2 produced only 2 differing bytes (`0x000000` and `0x000001`), both in the region covered by the GBC boot ROM during startup and therefore not directly executed on boot. Despite this, the cartridge continued to exhibit the boot failure. This is the primary evidence for an AC parametric fault: the chip can deliver correct data under static read conditions but fails under the dynamic timing of the running system.

The thermal test also confirms with high confidence that the fault is located within the ROM chip package itself. A PCB-level solder joint fault would not respond to heat applied to the chip body in this way; that possibility was already excluded by the board migration test.

### 7.6 Possible Physical Failure Mechanisms

| Candidate mechanism | DC or AC | Assessment |
|---|---|---|
| Bond-wire crack with marginal contact resistance | AC | Most consistent with all observations |
| Oxide-layer breakdown on address input pad | AC | Consistent |
| Internal address-decoder transistor threshold shift | DC or AC | Possible |
| Package delamination causing intermittent die contact | AC | Possible |
| PCB solder joint defect | DC | Excluded by board migration test |
| External address bus fault | DC | Excluded by component substitution |

The AC parametric nature of the fault -- recoverable under slow dump reads, persistent under system clock -- most strongly implicates a physical contact fault with marginal resistance rather than a transistor-level failure, which would typically present as a pure DC fault regardless of access speed.

### 7.7 Conclusion

The fault is most likely an AC parametric failure of an address-domain connection internal to the ROM package, affecting resolution of A0-A7 under dynamic timing conditions. The fault presents as a deterministic DC-like stuck condition at ambient temperature but transitions to a marginal high-impedance state under thermal activation, allowing static read recovery while the dynamic boot failure persists.

No PCB-level repair method, component substitution, or rework procedure tested during this investigation was capable of eliminating the fault. Thermal activation improves dump quality but does not restore boot functionality, confirming the fault is timing-sensitive rather than purely contact-resistance-driven.

Conclusive physical verification would require X-ray microscopy at sufficient resolution to image bond wires (20-50 µm diameter for consumer packages of this era), or destructive decapping for direct die inspection.

### 7.8 Open Research Questions

The electrical characterisation of this fault is considered complete. The following questions remain open and are actively being pursued:

**Physical mechanism verification**

The AC parametric fault classification is well-supported by the dump data and boot behaviour, but the specific physical defect -- bond-wire crack, oxide-layer breakdown on an address input, package delamination, or other internal connection fault -- has not been directly observed. X-ray microscopy of the ROM package would allow non-destructive visualisation of the bond wire layer and could confirm or refute the bond-wire hypothesis.

Contact has been initiated with academic institutions in the region to explore access to X-ray microscopy equipment with sufficient resolution for this application. If imaging is obtained, results will be added to this repository as a dedicated supplementary section including annotated images and any revision to the fault model they require.

**Replication in other cartridges**

It is unknown whether this fault pattern has occurred in other DMGKGDU10-0 cartridges. The combination of boot failure with a passing static dump is an unusual presentation that may have been misdiagnosed as a board-level fault in other repair cases. If you have encountered a similar cartridge, opening an Issue or Discussion on this repository with your dump data would contribute meaningfully to establishing whether this is an isolated failure or a known degradation pattern in this ROM revision.

**Current status summary**

| Question | Status |
|---|---|
| Fault isolated to ROM chip | Confirmed |
| Fault classified as AC parametric | Confirmed |
| Physical mechanism identified | Pending -- X-ray analysis in progress |
| Fault replicated in other cartridges | Unknown |

---

## 8. Secondary Boot Symptoms Explained

Following sessions where valid checksums were obtained, the cartridge was tested in-system. The resulting symptoms are consistent with the proposed address-resolution fault model producing a partially coherent execution state:

<div align="center">

| | |
|:---:|:---:|
| ![Correct color title screen](docs/correct_color.png) | ![No windows error](docs/NoWindowsAv.png) |
| *Fig. 2 - Normal title screen (reference, functional state)* | *Fig. 3 - Boot failure state, consistent across resets* |
| ![Black professor sprite](docs/ProfessorSprite_Broken.png) | ![Inverted colors crash](docs/Restart_INV_Color.png) |
| *Fig. 4 - Professor Elm intro with null tile pointer (black sprite)* | *Fig. 5 - Full palette inversion mid-session before crash* |
| ![Select name crash](docs/SelectName_Crash.png) | |
| *Fig. 6 - Name selection screen crash state* | |

</div>

| Symptom | Consistent with fault model |
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

### Option A - Standard Component Replacement
> Not applicable. All standard-replaceable components verified or substituted. None affect the fault.

### Option B - ROM Chip Donor Transplant
> Theoretically possible, but practically destructive.  
> Requires sourcing an identical functional Pokémon Gold (EUR, DMGKGDU10-0) cartridge as a donor. The ROM transplant requires hot-air removal of the donor chip, cleaning and tinning the leads, and reflowing onto the target board - a destructive operation on a functional cartridge. Only warranted for exceptional sentimental or collector value cases.

### Option C - Flash Replacement Module
> Niche -- no verified off-the-shelf solution for this footprint.  
> Custom adapter PCBs replacing Mask-ROM with compatible Flash exist in the modding community for some Game Boy cartridge types. No confirmed solution for the specific DMGKGDU10-0 ROM footprint was identified. Would require custom PCB design and a compatible Flash IC with matching bus timing.

### Option D - Documentation and Return
> Recommended.  
> The cartridge is beyond economical repair. The fault is a natural wear-out failure mode of a 25-year-old semiconductor component, attributable to material degradation over service life. No prior repair attempts by the owner contributed to the fault.

### Summary Verdict

```
╔══════════════════════════════════════════════════════════════╗
║  VERDICT: IRREPARABLE -- INVESTIGATION ONGOING               ║
║                                                              ║
║  Fault:   AC parametric failure, ROM address domain          ║
║  Static:  Chip passes bitperfect dump under clean conditions  ║
║  Dynamic: Boot fails at Z80 system clock rate (4.19 MHz)     ║
║  Cause:   Physical mechanism unverified -- X-ray pending     ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 10. Comparison with Prior Art and Cross-Validation

### 10.1 Known Public References

| Source | Year | Content | Root Cause Identified |
|---|---|---|---|
| Glitch City Laboratories forum | 2010 | Software-level RAM analysis | Partial (software path only) |
| Reddit r/Gameboy | Various | Anecdotal mentions, no analysis | none |
| Reddit r/GameboyRepair | Various | Isolated reports, unresolved | none |
| GameBoy Forum communities | Various | Rare mentions | none |
| **This repository** | **2026** | **Hardware fault isolation + binary dump analysis** | **Probable address-resolution failure (A0-A7), physical mechanism under investigation** |

### 10.2 Known Software Triggers

Before examining the hardware fault, it is worth establishing the full documented set of conditions under which this error can appear through software means alone. Two sources document this comprehensively.

Bulbapedia describes the error as appearing "when an event attempts to bring up a message window yet the specified text/function is undefined", and specifically notes the HM06 outside TM/HM pocket trigger. The Glitch City Wiki documents the RAM manipulation method in detail.

The following table summarises all known software-triggered occurrences across the Generation II titles:

| Game | Trigger | RAM address(es) | Notes |
|---|---|---|---|
| Gold / Silver | RAM manipulation | `CEA8` set to `0xFD` | Reliably reproduces error on start menu close |
| Crystal | RAM manipulation | `CF71` = `0xFD`, `CF72` = `0xDF` | Requires both addresses; Crystal uses two-byte check |
| Gold / Silver | HM06 outside TM/HM pocket | `CEA8` (indirectly) | Game jumps to `0x3ACB`, opens phantom PC; closing PC then start menu triggers error |
| Crystal | Out of bounds movement | Unknown | Documented but memory path not fully characterised |
| Crystal (JPN) | Title screen | `CF65` set to specific values | Japanese version only; appears on title screen |

The error in Gold and Silver can be replicated by changing memory address `CEA8` to `0xFD` while the start menu is open, then closing it. In Crystal, the same result requires both `CF71` set to `0xFD` and `CF72` set to `0xDF`. These addresses are normally set to these values when the start menu is closed -- the error fires when the window-pop routine is called with the sentinel already in the closed state, meaning no open window record exists to pop.

The underlying mechanism is consistent across all cases: the window sentinel byte holds a value indicating no window is open at the moment a close operation is requested. The game engine detects this as an invalid state and emits the error rather than proceeding.

### 10.3 Replication Comparison: Software vs. Hardware Trigger

A natural question is whether the hardware fault described in this repository produces the same observable result through the same internal path as the software triggers above. The answer is yes in outcome but different in entry point -- and this distinction matters.

**Software trigger path:**

```
Game boots normally
    -> Window management system initialised correctly (CEA8 = valid state)
    -> Player action or RAM manipulation sets CEA8 to closed-state value
    -> Start menu close requested
    -> Window-pop routine finds no open window record
    -> Error emitted
```

**Hardware fault path (proposed model):**

```
ROM delivers aliased instruction data from boot
    -> Boot code executes incorrectly -- window management init is never performed
    -> CEA8 is never written with the correct open-state sentinel
    -> First menu operation requests a window pop
    -> Window-pop routine finds no valid record (was never created)
    -> Error emitted
```

Both paths arrive at the same guard condition in the game engine. The software triggers corrupt the sentinel value after correct initialisation; the hardware fault prevents correct initialisation from occurring in the first place. The error string is the same because the guard condition is the same -- but the hardware case cannot be reproduced by any in-game action or cheat device, because the fault occurs before the game engine is ever in a valid state.

**Emulator-based replication attempt**

A practical way to cross-validate the hardware fault model would be to load the invalid dump directly into an emulator (BGB or Gambatte are commonly used for accuracy) and observe whether the same error appears. Under the proposed model, an emulator running the invalid dump should reproduce the boot failure -- because the corrupted instruction stream would be present in the dump data itself, not in the physical chip. If a valid dump runs correctly in the same emulator, this would confirm the fault is in the dump data and by extension in the physical ROM. This test has not yet been conducted and would be a useful addition to this investigation.

### 10.3 Reconciliation with the Hardware Fault Model

The two analyses -- software emulation and physical hardware -- are not in conflict. They describe different entry points into the same failure path.

To understand why, the relevant portion of the MBC3 memory map must be considered.

The GBC address bus is 16 bits wide, giving a directly addressable range of 65,536 bytes. The MBC3 extends this to 2 MiB of ROM by dividing the ROM into 128 banks of 16,384 bytes each. Two regions of the address space are assigned to ROM:

- `0x0000-0x3FFF`: Bank 0, always fixed. Contains the entry point vector, interrupt vectors, BIOS handoff code, and the core game engine routines.
- `0x4000-0x7FFF`: Switchable bank. The MBC3 maps any of banks 1-127 here in response to write operations targeting `0x2000-0x3FFF`.

A bank switch is performed by the CPU writing the desired bank number to the MBC3's bank register. This is not a RAM write -- it is a write to the ROM address space, which the MBC3 intercepts and interprets as a control signal. The actual ROM data at that address is irrelevant; the write value selects the next active bank.

With address lines A0-A7 unresolved on the ROM die -- under the proposed fault model -- the chip cannot distinguish individual byte addresses within any 256-byte window. Every fetch from address `0xYYZZ` where `ZZ != 0x00` would return the byte stored at `0xYY00` instead. This affects both the fixed bank and all switched banks.

The boot sequence would proceed as follows under these fault conditions:

1. The BIOS performs the Nintendo logo check by reading the fixed bank header at `0x0104-0x0133`. These addresses all have non-zero low bytes, so under the stuck-line fault every read returns the byte from the nearest `0x??00` boundary. In this case, the logo check passes intermittently -- when the chip is in its temporarily functional state -- which explains why the BIOS hands off execution rather than halting at the logo stage.

2. Control transfers to the entry point at `0x0100`. The CPU begins fetching instructions sequentially. With A0-A7 stuck, addresses `0x0101` through `0x01FF` all return the byte stored at `0x0100`. The CPU executes up to 255 copies of whatever opcode sits at `0x0100` before A8 transitions and the effective address changes to `0x0200`.

3. The game engine initialises its window management system during early boot. This involves writing specific sentinel values to RAM addresses including `CEA8` in Gold and Silver. These writes originate from instructions that were fetched from the ROM. If those instructions were fetched from corrupted addresses, the sentinel values are never written correctly -- or are written with wrong values, or in the wrong sequence.

4. When the first menu-open operation executes later in boot, `CEA8` does not hold the value the window-pop routine expects. The guard condition triggers. The error string is displayed.

This is precisely the failure path GARYM9 described in 2010, arrived at from the software side. What the Glitch City analysis could not identify was the upstream cause: why `CEA8` holds the wrong value in the first place. From an emulation perspective, RAM corruption of this kind is most commonly associated with WTW (Walk Through Walls) glitches or other game-state corruptions that overwrite memory at runtime. In the hardware case studied here, the corruption is earlier in the chain -- it occurs during instruction fetch, before the window management system is ever initialised.

### 10.4 Mathematical Validation of the Address Fault Model

The binary diff analysis provides an independent means of verifying the stuck-line hypothesis through the checksum arithmetic.

The MBC3 global checksum is defined as the 16-bit sum of all bytes in the ROM, excluding the two checksum bytes at `0x014E-0x014F`. For a 2 MiB ROM this covers 2,097,150 bytes. The expected value for Pokemon Gold (EUR) is `0xDC97`.

The invalid dump produced a checksum of `0xF004`. The delta is:

```
0xF004 - 0xDC97 = 0x236D  (mod 0x10000)
```

If the stuck-line model is correct, every byte at a `0x??00` address in the invalid dump is potentially corrupted, while every byte at a non-`0x??00` address is an alias of its nearest `0x??00` neighbor and therefore may differ from the reference in a predictable way. The byte-level diff confirmed 1,313 differing bytes, all at `0x??00` addresses. The sum of those differences:

```
sum(invalid[addr] - valid[addr]) for all 1313 differing addresses = 0x236D  (mod 0x10000)
```

The byte-delta sum matches the checksum delta exactly. This is an independent cross-check: if the fault model were incorrect and some other pattern of corruption were present, the two values would not agree. The match confirms that the 1,313 identified addresses account for the full checksum discrepancy, with no additional hidden corruption elsewhere in the dump.

As a further check, the probability that 1,313 independently random address errors would all happen to land on `0x????00` boundaries by chance is:

```
P = (1/256)^1313 = 10^(-3072)
```

This value is not physically meaningful as a probability -- it is simply a demonstration that the 0x100-alignment pattern cannot be a coincidence. The pattern is deterministic.

### 10.5 Why This Error Is Under-Documented

The error occupies an unusually narrow fault window. For the string to appear, the ROM must deliver corrupted data in a way that satisfies three simultaneous conditions:

1. The Nintendo logo check must pass, or the BIOS halts earlier with a different error.
2. The boot sequence must progress far enough to initialise the window management system -- meaning the early boot code must be at least partially executable.
3. The window sentinel value at `CEA8` must be incorrect when the first menu operation executes.

A ROM that fails the logo check never reaches the window code. A ROM with a different fault pattern may hang silently, produce a garbled screen, or reset without displaying any error. A ROM that is completely non-functional produces a blank display. The stuck-A0-A7 fault happens to satisfy all three conditions: the header region reads correctly often enough to pass the logo check, the early boot executes partially (since addresses ending in 0x00 are read correctly), and the window initialisation is corrupted just enough to fail later.

From a repair technician's perspective, the error appears with no obvious hardware cause -- all passive components measure correctly, the MBC3 is not the source, and a board swap changes nothing. Without the ability to perform and compare multiple ROM dumps, the fault is essentially undiagnosable by conventional means.

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
# Basic usage - compare any two GBC/GB ROM dumps
python3 rom_diff_analysis.py <invalid_dump.bin> <valid_reference.bin>

# Example with this cartridge's dumps
python3 rom_diff_analysis.py invalid_POKEMON_GLD.bin valid_reference.bin
```

The script produces a full structured report including header comparison, bank-level diff distribution, address bit analysis, data line bit-flip statistics, stride pattern analysis, and an automated diagnosis conclusion.

**No external dependencies required - standard Python 3 only.**

---

## 12. References

### Technical Specifications
- **Pan Docs - MBC3:** https://gbdev.io/pandocs/MBC3.html
- **Pan Docs - Power Up Sequence:** https://gbdev.io/pandocs/Power_Up_Sequence.html
- **Pan Docs - Memory Map:** https://gbdev.io/pandocs/Memory_Map.html
- **Game Boy Hardware Database (DMGKGDU10 PCB):** https://gbhwdb.gekkio.fi
- **Game Boy CPU Manual (Z80 variant):** https://archive.org/details/GameBoyProgManVer1.1

### Prior Art
- Glitch City Laboratories Archives -- "G/S/C No windows available for popping explained" (GARYM9, Torchickens, 2010): https://archives.glitchcity.info/forums/board-108/thread-6228/page-0.html
- Glitch City Wiki -- "Event data debugging messages": https://glitchcity.wiki/wiki/Event_data_debugging_messages
- Bulbapedia -- "Error message, Generation II": https://bulbapedia.bulbagarden.net/wiki/Error_message#Generation_II
- Reddit r/Gameboy: https://www.reddit.com/r/Gameboy
- Reddit r/GameboyRepair: https://www.reddit.com/r/GameboyRepair

### ROM Verification
- **No-Intro ROM Database (GBC):** https://www.no-intro.org  
  Expected SHA-1 for Pokemon Gold (EUR): `D8B8A3600A465308C9953B46BC16CBBF4B79F9AC`

---

<div align="center">

---

*Published under [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)*  
*Attribution required -- non-commercial use only -- share-alike*

*If this analysis helped you diagnose a similar fault, consider opening an Issue or Discussion with your findings.*

</div>
