# Testing of RISC-V Tests


We include the RISC-V ISA tests compiled binaries (compiled on 14/12/2024) to test the ISS.

To compile them we did:
```
git clone https://github.com/riscv-software-src/riscv-tests
cd risv-tests
./configure
make
```

We run the rv64 tests seperately than rv32 tests.

## RV64 Single Cycle Processor Version 

To run the RV64 test do

```
 python  tb_ISA_tests.py -c "runAllTests()"
```


***Summary***

<pre>
rv64mi-p        100.0 %  |█████████████████████████████████████████████|
rv64mzicbo-p    100.0 %  |█████████████████████████████████████████████|
rv64si-p        100.0 %  |█████████████████████████████████████████████|
rv64ssvnapot-p  100.0 %  |█████████████████████████████████████████████|
rv64ua-p        100.0 %  |█████████████████████████████████████████████|
rv64ua-v        100.0 %  |█████████████████████████████████████████████|
rv64uc-p        100.0 %  |█████████████████████████████████████████████|
rv64uc-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ud-p        100.0 %  |█████████████████████████████████████████████|
rv64ud-v        100.0 %  |█████████████████████████████████████████████|
rv64uf-p        100.0 %  |█████████████████████████████████████████████|
rv64uf-v        100.0 %  |█████████████████████████████████████████████|
rv64ui-p        100.0 %  |█████████████████████████████████████████████|
rv64ui-v        100.0 %  |█████████████████████████████████████████████|
rv64um-p        100.0 %  |█████████████████████████████████████████████|
rv64um-v        100.0 %  |█████████████████████████████████████████████|
rv64uzba-p      100.0 %  |█████████████████████████████████████████████|
rv64uzba-v      100.0 %  |█████████████████████████████████████████████|
rv64uzbb-p      100.0 %  |█████████████████████████████████████████████|
rv64uzbb-v      100.0 %  |█████████████████████████████████████████████|
rv64uzbc-p      100.0 %  |█████████████████████████████████████████████|
rv64uzbc-v      100.0 %  |█████████████████████████████████████████████|
rv64uzbs-p      100.0 %  |█████████████████████████████████████████████|
rv64uzbs-v      100.0 %  |█████████████████████████████████████████████|
rv64uzfh-p      100.0 %  |█████████████████████████████████████████████|
rv64uzfh-v      100.0 %  |█████████████████████████████████████████████|
</pre>

The detailed current output is:

```
Test rv64mi-p-access                = OK
Test rv64mi-p-breakpoint            = OK
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
Test rv64mzicbo-p-zero              = OK
Test rv64si-p-csr                   = OK
Test rv64si-p-dirty                 = OK
Test rv64si-p-icache-alias          = OK
Test rv64si-p-ma_fetch              = OK
Test rv64si-p-sbreak                = OK
Test rv64si-p-scall                 = OK
Test rv64si-p-wfi                   = OK
Test rv64ssvnapot-p-napot           = OK
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
Test rv64ud-v-fcvt_w                = OK
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
Test rv64uf-v-fcvt_w                = OK
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
Test rv64ui-v-ma_data               = OK
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
Test rv64uzbc-p-clmul               = OK
Test rv64uzbc-p-clmulh              = OK
Test rv64uzbc-p-clmulr              = OK
Test rv64uzbc-v-clmul               = OK
Test rv64uzbc-v-clmulh              = OK
Test rv64uzbc-v-clmulr              = OK
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
Test rv64uzfh-v-fcvt_w              = OK
Test rv64uzfh-v-fdiv                = OK
Test rv64uzfh-v-fmadd               = OK
Test rv64uzfh-v-fmin                = OK
Test rv64uzfh-v-ldst                = OK
Test rv64uzfh-v-move                = OK
Test rv64uzfh-v-recoding            = OK
Total: 349 Correct: 348 (99.7 %)
```

## RV32 Single Cycle Processor Version 

To run the RV32 test do

```
 python  tb_ISA_tests_32.py -c "runAllTests()"
```


***Summary***

<pre>
rv32mi-p        100.0 %  |█████████████████████████████████████████████|
rv32mzicbo-p    0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv32si-p        100.0 %  |█████████████████████████████████████████████|
rv32ssvnapot-p  0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv32ua-p        100.0 %  |█████████████████████████████████████████████|
rv32ua-v        100.0 %  |█████████████████████████████████████████████|
rv32uc-p        100.0 %  |█████████████████████████████████████████████|
rv32uc-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv32ud-p        100.0 %  |█████████████████████████████████████████████|
rv32ud-v        100.0 %  |█████████████████████████████████████████████|
rv32uf-p        100.0 %  |█████████████████████████████████████████████|
rv32uf-v        100.0 %  |█████████████████████████████████████████████|
rv32ui-p        100.0 %  |█████████████████████████████████████████████|
rv32ui-v        100.0 %  |█████████████████████████████████████████████|
rv32um-p        100.0 %  |█████████████████████████████████████████████|
rv32um-v        100.0 %  |█████████████████████████████████████████████|
rv32uzba-p      100.0 %  |█████████████████████████████████████████████|
rv32uzba-v      100.0 %  |█████████████████████████████████████████████|
rv32uzbb-p      100.0 %  |█████████████████████████████████████████████|
rv32uzbb-v      100.0 %  |█████████████████████████████████████████████|
rv32uzbc-p      100.0 %  |█████████████████████████████████████████████|
rv32uzbc-v      100.0 %  |█████████████████████████████████████████████|
rv32uzbs-p      100.0 %  |█████████████████████████████████████████████|
rv32uzbs-v      100.0 %  |█████████████████████████████████████████████|
rv32uzfh-p      100.0 %  |█████████████████████████████████████████████|
rv32uzfh-v      100.0 %  |█████████████████████████████████████████████|
</pre>

The detailed current output is:

```
Test rv32mi-p-breakpoint            = OK
Test rv32mi-p-csr                   = OK
Test rv32mi-p-illegal               = OK
Test rv32mi-p-lh-misaligned         = OK
Test rv32mi-p-lw-misaligned         = OK
Test rv32mi-p-ma_addr               = OK
Test rv32mi-p-ma_fetch              = OK
Test rv32mi-p-mcsr                  = OK
Test rv32mi-p-sbreak                = OK
Test rv32mi-p-scall                 = OK
Test rv32mi-p-sh-misaligned         = OK
Test rv32mi-p-shamt                 = OK
Test rv32mi-p-sw-misaligned         = OK
Test rv32mi-p-zicntr                = OK
Test rv32si-p-csr                   = OK
Test rv32si-p-dirty                 = OK
Test rv32si-p-ma_fetch              = OK
Test rv32si-p-sbreak                = OK
Test rv32si-p-scall                 = OK
Test rv32si-p-wfi                   = OK
Test rv32ua-p-amoadd_w              = OK
Test rv32ua-p-amoand_w              = OK
Test rv32ua-p-amomaxu_w             = OK
Test rv32ua-p-amomax_w              = OK
Test rv32ua-p-amominu_w             = OK
Test rv32ua-p-amomin_w              = OK
Test rv32ua-p-amoor_w               = OK
Test rv32ua-p-amoswap_w             = OK
Test rv32ua-p-amoxor_w              = OK
Test rv32ua-p-lrsc                  = OK
Test rv32ua-v-amoadd_w              = OK
Test rv32ua-v-amoand_w              = OK
Test rv32ua-v-amomaxu_w             = OK
Test rv32ua-v-amomax_w              = OK
Test rv32ua-v-amominu_w             = OK
Test rv32ua-v-amomin_w              = OK
Test rv32ua-v-amoor_w               = OK
Test rv32ua-v-amoswap_w             = OK
Test rv32ua-v-amoxor_w              = OK
Test rv32ua-v-lrsc                  = OK
Test rv32uc-p-rvc                   = OK
Test rv32uc-v-rvc                   = FAILED - Test return value = 5
Test rv32ud-p-fadd                  = OK
Test rv32ud-p-fclass                = OK
Test rv32ud-p-fcmp                  = OK
Test rv32ud-p-fcvt                  = OK
Test rv32ud-p-fcvt_w                = OK
Test rv32ud-p-fdiv                  = OK
Test rv32ud-p-fmadd                 = OK
Test rv32ud-p-fmin                  = OK
Test rv32ud-p-ldst                  = OK
Test rv32ud-p-recoding              = OK
Test rv32ud-v-fadd                  = OK
Test rv32ud-v-fclass                = OK
Test rv32ud-v-fcmp                  = OK
Test rv32ud-v-fcvt                  = OK
Test rv32ud-v-fcvt_w                = OK
Test rv32ud-v-fdiv                  = OK
Test rv32ud-v-fmadd                 = OK
Test rv32ud-v-fmin                  = OK
Test rv32ud-v-ldst                  = OK
Test rv32ud-v-recoding              = OK
Test rv32uf-p-fadd                  = OK
Test rv32uf-p-fclass                = OK
Test rv32uf-p-fcmp                  = OK
Test rv32uf-p-fcvt                  = OK
Test rv32uf-p-fcvt_w                = OK
Test rv32uf-p-fdiv                  = OK
Test rv32uf-p-fmadd                 = OK
Test rv32uf-p-fmin                  = OK
Test rv32uf-p-ldst                  = OK
Test rv32uf-p-move                  = OK
Test rv32uf-p-recoding              = OK
Test rv32uf-v-fadd                  = OK
Test rv32uf-v-fclass                = OK
Test rv32uf-v-fcmp                  = OK
Test rv32uf-v-fcvt                  = OK
Test rv32uf-v-fcvt_w                = OK
Test rv32uf-v-fdiv                  = OK
Test rv32uf-v-fmadd                 = OK
Test rv32uf-v-fmin                  = OK
Test rv32uf-v-ldst                  = OK
Test rv32uf-v-move                  = OK
Test rv32uf-v-recoding              = OK
Test rv32ui-p-add                   = OK
Test rv32ui-p-addi                  = OK
Test rv32ui-p-and                   = OK
Test rv32ui-p-andi                  = OK
Test rv32ui-p-auipc                 = OK
Test rv32ui-p-beq                   = OK
Test rv32ui-p-bge                   = OK
Test rv32ui-p-bgeu                  = OK
Test rv32ui-p-blt                   = OK
Test rv32ui-p-bltu                  = OK
Test rv32ui-p-bne                   = OK
Test rv32ui-p-fence_i               = OK
Test rv32ui-p-jal                   = OK
Test rv32ui-p-jalr                  = OK
Test rv32ui-p-lb                    = OK
Test rv32ui-p-lbu                   = OK
Test rv32ui-p-lh                    = OK
Test rv32ui-p-lhu                   = OK
Test rv32ui-p-lui                   = OK
Test rv32ui-p-lw                    = OK
Test rv32ui-p-ma_data               = OK
Test rv32ui-p-or                    = OK
Test rv32ui-p-ori                   = OK
Test rv32ui-p-sb                    = OK
Test rv32ui-p-sh                    = OK
Test rv32ui-p-simple                = OK
Test rv32ui-p-sll                   = OK
Test rv32ui-p-slli                  = OK
Test rv32ui-p-slt                   = OK
Test rv32ui-p-slti                  = OK
Test rv32ui-p-sltiu                 = OK
Test rv32ui-p-sltu                  = OK
Test rv32ui-p-sra                   = OK
Test rv32ui-p-srai                  = OK
Test rv32ui-p-srl                   = OK
Test rv32ui-p-srli                  = OK
Test rv32ui-p-sub                   = OK
Test rv32ui-p-sw                    = OK
Test rv32ui-p-xor                   = OK
Test rv32ui-p-xori                  = OK
Test rv32ui-v-add                   = OK
Test rv32ui-v-addi                  = OK
Test rv32ui-v-and                   = OK
Test rv32ui-v-andi                  = OK
Test rv32ui-v-auipc                 = OK
Test rv32ui-v-beq                   = OK
Test rv32ui-v-bge                   = OK
Test rv32ui-v-bgeu                  = OK
Test rv32ui-v-blt                   = OK
Test rv32ui-v-bltu                  = OK
Test rv32ui-v-bne                   = OK
Test rv32ui-v-fence_i               = OK
Test rv32ui-v-jal                   = OK
Test rv32ui-v-jalr                  = OK
Test rv32ui-v-lb                    = OK
Test rv32ui-v-lbu                   = OK
Test rv32ui-v-lh                    = OK
Test rv32ui-v-lhu                   = OK
Test rv32ui-v-lui                   = OK
Test rv32ui-v-lw                    = OK
Test rv32ui-v-ma_data               = OK
Test rv32ui-v-or                    = OK
Test rv32ui-v-ori                   = OK
Test rv32ui-v-sb                    = OK
Test rv32ui-v-sh                    = OK
Test rv32ui-v-simple                = OK
Test rv32ui-v-sll                   = OK
Test rv32ui-v-slli                  = OK
Test rv32ui-v-slt                   = OK
Test rv32ui-v-slti                  = OK
Test rv32ui-v-sltiu                 = OK
Test rv32ui-v-sltu                  = OK
Test rv32ui-v-sra                   = OK
Test rv32ui-v-srai                  = OK
Test rv32ui-v-srl                   = OK
Test rv32ui-v-srli                  = OK
Test rv32ui-v-sub                   = OK
Test rv32ui-v-sw                    = OK
Test rv32ui-v-xor                   = OK
Test rv32ui-v-xori                  = OK
Test rv32um-p-div                   = OK
Test rv32um-p-divu                  = OK
Test rv32um-p-mul                   = OK
Test rv32um-p-mulh                  = OK
Test rv32um-p-mulhsu                = OK
Test rv32um-p-mulhu                 = OK
Test rv32um-p-rem                   = OK
Test rv32um-p-remu                  = OK
Test rv32um-v-div                   = OK
Test rv32um-v-divu                  = OK
Test rv32um-v-mul                   = OK
Test rv32um-v-mulh                  = OK
Test rv32um-v-mulhsu                = OK
Test rv32um-v-mulhu                 = OK
Test rv32um-v-rem                   = OK
Test rv32um-v-remu                  = OK
Test rv32uzba-p-sh1add              = OK
Test rv32uzba-p-sh2add              = OK
Test rv32uzba-p-sh3add              = OK
Test rv32uzba-v-sh1add              = OK
Test rv32uzba-v-sh2add              = OK
Test rv32uzba-v-sh3add              = OK
Test rv32uzbb-p-andn                = OK
Test rv32uzbb-p-clz                 = OK
Test rv32uzbb-p-cpop                = OK
Test rv32uzbb-p-ctz                 = OK
Test rv32uzbb-p-max                 = OK
Test rv32uzbb-p-maxu                = OK
Test rv32uzbb-p-min                 = OK
Test rv32uzbb-p-minu                = OK
Test rv32uzbb-p-orc_b               = OK
Test rv32uzbb-p-orn                 = OK
Test rv32uzbb-p-rev8                = OK
Test rv32uzbb-p-rol                 = OK
Test rv32uzbb-p-ror                 = OK
Test rv32uzbb-p-rori                = OK
Test rv32uzbb-p-sext_b              = OK
Test rv32uzbb-p-sext_h              = OK
Test rv32uzbb-p-xnor                = OK
Test rv32uzbb-p-zext_h              = OK
Test rv32uzbb-v-andn                = OK
Test rv32uzbb-v-clz                 = OK
Test rv32uzbb-v-cpop                = OK
Test rv32uzbb-v-ctz                 = OK
Test rv32uzbb-v-max                 = OK
Test rv32uzbb-v-maxu                = OK
Test rv32uzbb-v-min                 = OK
Test rv32uzbb-v-minu                = OK
Test rv32uzbb-v-orc_b               = OK
Test rv32uzbb-v-orn                 = OK
Test rv32uzbb-v-rev8                = OK
Test rv32uzbb-v-rol                 = OK
Test rv32uzbb-v-ror                 = OK
Test rv32uzbb-v-rori                = OK
Test rv32uzbb-v-sext_b              = OK
Test rv32uzbb-v-sext_h              = OK
Test rv32uzbb-v-xnor                = OK
Test rv32uzbb-v-zext_h              = OK
Test rv32uzbc-p-clmul               = OK
Test rv32uzbc-p-clmulh              = OK
Test rv32uzbc-p-clmulr              = OK
Test rv32uzbc-v-clmul               = OK
Test rv32uzbc-v-clmulh              = OK
Test rv32uzbc-v-clmulr              = OK
Test rv32uzbs-p-bclr                = OK
Test rv32uzbs-p-bclri               = OK
Test rv32uzbs-p-bext                = OK
Test rv32uzbs-p-bexti               = OK
Test rv32uzbs-p-binv                = OK
Test rv32uzbs-p-binvi               = OK
Test rv32uzbs-p-bset                = OK
Test rv32uzbs-p-bseti               = OK
Test rv32uzbs-v-bclr                = OK
Test rv32uzbs-v-bclri               = OK
Test rv32uzbs-v-bext                = OK
Test rv32uzbs-v-bexti               = OK
Test rv32uzbs-v-binv                = OK
Test rv32uzbs-v-binvi               = OK
Test rv32uzbs-v-bset                = OK
Test rv32uzbs-v-bseti               = OK
Test rv32uzfh-p-fadd                = OK
Test rv32uzfh-p-fclass              = OK
Test rv32uzfh-p-fcmp                = OK
Test rv32uzfh-p-fcvt                = OK
Test rv32uzfh-p-fcvt_w              = OK
Test rv32uzfh-p-fdiv                = OK
Test rv32uzfh-p-fmadd               = OK
Test rv32uzfh-p-fmin                = OK
Test rv32uzfh-p-ldst                = OK
Test rv32uzfh-p-move                = OK
Test rv32uzfh-p-recoding            = OK
Test rv32uzfh-v-fadd                = OK
Test rv32uzfh-v-fclass              = OK
Test rv32uzfh-v-fcmp                = OK
Test rv32uzfh-v-fcvt                = OK
Test rv32uzfh-v-fcvt_w              = OK
Test rv32uzfh-v-fdiv                = OK
Test rv32uzfh-v-fmadd               = OK
Test rv32uzfh-v-fmin                = OK
Test rv32uzfh-v-ldst                = OK
Test rv32uzfh-v-move                = OK
Test rv32uzfh-v-recoding            = OK
Total: 266 Correct: 265 (99.6 %)
```
## RV64 Microprogrammed Version

To run them do

```
 python  tb_ISA_microprogrammed.py -c "runAllTests()"
```


***Summary***

<pre>
rv64mi-p        68.8 %   |███████████████████████████████░░░░░░░░░░░░░░|
rv64mzicbo-p    0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64si-p        57.1 %   |██████████████████████████░░░░░░░░░░░░░░░░░░░|
rv64ssvnapot-p  0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ua-p        100.0 %  |█████████████████████████████████████████████|
rv64ua-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uc-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uc-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ud-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ud-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uf-p        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uf-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64ui-p        100.0 %  |█████████████████████████████████████████████|
rv64ui-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64um-p        69.2 %   |████████████████████████████████░░░░░░░░░░░░░|
rv64um-v        0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzba-p      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzba-v      0.0 %    |░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
rv64uzbb-p      37.5 %   |█████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░|
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
Test rv64mi-p-access                = FAILED - Test return value = 7
Test rv64mi-p-breakpoint            = FAILED - Test return value = 5
Test rv64mi-p-csr                   = FAILED - Test return value = 25
Test rv64mi-p-illegal               = FAILED - Test return value = 0
Test rv64mi-p-ld-misaligned         = OK
Test rv64mi-p-lh-misaligned         = OK
Test rv64mi-p-lw-misaligned         = OK
Test rv64mi-p-ma_addr               = OK
Test rv64mi-p-ma_fetch              = FAILED - Test return value = 11
Test rv64mi-p-mcsr                  = OK
Test rv64mi-p-sbreak                = OK
Test rv64mi-p-scall                 = OK
Test rv64mi-p-sd-misaligned         = OK
Test rv64mi-p-sh-misaligned         = OK
Test rv64mi-p-sw-misaligned         = OK
Test rv64mi-p-zicntr                = OK
Test rv64mzicbo-p-zero              = FAILED - Test return value = 3
Test rv64si-p-csr                   = OK
Test rv64si-p-dirty                 = FAILED - Test return value = 7
Test rv64si-p-icache-alias          = FAILED - Test return value = 5
Test rv64si-p-ma_fetch              = FAILED - Test return value = 3
Test rv64si-p-sbreak                = OK
Test rv64si-p-scall                 = OK
Test rv64si-p-wfi                   = OK
Test rv64ssvnapot-p-napot           = FAILED - Test return value = 3
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
Test rv64ua-v-amoadd_d              = FAILED - Test return value = 73
Test rv64ua-v-amoadd_w              = FAILED - Test return value = 73
Test rv64ua-v-amoand_d              = FAILED - Test return value = 73
Test rv64ua-v-amoand_w              = FAILED - Test return value = 73
Test rv64ua-v-amomaxu_d             = FAILED - Test return value = 73
Test rv64ua-v-amomaxu_w             = FAILED - Test return value = 73
Test rv64ua-v-amomax_d              = FAILED - Test return value = 73
Test rv64ua-v-amomax_w              = FAILED - Test return value = 73
Test rv64ua-v-amominu_d             = FAILED - Test return value = 73
Test rv64ua-v-amominu_w             = FAILED - Test return value = 73
Test rv64ua-v-amomin_d              = FAILED - Test return value = 73
Test rv64ua-v-amomin_w              = FAILED - Test return value = 73
Test rv64ua-v-amoor_d               = FAILED - Test return value = 73
Test rv64ua-v-amoor_w               = FAILED - Test return value = 73
Test rv64ua-v-amoswap_d             = FAILED - Test return value = 73
Test rv64ua-v-amoswap_w             = FAILED - Test return value = 73
Test rv64ua-v-amoxor_d              = FAILED - Test return value = 73
Test rv64ua-v-amoxor_w              = FAILED - Test return value = 73
Test rv64ua-v-lrsc                  = FAILED - Test return value = 73
Test rv64uc-p-rvc                   = OK
Test rv64uc-v-rvc                   = FAILED - Test return value = 73
Test rv64ud-p-fadd                  = FAILED - Test return value = 7
Test rv64ud-p-fclass                = FAILED - Test return value = 5
Test rv64ud-p-fcmp                  = FAILED - Test return value = 5
Test rv64ud-p-fcvt                  = FAILED - Test return value = 19
Test rv64ud-p-fcvt_w                = FAILED - Test return value = 7
Test rv64ud-p-fdiv                  = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64ud-p-fmadd                 = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64ud-p-fmin                  = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64ud-p-ldst                  = FAILED - 'ControlUnit' object has no attribute 'freg'
Test rv64ud-p-move                  = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64ud-p-recoding              = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64ud-p-structural            = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64ud-v-fadd                  = FAILED - Test return value = 73
Test rv64ud-v-fclass                = FAILED - Test return value = 73
Test rv64ud-v-fcmp                  = FAILED - Test return value = 73
Test rv64ud-v-fcvt                  = FAILED - Test return value = 73
Test rv64ud-v-fcvt_w                = FAILED - Test return value = 73
Test rv64ud-v-fdiv                  = FAILED - Test return value = 73
Test rv64ud-v-fmadd                 = FAILED - Test return value = 73
Test rv64ud-v-fmin                  = FAILED - Test return value = 73
Test rv64ud-v-ldst                  = FAILED - Test return value = 73
Test rv64ud-v-move                  = FAILED - Test return value = 73
Test rv64ud-v-recoding              = FAILED - Test return value = 73
Test rv64ud-v-structural            = FAILED - Test return value = 73
Test rv64uf-p-fadd                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fclass                = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64uf-p-fcmp                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fcvt                  = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64uf-p-fcvt_w                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fdiv                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fmadd                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-fmin                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-ldst                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-p-move                  = FAILED - Test return value = 5
Test rv64uf-p-recoding              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uf-v-fadd                  = FAILED - Test return value = 73
Test rv64uf-v-fclass                = FAILED - Test return value = 73
Test rv64uf-v-fcmp                  = FAILED - Test return value = 73
Test rv64uf-v-fcvt                  = FAILED - Test return value = 73
Test rv64uf-v-fcvt_w                = FAILED - Test return value = 73
Test rv64uf-v-fdiv                  = FAILED - Test return value = 73
Test rv64uf-v-fmadd                 = FAILED - Test return value = 73
Test rv64uf-v-fmin                  = FAILED - Test return value = 73
Test rv64uf-v-ldst                  = FAILED - Test return value = 73
Test rv64uf-v-move                  = FAILED - Test return value = 73
Test rv64uf-v-recoding              = FAILED - Test return value = 73
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
Test rv64ui-v-add                   = FAILED - Test return value = 73
Test rv64ui-v-addi                  = FAILED - Test return value = 73
Test rv64ui-v-addiw                 = FAILED - Test return value = 73
Test rv64ui-v-addw                  = FAILED - Test return value = 73
Test rv64ui-v-and                   = FAILED - Test return value = 73
Test rv64ui-v-andi                  = FAILED - Test return value = 73
Test rv64ui-v-auipc                 = FAILED - Test return value = 73
Test rv64ui-v-beq                   = FAILED - Test return value = 73
Test rv64ui-v-bge                   = FAILED - Test return value = 73
Test rv64ui-v-bgeu                  = FAILED - Test return value = 73
Test rv64ui-v-blt                   = FAILED - Test return value = 73
Test rv64ui-v-bltu                  = FAILED - Test return value = 73
Test rv64ui-v-bne                   = FAILED - Test return value = 73
Test rv64ui-v-fence_i               = FAILED - Test return value = 73
Test rv64ui-v-jal                   = FAILED - Test return value = 73
Test rv64ui-v-jalr                  = FAILED - Test return value = 73
Test rv64ui-v-lb                    = FAILED - Test return value = 73
Test rv64ui-v-lbu                   = FAILED - Test return value = 73
Test rv64ui-v-ld                    = FAILED - Test return value = 73
Test rv64ui-v-lh                    = FAILED - Test return value = 73
Test rv64ui-v-lhu                   = FAILED - Test return value = 73
Test rv64ui-v-lui                   = FAILED - Test return value = 73
Test rv64ui-v-lw                    = FAILED - Test return value = 73
Test rv64ui-v-lwu                   = FAILED - Test return value = 73
Test rv64ui-v-ma_data               = FAILED - Test return value = 73
Test rv64ui-v-or                    = FAILED - Test return value = 73
Test rv64ui-v-ori                   = FAILED - Test return value = 73
Test rv64ui-v-sb                    = FAILED - Test return value = 73
Test rv64ui-v-sd                    = FAILED - Test return value = 73
Test rv64ui-v-sh                    = FAILED - Test return value = 73
Test rv64ui-v-simple                = FAILED - Test return value = 73
Test rv64ui-v-sll                   = FAILED - Test return value = 73
Test rv64ui-v-slli                  = FAILED - Test return value = 73
Test rv64ui-v-slliw                 = FAILED - Test return value = 73
Test rv64ui-v-sllw                  = FAILED - Test return value = 73
Test rv64ui-v-slt                   = FAILED - Test return value = 73
Test rv64ui-v-slti                  = FAILED - Test return value = 73
Test rv64ui-v-sltiu                 = FAILED - Test return value = 73
Test rv64ui-v-sltu                  = FAILED - Test return value = 73
Test rv64ui-v-sra                   = FAILED - Test return value = 73
Test rv64ui-v-srai                  = FAILED - Test return value = 73
Test rv64ui-v-sraiw                 = FAILED - Test return value = 73
Test rv64ui-v-sraw                  = FAILED - Test return value = 73
Test rv64ui-v-srl                   = FAILED - Test return value = 73
Test rv64ui-v-srli                  = FAILED - Test return value = 73
Test rv64ui-v-srliw                 = FAILED - Test return value = 73
Test rv64ui-v-srlw                  = FAILED - Test return value = 73
Test rv64ui-v-sub                   = FAILED - Test return value = 73
Test rv64ui-v-subw                  = FAILED - Test return value = 73
Test rv64ui-v-sw                    = FAILED - Test return value = 73
Test rv64ui-v-xor                   = FAILED - Test return value = 73
Test rv64ui-v-xori                  = FAILED - Test return value = 73
Test rv64um-p-div                   = OK
Test rv64um-p-divu                  = OK
Test rv64um-p-divuw                 = OK
Test rv64um-p-divw                  = OK
Test rv64um-p-mul                   = OK
Test rv64um-p-mulh                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mulhsu                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mulhu                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-mulw                  = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64um-p-rem                   = OK
Test rv64um-p-remu                  = OK
Test rv64um-p-remuw                 = OK
Test rv64um-p-remw                  = OK
Test rv64um-v-div                   = FAILED - Test return value = 73
Test rv64um-v-divu                  = FAILED - Test return value = 73
Test rv64um-v-divuw                 = FAILED - Test return value = 73
Test rv64um-v-divw                  = FAILED - Test return value = 73
Test rv64um-v-mul                   = FAILED - Test return value = 73
Test rv64um-v-mulh                  = FAILED - Test return value = 73
Test rv64um-v-mulhsu                = FAILED - Test return value = 73
Test rv64um-v-mulhu                 = FAILED - Test return value = 73
Test rv64um-v-mulw                  = FAILED - Test return value = 73
Test rv64um-v-rem                   = FAILED - Test return value = 73
Test rv64um-v-remu                  = FAILED - Test return value = 73
Test rv64um-v-remuw                 = FAILED - Test return value = 73
Test rv64um-v-remw                  = FAILED - Test return value = 73
Test rv64uzba-p-add_uw              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh1add              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh1add_uw           = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh2add              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh2add_uw           = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh3add              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-sh3add_uw           = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzba-p-slli_uw             = FAILED - Test return value = 17
Test rv64uzba-v-add_uw              = FAILED - Test return value = 73
Test rv64uzba-v-sh1add              = FAILED - Test return value = 73
Test rv64uzba-v-sh1add_uw           = FAILED - Test return value = 73
Test rv64uzba-v-sh2add              = FAILED - Test return value = 73
Test rv64uzba-v-sh2add_uw           = FAILED - Test return value = 73
Test rv64uzba-v-sh3add              = FAILED - Test return value = 73
Test rv64uzba-v-sh3add_uw           = FAILED - Test return value = 73
Test rv64uzba-v-slli_uw             = FAILED - Test return value = 73
Test rv64uzbb-p-andn                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-clz                 = FAILED - name 'count_leading_zeros' is not defined
Test rv64uzbb-p-clzw                = FAILED - name 'count_leading_zeros' is not defined
Test rv64uzbb-p-cpop                = FAILED - name 'pop_count' is not defined
Test rv64uzbb-p-cpopw               = FAILED - name 'pop_count' is not defined
Test rv64uzbb-p-ctz                 = FAILED - name 'count_trailing_zeros' is not defined
Test rv64uzbb-p-ctzw                = FAILED - name 'count_trailing_zeros' is not defined
Test rv64uzbb-p-max                 = OK
Test rv64uzbb-p-maxu                = OK
Test rv64uzbb-p-min                 = OK
Test rv64uzbb-p-minu                = OK
Test rv64uzbb-p-orc_b               = FAILED - name 'gorc' is not defined
Test rv64uzbb-p-orn                 = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-rev8                = FAILED - name 'grev' is not defined
Test rv64uzbb-p-rol                 = OK
Test rv64uzbb-p-rolw                = OK
Test rv64uzbb-p-ror                 = OK
Test rv64uzbb-p-rori                = OK
Test rv64uzbb-p-roriw               = OK
Test rv64uzbb-p-rorw                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-sext_b              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-sext_h              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-xnor                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-p-zext_h              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbb-v-andn                = FAILED - Test return value = 73
Test rv64uzbb-v-clz                 = FAILED - Test return value = 73
Test rv64uzbb-v-clzw                = FAILED - Test return value = 73
Test rv64uzbb-v-cpop                = FAILED - Test return value = 73
Test rv64uzbb-v-cpopw               = FAILED - Test return value = 73
Test rv64uzbb-v-ctz                 = FAILED - Test return value = 73
Test rv64uzbb-v-ctzw                = FAILED - Test return value = 73
Test rv64uzbb-v-max                 = FAILED - Test return value = 73
Test rv64uzbb-v-maxu                = FAILED - Test return value = 73
Test rv64uzbb-v-min                 = FAILED - Test return value = 73
Test rv64uzbb-v-minu                = FAILED - Test return value = 73
Test rv64uzbb-v-orc_b               = FAILED - Test return value = 73
Test rv64uzbb-v-orn                 = FAILED - Test return value = 73
Test rv64uzbb-v-rev8                = FAILED - Test return value = 73
Test rv64uzbb-v-rol                 = FAILED - Test return value = 73
Test rv64uzbb-v-rolw                = FAILED - Test return value = 73
Test rv64uzbb-v-ror                 = FAILED - Test return value = 73
Test rv64uzbb-v-rori                = FAILED - Test return value = 73
Test rv64uzbb-v-roriw               = FAILED - Test return value = 73
Test rv64uzbb-v-rorw                = FAILED - Test return value = 73
Test rv64uzbb-v-sext_b              = FAILED - Test return value = 73
Test rv64uzbb-v-sext_h              = FAILED - Test return value = 73
Test rv64uzbb-v-xnor                = FAILED - Test return value = 73
Test rv64uzbb-v-zext_h              = FAILED - Test return value = 73
Test rv64uzbc-p-clmul               = FAILED - name 'clmul' is not defined
Test rv64uzbc-p-clmulh              = FAILED - name 'clmul' is not defined
Test rv64uzbc-p-clmulr              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbc-v-clmul               = FAILED - Test return value = 73
Test rv64uzbc-v-clmulh              = FAILED - Test return value = 73
Test rv64uzbc-v-clmulr              = FAILED - Test return value = 73
Test rv64uzbs-p-bclr                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bclri               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bext                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bexti               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-binv                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-binvi               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bset                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-p-bseti               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-bclr                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-bclri               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-bext                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-bexti               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-binv                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-binvi               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-bset                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzbs-v-bseti               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fadd                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fclass              = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64uzfh-p-fcmp                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fcvt                = FAILED - 'ControlUnit' object has no attribute 'fpu'
Test rv64uzfh-p-fcvt_w              = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fdiv                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fmadd               = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-fmin                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-ldst                = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-p-move                = FAILED - Test return value = 5
Test rv64uzfh-p-recoding            = FAILED - 'ControlUnit' object has no attribute 'reg'
Test rv64uzfh-v-fadd                = FAILED - Test return value = 73
Test rv64uzfh-v-fclass              = FAILED - Test return value = 73
Test rv64uzfh-v-fcmp                = FAILED - Test return value = 73
Test rv64uzfh-v-fcvt                = FAILED - Test return value = 73
Test rv64uzfh-v-fcvt_w              = FAILED - Test return value = 73
Test rv64uzfh-v-fdiv                = FAILED - Test return value = 73
Test rv64uzfh-v-fmadd               = FAILED - Test return value = 73
Test rv64uzfh-v-fmin                = FAILED - Test return value = 73
Test rv64uzfh-v-ldst                = FAILED - Test return value = 73
Test rv64uzfh-v-move                = FAILED - Test return value = 73
Test rv64uzfh-v-recoding            = FAILED - Test return value = 73
Total: 349 Correct: 105 (30.1 %)
```

