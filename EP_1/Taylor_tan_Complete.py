import os, sys, math

def tan_manual(x, precision):
    
    x_mod = x % (2 * math.pi)
    if x_mod > math.pi:
        x_mod -= 2 * math.pi

    def factorial(n):
        if n == 0 or n == 1:
            return 1
        
        soluction = 1
        for i in range(2, n + 1):
            soluction *= i
        return (soluction)

    def Taylor_seno(x, precision):
        seno = 0
        for n in range(precision):
            coef = (-1) ** n
            numerator = x ** (2 * n + 1)
            denominador = factorial(2 * n + 1)
            term = coef * (numerator / denominador)
            seno += term
        return (seno)

    def Taylor_coseno(x, precision):
        coseno = 0
        for n in range(precision):
            coeficiente = (-1) ** n
            numerador = x ** (2 * n)
            denominador = factorial(2 * n)
            termo = coeficiente * (numerador / denominador)
            coseno += termo
        return (coseno)

    seno = Taylor_seno(x, precision)
    cosseno = Taylor_coseno(x, precision)

    if abs(cosseno) < 1e-15:
        raise ValueError("Cosseno muito próximo de zero, tangente indefinida.")
   
    return (seno / cosseno)

for x in [0, 0.1, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]:
    try:
        tan_manuel = tan_manual(x, 150)
        tan_lib = math.tan(x)
        print(f"x: {x:.1f} | tan_manual: {tan_manuel:.10f} | tan_lib: {tan_lib:.10f} | Diferença: {abs(tan_manuel - tan_lib):.10f}")
    except ValueError as e:
        print(f"x: {x:.1f} | Error: {e}")

# Taylor Tan Complete
def tan_taylor_complete_direct(x, precision):
    def factorial(n):
        soluction = 1
        for i in range(2, n + 1):
            soluction *= i
        return (soluction)
    
    def bernoulli_number(n):
        bernoulli_number = {
            0: 1,
            1: -1/2,
            2: 1/6,
            3: 0,
            4: -1/30,
            5: 0,
            6: 1/42,
            7: 0,
            8: -1/30,
            9: 0,
            10: 5/66,
            11: 0,
            12: -691/2730,
            13: 0,
            14: 7/6,
        }
        return (bernoulli_number.get(n, 0))
    
    if abs(x) >= math.pi / 2:
        x_mod = x % (2 * math.pi)
        if x_mod > math.pi / 2:
            x_mod = math.pi - x_mod
        x = x_mod

    soluction = 0
    for n in range(1, precision + 1):
        B = bernoulli_number(2 * n)
        coef = B * ((-4) ** n) * (1 - (4 ** n)) / factorial(2 * n)
        term = coef * (x ** (2 * n - 1))
        soluction += term
    return soluction

# With Otimization
def tan_taylor_complete_otimized(x, precision):
    COEF = [
        1,          
        1/3,        
        2/15,       
        17/315,     
        62/2835,    
        1382/155925,
        21844/6081075,
        929569/638512875,
    ]

    if abs(x) >= math.pi / 2:
        x_mod = x % (2 * math.pi)
        if x_mod > math.pi / 2:
            x_mod = math.pi - x_mod
        x = x_mod

    soluction = 0
    x_power = x

    for i in range(min(precision, len(COEF))):
        soluction += COEF[i] * x_power
        x_power *= x * x
    return (soluction)

for x in [0.1, 0.3, 0.5, 0.8]:
    try:
        otimizado = tan_taylor_complete_otimized(x, 8)
        math_lib = math.tan(x)
        erro = abs(otimizado - math_lib)
        print(f"tan({x:.1f}) | Otimizado: {otimizado:.8f} | Math: {math_lib:.8f} | Erro: {erro:.2e}")
    except ValueError as e:
        print(f"tan({x:.1f}) | {e}")