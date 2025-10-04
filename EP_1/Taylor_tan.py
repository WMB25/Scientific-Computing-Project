import os, sys, math, time
import matplotlib.pyplot as plt

#ck
COEFS = [
    1.0,
    1/3,
    2/15,
    17/315,
    62/2835,
    1382/155925,
    21844/6081075,
    929569/638512875,
    0.00059002744094558616,
    0.00023912911424355256
    ]

def Tan_real(x):
    return math.tan(x)

def Tan_taylor(x, N):
    aprpox = 0
    for k in range(N):
        approx += COEFS[k] * (x**(2*k + 1))
    return approx

def Find_min_N(x, eps, Nmax=len(COEFS)):
    true = Tan_real(x)
    approx = 0

    for N in range(1, Nmax+1):
        approx = Tan_taylor(x, N)
        error = abs(true - approx)
        if error < eps:
            return N, approx, error        
    return None, approx, error

x = math.pi/4
real_value_tan_x = Tan_real(x)
for N in range(1, len(COEFS)+1):
    aprrox_value_tan_x = Tan_taylor(x, N)
    error = abs(real_value_tan_x - aprrox_value_tan_x)
    print(f"N={N}, tan_taylor({x})={aprrox_value_tan_x}, error={error}")

