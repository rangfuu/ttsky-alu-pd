import cocotb
from cocotb.triggers import Timer

# Independent oracle: illuminated segments in a,b,c,d,e,f,g order.
GLYPHS = ("abcdef", "bc", "abdeg", "abcdg", "bcfg", "acdfg",
          "acdefg", "abc", "abcdefg", "abcdfg", "abcefg", "cdefg",
          "adef", "bcdeg", "adefg", "aefg")


def expected(a, b, op):
    result = ((a + b) & 15, (a - b) & 15, a & b, a | b, a ^ b,
              (a << 1) & 15, a >> 1, int(a == b))[op]
    carry = int(a + b > 15) if op == 0 else int(a < b) if op == 1 else 0
    segments = sum(1 << (ord(s) - ord("a")) for s in GLYPHS[result])
    return (carry << 7) | segments, (result << 4) | (int(result == 0) << 3)


@cocotb.test()
async def test_exhaustive_alu_display(dut):
    dut.clk.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 1
    dut.ui_in.value = 255
    dut.uio_in.value = 255
    await Timer(100, unit="ns")
    for a in range(16):
        for b in range(16):
            for op in range(8):
                dut.ui_in.value = (b << 4) | a
                dut.uio_in.value = op | (((a + b) & 31) << 3)
                await Timer(100, unit="ns")
                uo, uio = expected(a, b, op)
                context = f"A={a} B={b} op={op}"
                assert int(dut.uo_out.value) == uo, context
                assert int(dut.uio_out.value) == uio, context
                assert int(dut.uio_oe.value) == 0xF8, context
    # A combinational project does not depend on clock, reset or ena.
    for clk, reset, ena in ((1, 0, 1), (0, 1, 0), (1, 1, 1)):
        dut.clk.value = clk
        dut.rst_n.value = reset
        dut.ena.value = ena
        await Timer(100, unit="ns")
        assert int(dut.uo_out.value) == expected(15, 15, 7)[0]
        assert int(dut.uio_out.value) == expected(15, 15, 7)[1]
        assert int(dut.uio_oe.value) == 0xF8
