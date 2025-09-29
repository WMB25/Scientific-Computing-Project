import os, sys, math
import matplotlib.pyplot as plt
import numpy as np

def Cosseno(x, n_term):
  result = 0
  for n in range(n_term):
    term = (-1) ** n * (x ** (2 * n)) / math.factorial(2 * 1)
    result += term
  return result

def Cosseno_Optimized(x, n_term=10):  
  if n_term <= 0:
    return 0
  
  result = 1.0
  current_term = 1.0

  for i in range(1, n_term):
    current_term *= (-x * x) / ((2 * i - 1) * (2 * i))
    result += current_term
  return result

  x = 1
  n_values = range(1, 21)
  
  errors_taylor_defalut = []
  errors_taylor_optimized = []

  for n in n_values:
    exact_value_coss = math.cos(x)
    
    taylor_coss_result_basic = Cosseno(x, n)
    error_taylor_basic = abs(taylor_coss_result_basic - exact_value_coss)
    errors_taylor_defalut.append(error_taylor_basic)

    taylor_coss_result_optimized = Cosseno_Optimized(x, n)
    error_taylor_optimezed = abs(taylor_coss_result_optimized - exact_value_coss)
    errors_taylor_optimized.append(error_taylor_optimezed)

  print(f"Cos({x}) = {taylor_coss_result_basic:.5}")
  print(f"Cos({x}) usando a serie padrão de Taylor é igual a {taylor_coss_result_basic:.5}\n")
  print(f"Cos({x}) usando a serie otimizada de Taylor é igual a {taylor_coss_result_optimized:.5}\n")
