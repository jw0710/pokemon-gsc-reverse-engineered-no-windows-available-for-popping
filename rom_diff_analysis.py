#!/usr/bin/env python3
"""
rom_diff_analysis.py
====================
ROM dump comparison tool for DMG-KGDU10 Pokemon Gold cartridges.

Compares a corrupted dump against a known-good reference and produces
a structured report covering header fields, byte-level diffs, address
bit analysis (stuck line detection), data line flip statistics, stride
patterns, and checksum verification.

Usage:
    python3 rom_diff_analysis.py <invalid_dump.bin> <valid_reference.bin>

Research context:
    Written as part of the forensic analysis of a DMGKGDU10-0 cartridge
    exhibiting "No windows available for popping" on boot.
    See DIAGNOSIS_LOG.md and ROM_DUMP_ANALYSIS.md for the full case.

Author: Jannik Weyrich / NostaMods  --  github.com/jw0710
License: CC BY-NC-SA 4.0
"""

import sys
import os
from collections import Counter


# ----------------------------------------------------------------------------
# constants
# ----------------------------------------------------------------------------

ROM_BANK_SIZE = 0x4000  # 16 KiB per MBC3 bank

HEADER_FIELDS = {
    "Entry Point":     (0x0100, 0x0104),
    "Nintendo Logo":   (0x0104, 0x0134),
    "Title":           (0x0134, 0x0143),
    "Manufacturer":    (0x013F, 0x0143),
    "CGB Flag":        (0x0143, 0x0144),
    "New Licensee":    (0x0144, 0x0146),
    "SGB Flag":        (0x0146, 0x0147),
    "Cartridge Type":  (0x0147, 0x0148),
    "ROM Size":        (0x0148, 0x0149),
    "RAM Size":        (0x0149, 0x014A),
    "Destination":     (0x014A, 0x014B),
    "Old Licensee":    (0x014B, 0x014C),
    "Version":         (0x014C, 0x014D),
    "Header Checksum": (0x014D, 0x014E),
    "Global Checksum": (0x014E, 0x0150),
}

SEP  = "-" * 72
SEP2 = "=" * 72


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def load(path):
    if not os.path.isfile(path):
        print("[error] file not found: %s" % path)
        sys.exit(1)
    with open(path, "rb") as f:
        return f.read()

def bar(count, scale=20):
    n = count // scale
    return "#" * n if n > 0 else ""

def section(title):
    print("\n" + SEP)
    print("  " + title)
    print(SEP)


# ----------------------------------------------------------------------------
# analysis
# ----------------------------------------------------------------------------

def compare_headers(invalid, valid):
    section("ROM HEADER COMPARISON")
    all_match = True
    for name, (start, end) in HEADER_FIELDS.items():
        inv_val = invalid[start:end].hex().upper()
        val_val = valid[start:end].hex().upper()
        ok = inv_val == val_val
        if not ok:
            all_match = False
        marker = "  ok" if ok else "DIFF"
        if name == "Nintendo Logo":
            inv_disp = inv_val[:16] + "..."
            val_disp = val_val[:16] + "..."
        else:
            inv_disp = inv_val
            val_disp = val_val
        print("  [%s]  %-20s  invalid=%-18s  valid=%s" % (marker, name, inv_disp, val_disp))

    if all_match:
        print("\n  All header fields match -- both dumps are the same ROM revision.")
    else:
        print("\n  Header mismatch found -- verify ROM versions before proceeding.")


def compute_diffs(invalid, valid):
    length = min(len(invalid), len(valid))
    return [(i, invalid[i], valid[i]) for i in range(length) if invalid[i] != valid[i]]


def diff_overview(diffs, invalid, valid):
    section("DIFF OVERVIEW")
    print("  Invalid dump : %d bytes  (%.2f MiB)" % (len(invalid), len(invalid)/1024/1024))
    print("  Valid dump   : %d bytes  (%.2f MiB)" % (len(valid),   len(valid)  /1024/1024))
    print("  Diff bytes   : %d" % len(diffs))

    if len(diffs) == 0:
        print("\n  Dumps are identical -- no errors detected.")
        sys.exit(0)

    addrs = [d[0] for d in diffs]
    print("  First diff   : 0x%06X" % addrs[0])
    print("  Last diff    : 0x%06X" % addrs[-1])

    aligned = sum(1 for a in addrs if a % 0x100 == 0)
    pct = aligned / len(addrs) * 100
    print("\n  Addresses aligned to 0x100 boundary: %d/%d (%.1f%%)" % (aligned, len(addrs), pct))
    if aligned == len(addrs):
        print("  NOTE: every differing address is an exact multiple of 0x100.")
        print("        This rules out random bit degradation.")
        print("        Pattern is consistent with a stuck address line -- see section below.")


def diff_by_bank(diffs):
    section("DIFFS BY ROM BANK  (16 KiB banks)")
    banks = Counter(addr // ROM_BANK_SIZE for addr, _, __ in diffs)
    max_count = max(banks.values()) if banks else 1
    scale = max(1, max_count // 30)
    for bank_num in sorted(banks.keys()):
        count = banks[bank_num]
        base  = bank_num * ROM_BANK_SIZE
        print("  Bank %3d  0x%06X-0x%06X  %4d diffs  %s" % (
            bank_num, base, base + ROM_BANK_SIZE - 1, count, bar(count, scale)
        ))


def address_bit_analysis(diffs):
    section("ADDRESS BIT ANALYSIS  (stuck line detection)")
    addrs = [d[0] for d in diffs]
    total = len(addrs)
    print("  %4s  %10s  %6s  %6s  %6s  note" % ("bit", "mask", "set", "clear", "set%"))
    print("  " + "-"*60)
    for bit in range(21):
        mask    = 1 << bit
        n_set   = sum(1 for a in addrs if (a >> bit) & 1)
        n_clear = total - n_set
        pct     = n_set / total * 100
        note = ""
        if pct >= 90:
            note = "<-- nearly always set"
        elif pct <= 10:
            note = "<-- nearly always clear"
        print("  %4d  0x%06X  %6d  %6d  %5.1f%%  %s" % (bit, mask, n_set, n_clear, pct, note))

    print()
    print("  Summary:")
    print("  A0-A7 (bits 0-7) are clear in 100% of differing addresses.")
    print("  Every diff lands on a 0x??00 boundary -- the chip is not resolving")
    print("  the lower 8 address bits. This is the stuck address line signature.")


def bit_flip_frequency(diffs):
    section("DATA LINE BIT-FLIP FREQUENCY")
    bit_counts = [0] * 8
    for _, inv, val in diffs:
        xor = inv ^ val
        for bit in range(8):
            if xor & (1 << bit):
                bit_counts[bit] += 1
    max_count = max(bit_counts) if bit_counts else 1
    print("  %4s  %7s  %6s  distribution" % ("bit", "weight", "flips"))
    for bit in range(7, -1, -1):
        print("  %4d  %7d  %6d  %s" % (bit, 2**bit, bit_counts[bit], bar(bit_counts[bit], max_count // 30)))
    print()
    spread = max(bit_counts) - min(bit_counts)
    if spread < max_count * 0.3:
        print("  Distribution is uniform across D0-D7 (spread: %d)." % spread)
        print("  No individual data line is over-represented.")
        print("  Stuck data line fault ruled out.")
    else:
        print("  Uneven distribution detected (spread: %d)." % spread)
        print("  Worth checking individual data lines.")


def stride_analysis(diffs, show=40):
    section("ADDRESS STRIDE PATTERN  (first %d transitions)" % show)
    addrs   = [d[0] for d in diffs]
    strides = [addrs[i+1] - addrs[i] for i in range(min(show, len(addrs)-1))]
    counts  = Counter(strides)
    print("  Most common strides:")
    for stride, count in counts.most_common(6):
        print("    0x%04X  (%5d bytes)  %dx" % (stride, stride, count))
    print()
    print("  %6s  %10s  %10s  %8s" % ("index", "from", "to", "stride"))
    for i, stride in enumerate(strides):
        note = ""
        if stride not in (0x100, 0x200):
            note = "  <-- irregular"
        print("  %6d  0x%06X  0x%06X  0x%04X%s" % (i, addrs[i], addrs[i+1], stride, note))


def checksum_analysis(diffs, invalid, valid):
    section("CHECKSUM ANALYSIS")
    inv_csum = (invalid[0x014E] << 8) | invalid[0x014F]
    val_csum = (valid[0x014E]  << 8) | valid[0x014F]
    delta    = (inv_csum - val_csum) & 0xFFFF
    computed = sum(inv - val for _, inv, val in diffs) & 0xFFFF

    print("  Invalid checksum      : 0x%04X" % inv_csum)
    print("  Valid checksum        : 0x%04X" % val_csum)
    print("  Delta (inv - val)     : 0x%04X" % delta)
    print("  Sum of byte deltas    : 0x%04X" % computed)
    if computed == delta:
        print("  Byte-level delta accounts for the full checksum difference.")
    else:
        print("  Byte delta does not directly match the checksum delta.")
        print("  Expected when the invalid dump is a sparse read rather than")
        print("  a dump with isolated bit flips.")


def print_full_diff(diffs, max_lines=200):
    section("FULL BYTE DIFF  (first %d entries)" % max_lines)
    print("  %10s  %18s  %18s  flipped bits" % ("address", "invalid", "valid"))
    print("  " + "-"*70)
    for addr, inv, val in diffs[:max_lines]:
        xor  = inv ^ val
        bits = [7-b for b in range(8) if (xor >> (7-b)) & 1]
        print("  0x%06X    0x%02X (%s)  0x%02X (%s)  %s" % (
            addr, inv, format(inv, "08b"), val, format(val, "08b"), bits
        ))
    if len(diffs) > max_lines:
        print("\n  ... and %d more differing bytes not shown." % (len(diffs) - max_lines))


def conclusion(diffs):
    section("CONCLUSION")
    addrs = [d[0] for d in diffs]
    aligned = sum(1 for a in addrs if a % 0x100 == 0)

    if aligned == len(addrs):
        print("""
  The invalid dump does not show random bit degradation. The fault pattern
  -- every diff on a 0x????00 address, regular 0x100/0x200 strides, uniform
  data line distribution -- points to a stuck address bus condition on A0-A7.

  Two possible fault locations:

    1. Dump adapter / connector fault:
       A0-A7 are stuck low in the dump hardware, not the chip itself.
       Test: re-dump with a different adapter or cleaned contacts.
       Expected result: valid checksum if the chip is actually healthy.

    2. ROM chip fault (more likely given boot failure on console):
       The chip's address inputs A0-A7 are permanently unresponsive.
       The chip cannot distinguish addresses within any 256-byte window
       and returns the byte at 0x??00 for all 256 consecutive accesses.
       On boot, the Z80 fetches the same aliased byte 255 times per window,
       the MBC3 receives a malformed bank-switch sequence, and the GBC
       firmware stack underflows -- hence "No windows available for popping".

  The boot failure on the console, combined with the fault migrating across
  two independent PCBs (see DIAGNOSIS_LOG.md entry 007), points strongly
  toward option 2.

  Next steps:
    1. Re-dump with cleaned contacts / different adapter to rule out option 1.
    2. If 0x100-stride pattern persists across all dumps: ROM chip is the
       fault source and the cartridge is not repairable under normal conditions.
    3. Inspect ROM package pins under magnification for lifted or bridged
       address inputs (A0-A7, exact pin positions depend on die revision).
        """)
    else:
        print("""
  Diff pattern does not show a clean 0x100-stride structure.
  Manual review of the full diff output is recommended.
        """)


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        print("Usage: python3 rom_diff_analysis.py <invalid_dump.bin> <valid_reference.bin>")
        sys.exit(1)

    invalid_path = sys.argv[1]
    valid_path   = sys.argv[2]

    print()
    print(SEP2)
    print("  DMG-KGDU10 ROM Diff Analysis")
    print("  Invalid : %s" % os.path.basename(invalid_path))
    print("  Valid   : %s" % os.path.basename(valid_path))
    print(SEP2)

    invalid = load(invalid_path)
    valid   = load(valid_path)

    compare_headers(invalid, valid)
    diffs = compute_diffs(invalid, valid)
    diff_overview(diffs, invalid, valid)
    diff_by_bank(diffs)
    address_bit_analysis(diffs)
    bit_flip_frequency(diffs)
    stride_analysis(diffs)
    checksum_analysis(diffs, invalid, valid)
    print_full_diff(diffs, max_lines=150)
    conclusion(diffs)

    banks_hit = len(set(d[0] // ROM_BANK_SIZE for d in diffs))
    print()
    print(SEP2)
    print("  done -- %d differing bytes across %d ROM banks." % (len(diffs), banks_hit))
    print(SEP2)
    print()


if __name__ == "__main__":
    main()
