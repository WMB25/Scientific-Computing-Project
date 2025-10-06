import matplotlib.pyplot as plt
import numpy as np

# ======================
# Dados
# ======================
mes = np.arange(12) + 1  # meses de 1 a 12

creme_facial = np.array([2500, 2630, 2140, 3400, 3600, 2760, 2980, 3700, 3540, 1990, 2340, 2900])
limpeza_facial = np.array([1500, 1200, 1340, 1130, 1740, 1555, 1120, 1400, 1780, 1890, 2100, 1760])
pasta_dentaria = np.array([5200, 5100, 4550, 5870, 4560, 4890, 4780, 5860, 6100, 8300, 7300, 7400])
sabonete = np.array([9200, 6100, 9550, 8870, 7760, 7490, 8980, 9960, 8100, 10300, 13300, 14400])
shampoo = np.array([1200, 2100, 3550, 1870, 1560, 1890, 1780, 2860, 2100, 2300, 2400, 1800])
hidratante = np.array([1500, 1200, 1340, 1130, 1740, 1555, 1120, 1400, 1780, 1890, 2100, 1760])

# ======================
# 1. Total de produtos vendidos por mês (linha)
# ======================
total_mes = creme_facial + limpeza_facial + pasta_dentaria + sabonete + shampoo + hidratante
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(mes, total_mes, color='royalblue', linewidth=2, marker='o')
ax.set_title('Total de Produtos Vendidos por Mês')
ax.set_xlabel('Mês')
ax.set_ylabel('Total Vendido')
plt.tight_layout()
plt.show()

# ======================
# 2. Todos os produtos vendidos por mês (linhas)
# ======================
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(mes, creme_facial, linewidth=2, label='Creme Facial')
ax.plot(mes, limpeza_facial, linewidth=2, label='Limpeza Facial')
ax.plot(mes, pasta_dentaria, linewidth=2, label='Pasta Dentária')
ax.plot(mes, sabonete, linewidth=2, label='Sabonete')
ax.plot(mes, shampoo, linewidth=2, label='Shampoo')
ax.plot(mes, hidratante, linewidth=2, label='Hidratante')
ax.set_title('Produtos Vendidos por Mês')
ax.set_xlabel('Mês')
ax.set_ylabel('Quantidade Vendida')
ax.legend(fontsize=8)
plt.tight_layout()
plt.show()

# ======================
# 3. Comparativo Creme Facial x Limpeza Facial (barras)
# ======================
largura = 0.35
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(mes - largura/2, creme_facial, width=largura, color='skyblue', label='Creme Facial')
ax.bar(mes + largura/2, limpeza_facial, width=largura, color='orange', label='Limpeza Facial')
ax.set_title('Comparativo: Creme Facial x Limpeza Facial')
ax.set_xlabel('Mês')
ax.set_ylabel('Quantidade Vendida')
ax.legend(fontsize=9)
plt.tight_layout()
plt.show()

# ======================
# 4. Histograma (faixas de vendas totais)
# ======================
bins = [1000, 2000, 3000, 4000, 5000, 10000, 15000]
fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(total_mes, bins=bins, edgecolor='black', color='lightgreen')
ax.set_title('Histograma - Faixas de Quantidade Vendida por Mês')
ax.set_xlabel('Faixas de Vendas (1000–1999, 2000–2999, ...)')
ax.set_ylabel('Quantidade de Meses')
plt.tight_layout()
plt.show()

# ======================
# 5. Pizza (% de vendas no ano por produto)
# ======================
total_ano = np.array([
    creme_facial.sum(),
    limpeza_facial.sum(),
    pasta_dentaria.sum(),
    sabonete.sum(),
    shampoo.sum(),
    hidratante.sum()
])
labels = ['Creme Facial', 'Limpeza Facial', 'Pasta Dentária', 'Sabonete', 'Shampoo', 'Hidratante']
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(total_ano, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
ax.set_title('Percentual de Vendas no Ano por Produto')
plt.tight_layout()
plt.show()
