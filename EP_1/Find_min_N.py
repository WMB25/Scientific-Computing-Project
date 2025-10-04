import math

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

def find_min_N(x, eps, Nmax=len(COEFS)):
    x = ((x + math.pi/2) % math.pi) - math.pi/2
    true = math.tan(x)
    approx = 0
    x_power = x

    for k in range(Nmax):
        approx += COEFS[k] * x_power
        error = abs(true - approx)
        if error < eps:
            return k + 1, approx, error
        
        x_power *= x*x
    return None, approx, error

    

