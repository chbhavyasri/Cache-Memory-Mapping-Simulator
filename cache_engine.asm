; CACHE MEMORY MAPPING EMULATOR

#make_COM#
ORG 100H

START:
    ; 1. Print Banner
    LEA DX, TITLE_MSG
    MOV AH, 09H
    INT 21H

    LEA SI, TRACE
    MOV CX, TRACE_LEN

TRACE_LOOP:
    PUSH CX
    MOV AX, [SI]
    MOV CURR_ADDR, AX

    ; --- Bit Slicing ---
    ; 1. Offset Bits (Bits 0-2 -> Mask 0007h)
    MOV AX, CURR_ADDR
    AND AX, 0007H
    MOV CURR_OFF, AX

    ; 2. Set Index Bits (Bits 3-5 -> Shift 3, Mask 0007h)
    MOV AX, CURR_ADDR
    SHR AX, 1
    SHR AX, 1
    SHR AX, 1
    AND AX, 0007H
    MOV CURR_SET, AX

    ; 3. Tag Bits (Bits 6-15 -> Shift 6)
    MOV AX, CURR_ADDR
    MOV CL, 6
    SHR AX, CL
    MOV CURR_TAG, AX

    ; --- Print Cycle Trace Line ---
    LEA DX, ADDR_MSG
    MOV AH, 09H
    INT 21H
    MOV AX, CURR_ADDR
    CALL PRINT_HEX

    LEA DX, TAG_MSG
    MOV AH, 09H
    INT 21H
    MOV AX, CURR_TAG
    CALL PRINT_HEX

    LEA DX, SET_MSG
    MOV AH, 09H
    INT 21H
    MOV AX, CURR_SET
    ADD AL, '0'
    MOV DL, AL
    MOV AH, 02H
    INT 21H

    LEA DX, OFF_MSG
    MOV AH, 09H
    INT 21H
    MOV AX, CURR_OFF
    ADD AL, '0'
    MOV DL, AL
    MOV AH, 02H
    INT 21H

    ; --- Hardware Lookup ---
    MOV BX, CURR_SET
    CMP VALID_ARRAY[BX], 1
    JNE CACHE_MISS

    MOV DI, BX
    SHL DI, 1
    MOV AX, CURR_TAG
    CMP TAG_ARRAY[DI], AX
    JNE CACHE_MISS

    ; Hit Branch
    INC HIT_COUNT
    LEA DX, HIT_MSG
    MOV AH, 09H
    INT 21H
    JMP NEXT_CYCLE

CACHE_MISS:
    ; Miss Branch (Allocate line)
    INC MISS_COUNT
    MOV VALID_ARRAY[BX], 1
    MOV DI, BX
    SHL DI, 1
    MOV AX, CURR_TAG
    MOV TAG_ARRAY[DI], AX

    LEA DX, MISS_MSG
    MOV AH, 09H
    INT 21H

NEXT_CYCLE:
    ADD SI, 2
    POP CX
    DEC CX
    JNZ TRACE_LOOP

    ; PERFORMANCE METRICS & HIT RATIO REPORT
    LEA DX, STATS_HDR
    MOV AH, 09H
    INT 21H

    LEA DX, TOTAL_MSG
    MOV AH, 09H
    INT 21H
    MOV AX, TRACE_LEN
    CALL PRINT_DEC

    LEA DX, HITS_MSG
    MOV AH, 09H
    INT 21H
    MOV AX, HIT_COUNT
    CALL PRINT_DEC

    LEA DX, MISS_MSG_STAT
    MOV AH, 09H
    INT 21H
    MOV AX, MISS_COUNT
    CALL PRINT_DEC

    LEA DX, RATE_MSG
    MOV AH, 09H
    INT 21H
    MOV AX, HIT_COUNT
    MOV BX, 100
    MUL BX
    MOV BX, TRACE_LEN
    DIV BX
    CALL PRINT_DEC
    MOV DL, '%'
    MOV AH, 02H
    INT 21H

    ; Pause
    LEA DX, END_MSG
    MOV AH, 09H
    INT 21H

    MOV AH, 01H
    INT 21H
    RET

; ------------------------------------------------------------------------------
; HELPER: PRINT AX IN HEXADECIMAL (4 DIGITS)
; ------------------------------------------------------------------------------
PRINT_HEX PROC
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    MOV BX, AX
    MOV CX, 4
HEX_LOOP:
    ROL BX, 1
    ROL BX, 1
    ROL BX, 1
    ROL BX, 1
    MOV DL, BL
    AND DL, 0FH
    CMP DL, 9
    JBE NUM_CHAR
    ADD DL, 7
NUM_CHAR:
    ADD DL, '0'
    MOV AH, 02H
    INT 21H
    LOOP HEX_LOOP
    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_HEX ENDP

; ------------------------------------------------------------------------------
; HELPER: PRINT AX IN DECIMAL
; ------------------------------------------------------------------------------
PRINT_DEC PROC
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    MOV CX, 0
    MOV BX, 10
DEC_DIV:
    MOV DX, 0
    DIV BX
    PUSH DX
    INC CX
    CMP AX, 0
    JNE DEC_DIV
DEC_PRINT:
    POP DX
    ADD DL, '0'
    MOV AH, 02H
    INT 21H
    LOOP DEC_PRINT
    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_DEC ENDP

; ------------------------------------------------------------------------------
; DATA STORAGE
; ------------------------------------------------------------------------------
TITLE_MSG       DB '', 0DH, 0AH
                DB '8086 HARDWARE CACHE ARCHITECTURE SIMULATOR      ', 0DH, 0AH
                DB '', 0DH, 0AH, '$'
ADDR_MSG        DB 0DH, 0AH, 'Address: 0x', '$'
TAG_MSG         DB ' | Tag: 0x', '$'
SET_MSG         DB ' | Set: ', '$'
OFF_MSG         DB ' | Offset: ', '$'
HIT_MSG         DB ' -> [ HIT  ]', '$'
MISS_MSG        DB ' -> [ MISS ]', '$'

STATS_HDR       DB 0DH, 0AH, 0DH, 0AH, '--- PERFORMANCE METRICS ---', 0DH, 0AH, '$'
TOTAL_MSG       DB '  Total Accesses : ', '$'
HITS_MSG        DB 0DH, 0AH, '  Total Hits     : ', '$'
MISS_MSG_STAT   DB 0DH, 0AH, '  Total Misses   : ', '$'
RATE_MSG        DB 0DH, 0AH, '  Hit Ratio      : ', '$'
END_MSG         DB 0DH, 0AH, 0DH, 0AH, 'Press any key to exit...', '$'

; Benchmark Address Stream
TRACE           DW 0000H, 0004H, 0040H, 0000H, 0080H
TRACE_LEN       EQU 5

; Hardware Array
VALID_ARRAY     DB 8 DUP(0)
TAG_ARRAY       DW 8 DUP(0)

HIT_COUNT       DW 0
MISS_COUNT      DW 0

CURR_ADDR       DW 0
CURR_TAG        DW 0
CURR_SET        DW 0
CURR_OFF        DW 0