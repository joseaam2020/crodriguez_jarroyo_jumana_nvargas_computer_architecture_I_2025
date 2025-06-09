ADD R5, R0, 3
loop:
SUB R5, R5, 1
ADD R7, R7, R5
LOOP R5, end
LOOP R0, loop
end:
ADD R3, R0, 5
