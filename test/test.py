# SPDX-FileCopyrightText: © 2024 Garima Bajpayi
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
from cocotb.handle import Force, Release

@cocotb.test()
async def spi_slave_sevenseg_test(dut):
    """Test SPI Slave Seven Segment Display"""
    # Start SPI clock
    cocotb.start_soon(Clock(dut.ui_in[7], 10, units="us").start())
    
    # Reset
    dut.rst_n.value = 0
    await RisingEdge(dut.ui_in[7])
    dut.rst_n.value = 1
    
    async def spi_transfer(command, data):
        """Helper function to send SPI data"""
        full_data = (command << 4) | data
        for i in range(6):
            dut.ui_in[1].value = (full_data >> (5 - i)) & 1  # MOSI
            await RisingEdge(dut.ui_in[7])  # SCLK
        dut.ui_in[0].value = 1  # Deselect slave
        await RisingEdge(dut.ui_in[7])
        dut.ui_in[0].value = 0  # Select slave
    
    # Define expected outputs for valid cases
    seven_seg_map = {
        0x0: 0x3F, 0x1: 0x06, 0x2: 0x5B, 0x3: 0x4F,
        0x4: 0x66, 0x5: 0x6D, 0x6: 0x7D, 0x7: 0x07,
        0x8: 0x7F, 0x9: 0x6F, 0xA: 0x77, 0xB: 0x7C,
        0xC: 0x39, 0xD: 0x5E, 0xE: 0x79, 0xF: 0x71
    }
    
    # Test command 10: Display data
    for data in range(16):
        await spi_transfer(0b10, data)
        assert dut.uo_out.value == seven_seg_map[data], f"Failed for 10 {data:X}"
    
    # Test command 01: Display data with decimal point
    for data in range(16):
        await spi_transfer(0b01, data)
        expected_output = seven_seg_map[data] | 0x80  # Turn on decimal point
        assert dut.uo_out.value == expected_output, f"Failed for 01 {data:X}"
    
    # Test malformed commands (should turn off display)
    for command in [0b00, 0b11]:
        for data in range(16):
            await spi_transfer(command, data)
            assert dut.uo_out.value == 0x40, f"Failed for malformed {command:02b} {data:X}"

