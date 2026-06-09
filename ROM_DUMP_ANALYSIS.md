# ROM Dump Analysis — DMGKGDU10-0 · Pokémon Gold

> **Cartridge:** Pokémon Gold · PCB DMGKGDU10-0  
> **Mapper:** MBC3 + RTC · **ROM:** 2 MiB · **SRAM:** 32 KiB  
> **Analysis tool:** [`rom_diff_analysis.py`](rom_diff_analysis.py)

---

## 1. Dump Session Protocol

All four dumps were performed using a GB cartridge flasher under identical conditions. Between sessions, no hardware changes were made — same cartridge, same adapter, same host machine. This is a critical methodological requirement: variable-free sessions ensure that any inconsistency between dumps is attributable to the cartridge alone, not to external factors.

| Parameter | Value |
|---|---|
| Flasher | GB cartridge reader/writer |
| Connection | Clean edge connector (IPA + glass fibre, pre-session) |
| Host OS | Constant across all sessions |
| Inter-dump changes | None |
| File format | Raw binary (`.bin` / `.gbc`) |
| Expected file size | 2,097,152 bytes (2.00 MiB) |

---

## 2. ROM Header — Full Field Table

The following metadata was extracted from the ROM header at addresses `0x0100`–`0x014F`. Fields were compared against the known-good reference dump byte-for-byte.

| Address | Field | Invalid Dump | Valid Reference | Match |
|---|---|---|---|---|
| `0x0100–0x0103` | **Entry Point** | `F3 C3 C6 05` | `00 C3 C6 05` | ❌ |
| `0x0104–0x0133` | Nintendo Logo | `CEED6666…` | `CEED6666…` | ✅ |
| `0x0134–0x013E` | Title | `POKEMON_GLD` | `POKEMON_GLD` | ✅ |
| `0x013F–0x0142` | Manufacturer | `AAUD` | `AAUD` | ✅ |
| `0x0143` | CGB Flag | `0x80` | `0x80` | ✅ |
| `0x0144–0x0145` | New Licensee | `3031` (Nintendo) | `3031` | ✅ |
| `0x0146` | SGB Flag | `0x03` | `0x03` | ✅ |
| `0x0147` | Cartridge Type | `0x10` (MBC3+RAM+TIMER) | `0x10` | ✅ |
| `0x0148` | ROM Size | `0x06` (2 MiB) | `0x06` | ✅ |
| `0x0149` | RAM Size | `0x03` (32 KiB) | `0x03` | ✅ |
| `0x014A` | Destination | `0x01` (Non-JP) | `0x01` | ✅ |
| `0x014B` | Old Licensee | `0x33` | `0x33` | ✅ |
| `0x014C` | **Version** | `0x00` | `0x00` | ✅ |
| `0x014D` | Header Checksum | `0x4C` | `0x4C` | ✅ |
| `0x014E–0x014F` | **Global Checksum** | `0xDC97` / `0xF004` | `0xDC97` | ⚠️ |

### Entry Point Discrepancy

The entry point at `0x0100` differs between dumps:

```
Invalid:  F3 C3 C6 05   →  DI / JP $05C6
Valid:    00 C3 C6 05   →  NOP / JP $05C6
```

`0xF3` is the opcode for **DI** (Disable Interrupts). While this is a valid and common Game Boy opcode, its presence here instead of `NOP` (`0x00`) in the invalid dump indicates this byte is being read incorrectly — it is the first address fetched by the Z80 CPU on boot (`0x0100`) and also the first address where A0–A7 transitions from all-zero to non-zero after the BIOS hands off execution. Its corruption is directly causal to the subsequent boot failure.

---

## 3. Checksum Results — All Four Dumps

### Raw Results

| Dump | File Size | Header CRC | Global CRC | Valid |
|---|---|---|---|---|
| 1 — invalid_POKEMON_GLD_AAUD-0.bin | 2,097,152 B | `0x4C` ✅ | `0xF004` | ❌ |
| 2 | 2,097,152 B | `0x4C` ✅ | `0xF004` | ❌ |
| 3 | 2,097,152 B | `0x4C` ✅ | `0xDC97` | ✅ |
| 4 — Valid_4_Pokemon_Goldene_Edition.bin | 2,097,152 B | `0x4C` ✅ | `0xDC97` | ✅ |

### Statistical Interpretation

The **header checksum** (`0x4C`, covering `0x0134`–`0x014C`) is valid and **identical across all four dumps**. This confirms:
- The cartridge header block is intact and readable
- The dump hardware is functioning correctly for at least this address range
- Both dumps are confirmed as the same ROM revision

The **global checksum** (`0xDC97`, covering the full 2 MiB) is valid in 50% of dumps and invalid in 50%, with the invalid value consistently `0xF004`. This is **not random variance** — it is a deterministic fault state that the chip resolves into under specific conditions.

| Metric | Value |
|---|---|
| Valid dump rate | 50% (2/4) |
| Invalid dump rate | 50% (2/4) |
| Invalid checksum value | `0xF004` (consistent) |
| Delta (invalid − valid) | `0x236D` |
| Random noise hypothesis | ❌ Ruled out (consistent invalid value) |
| Contact fault hypothesis | ❌ Ruled out (would produce random variance) |
| **Intermittent address fault** | ✅ Consistent with findings |

---

## 4. Binary Diff Results

### 4.1 Top-Level Statistics

Byte-level comparison of Dump 1 (invalid) vs. Dump 4 (valid reference):

| Metric | Result |
|---|---|
| Total differing bytes | **1,313** |
| ROM banks containing diffs | **101 / 128** |
| Addresses at exact 0x100 boundary | **1,313 / 1,313 (100.0%)** |
| Low byte (`addr & 0xFF`) for all diffs | **`0x00`** (100%) |
| Primary stride between diffs | **`0x0200`** (661 occurrences) |
| Secondary stride | **`0x0100`** (652 occurrences) |

### 4.2 The 0x100-Alignment Finding

The single most significant finding of the binary analysis:

> **Every differing byte is located at an address that is a multiple of 256.**

No diff occurs at `0x????01`, `0x????7F`, `0x????FF`, or any non-`0x????00` address. Across 1,313 data points spanning 101 ROM banks, the alignment rate is **100.000%**.

For reference: if errors were randomly distributed across the 2 MiB address space, the probability that all 1,313 would independently land on `0x????00` addresses is:

```
P = (1/256)^1313 ≈ 10^(-3,072)
```

This is not a statistical anomaly. It is a **deterministic hardware signature**.

### 4.3 Bank-Level Distribution

```
Bank 00  (0x000000): 41 diffs  ←  highest concentration (boot + engine code)
Bank 01  (0x004000): 30 diffs
Bank 02  (0x008000): 31 diffs
Bank 03  (0x00C000): 29 diffs
Bank 04  (0x010000): 28 diffs
...
Bank 63  (0x0FC000): 11 diffs
Bank 64  (0x100000): 11 diffs
...
Bank 112 (0x1C0000):  5 diffs  ←  lowest concentration (upper graphics banks)
```

The decreasing diff density from low to high banks is consistent with the intermittent nature of the fault: the fixed bank (Bank 0, always mapped, first accessed on boot) shows the greatest corruption, while upper switched banks accessed later — or in sessions where the chip was temporarily functional — show fewer diffs.

### 4.4 Data Line Bit-Flip Distribution

| Data Line | Flips | Distribution |
|---|---|---|
| D7 | 543 | ███████████████████████████ |
| D6 | 565 | ████████████████████████████ |
| D5 | 593 | █████████████████████████████ |
| D4 | 645 | ████████████████████████████████ |
| D3 | 624 | ███████████████████████████████ |
| D2 | 668 | █████████████████████████████████ |
| D1 | 664 | █████████████████████████████████ |
| D0 | 652 | ████████████████████████████████ |

**Distribution is uniform.** Spread between most and least affected line: 125 flips. No individual data line is significantly over- or under-represented. This rules out a stuck data line fault and confirms the fault is in the **address domain**, not the data domain.

---

## 5. Conclusion

The dump analysis establishes the following with high confidence:

1. **The ROM header and version are intact** — both dumps are the same DMGKGDU10-0 revision
2. **The fault is not random bit degradation** — 100% alignment to 0x100 boundaries is a deterministic hardware signature
3. **The fault is not a data line fault** — uniform bit flip distribution across D0–D7
4. **The fault is consistent with stuck-low address lines A0–A7** — the chip cannot resolve addresses within any 256-byte window, aliasing every access to offset `0x??00`
5. **The fault is intermittent** — 50% valid dump rate suggests a high-impedance rather than fully open fault condition

For the full root cause analysis and boot failure mechanism, see [README.md §7](README.md#7-root-cause-stuck-address-lines-a0a7).

---

*Analysis by Jannik Weyrich / NostaMods · [github.com/jw0710](https://github.com/jw0710)*
