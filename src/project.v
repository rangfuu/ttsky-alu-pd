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

    // TT demo board: active-high segments, bit 0=a through bit 6=g.
    reg [6:0] segments;
    always @(*) begin
        case (result)
            4'h0: segments = 7'h3f;
            4'h1: segments = 7'h06;
            4'h2: segments = 7'h5b;
            4'h3: segments = 7'h4f;
            4'h4: segments = 7'h66;
            4'h5: segments = 7'h6d;
            4'h6: segments = 7'h7d;
            4'h7: segments = 7'h07;
            4'h8: segments = 7'h7f;
            4'h9: segments = 7'h6f;
            4'ha: segments = 7'h77;
            4'hb: segments = 7'h7c;
            4'hc: segments = 7'h39;
            4'hd: segments = 7'h5e;
            4'he: segments = 7'h79;
            4'hf: segments = 7'h71;
            default: segments = 7'h00;
        endcase
    end
    // Decimal point means ADD carry or SUB borrow; shifts leave it off.
    assign uo_out = {carry, segments};
    // Retain binary observability for board-level exhaustive testing.
    assign uio_out = {result, (result == 4'b0000), 3'b000};
    assign uio_oe  = 8'b11111000;

    wire _unused = &{ena, clk, rst_n, uio_in[7:3], 1'b0};

endmodule

`default_nettype wire
