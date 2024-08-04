# Testing of RISC-V Tests


We include the RISC-V ISA tests compiled binaries (compiled on 20/5/2024) to test the ISS.
We do not run the rv32 tests.

## Single Cycle Processor Version

To run them do

```
 python  tb_ISA_tests.py -c "runAllTests()"
```


***Summary***

<pre>
rv64mi-p        93.8 %   |███████████████████████████████████████████░░|
rv64mzicbo-p    0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64si-p        100.0 %  |█████████████████████████████████████████████|
rv64ssvnapot-p  0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ua-p        100.0 %  |█████████████████████████████████████████████|
rv64ua-v        100.0 %  |█████████████████████████████████████████████|
rv64uc-p        100.0 %  |█████████████████████████████████████████████|
rv64uc-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ud-p        100.0 %  |█████████████████████████████████████████████|
rv64ud-v        91.7 %   |██████████████████████████████████████████░░░|
rv64uf-p        100.0 %  |█████████████████████████████████████████████|
rv64uf-v        90.9 %   |█████████████████████████████████████████░░░░|
rv64ui-p        100.0 %  |█████████████████████████████████████████████|
rv64ui-v        98.1 %   |█████████████████████████████████████████████|
rv64um-p        100.0 %  |█████████████████████████████████████████████|
rv64um-v        100.0 %  |█████████████████████████████████████████████|
rv64uzba-p      100.0 %  |█████████████████████████████████████████████|
rv64uzba-v      100.0 %  |█████████████████████████████████████████████|
rv64uzbb-p      100.0 %  |█████████████████████████████████████████████|
rv64uzbb-v      100.0 %  |█████████████████████████████████████████████|
rv64uzbc-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbc-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbs-p      100.0 %  |█████████████████████████████████████████████|
rv64uzbs-v      100.0 %  |█████████████████████████████████████████████|
rv64uzfh-p      100.0 %  |█████████████████████████████████████████████|
rv64uzfh-v      90.9 %   |█████████████████████████████████████████░░░░|
</pre>

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
Test rv64si-p-icache-alias          = OK
Test rv64si-p-ma_fetch              = OK
Test rv64si-p-sbreak                = OK
Test rv64si-p-scall                 = OK
Test rv64si-p-wfi                   = OK
Test rv64ssvnapot-p-napot           = FAILED - bytearray index out of range
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
Test rv64ua-v-amoadd_d              = OK
Test rv64ua-v-amoadd_w              = OK
Test rv64ua-v-amoand_d              = OK
Test rv64ua-v-amoand_w              = OK
Test rv64ua-v-amomaxu_d             = OK
Test rv64ua-v-amomaxu_w             = OK
Test rv64ua-v-amomax_d              = OK
Test rv64ua-v-amomax_w              = OK
Test rv64ua-v-amominu_d             = OK
Test rv64ua-v-amominu_w             = OK
Test rv64ua-v-amomin_d              = OK
Test rv64ua-v-amomin_w              = OK
Test rv64ua-v-amoor_d               = OK
Test rv64ua-v-amoor_w               = OK
Test rv64ua-v-amoswap_d             = OK
Test rv64ua-v-amoswap_w             = OK
Test rv64ua-v-amoxor_d              = OK
Test rv64ua-v-amoxor_w              = OK
Test rv64ua-v-lrsc                  = OK
Test rv64uc-p-rvc                   = OK
Test rv64uc-v-rvc                   = FAILED - Test return value = 5
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
Test rv64ud-v-fadd                  = OK
Test rv64ud-v-fclass                = OK
Test rv64ud-v-fcmp                  = OK
Test rv64ud-v-fcvt                  = OK
Test rv64ud-v-fcvt_w                = FAILED - Test return value = 0
Test rv64ud-v-fdiv                  = OK
Test rv64ud-v-fmadd                 = OK
Test rv64ud-v-fmin                  = OK
Test rv64ud-v-ldst                  = OK
Test rv64ud-v-move                  = OK
Test rv64ud-v-recoding              = OK
Test rv64ud-v-structural            = OK
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
Test rv64uf-v-fadd                  = OK
Test rv64uf-v-fclass                = OK
Test rv64uf-v-fcmp                  = OK
Test rv64uf-v-fcvt                  = OK
Test rv64uf-v-fcvt_w                = FAILED - Test return value = 0
Test rv64uf-v-fdiv                  = OK
Test rv64uf-v-fmadd                 = OK
Test rv64uf-v-fmin                  = OK
Test rv64uf-v-ldst                  = OK
Test rv64uf-v-move                  = OK
Test rv64uf-v-recoding              = OK
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
Test rv64ui-v-add                   = OK
Test rv64ui-v-addi                  = OK
Test rv64ui-v-addiw                 = OK
Test rv64ui-v-addw                  = OK
Test rv64ui-v-and                   = OK
Test rv64ui-v-andi                  = OK
Test rv64ui-v-auipc                 = OK
Test rv64ui-v-beq                   = OK
Test rv64ui-v-bge                   = OK
Test rv64ui-v-bgeu                  = OK
Test rv64ui-v-blt                   = OK
Test rv64ui-v-bltu                  = OK
Test rv64ui-v-bne                   = OK
Test rv64ui-v-fence_i               = OK
Test rv64ui-v-jal                   = OK
Test rv64ui-v-jalr                  = OK
Test rv64ui-v-lb                    = OK
Test rv64ui-v-lbu                   = OK
Test rv64ui-v-ld                    = OK
Test rv64ui-v-lh                    = OK
Test rv64ui-v-lhu                   = OK
Test rv64ui-v-lui                   = OK
Test rv64ui-v-lw                    = OK
Test rv64ui-v-lwu                   = OK
Test rv64ui-v-ma_data               = FAILED - Test return value = 0
Test rv64ui-v-or                    = OK
Test rv64ui-v-ori                   = OK
Test rv64ui-v-sb                    = OK
Test rv64ui-v-sd                    = OK
Test rv64ui-v-sh                    = OK
Test rv64ui-v-simple                = OK
Test rv64ui-v-sll                   = OK
Test rv64ui-v-slli                  = OK
Test rv64ui-v-slliw                 = OK
Test rv64ui-v-sllw                  = OK
Test rv64ui-v-slt                   = OK
Test rv64ui-v-slti                  = OK
Test rv64ui-v-sltiu                 = OK
Test rv64ui-v-sltu                  = OK
Test rv64ui-v-sra                   = OK
Test rv64ui-v-srai                  = OK
Test rv64ui-v-sraiw                 = OK
Test rv64ui-v-sraw                  = OK
Test rv64ui-v-srl                   = OK
Test rv64ui-v-srli                  = OK
Test rv64ui-v-srliw                 = OK
Test rv64ui-v-srlw                  = OK
Test rv64ui-v-sub                   = OK
Test rv64ui-v-subw                  = OK
Test rv64ui-v-sw                    = OK
Test rv64ui-v-xor                   = OK
Test rv64ui-v-xori                  = OK
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
Test rv64um-v-div                   = OK
Test rv64um-v-divu                  = OK
Test rv64um-v-divuw                 = OK
Test rv64um-v-divw                  = OK
Test rv64um-v-mul                   = OK
Test rv64um-v-mulh                  = OK
Test rv64um-v-mulhsu                = OK
Test rv64um-v-mulhu                 = OK
Test rv64um-v-mulw                  = OK
Test rv64um-v-rem                   = OK
Test rv64um-v-remu                  = OK
Test rv64um-v-remuw                 = OK
Test rv64um-v-remw                  = OK
Test rv64uzba-p-add_uw              = OK
Test rv64uzba-p-sh1add              = OK
Test rv64uzba-p-sh1add_uw           = OK
Test rv64uzba-p-sh2add              = OK
Test rv64uzba-p-sh2add_uw           = OK
Test rv64uzba-p-sh3add              = OK
Test rv64uzba-p-sh3add_uw           = OK
Test rv64uzba-p-slli_uw             = OK
Test rv64uzba-v-add_uw              = OK
Test rv64uzba-v-sh1add              = OK
Test rv64uzba-v-sh1add_uw           = OK
Test rv64uzba-v-sh2add              = OK
Test rv64uzba-v-sh2add_uw           = OK
Test rv64uzba-v-sh3add              = OK
Test rv64uzba-v-sh3add_uw           = OK
Test rv64uzba-v-slli_uw             = OK
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
Test rv64uzbb-v-andn                = OK
Test rv64uzbb-v-clz                 = OK
Test rv64uzbb-v-clzw                = OK
Test rv64uzbb-v-cpop                = OK
Test rv64uzbb-v-cpopw               = OK
Test rv64uzbb-v-ctz                 = OK
Test rv64uzbb-v-ctzw                = OK
Test rv64uzbb-v-max                 = OK
Test rv64uzbb-v-maxu                = OK
Test rv64uzbb-v-min                 = OK
Test rv64uzbb-v-minu                = OK
Test rv64uzbb-v-orc_b               = OK
Test rv64uzbb-v-orn                 = OK
Test rv64uzbb-v-rev8                = OK
Test rv64uzbb-v-rol                 = OK
Test rv64uzbb-v-rolw                = OK
Test rv64uzbb-v-ror                 = OK
Test rv64uzbb-v-rori                = OK
Test rv64uzbb-v-roriw               = OK
Test rv64uzbb-v-rorw                = OK
Test rv64uzbb-v-sext_b              = OK
Test rv64uzbb-v-sext_h              = OK
Test rv64uzbb-v-xnor                = OK
Test rv64uzbb-v-zext_h              = OK
Test rv64uzbc-p-clmul               = FAILED - Test return value = 65
Test rv64uzbc-p-clmulh              = FAILED - Test return value = 65
Test rv64uzbc-p-clmulr              = FAILED - Test return value = 65
Test rv64uzbc-v-clmul               = FAILED - Test return value = 65
Test rv64uzbc-v-clmulh              = FAILED - Test return value = 65
Test rv64uzbc-v-clmulr              = FAILED - Test return value = 65
Test rv64uzbs-p-bclr                = OK
Test rv64uzbs-p-bclri               = OK
Test rv64uzbs-p-bext                = OK
Test rv64uzbs-p-bexti               = OK
Test rv64uzbs-p-binv                = OK
Test rv64uzbs-p-binvi               = OK
Test rv64uzbs-p-bset                = OK
Test rv64uzbs-p-bseti               = OK
Test rv64uzbs-v-bclr                = OK
Test rv64uzbs-v-bclri               = OK
Test rv64uzbs-v-bext                = OK
Test rv64uzbs-v-bexti               = OK
Test rv64uzbs-v-binv                = OK
Test rv64uzbs-v-binvi               = OK
Test rv64uzbs-v-bset                = OK
Test rv64uzbs-v-bseti               = OK
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
Test rv64uzfh-v-fadd                = OK
Test rv64uzfh-v-fclass              = OK
Test rv64uzfh-v-fcmp                = OK
Test rv64uzfh-v-fcvt                = OK
Test rv64uzfh-v-fcvt_w              = FAILED - Test return value = 0
Test rv64uzfh-v-fdiv                = OK
Test rv64uzfh-v-fmadd               = OK
Test rv64uzfh-v-fmin                = OK
Test rv64uzfh-v-ldst                = OK
Test rv64uzfh-v-move                = OK
Test rv64uzfh-v-recoding            = OK
Total: 349 Correct: 335 (96.0 %)
```

## Microcoded Version

To run them do

```
 python  tb_ISA_tests.py -c "runAllTests()"
```


***Summary***

<pre>
rv64mi-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64mzicbo-p    0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64si-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ssvnapot-p  0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ua-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ua-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uc-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uc-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ud-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ud-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uf-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uf-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ui-p        17.3 %   |████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ui-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64um-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64um-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzba-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzba-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbb-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbb-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbc-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbc-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbs-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbs-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzfh-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzfh-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
</pre>

The detailed current output is:

```
Test rv64mi-p-access                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-breakpoint            = FAILED - 'ControlUnit' object has no attribute 'readCSR'
Test rv64mi-p-csr                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-illegal               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-ld-misaligned         = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-lh-misaligned         = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-lw-misaligned         = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-ma_addr               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-ma_fetch              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-mcsr                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-sbreak                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-scall                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-sd-misaligned         = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-sh-misaligned         = FAILED - not implemented
Test rv64mi-p-sw-misaligned         = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mi-p-zicntr                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64mzicbo-p-zero              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64si-p-csr                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64si-p-dirty                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64si-p-icache-alias          = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64si-p-ma_fetch              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64si-p-sbreak                = FAILED - 'ControlUnit' object has no attribute 'csr'
Test rv64si-p-scall                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64si-p-wfi                   = FAILED - 'ControlUnit' object has no attribute 'readCSR'
Test rv64ssvnapot-p-napot           = FAILED - bytearray index out of range
Test rv64ua-p-amoadd_d              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoadd_w              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoand_d              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoand_w              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amomaxu_d             = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amomaxu_w             = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amomax_d              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amomax_w              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amominu_d             = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amominu_w             = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amomin_d              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amomin_w              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoor_d               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoor_w               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoswap_d             = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoswap_w             = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoxor_d              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-amoxor_w              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-p-lrsc                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ua-v-amoadd_d              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoadd_w              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoand_d              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoand_w              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amomaxu_d             = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amomaxu_w             = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amomax_d              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amomax_w              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amominu_d             = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amominu_w             = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amomin_d              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amomin_w              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoor_d               = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoor_w               = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoswap_d             = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoswap_w             = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoxor_d              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-amoxor_w              = FAILED - 'sel_alu_1_P'
Test rv64ua-v-lrsc                  = FAILED - 'sel_alu_1_P'
Test rv64uc-p-rvc                   = FAILED - C.ADDI4SPN - Not supported!
Test rv64uc-v-rvc                   = FAILED - 'sel_alu_1_P'
Test rv64ud-p-fadd                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-fclass                = FAILED - FMV.D.X - Not supported!
Test rv64ud-p-fcmp                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-fcvt                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-fcvt_w                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-fdiv                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-fmadd                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-fmin                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-ldst                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-move                  = FAILED - FMV.D.X - Not supported!
Test rv64ud-p-recoding              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ud-p-structural            = FAILED - FMV.D.X - Not supported!
Test rv64ud-v-fadd                  = FAILED - 'sel_alu_1_P'
Test rv64ud-v-fclass                = FAILED - 'sel_alu_1_P'
Test rv64ud-v-fcmp                  = FAILED - 'sel_alu_1_P'
Test rv64ud-v-fcvt                  = FAILED - 'sel_alu_1_P'
Test rv64ud-v-fcvt_w                = FAILED - 'sel_alu_1_P'
Test rv64ud-v-fdiv                  = FAILED - 'sel_alu_1_P'
Test rv64ud-v-fmadd                 = FAILED - 'sel_alu_1_P'
Test rv64ud-v-fmin                  = FAILED - 'sel_alu_1_P'
Test rv64ud-v-ldst                  = FAILED - 'sel_alu_1_P'
Test rv64ud-v-move                  = FAILED - 'sel_alu_1_P'
Test rv64ud-v-recoding              = FAILED - 'sel_alu_1_P'
Test rv64ud-v-structural            = FAILED - 'sel_alu_1_P'
Test rv64uf-p-fadd                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fclass                = FAILED - FMV.W.X - Not supported!
Test rv64uf-p-fcmp                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fcvt                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fcvt_w                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fdiv                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fmadd                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fmin                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-ldst                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-move                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-recoding              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-v-fadd                  = FAILED - 'sel_alu_1_P'
Test rv64uf-v-fclass                = FAILED - 'sel_alu_1_P'
Test rv64uf-v-fcmp                  = FAILED - 'sel_alu_1_P'
Test rv64uf-v-fcvt                  = FAILED - 'sel_alu_1_P'
Test rv64uf-v-fcvt_w                = FAILED - 'sel_alu_1_P'
Test rv64uf-v-fdiv                  = FAILED - 'sel_alu_1_P'
Test rv64uf-v-fmadd                 = FAILED - 'sel_alu_1_P'
Test rv64uf-v-fmin                  = FAILED - 'sel_alu_1_P'
Test rv64uf-v-ldst                  = FAILED - 'sel_alu_1_P'
Test rv64uf-v-move                  = FAILED - 'sel_alu_1_P'
Test rv64uf-v-recoding              = FAILED - 'sel_alu_1_P'
Test rv64ui-p-add                   = OK
Test rv64ui-p-addi                  = OK
Test rv64ui-p-addiw                 = OK
Test rv64ui-p-addw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-and                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-andi                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-auipc                 = FAILED - 'sel_alu_1_P'
Test rv64ui-p-beq                   = OK
Test rv64ui-p-bge                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-bgeu                  = OK
Test rv64ui-p-blt                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-bltu                  = OK
Test rv64ui-p-bne                   = OK
Test rv64ui-p-fence_i               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-jal                   = FAILED - 'sel_alu_1_P'
Test rv64ui-p-jalr                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-lb                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-lbu                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-ld                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-lh                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-lhu                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-lui                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-lw                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-lwu                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-ma_data               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-or                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-ori                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sb                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sd                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sh                    = FAILED - not implemented
Test rv64ui-p-simple                = OK
Test rv64ui-p-sll                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-slli                  = OK
Test rv64ui-p-slliw                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sllw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-slt                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-slti                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sltiu                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sltu                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sra                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-srai                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sraiw                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sraw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-srl                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-srli                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-srliw                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-srlw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sub                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-subw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-sw                    = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-xor                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-p-xori                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64ui-v-add                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-addi                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-addiw                 = FAILED - 'sel_alu_1_P'
Test rv64ui-v-addw                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-and                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-andi                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-auipc                 = FAILED - 'sel_alu_1_P'
Test rv64ui-v-beq                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-bge                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-bgeu                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-blt                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-bltu                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-bne                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-fence_i               = FAILED - 'sel_alu_1_P'
Test rv64ui-v-jal                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-jalr                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-lb                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-lbu                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-ld                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-lh                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-lhu                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-lui                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-lw                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-lwu                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-ma_data               = FAILED - 'sel_alu_1_P'
Test rv64ui-v-or                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-ori                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sb                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sd                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sh                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-simple                = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sll                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-slli                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-slliw                 = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sllw                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-slt                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-slti                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sltiu                 = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sltu                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sra                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-srai                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sraiw                 = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sraw                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-srl                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-srli                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-srliw                 = FAILED - 'sel_alu_1_P'
Test rv64ui-v-srlw                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sub                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-subw                  = FAILED - 'sel_alu_1_P'
Test rv64ui-v-sw                    = FAILED - 'sel_alu_1_P'
Test rv64ui-v-xor                   = FAILED - 'sel_alu_1_P'
Test rv64ui-v-xori                  = FAILED - 'sel_alu_1_P'
Test rv64um-p-div                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-divu                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-divuw                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-divw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mul                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mulh                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mulhsu                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mulhu                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mulw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-rem                   = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-remu                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-remuw                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-remw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-v-div                   = FAILED - 'sel_alu_1_P'
Test rv64um-v-divu                  = FAILED - 'sel_alu_1_P'
Test rv64um-v-divuw                 = FAILED - 'sel_alu_1_P'
Test rv64um-v-divw                  = FAILED - 'sel_alu_1_P'
Test rv64um-v-mul                   = FAILED - 'sel_alu_1_P'
Test rv64um-v-mulh                  = FAILED - 'sel_alu_1_P'
Test rv64um-v-mulhsu                = FAILED - 'sel_alu_1_P'
Test rv64um-v-mulhu                 = FAILED - 'sel_alu_1_P'
Test rv64um-v-mulw                  = FAILED - 'sel_alu_1_P'
Test rv64um-v-rem                   = FAILED - 'sel_alu_1_P'
Test rv64um-v-remu                  = FAILED - 'sel_alu_1_P'
Test rv64um-v-remuw                 = FAILED - 'sel_alu_1_P'
Test rv64um-v-remw                  = FAILED - 'sel_alu_1_P'
Test rv64uzba-p-add_uw              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh1add              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh1add_uw           = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh2add              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh2add_uw           = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh3add              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh3add_uw           = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-slli_uw             = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-v-add_uw              = FAILED - 'sel_alu_1_P'
Test rv64uzba-v-sh1add              = FAILED - 'sel_alu_1_P'
Test rv64uzba-v-sh1add_uw           = FAILED - 'sel_alu_1_P'
Test rv64uzba-v-sh2add              = FAILED - 'sel_alu_1_P'
Test rv64uzba-v-sh2add_uw           = FAILED - 'sel_alu_1_P'
Test rv64uzba-v-sh3add              = FAILED - 'sel_alu_1_P'
Test rv64uzba-v-sh3add_uw           = FAILED - 'sel_alu_1_P'
Test rv64uzba-v-slli_uw             = FAILED - 'sel_alu_1_P'
Test rv64uzbb-p-andn                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-clz                 = FAILED - name 'count_leading_zeros' is not defined
Test rv64uzbb-p-clzw                = FAILED - name 'count_leading_zeros' is not defined
Test rv64uzbb-p-cpop                = FAILED - name 'pop_count' is not defined
Test rv64uzbb-p-cpopw               = FAILED - name 'pop_count' is not defined
Test rv64uzbb-p-ctz                 = FAILED - name 'count_trailing_zeros' is not defined
Test rv64uzbb-p-ctzw                = FAILED - name 'count_trailing_zeros' is not defined
Test rv64uzbb-p-max                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-maxu                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-min                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-minu                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-orc_b               = FAILED - name 'gorc' is not defined
Test rv64uzbb-p-orn                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-rev8                = FAILED - name 'grev' is not defined
Test rv64uzbb-p-rol                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-rolw                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-ror                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-rori                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-roriw               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-rorw                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-sext_b              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-sext_h              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-xnor                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-zext_h              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-v-andn                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-clz                 = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-clzw                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-cpop                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-cpopw               = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-ctz                 = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-ctzw                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-max                 = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-maxu                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-min                 = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-minu                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-orc_b               = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-orn                 = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-rev8                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-rol                 = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-rolw                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-ror                 = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-rori                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-roriw               = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-rorw                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-sext_b              = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-sext_h              = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-xnor                = FAILED - 'sel_alu_1_P'
Test rv64uzbb-v-zext_h              = FAILED - 'sel_alu_1_P'
Test rv64uzbc-p-clmul               = FAILED - name 'clmul' is not defined
Test rv64uzbc-p-clmulh              = FAILED - name 'clmul' is not defined
Test rv64uzbc-p-clmulr              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbc-v-clmul               = FAILED - 'sel_alu_1_P'
Test rv64uzbc-v-clmulh              = FAILED - 'sel_alu_1_P'
Test rv64uzbc-v-clmulr              = FAILED - 'sel_alu_1_P'
Test rv64uzbs-p-bclr                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bclri               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bext                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bexti               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-binv                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-binvi               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bset                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bseti               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-bclr                = FAILED - 'sel_alu_1_P'
Test rv64uzbs-v-bclri               = FAILED - 'sel_alu_1_P'
Test rv64uzbs-v-bext                = FAILED - 'sel_alu_1_P'
Test rv64uzbs-v-bexti               = FAILED - 'sel_alu_1_P'
Test rv64uzbs-v-binv                = FAILED - 'sel_alu_1_P'
Test rv64uzbs-v-binvi               = FAILED - 'sel_alu_1_P'
Test rv64uzbs-v-bset                = FAILED - 'sel_alu_1_P'
Test rv64uzbs-v-bseti               = FAILED - 'sel_alu_1_P'
Test rv64uzfh-p-fadd                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fclass              = FAILED - FMV.H.X - Not supported!
Test rv64uzfh-p-fcmp                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fcvt                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fcvt_w              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fdiv                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fmadd               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fmin                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-ldst                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-move                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-recoding            = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-v-fadd                = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-fclass              = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-fcmp                = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-fcvt                = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-fcvt_w              = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-fdiv                = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-fmadd               = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-fmin                = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-ldst                = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-move                = FAILED - 'sel_alu_1_P'
Test rv64uzfh-v-recoding            = FAILED - 'sel_alu_1_P'
Total: 349 Correct: 9 (2.6 %)
```

