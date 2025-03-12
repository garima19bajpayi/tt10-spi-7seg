# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset and initial values
    dut._log.info("Reset")
    dut.clk.value = 0
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.ui_in.value = 1  # ui_in[0] = 1'b1
    await ClockCycles(dut.clk, 2)  # 10 time units
    dut.rst_n.value = 1
    
    await ClockCycles(dut.clk, 1)  # 10 time units
    dut.ui_in.value = 0  # ui_in[0] = 1'b0
    
    await ClockCycles(dut.clk, 1)  # 10 time units
    dut.ui_in.value = 2  # ui_in[1] = 1'b1
    
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0  # ui_in[1] = 1'b0
    
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 2  # ui_in[1] = 1'b1
    
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 2  # ui_in[1] = 1'b1
    
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0  # ui_in[1] = 1'b0
    
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 2  # ui_in[1] = 1'b1
    
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 1  # ui_in[0] = 1'b1
    
    await ClockCycles(dut.clk, 2)
    
    # Assertion to check if out[7:0] is 0x5E
    assert dut.uo_out.value == 0x5E, f"Test failed: Expected 0x5E, got {hex(dut.uo_out.value)}"
    dut._log.info("Test complete")
    await cocotb.triggers.Timer(1, units='ns')  # Small delay before finishing
 
