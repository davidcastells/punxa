# Testing


We include the RISC-V ISA tests compiled binaries (compiled on 20/5/2024) to test the ISS.

To run them do

```
 python  tb_ISA_tests.py -c "runAllTests()"
```

Currently, we do not check all the tests. We do not run the rv32 tests, and we also bypass the vector instructions tests.
Moreover, not all tests pass. The current output is:

```
Test rv64mi-p-access                = FAILED - Test return value = 5
Test rv64mi-p-breakpoint            = FAILED - Test return value = 5
Test rv64mi-p-csr                   = OK
Test rv64mi-p-illegal               = FAILED - Test return value = 0
Test rv64mi-p-ld-misaligned         = OK
Test rv64mi-p-lh-misaligned         = OK
Test rv64mi-p-lw-misaligned         = OK
Test rv64mi-p-ma_addr               = OK
Test rv64mi-p-ma_fetch              = OK
Test rv64mi-p-mcsr                  = OK
Test rv64mi-p-sbreak                = FAILED - Test return value = 5
Test rv64mi-p-scall                 = OK
Test rv64mi-p-sd-misaligned         = OK
Test rv64mi-p-sh-misaligned         = OK
Test rv64mi-p-sw-misaligned         = OK
Test rv64mi-p-zicntr                = OK
Test rv64si-p-csr                   = OK
Test rv64si-p-dirty                 = FAILED - Test return value = 0
Test rv64si-p-icache-alias          = FAILED - Test return value = 0
Test rv64si-p-ma_fetch              = OK
Test rv64si-p-sbreak                = FAILED - Test return value = 5
Test rv64si-p-scall                 = OK
Test rv64si-p-wfi                   = OK
Test rv64ssvnapot-p-napot           = FAILED - Test return value = 0
Test rv64ua-p-amoadd_d              = OK
Test rv64ua-p-amoadd_w              = OK
Test rv64ua-p-amoand_d              = OK
Test rv64ua-p-amoand_w              = OK
Test rv64ua-p-amomaxu_d             = OK
Test rv64ua-p-amomaxu_w             = OK
Test rv64ua-p-amomax_d              = OK
Test rv64ua-p-amomax_w              = OK
Test rv64ua-p-amominu_d             = OK
Test rv64ua-p-amominu_w             = OK
Test rv64ua-p-amomin_d              = OK
Test rv64ua-p-amomin_w              = OK
Test rv64ua-p-amoor_d               = OK
Test rv64ua-p-amoor_w               = OK
Test rv64ua-p-amoswap_d             = OK
Test rv64ua-p-amoswap_w             = OK
Test rv64ua-p-amoxor_d              = OK
Test rv64ua-p-amoxor_w              = OK
Test rv64ua-p-lrsc                  = FAILED - Test return value = 5
Test rv64uc-p-rvc                   = OK
Test rv64ud-p-fadd                  = OK
Test rv64ud-p-fclass                = OK
Test rv64ud-p-fcmp                  = OK
Test rv64ud-p-fcvt                  = FAILED - Test return value = 25
Test rv64ud-p-fcvt_w                = OK
Test rv64ud-p-fdiv                  = FAILED - Test return value = 5
Test rv64ud-p-fmadd                 = OK
Test rv64ud-p-fmin                  = OK
Test rv64ud-p-ldst                  = OK
Test rv64ud-p-move                  = OK
Test rv64ud-p-recoding              = OK
Test rv64ud-p-structural            = OK
Test rv64uf-p-fadd                  = FAILED - Test return value = 7
Test rv64uf-p-fclass                = FAILED - Test return value = 5
Test rv64uf-p-fcmp                  = OK
Test rv64uf-p-fcvt                  = OK
Test rv64uf-p-fcvt_w                = OK
Test rv64uf-p-fdiv                  = FAILED - Test return value = 5
Test rv64uf-p-fmadd                 = FAILED - Test return value = 5
Test rv64uf-p-fmin                  = OK
Test rv64uf-p-ldst                  = OK
Test rv64uf-p-move                  = OK
Test rv64uf-p-recoding              = FAILED - Test return value = 11
Test rv64ui-p-add                   = OK
Test rv64ui-p-addi                  = OK
Test rv64ui-p-addiw                 = OK
Test rv64ui-p-addw                  = OK
Test rv64ui-p-and                   = OK
Test rv64ui-p-andi                  = OK
Test rv64ui-p-auipc                 = OK
Test rv64ui-p-beq                   = OK
Test rv64ui-p-bge                   = OK
Test rv64ui-p-bgeu                  = OK
Test rv64ui-p-blt                   = OK
Test rv64ui-p-bltu                  = OK
Test rv64ui-p-bne                   = OK
Test rv64ui-p-fence_i               = OK
Test rv64ui-p-jal                   = OK
Test rv64ui-p-jalr                  = OK
Test rv64ui-p-lb                    = OK
Test rv64ui-p-lbu                   = OK
Test rv64ui-p-ld                    = OK
Test rv64ui-p-lh                    = OK
Test rv64ui-p-lhu                   = OK
Test rv64ui-p-lui                   = OK
Test rv64ui-p-lw                    = OK
Test rv64ui-p-lwu                   = OK
Test rv64ui-p-ma_data               = OK
Test rv64ui-p-or                    = OK
Test rv64ui-p-ori                   = OK
Test rv64ui-p-sb                    = OK
Test rv64ui-p-sd                    = OK
Test rv64ui-p-sh                    = OK
Test rv64ui-p-simple                = OK
Test rv64ui-p-sll                   = OK
Test rv64ui-p-slli                  = OK
Test rv64ui-p-slliw                 = OK
Test rv64ui-p-sllw                  = OK
Test rv64ui-p-slt                   = OK
Test rv64ui-p-slti                  = OK
Test rv64ui-p-sltiu                 = OK
Test rv64ui-p-sltu                  = OK
Test rv64ui-p-sra                   = OK
Test rv64ui-p-srai                  = OK
Test rv64ui-p-sraiw                 = OK
Test rv64ui-p-sraw                  = OK
Test rv64ui-p-srl                   = OK
Test rv64ui-p-srli                  = OK
Test rv64ui-p-srliw                 = OK
Test rv64ui-p-srlw                  = OK
Test rv64ui-p-sub                   = OK
Test rv64ui-p-subw                  = OK
Test rv64ui-p-sw                    = OK
Test rv64ui-p-xor                   = OK
Test rv64ui-p-xori                  = OK
Test rv64um-p-div                   = OK
Test rv64um-p-divu                  = OK
Test rv64um-p-divuw                 = OK
Test rv64um-p-divw                  = OK
Test rv64um-p-mul                   = OK
Test rv64um-p-mulh                  = OK
Test rv64um-p-mulhsu                = OK
Test rv64um-p-mulhu                 = OK
Test rv64um-p-mulw                  = OK
Test rv64um-p-rem                   = OK
Test rv64um-p-remu                  = OK
Test rv64um-p-remuw                 = OK
Test rv64um-p-remw                  = OK
Test rv64uzba-p-add_uw              = OK
Test rv64uzba-p-sh1add              = OK
Test rv64uzba-p-sh1add_uw           = OK
Test rv64uzba-p-sh2add              = OK
Test rv64uzba-p-sh2add_uw           = OK
Test rv64uzba-p-sh3add              = OK
Test rv64uzba-p-sh3add_uw           = OK
Test rv64uzba-p-slli_uw             = OK
Test rv64uzbb-p-andn                = OK
Test rv64uzbb-p-clz                 = OK
Test rv64uzbb-p-clzw                = OK
Test rv64uzbb-p-cpop                = OK
Test rv64uzbb-p-cpopw               = OK
Test rv64uzbb-p-ctz                 = OK
Test rv64uzbb-p-ctzw                = OK
Test rv64uzbb-p-max                 = OK
Test rv64uzbb-p-maxu                = OK
Test rv64uzbb-p-min                 = OK
Test rv64uzbb-p-minu                = OK
Test rv64uzbb-p-orc_b               = OK
Test rv64uzbb-p-orn                 = FAILED - Test return value = 5
Test rv64uzbb-p-rev8                = OK
Test rv64uzbb-p-rol                 = OK
Test rv64uzbb-p-rolw                = OK
Test rv64uzbb-p-ror                 = OK
Test rv64uzbb-p-rori                = OK
Test rv64uzbb-p-roriw               = OK
Test rv64uzbb-p-rorw                = OK
Test rv64uzbb-p-sext_b              = OK
Test rv64uzbb-p-sext_h              = OK
Test rv64uzbb-p-xnor                = OK
Test rv64uzbb-p-zext_h              = FAILED - Test return value = 11
Test rv64uzbc-p-clmul               = FAILED - Test return value = 65
Test rv64uzbc-p-clmulh              = FAILED - Test return value = 7
Test rv64uzbc-p-clmulr              = FAILED - Test return value = 65
Test rv64uzbs-p-bclr                = OK
Test rv64uzbs-p-bclri               = OK
Test rv64uzbs-p-bext                = OK
Test rv64uzbs-p-bexti               = OK
Test rv64uzbs-p-binv                = OK
Test rv64uzbs-p-binvi               = OK
Test rv64uzbs-p-bset                = OK
Test rv64uzbs-p-bseti               = OK
Test rv64uzfh-p-fadd                = FAILED - Test return value = 5
Test rv64uzfh-p-fclass              = FAILED - Test return value = 5
Test rv64uzfh-p-fcmp                = FAILED - Test return value = 5
Test rv64uzfh-p-fcvt                = FAILED - Test return value = 5
Test rv64uzfh-p-fcvt_w              = FAILED - Test return value = 5
Test rv64uzfh-p-fdiv                = FAILED - Test return value = 5
Test rv64uzfh-p-fmadd               = FAILED - Test return value = 5
Test rv64uzfh-p-fmin                = FAILED - Test return value = 7
Test rv64uzfh-p-ldst                = FAILED - Test return value = 0
Test rv64uzfh-p-move                = OK
Test rv64uzfh-p-recoding            = FAILED - Test return value = 11
Total: 186 Correct: 155 (83.3 %)
```

