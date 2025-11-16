"""instalar bibliotecas necessárias"""
# !pip install simpy

import simpy
import random
import statistics
from ast import Yield
from os import wait

# Tempo de chegada (taxa de minutos)
FIFO_ARRIVAL_TIME = 3.0 # Comum
PRI_ARRIVE_TIME = 15.0 # Prioridade (VIP)

# Parametros da montanha russa (servidor)
CAPACITY = 24
ENTRY_EXIT_TIME = 4.0
DEVIATION_ENTRY_EXIT = 0.5
JOURNEY_TIME = 2.0
START_LIMITY = 10.0
PLAYTIME = ENTRY_EXIT_TIME + JOURNEY_TIME

# Duração da simulação
SIMULATION_DURATION = 180

WAIT_TIME = []

# Regra da prioridade: A cada três comuns 1 prioritario
LAW_FIFO_PRI = 3

# Resource (serviço) -> montanha russa FIFO e PRI (2)

class Rollercoaster_FIFO:

  def __init__(self, env):
    self.env = env
    self.train = simpy.Resource(env, capacity=1)
    self.boarding_line = []

  def cycle_service(self):
    """Calcula o tempo de serviço e simula a duração do passeio."""

    # A 'service_time' é a parte da soma total da variavel de tempo para embarque/desembarque e a fixa de trajetoria
    service_time = (random.normalvariate(ENTRY_EXIT_TIME, DEVIATION_ENTRY_EXIT) + JOURNEY_TIME)

    yield self.env.timeout(max(0, service_time))

  def manage_shipment(self):
    """Lógica de carregamento do trem em lote (FIFO)."""

    while True:
      with self.train.request() as req:
        yield req

        wait_start = self.env.now
        while len(self.boarding_line) < CAPACITY and (self.env.now - wait_start) < START_LIMITY:
          yield self.env.timeout(1)

        crew_of_gear = []
        num_crew = min(len(self.boarding_line), CAPACITY)

        for _ in range(num_crew):
          gear = self.boarding_line.pop(0)
          wait_time = self.env.now - gear['arrive_time']
          WAIT_TIME.append(wait_time)
          crew_of_gear.append(gear['id'])

        # Inicia o brinquedo
        yield self.env.process(self.cycle_service())


        # Resource (serviço) -> montanha russa FIFO e PRI (2)

class Rollercoaster_FIFO_PRI:

  def __init__(self, env):
    self.env = env
    # Apenas um trem (roda por vez), capacidade 1
    self.train = simpy.Resource(env, capacity=1)
    self.commom_line = []
    self.priority_line = []
    self.wait_time = { 'Comum': [], 'Prioridade': [] }
    self.counter_fifo = 0

  def cycle_service(self, goers):
    """Simula o tempo que leva para o frequentador embarcar e completar o ciclo."""

    service_time = random.normalvariate(ENTRY_EXIT_TIME, 0.5)

    yield self.env.timeout(service_time + JOURNEY_TIME)

    total_wait_time = self.env.now - goers['arrival_time']
    self.wait_time[goers['type']].append(total_wait_time)

    print(f"[{self.env.now:.2f}] Frequentador {goers['id']} ({goers['type']}) saiu do brinquedo.")

  def menage_shipiment(self):
    """Lógica de gerenciamento das duas filas e prioridade"""

    while True:
      next_goer = None
      line_type_served = None

      # Regra de prioridade; Vefifica se tem clientes prioritarios e se é o momento de atender.
      if self.priority_line and (self.counter_fifo >= LAW_FIFO_PRI or not self.commom_line):
        next_goer = self.priority_line.pop(0)
        line_type_served = 'Prioridade'
        self.counter_fifo = 0
      elif self.commom_line:
        next_goer = self.commom_line.pop(0)
        line_type_served = 'Comum'
        self.counter_fifo += 1
      else:
        yield self.env.timeout(1)
        continue

      """Para simplificação, estamos tratando 1 cliente por vez,
      mas no modelo real de acentos (CAPACITY_TRAIN) o trem deveria carregar N clientes, antes de partir (cycle)."""
      with self.train.request() as req:
        # Inicia o serviço do proximo cliente
        yield req
        yield self.env.process(self.cycle_service(next_goer))

        def arrive_gears_FIFO(env, Rollercoaster_FIFO):
            gear_id = 0

            while True:
                wait_time = random.expovariate(1.0 / ENTRY_EXIT_TIME)
                yield env.timeout(wait_time)

                gear_id += 1
                customer = {
                    'id' : gear_id,
                    'arrive_time' : env.now
                }
                Rollercoaster_FIFO.boarding_line.append(customer)
                print(f"[{env.now:.2f}] Chegou Frequentador {gear_id} (comum).")

                # "Prioritario" padrão
                if random.random() < (wait_time / ENTRY_EXIT_TIME):
                    gear_id += 1
                    customer_pri = {
                        'id' : gear_id,
                        'arrive_time' : env.now
                    }
                    Rollercoaster_FIFO.boarding_line.append(customer_pri)
                    print(f"[{env.now:.2f}] Chegou Frequentador {gear_id} (prioritario).")


      def arrive_gears_FIFO_PRI(env, rollercoaster):
        """Gera os clinetes e os coloca nas filas"""

        gear_id = 0

        while True:
            # Comuns
            commom_wait_time = random.expovariate(1.0 / FIFO_ARRIVAL_TIME)
            yield env.timeout(commom_wait_time)
            gear_id += 1

            customer_commom = {
                'id' : gear_id,
                'type' : 'Comum',
                'arrival_time' : env.now
            }
            rollercoaster.commom_line.append(customer_commom)
            print(f"[{env.now:.2f}] Chegou Frequentador {gear_id} (comum).")

            if random.random() < (FIFO_ARRIVAL_TIME / PRI_ARRIVE_TIME):
                gear_id += 1
                customer_priority = {
                    'id' : gear_id,
                    'type' : 'Prioridade',
                    'arrival_time' : env.now
                }
                rollercoaster.priority_line.append(customer_priority)
                print(f"[{env.now:.2f}] Chegou Frequentador {gear_id} (prioridade).")


      def test_one():
        env = simpy.Environment()
        rollercoaster = Rollercoaster_FIFO(env)

        env.process(arrive_gears_FIFO(env, rollercoaster))
        env.process(rollercoaster.manage_shipment())

        env.run(until=SIMULATION_DURATION)

        if WAIT_TIME:
            average_waiting_time = statistics.mean(WAIT_TIME)
            waiting_max = max(WAIT_TIME)
            print(f"Total de frequentadores atendidos: {len(WAIT_TIME)}")
            print(f"Tempo médio de espera Unica: {average_waiting_time:.2f} minutos")
            print(f"Tempo maximo de espera: {waiting_max:.2f} minutos")
            print(f"Tamanho final da fila: {len(rollercoaster.boarding_line)}")
        else:
            print("Nenhum frequentador foi atendida durante a simulação.")


    def test_two():
        env = simpy.Environment()
        rollercoaster = Rollercoaster_FIFO_PRI(env)

        env.process(arrive_gears_FIFO_PRI(env, rollercoaster))
        env.process(rollercoaster.menage_shipiment())

        env.run(until=SIMULATION_DURATION)

        if rollercoaster.wait_time['Comum']:
            avarage_time_commom = statistics.mean(rollercoaster.wait_time['Comum'])
            print(f"Tempo médio de espera para comuns: {avarage_time_commom:.2f} min")
        else:
            print("Nenhum cliente comum atendido!")

        if rollercoaster.wait_time['Prioridade']:
            avarage_time_priority = statistics.mean(rollercoaster.wait_time['Prioridade'])
            print(f"Tempo médio de espera para prioritario (VIP): {avarage_time_priority:.2f} min")
        else:
            print("Nenhum cliente prioritario (VIP) atendido!")

        print(f"total de clientes comum atendidos: {len(rollercoaster.wait_time['Comum'])}")
        print(f"total de clientes prioridade (VIP) atendidos: {len(rollercoaster.wait_time['Prioridade'])}")


  def main():
    test_one()
    print("\n")
    test_two()

    if __name__ == "__main__":
        main()