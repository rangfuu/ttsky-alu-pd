import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer

async def drive(dut, a, b, op):
    dut.ui_in.value = ((b & 0xF) << 4) | (a & 0xF)
    dut.uio_in.value = op & 0x7
    await Timer(1, unit="ns")
    return int(dut.uo_out.value)

@cocotb.test()
async def test_alu(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.ena.value = 1
    dut.rst_n.value = 1

    y = await drive(dut, 3, 5, 0)
    assert (y & 0xF) == 8

    y = await drive(dut, 9, 4, 1)
    assert (y & 0xF) == 5

    y = await drive(dut, 0xA, 0xC, 2)
    assert (y & 0xF) == 0x8

    y = await drive(dut, 0xA, 0x5, 3)
    assert (y & 0xF) == 0xF

    y = await drive(dut, 0xA, 0x5, 4)
    assert (y & 0xF) == 0xF

    y = await drive(dut, 3, 0, 5)
    assert (y & 0xF) == 6

    y = await drive(dut, 8, 0, 6)
    assert (y & 0xF) == 4

    y = await drive(dut, 7, 7, 7)
    assert (y & 0xF) == 1

    y = await drive(dut, 0, 0, 2)
    assert ((y >> 5) & 1) == 1
