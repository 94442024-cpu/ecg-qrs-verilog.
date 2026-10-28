`timescale 1ns/1ps
module tb_moving_avg;
    reg clk = 0, rst_n = 0, en = 0;
    reg signed [15:0] x = 0;
    wire signed [15:0] y;
    integer k;

    moving_avg #(.W(16), .LOG2N(5)) dut (.clk(clk), .rst_n(rst_n), .en(en), .x(x), .y(y));

    always #5 clk = ~clk;

    initial begin
        $dumpfile("tb_moving_avg.vcd");
        $dumpvars(0, tb_moving_avg);
        #20 rst_n = 1;

        for (k = 0; k < 40; k = k + 1) begin
            @(posedge clk); x <= 100; en <= 1;
            @(posedge clk); en <= 0;
            @(posedge clk);
            if (k == 31 && y !== 100) $display("FAIL: y=%0d at k=%0d", y, k);
        end
        if (y === 100) $display("PASS");
        $finish;
    end
endmodule
