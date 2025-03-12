# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.triggers import FallingEdge, Timer
from cocotb.clock import Clock

async def spi_transfer(dut, command, data):
    """ Helper function to send a 6-bit SPI command (2-bit command + 4-bit data) """
    bits = (command << 4) | data
    for i in range(6):
        dut.ui_in[1].value = (bits >> (5 - i)) & 1  # Set MOSI
        await FallingEdge(dut.ui_in[7])  # Wait for clock edge

@cocotb.test()
async def test_spi_sevenseg(dut):
    """ Testbench for SPI slave seven-segment display """
    dut._log.info("Starting testbench")
    
    # Generate a clock on SCLK (ui_in[7])
    cocotb.start_soon(Clock(dut.ui_in[7], 10, units="ns").start())
    dut._log.info("Reset")
    dut.ena.value = 1
    #dut.ui_in[6:0].value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0  # Reset active
    await Timer(20, units="ns")
    dut.rst_n.value = 1  # Release reset
    await Timer(20, units="ns")
    
    # Test all 16 possible 4-bit values for command 10 (display data)
    for data in range(16):
        dut.ui_in[0].value = 0  # Activate SS
        await spi_transfer(dut, 0b10, data)
        dut.ui_in[0].value = 1  # Deactivate SS
        await Timer(20, units="ns")
        expected_output = dut.spi_slave_sevenseg.segment_data.value | (0 << 7)
        assert dut.uo_out.value == expected_output, f"Failed for data {data}" 

    # Test blinking command 01
    dut.ui_in[0].value = 0  # Activate SS
    await spi_transfer(dut, 0b01, 0x0)
    dut.ui_in[0].value = 1  # Deactivate SS
    await Timer(20, units="ns")
    
    for _ in range(4):
        await FallingEdge(dut.ui_in[7])  # Wait for clock edge
        assert dut.uo_out[7].value == 1, "Blinking DP failed (should be 1)"
        await FallingEdge(dut.ui_in[7])
        assert dut.uo_out[7].value == 0, "Blinking DP failed (should be 0)"

    dut._log.info("Testbench completed successfully")
