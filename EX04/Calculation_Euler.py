import os, sys, math

def Calulate_precision(decimal_value):
    return 10 ** (-decimal_value)

def Calculate_euler(precision):
    euler_approx = 0.0
    TERM = 1.0
    interation_count = 0

    while TERM > precision:
        euler_approx += TERM
        interation_count += 1
        TERM /= interation_count

    return euler_approx, interation_count

decimal_value_precision = int(input("Digite a precisão desejada (número de casas decimais): "))
precision_value = Calulate_precision(decimal_value_precision)
EULER, interation_nedded = Calculate_euler(precision_value)

print(f"Valor de Euler: {EULER:.10f} Quantidade de iterações: {interation_nedded} Precisão: {precision_value}")