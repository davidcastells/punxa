# Paranoia #

This is an adaptation of the well-known paranoia floating point test.
We've changed the output format to a more structured (hopefully easier to read) format.

It detects some flaws that were not detected by RISC-V ISA tests


The current output is...

```
Paranoia
[PROGRESS] Program is now RUNNING tests on small integers:
[CHECK   ] -1, 0, 1/2, 1, 2, 3, 4, 5, 9, 27, 32 & 240           [OK]
[PROGRESS] Searching for Radix and Precision.
[INFO    ]                                                      Radix = 2.000000
[INFO    ] Closest relative separation found                    U1 = 1.1102230e-16
[PROGRESS] Recalculating radix and precision
[CHECK   ] confirms closest relative separation U1              [OK]
[CHECK   ] Radix confirmed.                                     [OK]
[INFO    ] Significant digits                                   Precision =  53.000000
[CHECK   ] Subtraction appears to be normalized.                [OK]
[PROGRESS] Checking for guard digit in *, /, and -.
[CHECK   ] *, /, and - appear to have guard digits.             [OK]
[PROGRESS] Checking rounding on *,/,+,-.
Multiplication appears to round correctly.
[CHECK   ] Division appears to round correctly.                 [OK]
[CHECK   ] Addition/Subtraction appears to round correctly.     [OK]
Checking for sticky bit.
[CHECK   ] Sticky bit used incorrectly or not at all.           [FLAW]

[PROGRESS] Does Multiplication commute?
[PROGRESS] Testing on 20 random pairs.
[CHECK   ] No failures found in 20 integer pairs.               [OK]
[PROGRESS] Running test of square root(x).
FAILURE:  Square root of 0.0, -0.0 or 1.0 wrong.
[PROGRESS] Testing if sqrt(X * X) == X for 20 Integers X.
[PROGRESS] Test for sqrt monotonicity.
[CHECK   ] sqrt has passed a test for Monotonicity.             [OK]
[PROGRESS] Testing whether sqrt is rounded or chopped.
Square root is neither chopped nor correctly rounded.
Observed errors run from -6.0493828e-01 to 1.1102230e-16 ulps.
[PROGRESS] Testing powers Z^i for small Integers Z and i.
DEFECT:  computing
        (2.00000000000000000e+00) ^ (3.00000000000000000e+00)
        yielded 7.99999999999999911e+00;
        which compared unequal to correct 8.00000000000000000e+00 ;
                they differ by -8.88178419700125232e-16 .
Errors like this may invalidate financial calculations
        involving interest rates.
Similar discrepancies have occurred 212 times.
[PROGRESS] Seeking Underflow thresholds UfThold and E0.
[INFO    ] Smallest strictly positive number                    E0 = 4.94066e-324
[PROGRESS] Z != 0, evaluating (Z + Z) / Z.
[INFO    ] What the machine gets for (Z+Z)/Z                    Q9 = 2.00000000000000000e+00
[CHECK   ] Assuming Over/Underflow was not signaled.            [OK]
[CHECK   ] Underflow is gradual; Abs.Err. (rndoff UfThold) < E0.[OK]
[INFO    ] Underflow threshold                                  UfThold=2.22507385850720188e-308
[PROGRESS] Checking underflow effect
[INFO    ]                                                      HInverse = 2.00000000000000000e+00
[INFO    ]                                                      Y = -1.02200000000000000e+03
[INFO    ]                                                      Y2 = -2.04400000000000000e+03
[INFO    ] actually calculating yields.                         V9 =  0.00000000000000000e+00
[CHECK   ] This computed value is O.K.                          [OK]
[PROGRESS] Testing X^((X + 1) / (X - 1)) vs. exp(2) as X -> 1.
[CHECK   ] Accuracy seems adequate.                             [OK]
[PROGRESS] Testing powers Z^Q at four nearly extreme values.
DEFECT:  computing
        (2.00000000000000000e+00) ^ (1.00700000000000000e+03)
        yielded 1.37153101719845597e+303;
        which compared unequal to correct 1.37153101719842217e+303 ;
                they differ by 3.38040579770437468e+289 .
Similar discrepancies have occurred 4 times.
[PROGRESS] Searching for Overflow threshold:
[PROGRESS] Can `Z = -Y' overflow?
[PROGRESS] Trying it on Y = -inf .
[CHECK   ] Z = -Y overflow.                                     [OK]
[INFO    ] Overflow threshold is                                V  = 1.79769313486231571e+308
[INFO    ] Overflow saturates at                                V0 = inf
[INFO    ] No Overflow should be signaled for V * 1 =           V9 = 1.79769313486231571e+308
[INFO    ]                            nor for V / 1 =           V9 = 1.79769313486231571e+308
[PROGRESS] What message and/or values does Division by Zero produce?
[INFO    ] Trying to compute 1 / 0 produces ...                 V = nan
[INFO    ] Trying to compute 0 / 0 produces ...                 V = nan

The number of  FAILUREs  encountered =       1.
The number of  DEFECTs  discovered =         2.

The arithmetic diagnosed has unacceptable Serious Defects.
Potentially fatal FAILURE may have spoiled this program's subsequent diagnoses.
END OF TEST.
```

