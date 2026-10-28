module moving_avg #(
    parameter W    = 16,
    parameter LOG2N = 5
)(
    input  wire                clk,
    input  wire                rst_n,
    input  wire                en,
    input  wire signed [W-1:0] x,
    output reg  signed [W-1:0] y
);
    localparam N = 1 << LOG2N;

    reg signed [W-1:0]        dly [0:N-1];
    reg signed [W+LOG2N-1:0]  sum;
    wire signed [W+LOG2N-1:0] sum_next = sum + x - dly[N-1];
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sum <= 0;
            y   <= 0;
            for (i = 0; i < N; i = i + 1) dly[i] <= 0;
        end else if (en) begin
            sum <= sum_next;
            y   <= sum_next >>> LOG2N;
            for (i = N-1; i > 0; i = i - 1) dly[i] <= dly[i-1];
            dly[0] <= x;
        end
    end
endmodule
