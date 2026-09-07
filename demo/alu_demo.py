"""Run on a TinyTapeout demo board after this revised chip is delivered.

Load this module using the board REPL. Hardware validation is pending silicon.
"""
from time import sleep_ms
from ttboard.demoboard import DemoBoard
from ttboard.mode import RPMode

tt = None
OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR", "EQ")
GLYPHS = (0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07,
          0x7F, 0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71)
_manual = False


def setup(manual=False):
    """manual=True: board DIP switches drive A/B; MCU still drives opcode."""
    global tt, _manual
    tt = DemoBoard.get()
    # Release all bidirectional drivers before selecting the chip project.
    tt.uio_oe_pico.value = 0
    tt.shuttle.tt_um_rangfuu_alu.enable()
    tt.mode = RPMode.ASIC_MANUAL_INPUTS if manual else RPMode.ASIC_RP_CONTROL
    tt.clock_project_stop()
    tt.reset_project(False)
    tt.uio_in.value = 0
    tt.uio_oe_pico.value = 0x07  # MCU drives opcode only; ASIC drives bits 3..7.
    if not manual:
        tt.ui_in.value = 0
    _manual = manual
    return tt


def oracle(a, b, op):
    result = ((a+b) & 15, (a-b) & 15, a & b, a | b, a ^ b,
              (a << 1) & 15, a >> 1, int(a == b))[op]
    flag = int(a+b > 15) if op == 0 else int(a < b) if op == 1 else 0
    return result, flag, int(result == 0)


def _read(a, b, op):
    sleep_ms(1)  # Static functional observation, not a timing measurement.
    uo = int(tt.uo_out.value)
    uio = int(tt.uio_out.value)
    result, flag, zero = uio >> 4, uo >> 7, (uio >> 3) & 1
    expected, expected_flag, expected_zero = oracle(a, b, op)
    assert (result, flag, zero) == (expected, expected_flag, expected_zero), \
        "Silicon binary result/flags mismatch"
    assert (uo & 0x7F) == GLYPHS[expected], "Silicon segment output mismatch"
    return result, flag, zero


def show(a, b, op=0):
    """Example: show(3, 5, 0) displays 8 on the ASIC-driven 7-segment."""
    assert 0 <= a < 16 and 0 <= b < 16 and 0 <= op < 8
    if tt is None or _manual:
        setup(False)
    tt.uio_in.value = op
    tt.ui_in.value = (b << 4) | a
    result, flag, zero = _read(a, b, op)
    print("%X %s %X -> %X  carry/borrow=%d zero=%d" %
          (a, OPS[op], b, result, flag, zero))
    return result


def opcode(op):
    """Select opcode while the board DIP switches provide A and B."""
    assert 0 <= op < 8
    if tt is None or not _manual:
        setup(True)
    tt.uio_in.value = op
    sleep_ms(1)
    value = int(tt.ui_in.value)
    result, flag, zero = _read(value & 15, value >> 4, op)
    print("%s: Y=%X carry/borrow=%d zero=%d" % (OPS[op], result, flag, zero))


def selftest():
    """Read actual silicon outputs for all 2,048 combinations."""
    setup(False)
    count = 0
    for a in range(16):
        for b in range(16):
            for op in range(8):
                tt.ui_in.value = (b << 4) | a
                tt.uio_in.value = op
                _read(a, b, op)
                count += 1
    print("PASS: %d silicon vectors" % count)
