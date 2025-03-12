# Copyright (c) 2024 Garima Bajpayi
# SPDX-License-Identifier: Apache-2.0 

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.handle import Force, Release

@cocotb.test()
async def spi_slave_sevenseg_test(dut):
    """Test SPI Slave Seven Segment Display"""
    # Start SPI clock before anything else
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Allow clock to stabilize before using RisingEdge
    await Timer(20, units="ns")
    
    # Reset
    dut.rst_n.value = 0
    await Timer(20, units="ns")  # Give reset some time
    dut.rst_n.value = 1
    await Timer(20, units="ns")  # Allow system to stabilize
    
    async def spi_transfer(command, data):
        """Helper function to send SPI data"""
        full_data = (command << 4) | data
        dut.ui_in[0].value = 0  # Select slave

        for i in range(6):
            dut.ui_in[1].value = (full_data >> (5 - i)) & 1  # Set MOSI
            await Timer(1, units="ns")  # Ensure MOSI is stable
            await RisingEdge(dut.clk)  # Clock the data in

        await Timer(1, units="ns")  # Allow processing time
        dut.ui_in[0].value = 1  # Deselect slave
        await RisingEdge(dut.clk)  # Ensure slave registers data

        # Debug print after transfer
        print(f"Sent: cmd={command:02b}, data={data:01X}, Received Output: {int(dut.uo_out.value):08b}")
    '''
    async def spi_transfer(command, data):
        """Helper function to send SPI data"""
        full_data = (command << 4) | data
        dut.ui_in[0].value = 0  # Select slave
        for i in range(6):
            dut.ui_in[1].value = (full_data >> (5 - i)) & 1  # MOSI
            await RisingEdge(dut.clk)  # SCLK
        dut.ui_in[0].value = 1  # Deselect slave
        await RisingEdge(dut.clk)
        
        # Debug print after transfer
        print(f"Sent: cmd={command:02b}, data={data:01X}, Received Output: {int(dut.uo_out.value):08b}")
    '''
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
    
    # Test malformed commands (should switch off display but keep decimal point on)
    for command in [0b00, 0b11]:
        for data in range(16):
            await spi_transfer(command, data)
            assert dut.uo_out.value == 0x80, f"Failed for malformed {command:02b} {data:X}"

