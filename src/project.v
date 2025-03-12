/*
 * Copyright (c) 2024 Garima Bajpayi
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_gxrii_spi_sevenseg (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  spi_slave_sevenseg top(.sclk(ui_in[7]), .mosi(ui_in[1]), .ss(ui_in[0]), .rst_n(rst_n), .out(uo_out[7:0])); 

  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, uio_in[7:0], ui_in[6:2], 1'b0};

endmodule

module spi_slave_sevenseg (
    input wire sclk,
    input wire mosi,
    input wire ss,
    input wire rst_n, // Active-low reset
    output reg [7:0] out
);

    reg [5:0] shift_reg; // 6-bit shift register (2-bit command + 4-bit data)
    reg [2:0] bit_count; // Track received bits
    reg [3:0] blink_count;
    reg dp_state;
    reg [6:0] segment_data;

    always @(*) begin
        case (shift_reg[3:0])
            4'h0: segment_data = 7'b0111111;
            4'h1: segment_data = 7'b0000110;
            4'h2: segment_data = 7'b1011011;
            4'h3: segment_data = 7'b1001111;
            4'h4: segment_data = 7'b1100110;
            4'h5: segment_data = 7'b1101101;
            4'h6: segment_data = 7'b1111101;
            4'h7: segment_data = 7'b0000111;
            4'h8: segment_data = 7'b1111111;
            4'h9: segment_data = 7'b1101111;
            4'hA: segment_data = 7'b1110111;
            4'hB: segment_data = 7'b1111100;
            4'hC: segment_data = 7'b0111001;
            4'hD: segment_data = 7'b1011110;
            4'hE: segment_data = 7'b1111001;
            4'hF: segment_data = 7'b1110001;
            default: segment_data = 7'b0000000;
        endcase
    end

    always @(posedge sclk) begin
        if (!rst_n) begin
            bit_count <= 0;
            blink_count <= 0;
            dp_state <= 0;
            shift_reg <= 0;
            out <= 0;
        end else begin
            if (ss) begin
                bit_count <= 0;
            end else begin
                shift_reg <= {shift_reg[4:0], mosi};
                bit_count <= bit_count + 1;
                
                if (bit_count == 5) begin // 6th bit received
                    if (shift_reg[5:4] == 2'b10) begin // Display data
                        out[6:0] <= segment_data;
                        out[7] <= 0; // Turn off decimal point
                    end
                    else if (shift_reg[5:4] == 2'b01) begin // Blink decimal point
                        blink_count <= 4;
                        dp_state <= 1;
                    end
                end
            end
        end
    end

    always @(posedge sclk) begin
        if (!rst_n) begin
            dp_state <= 0;
            blink_count <= 0;
        end else if (blink_count > 0) begin
            dp_state <= ~dp_state;
            out[7] <= dp_state;
            blink_count <= blink_count - 1;
        end
    end

endmodule


