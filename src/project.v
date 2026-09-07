`default_nettype none

module tt_um_rangfuu_alu (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    wire [3:0] a = ui_in[3:0];
    wire [3:0] b = ui_in[7:4];
    wire [2:0] op = uio_in[2:0];

    reg [3:0] result;
    reg carry;

    always @(*) begin
        result = 4'b0000;
        carry = 1'b0;

        case (op)
            3'b000: {carry, result} = {1'b0, a} + {1'b0, b};
            3'b001: {carry, result} = {1'b0, a} - {1'b0, b};
            3'b010: result = a & b;
            3'b011: result = a | b;
            3'b100: result = a ^ b;
            3'b101: result = a << 1;
            3'b110: result = a >> 1;
            3'b111: result = (a == b) ? 4'b0001 : 4'b0000;
            default: begin
                result = 4'b0000;
                carry = 1'b0;
            end
        endcase
    end

    assign uo_out[3:0] = result;
    assign uo_out[4] = carry;
    assign uo_out[5] = (result == 4'b0000);
    assign uo_out[7:6] = 2'b00;

    assign uio_out = 8'b00000000;
    assign uio_oe  = 8'b00000000;

    wire _unused = &{ena, clk, rst_n, uio_in[7:3], 1'b0};

endmodule

`default_nettype wire
