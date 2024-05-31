# Testing


We include the RISC-V ISA tests compiled binaries (compiled on 20/5/2024) to test the ISS.

To run them do

```
 python  tb_ISA_tests.py -c "runAllTests()"
```

Currently, we do not check all the tests. We do not run the rv32 tests, and we also bypass the vector instructions tests.
Moreover, not all tests pass. The current output is:

```
Test rv64mi-p-ma_addr               = OK
Test rv64mi-p-sh-misaligned         = OK
Test rv64mi-p-scall                 = OK
Test rv64mi-p-sbreak                = FAILED - Test return value = 5
Test rv64mi-p-sd-misaligned         = OK
Test rv64mi-p-lh-misaligned         = OK
Test rv64mi-p-csr                   = OK
Test rv64mi-p-zicntr                = OK
Test rv64mi-p-illegal               = FAILED - Test return value = 0
Test rv64mi-p-ld-misaligned         = OK
Test rv64mi-p-sw-misaligned         = OK
Test rv64mi-p-mcsr                  = OK
Test rv64mi-p-ma_fetch              = OK
Test rv64mi-p-breakpoint            = FAILED - Test return value = 5
Test rv64mi-p-lw-misaligned         = OK
Test rv64mi-p-access                = FAILED - Test return value = 5
Test rv64si-p-dirty                 = FAILED - Test return value = 0
Test rv64si-p-ma_fetch              = OK
Test rv64si-p-csr                   = OK
Test rv64si-p-sbreak                = FAILED - Test return value = 5
Test rv64si-p-scall                 = OK
Test rv64si-p-wfi                   = OK
Test rv64si-p-icache-alias          = FAILED - Test return value = 0
Test rv64ssvnapot-p-napot           = FAILED - Test return value = 0
Test rv64ua-p-amoswap_w             = OK
Test rv64ua-p-amoor_w               = OK
Test rv64ua-p-amoxor_w              = OK
Test rv64ua-p-amomax_d              = OK
Test rv64ua-p-amoadd_w              = OK
Test rv64ua-p-amomin_w              = OK
Test rv64ua-p-amoor_d               = OK
Test rv64ua-p-amomaxu_d             = OK
Test rv64ua-p-amoand_d              = OK
Test rv64ua-p-amoadd_d              = OK
Test rv64ua-p-amominu_w             = OK
Test rv64ua-p-amoswap_d             = OK
Test rv64ua-p-amomin_d              = OK
Test rv64ua-p-amomaxu_w             = OK
Test rv64ua-p-amoand_w              = OK
Test rv64ua-p-amominu_d             = OK
Test rv64ua-p-amomax_w              = OK
Test rv64ua-p-lrsc                  = FAILED - Test return value = 5
Test rv64ua-p-amoxor_d              = OK
Test rv64uc-p-rvc                   = OK
Test rv64ud-p-fmadd                 = OK
Test rv64ud-p-fmin                  = OK
Test rv64ud-p-fadd                  = OK
Test rv64ud-p-fcmp                  = OK
Test rv64ud-p-ldst                  = OK
Test rv64ud-p-fclass                = OK
Test rv64ud-p-fcvt_w                = OK
Test rv64ud-p-structural            = OK
Test rv64ud-p-fdiv                  = FAILED - Test return value = 5
Test rv64ud-p-recoding              = OK
Test rv64ud-p-fcvt                  = FAILED - Test return value = 25
Test rv64ud-p-move                  = OK
Test rv64uf-p-fcmp                  = OK
Test rv64uf-p-move                  = FAILED - Test return value = 41
Test rv64uf-p-fadd                  = FAILED - Test return value = 7
Test rv64uf-p-fdiv                  = FAILED - Test return value = 5
Test rv64uf-p-recoding              = FAILED - Test return value = 11
Test rv64uf-p-fcvt                  = OK
Test rv64uf-p-fclass                = FAILED - Test return value = 5
Test rv64uf-p-fmadd                 = FAILED - Test return value = 5
Test rv64uf-p-ldst                  = OK
Test rv64uf-p-fmin                  = OK
Test rv64uf-p-fcvt_w                = OK
Test rv64ui-p-srai                  = OK
Test rv64ui-p-add                   = OK
Test rv64ui-p-sub                   = OK
Test rv64ui-p-or                    = OK
Test rv64ui-p-sllw                  = OK
Test rv64ui-p-srli                  = OK
Test rv64ui-p-sltiu                 = OK
Test rv64ui-p-sra                   = OK
Test rv64ui-p-slli                  = OK
Test rv64ui-p-lwu                   = OK
Test rv64ui-p-xori                  = OK
Test rv64ui-p-simple                = OK
Test rv64ui-p-xor                   = OK
Test rv64ui-p-srl                   = OK
Test rv64ui-p-srlw                  = OK
Test rv64ui-p-ld                    = OK
Test rv64ui-p-auipc                 = OK
Test rv64ui-p-ori                   = OK
Test rv64ui-p-bge                   = OK
Test rv64ui-p-sraw                  = OK
Test rv64ui-p-andi                  = OK
Test rv64ui-p-jal                   = OK
Test rv64ui-p-slt                   = OK
Test rv64ui-p-ma_data               = OK
Test rv64ui-p-blt                   = OK
Test rv64ui-p-lui                   = OK
Test rv64ui-p-slliw                 = OK
Test rv64ui-p-addw                  = OK
Test rv64ui-p-lh                    = OK
Test rv64ui-p-sltu                  = OK
Test rv64ui-p-bltu                  = OK
Test rv64ui-p-bgeu                  = OK
Test rv64ui-p-sd                    = OK
Test rv64ui-p-lw                    = OK
Test rv64ui-p-fence_i               = OK
Test rv64ui-p-beq                   = OK
Test rv64ui-p-sb                    = OK
Test rv64ui-p-lbu                   = OK
Test rv64ui-p-lb                    = OK
Test rv64ui-p-lhu                   = OK
Test rv64ui-p-sh                    = OK
Test rv64ui-p-srliw                 = OK
Test rv64ui-p-sraiw                 = OK
Test rv64ui-p-sw                    = OK
Test rv64ui-p-bne                   = OK
Test rv64ui-p-slti                  = OK
Test rv64ui-p-and                   = OK
Test rv64ui-p-jalr                  = OK
Test rv64ui-p-subw                  = OK
Test rv64ui-p-addiw                 = OK
Test rv64ui-p-addi                  = OK
Test rv64ui-p-sll                   = OK
Test rv64um-p-mulhsu                = OK
Test rv64um-p-div                   = OK
Test rv64um-p-mulw                  = OK
Test rv64um-p-mulhu                 = OK
Test rv64um-p-remu                  = OK
Test rv64um-p-remw                  = OK
Test rv64um-p-divu                  = OK
Test rv64um-p-divuw                 = OK
Test rv64um-p-remuw                 = OK
Test rv64um-p-divw                  = OK
Test rv64um-p-mul                   = OK
Test rv64um-p-mulh                  = OK
Test rv64um-p-rem                   = OK
Test rv64uzba-p-sh1add_uw           = FAILED - SH1ADD.UW - Not supported!
Test rv64uzba-p-sh1add              = FAILED - SH1ADD - Not supported!
Test rv64uzba-p-sh3add_uw           = FAILED - SH3ADD.UW - Not supported!
Test rv64uzba-p-sh2add              = FAILED - SH2ADD - Not supported!
Test rv64uzba-p-add_uw              = FAILED - ADD.UW - Not supported!
Test rv64uzba-p-sh3add              = FAILED - SH3ADD - Not supported!
Test rv64uzba-p-sh2add_uw           = FAILED - SH2ADD.UW - Not supported!
Test rv64uzba-p-slli_uw             = FAILED - SLLI.UW - Not supported!
Test rv64uzbb-p-maxu                = OK
Test rv64uzbb-p-ctzw                = OK
Test rv64uzbb-p-clz                 = OK
Test rv64uzbb-p-rolw                = FAILED - ROLW - Not supported!
Test rv64uzbb-p-ror                 = FAILED - ROR - Not supported!
Test rv64uzbb-p-andn                = FAILED - ANDN - R-Type instruction not supported!
Test rv64uzbb-p-sext_h              = OK
Test rv64uzbb-p-orn                 = FAILED - ORN - Not supported!
Test rv64uzbb-p-cpop                = OK
Test rv64uzbb-p-clzw                = OK
Test rv64uzbb-p-minu                = OK
Test rv64uzbb-p-orc_b               = FAILED - GORCI - Not supported!
Test rv64uzbb-p-max                 = OK
Test rv64uzbb-p-rori                = FAILED - RORI - Not supported!
Test rv64uzbb-p-min                 = OK
Test rv64uzbb-p-cpopw               = OK
Test rv64uzbb-p-xnor                = FAILED - XNOR - Not supported!
Test rv64uzbb-p-rol                 = FAILED - ROL - Not supported!
Test rv64uzbb-p-zext_h              = FAILED - PACKW - R-Type instruction not supported!
Test rv64uzbb-p-rev8                = FAILED - GREVI - Not supported!
Test rv64uzbb-p-roriw               = FAILED - RORIW - Not supported!
Test rv64uzbb-p-ctz                 = OK
Test rv64uzbb-p-rorw                = FAILED - RORW - Not supported!
Test rv64uzbb-p-sext_b              = OK
Test rv64uzbc-p-clmulr              = FAILED - CLMULR - Not supported!
Test rv64uzbc-p-clmulh              = FAILED - CLMULH - Not supported!
Test rv64uzbc-p-clmul               = FAILED - CLMUL - Not supported!
Test rv64uzbs-p-bext                = OK
Test rv64uzbs-p-bexti               = OK
Test rv64uzbs-p-bclri               = OK
Test rv64uzbs-p-bclr                = OK
Test rv64uzbs-p-binv                = OK
Test rv64uzbs-p-bset                = OK
Test rv64uzbs-p-binvi               = OK
Test rv64uzbs-p-bseti               = OK
Test rv64uzfh-p-move                = FAILED - Unknown opcode 1010011 func3 000 func7 1111010 rs2 0000 full f40580d3
Test rv64uzfh-p-ldst                = FAILED - Unknown opcode 0000111 func3 001 func7 0000000 rs2 0100 full 00459087
Test rv64uzfh-p-fcvt_w              = FAILED - Unknown opcode 0000111 func3 001 func7 0000000 rs2 0000 full 00051007
Test rv64uzfh-p-fdiv                = FAILED - Unknown opcode 0000111 func3 001 func7 0000000 rs2 0000 full 00051007
Test rv64uzfh-p-fclass              = FAILED - Unknown opcode 1010011 func3 000 func7 1111010 rs2 0000 full f4050553
Test rv64uzfh-p-fcvt                = FAILED - Unknown opcode 1010011 func3 111 func7 1101010 rs2 0000 full d4057053
Test rv64uzfh-p-recoding            = FAILED - Test return value = 11
Test rv64uzfh-p-fcmp                = FAILED - Unknown opcode 0000111 func3 001 func7 0000000 rs2 0000 full 00051007
Test rv64uzfh-p-fmin                = FAILED - Unknown opcode 0000111 func3 001 func7 0000000 rs2 0000 full 00051007
Test rv64uzfh-p-fmadd               = FAILED - Unknown opcode 0000111 func3 001 func7 0000000 rs2 0000 full 00051007
Test rv64uzfh-p-fadd                = FAILED - Unknown opcode 0000111 func3 001 func7 0000000 rs2 0000 full 00051007
Total: 186 Correct: 135 (72.6 %)
```

