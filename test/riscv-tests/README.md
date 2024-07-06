# Testing of RISC-V Tests


We include the RISC-V ISA tests compiled binaries (compiled on 20/5/2024) to test the ISS.

To run them do

```
 python  tb_ISA_tests.py -c "runAllTests()"
```

Currently, we still have issues with virtual memory.
We do not run the rv32 tests.

***Summary***

<pre>
rv64mi-p        93.8 %   |███████████████████████████████████████████░░|
rv64mzicbo-p    0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64si-p        85.7 %   |███████████████████████████████████████░░░░░░|
rv64ssvnapot-p  0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ua-p        100.0 %  |█████████████████████████████████████████████|
rv64ua-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uc-p        100.0 %  |█████████████████████████████████████████████|
rv64uc-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ud-p        100.0 %  |█████████████████████████████████████████████|
rv64ud-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uf-p        100.0 %  |█████████████████████████████████████████████|
rv64uf-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ui-p        100.0 %  |█████████████████████████████████████████████|
rv64ui-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64um-p        100.0 %  |█████████████████████████████████████████████|
rv64um-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzba-p      100.0 %  |█████████████████████████████████████████████|
rv64uzba-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbb-p      100.0 %  |█████████████████████████████████████████████|
rv64uzbb-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbc-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbc-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbs-p      100.0 %  |█████████████████████████████████████████████|
rv64uzbs-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzfh-p      100.0 %  |█████████████████████████████████████████████|
rv64uzfh-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|</pre>

The detailed current output is:

```
Test rv64mi-p-access                = OK
Test rv64mi-p-breakpoint            = FAILED - Test return value = 5
Test rv64mi-p-csr                   = OK
Test rv64mi-p-illegal               = OK
Test rv64mi-p-ld-misaligned         = OK
Test rv64mi-p-lh-misaligned         = OK
Test rv64mi-p-lw-misaligned         = OK
Test rv64mi-p-ma_addr               = OK
Test rv64mi-p-ma_fetch              = OK
Test rv64mi-p-mcsr                  = OK
Test rv64mi-p-sbreak                = OK
Test rv64mi-p-scall                 = OK
Test rv64mi-p-sd-misaligned         = OK
Test rv64mi-p-sh-misaligned         = OK
Test rv64mi-p-sw-misaligned         = OK
Test rv64mi-p-zicntr                = OK
Test rv64mzicbo-p-zero              = FAILED - Test return value = 3
Test rv64si-p-csr                   = OK
Test rv64si-p-dirty                 = OK
Test rv64si-p-icache-alias          = FAILED - Test return value = 5
Test rv64si-p-ma_fetch              = OK
Test rv64si-p-sbreak                = OK
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
Test rv64ua-p-lrsc                  = OK
Test rv64ua-v-amoadd_d              = FAILED - Test return value = 0
Test rv64ua-v-amoadd_w              = FAILED - Test return value = 0
Test rv64ua-v-amoand_d              = FAILED - Test return value = 0
Test rv64ua-v-amoand_w              = FAILED - Test return value = 0
Test rv64ua-v-amomaxu_d             = FAILED - Test return value = 0
Test rv64ua-v-amomaxu_w             = FAILED - Test return value = 0
Test rv64ua-v-amomax_d              = FAILED - Test return value = 0
Test rv64ua-v-amomax_w              = FAILED - Test return value = 0
Test rv64ua-v-amominu_d             = FAILED - Test return value = 0
Test rv64ua-v-amominu_w             = FAILED - Test return value = 0
Test rv64ua-v-amomin_d              = FAILED - Test return value = 0
Test rv64ua-v-amomin_w              = FAILED - Test return value = 0
Test rv64ua-v-amoor_d               = FAILED - Test return value = 0
Test rv64ua-v-amoor_w               = FAILED - Test return value = 0
Test rv64ua-v-amoswap_d             = FAILED - Test return value = 0
Test rv64ua-v-amoswap_w             = FAILED - Test return value = 0
Test rv64ua-v-amoxor_d              = FAILED - Test return value = 0
Test rv64ua-v-amoxor_w              = FAILED - Test return value = 0
Test rv64ua-v-lrsc                  = FAILED - Test return value = 0
Test rv64uc-p-rvc                   = OK
Test rv64uc-v-rvc                   = FAILED - Test return value = 0
Test rv64ud-p-fadd                  = OK
Test rv64ud-p-fclass                = OK
Test rv64ud-p-fcmp                  = OK
Test rv64ud-p-fcvt                  = OK
Test rv64ud-p-fcvt_w                = OK
Test rv64ud-p-fdiv                  = OK
Test rv64ud-p-fmadd                 = OK
Test rv64ud-p-fmin                  = OK
Test rv64ud-p-ldst                  = OK
Test rv64ud-p-move                  = OK
Test rv64ud-p-recoding              = OK
Test rv64ud-p-structural            = OK
Test rv64ud-v-fadd                  = FAILED - Test return value = 0
Test rv64ud-v-fclass                = FAILED - Test return value = 0
Test rv64ud-v-fcmp                  = FAILED - Test return value = 0
Test rv64ud-v-fcvt                  = FAILED - Test return value = 0
Test rv64ud-v-fcvt_w                = FAILED - Test return value = 0
Test rv64ud-v-fdiv                  = FAILED - Test return value = 0
Test rv64ud-v-fmadd                 = FAILED - Test return value = 0
Test rv64ud-v-fmin                  = FAILED - Test return value = 0
Test rv64ud-v-ldst                  = FAILED - Test return value = 0
Test rv64ud-v-move                  = FAILED - Test return value = 0
Test rv64ud-v-recoding              = FAILED - Test return value = 0
Test rv64ud-v-structural            = FAILED - Test return value = 0
Test rv64uf-p-fadd                  = OK
Test rv64uf-p-fclass                = OK
Test rv64uf-p-fcmp                  = OK
Test rv64uf-p-fcvt                  = OK
Test rv64uf-p-fcvt_w                = OK
Test rv64uf-p-fdiv                  = OK
Test rv64uf-p-fmadd                 = OK
Test rv64uf-p-fmin                  = OK
Test rv64uf-p-ldst                  = OK
Test rv64uf-p-move                  = OK
Test rv64uf-p-recoding              = OK
Test rv64uf-v-fadd                  = FAILED - Test return value = 0
Test rv64uf-v-fclass                = FAILED - Test return value = 0
Test rv64uf-v-fcmp                  = FAILED - Test return value = 0
Test rv64uf-v-fcvt                  = FAILED - Test return value = 0
Test rv64uf-v-fcvt_w                = FAILED - Test return value = 0
Test rv64uf-v-fdiv                  = FAILED - Test return value = 0
Test rv64uf-v-fmadd                 = FAILED - Test return value = 0
Test rv64uf-v-fmin                  = FAILED - Test return value = 0
Test rv64uf-v-ldst                  = FAILED - Test return value = 0
Test rv64uf-v-move                  = FAILED - Test return value = 0
Test rv64uf-v-recoding              = FAILED - Test return value = 0
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
Test rv64ui-v-add                   = FAILED - Test return value = 0
Test rv64ui-v-addi                  = FAILED - Test return value = 0
Test rv64ui-v-addiw                 = FAILED - Test return value = 0
Test rv64ui-v-addw                  = FAILED - Test return value = 0
Test rv64ui-v-and                   = FAILED - Test return value = 0
Test rv64ui-v-andi                  = FAILED - Test return value = 0
Test rv64ui-v-auipc                 = FAILED - Test return value = 0
Test rv64ui-v-beq                   = FAILED - Test return value = 0
Test rv64ui-v-bge                   = FAILED - Test return value = 0
Test rv64ui-v-bgeu                  = FAILED - Test return value = 0
Test rv64ui-v-blt                   = FAILED - Test return value = 0
Test rv64ui-v-bltu                  = FAILED - Test return value = 0
Test rv64ui-v-bne                   = FAILED - Test return value = 0
Test rv64ui-v-fence_i               = FAILED - Test return value = 0
Test rv64ui-v-jal                   = FAILED - Test return value = 0
Test rv64ui-v-jalr                  = FAILED - Test return value = 0
Test rv64ui-v-lb                    = FAILED - Test return value = 0
Test rv64ui-v-lbu                   = FAILED - Test return value = 0
Test rv64ui-v-ld                    = FAILED - Test return value = 0
Test rv64ui-v-lh                    = FAILED - Test return value = 0
Test rv64ui-v-lhu                   = FAILED - Test return value = 0
Test rv64ui-v-lui                   = FAILED - Test return value = 0
Test rv64ui-v-lw                    = FAILED - Test return value = 0
Test rv64ui-v-lwu                   = FAILED - Test return value = 0
Test rv64ui-v-ma_data               = FAILED - Test return value = 0
Test rv64ui-v-or                    = FAILED - Test return value = 0
Test rv64ui-v-ori                   = FAILED - Test return value = 0
Test rv64ui-v-sb                    = FAILED - Test return value = 0
Test rv64ui-v-sd                    = FAILED - Test return value = 0
Test rv64ui-v-sh                    = FAILED - Test return value = 0
Test rv64ui-v-simple                = FAILED - Test return value = 0
Test rv64ui-v-sll                   = FAILED - Test return value = 0
Test rv64ui-v-slli                  = FAILED - Test return value = 0
Test rv64ui-v-slliw                 = FAILED - Test return value = 0
Test rv64ui-v-sllw                  = FAILED - Test return value = 0
Test rv64ui-v-slt                   = FAILED - Test return value = 0
Test rv64ui-v-slti                  = FAILED - Test return value = 0
Test rv64ui-v-sltiu                 = FAILED - Test return value = 0
Test rv64ui-v-sltu                  = FAILED - Test return value = 0
Test rv64ui-v-sra                   = FAILED - Test return value = 0
Test rv64ui-v-srai                  = FAILED - Test return value = 0
Test rv64ui-v-sraiw                 = FAILED - Test return value = 0
Test rv64ui-v-sraw                  = FAILED - Test return value = 0
Test rv64ui-v-srl                   = FAILED - Test return value = 0
Test rv64ui-v-srli                  = FAILED - Test return value = 0
Test rv64ui-v-srliw                 = FAILED - Test return value = 0
Test rv64ui-v-srlw                  = FAILED - Test return value = 0
Test rv64ui-v-sub                   = FAILED - Test return value = 0
Test rv64ui-v-subw                  = FAILED - Test return value = 0
Test rv64ui-v-sw                    = FAILED - Test return value = 0
Test rv64ui-v-xor                   = FAILED - Test return value = 0
Test rv64ui-v-xori                  = FAILED - Test return value = 0
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
Test rv64um-v-div                   = FAILED - Test return value = 0
Test rv64um-v-divu                  = FAILED - Test return value = 0
Test rv64um-v-divuw                 = FAILED - Test return value = 0
Test rv64um-v-divw                  = FAILED - Test return value = 0
Test rv64um-v-mul                   = FAILED - Test return value = 0
Test rv64um-v-mulh                  = FAILED - Test return value = 0
Test rv64um-v-mulhsu                = FAILED - Test return value = 0
Test rv64um-v-mulhu                 = FAILED - Test return value = 0
Test rv64um-v-mulw                  = FAILED - Test return value = 0
Test rv64um-v-rem                   = FAILED - Test return value = 0
Test rv64um-v-remu                  = FAILED - Test return value = 0
Test rv64um-v-remuw                 = FAILED - Test return value = 0
Test rv64um-v-remw                  = FAILED - Test return value = 0
Test rv64uzba-p-add_uw              = OK
Test rv64uzba-p-sh1add              = OK
Test rv64uzba-p-sh1add_uw           = OK
Test rv64uzba-p-sh2add              = OK
Test rv64uzba-p-sh2add_uw           = OK
Test rv64uzba-p-sh3add              = OK
Test rv64uzba-p-sh3add_uw           = OK
Test rv64uzba-p-slli_uw             = OK
Test rv64uzba-v-add_uw              = FAILED - Test return value = 0
Test rv64uzba-v-sh1add              = FAILED - Test return value = 0
Test rv64uzba-v-sh1add_uw           = FAILED - Test return value = 0
Test rv64uzba-v-sh2add              = FAILED - Test return value = 0
Test rv64uzba-v-sh2add_uw           = FAILED - Test return value = 0
Test rv64uzba-v-sh3add              = FAILED - Test return value = 0
Test rv64uzba-v-sh3add_uw           = FAILED - Test return value = 0
Test rv64uzba-v-slli_uw             = FAILED - Test return value = 0
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
Test rv64uzbb-p-orn                 = OK
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
Test rv64uzbb-p-zext_h              = OK
Test rv64uzbb-v-andn                = FAILED - Test return value = 0
Test rv64uzbb-v-clz                 = FAILED - Test return value = 0
Test rv64uzbb-v-clzw                = FAILED - Test return value = 0
Test rv64uzbb-v-cpop                = FAILED - Test return value = 0
Test rv64uzbb-v-cpopw               = FAILED - Test return value = 0
Test rv64uzbb-v-ctz                 = FAILED - Test return value = 0
Test rv64uzbb-v-ctzw                = FAILED - Test return value = 0
Test rv64uzbb-v-max                 = FAILED - Test return value = 0
Test rv64uzbb-v-maxu                = FAILED - Test return value = 0
Test rv64uzbb-v-min                 = FAILED - Test return value = 0
Test rv64uzbb-v-minu                = FAILED - Test return value = 0
Test rv64uzbb-v-orc_b               = FAILED - Test return value = 0
Test rv64uzbb-v-orn                 = FAILED - Test return value = 0
Test rv64uzbb-v-rev8                = FAILED - Test return value = 0
Test rv64uzbb-v-rol                 = FAILED - Test return value = 0
Test rv64uzbb-v-rolw                = FAILED - Test return value = 0
Test rv64uzbb-v-ror                 = FAILED - Test return value = 0
Test rv64uzbb-v-rori                = FAILED - Test return value = 0
Test rv64uzbb-v-roriw               = FAILED - Test return value = 0
Test rv64uzbb-v-rorw                = FAILED - Test return value = 0
Test rv64uzbb-v-sext_b              = FAILED - Test return value = 0
Test rv64uzbb-v-sext_h              = FAILED - Test return value = 0
Test rv64uzbb-v-xnor                = FAILED - Test return value = 0
Test rv64uzbb-v-zext_h              = FAILED - Test return value = 0
Test rv64uzbc-p-clmul               = FAILED - Test return value = 65
Test rv64uzbc-p-clmulh              = FAILED - Test return value = 65
Test rv64uzbc-p-clmulr              = FAILED - Test return value = 65
Test rv64uzbc-v-clmul               = FAILED - Test return value = 0
Test rv64uzbc-v-clmulh              = FAILED - Test return value = 0
Test rv64uzbc-v-clmulr              = FAILED - Test return value = 0
Test rv64uzbs-p-bclr                = OK
Test rv64uzbs-p-bclri               = OK
Test rv64uzbs-p-bext                = OK
Test rv64uzbs-p-bexti               = OK
Test rv64uzbs-p-binv                = OK
Test rv64uzbs-p-binvi               = OK
Test rv64uzbs-p-bset                = OK
Test rv64uzbs-p-bseti               = OK
Test rv64uzbs-v-bclr                = FAILED - Test return value = 0
Test rv64uzbs-v-bclri               = FAILED - Test return value = 0
Test rv64uzbs-v-bext                = FAILED - Test return value = 0
Test rv64uzbs-v-bexti               = FAILED - Test return value = 0
Test rv64uzbs-v-binv                = FAILED - Test return value = 0
Test rv64uzbs-v-binvi               = FAILED - Test return value = 0
Test rv64uzbs-v-bset                = FAILED - Test return value = 0
Test rv64uzbs-v-bseti               = FAILED - Test return value = 0
Test rv64uzfh-p-fadd                = OK
Test rv64uzfh-p-fclass              = OK
Test rv64uzfh-p-fcmp                = OK
Test rv64uzfh-p-fcvt                = OK
Test rv64uzfh-p-fcvt_w              = OK
Test rv64uzfh-p-fdiv                = OK
Test rv64uzfh-p-fmadd               = OK
Test rv64uzfh-p-fmin                = OK
Test rv64uzfh-p-ldst                = OK
Test rv64uzfh-p-move                = OK
Test rv64uzfh-p-recoding            = OK
Test rv64uzfh-v-fadd                = FAILED - Test return value = 0
Test rv64uzfh-v-fclass              = FAILED - Test return value = 0
Test rv64uzfh-v-fcmp                = FAILED - Test return value = 0
Test rv64uzfh-v-fcvt                = FAILED - Test return value = 0
Test rv64uzfh-v-fcvt_w              = FAILED - Test return value = 0
Test rv64uzfh-v-fdiv                = FAILED - Test return value = 0
Test rv64uzfh-v-fmadd               = FAILED - Test return value = 0
Test rv64uzfh-v-fmin                = FAILED - Test return value = 0
Test rv64uzfh-v-ldst                = FAILED - Test return value = 0
Test rv64uzfh-v-move                = FAILED - Test return value = 0
Test rv64uzfh-v-recoding            = FAILED - Test return value = 0
Total: 349 Correct: 180 (51.6 %)
```

