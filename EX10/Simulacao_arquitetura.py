"""instalar bibliotecas necessárias"""
# pip install simpy

import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Tempo de chegada (taxa de minutos)
FIFO_ARRIVAL_TIME = 3.0   # Comum
PRI_ARRIVE_TIME = 15.0    # Prioridade (VIP)
SR_ARRIVE_TIME = 15.5     # Preferencial

# Parâmetros da montanha russa (servidor)
QTD_TRAIN = 6
SETS_TRAIN = 4
TOTAL_CAPACITY = QTD_TRAIN * SETS_TRAIN  # 6 trens x 4 pessoas = 24
ENTRY_EXIT_TIME = 4.0
DEVIATION_ENTRY_EXIT = 0.5
JOURNEY_TIME = 2.0
START_LIMITY = 10.0
PLAYTIME = ENTRY_EXIT_TIME + JOURNEY_TIME

# Duração da simulação
SIMULATION_DURATION = 180

# Métricas FIFO
WAIT_TIME = []

# Regra da prioridade: a cada dois comuns, 1 prioritário
LAW_FIFO_PRI = 2
# Regra preferencial: a cada três pessoas (comum + prioridade), 1 preferencial
LAW_SR = 3



#  ARQUITETURA FIFO
class Rollercoaster_FIFO:
    def __init__(self, env):
        self.env = env
        self.train = simpy.Resource(env, capacity=1)
        self.boarding_line = []

    def cycle_service(self):
        """Tempo de serviço: embarque/desembarque + trajeto."""
        service_time = random.normalvariate(ENTRY_EXIT_TIME, DEVIATION_ENTRY_EXIT) + JOURNEY_TIME
        yield self.env.timeout(max(0, service_time))

    def manage_shipment(self):
        """Carregamento do trem em lote (FIFO)."""
        while True:
            with self.train.request() as req:
                yield req

                # espera até encher ou até o limite de espera
                wait_start = self.env.now
                while len(self.boarding_line) < TOTAL_CAPACITY and (self.env.now - wait_start) < START_LIMITY:
                    yield self.env.timeout(1)

                crew_of_gear = []
                num_crew = min(len(self.boarding_line), TOTAL_CAPACITY)

                for _ in range(num_crew):
                    gear = self.boarding_line.pop(0)
                    wait_time = self.env.now - gear['arrive_time']
                    WAIT_TIME.append(wait_time)
                    crew_of_gear.append(gear['id'])

                # não roda trem vazio
                if not crew_of_gear:
                    yield self.env.timeout(1)
                    continue

                yield self.env.process(self.cycle_service())



#  ARQUITETURA FIFO + PRI
class Rollercoaster_FIFO_PRI:
    def __init__(self, env):
        self.env = env
        self.train = simpy.Resource(env, capacity=1)
        self.commom_line = []
        self.priority_line = []

        # métricas
        self.wait_queue = {'Comum': [], 'Prioridade': []}
        self.time_in_system = {'Comum': [], 'Prioridade': []}

        # controle da regra
        self.counter_fifo = 0

    def cycle_service(self, goers):
        """Tempo do trem com o grupo (FIFO+PRI)."""
        service_time = random.normalvariate(ENTRY_EXIT_TIME, DEVIATION_ENTRY_EXIT) + JOURNEY_TIME
        yield self.env.timeout(service_time)

        # tempo no sistema = agora - arrival_time
        for goer in goers:
            total_time = self.env.now - goer['arrival_time']
            self.time_in_system[goer['type']].append(total_time)

    def menage_shipiment(self):
        """Gerenciamento das duas filas com prioridade."""
        while True:
            if not (self.commom_line or self.priority_line):
                yield self.env.timeout(1)
                continue

            boarding_group = []

            with self.train.request() as req:
                yield req

                while len(boarding_group) < TOTAL_CAPACITY and (self.commom_line or self.priority_line):
                    next_goer = None

                    # regra de prioridade (VIP depois de LAW_FIFO_PRI comuns)
                    if self.priority_line and (self.counter_fifo >= LAW_FIFO_PRI or not self.commom_line):
                        next_goer = self.priority_line.pop(0)
                        self.counter_fifo = 0
                    elif self.commom_line:
                        next_goer = self.commom_line.pop(0)
                        self.counter_fifo += 1

                    if next_goer is None:
                        break

                    # tempo na fila
                    wait_queue = self.env.now - next_goer['arrival_time']
                    self.wait_queue[next_goer['type']].append(wait_queue)

                    boarding_group.append(next_goer)

                if not boarding_group:
                    yield self.env.timeout(1)
                    continue

                yield self.env.process(self.cycle_service(boarding_group))



#  ARQUITETURA FIFO + PRI + SR
class Rollercoaster_FIFO_PRI_SR:
    def __init__(self, env):
        self.env = env
        self.train = simpy.Resource(env, capacity=1)

        self.commom_line = []
        self.priority_line = []
        self.special_line = []

        self.counter_commom_line = 0
        self.counter_total_served = 0

        self.wait_queue = {'Comum': [], 'Prioridade': [], 'Preferencial': []}
        self.time_in_system = {'Comum': [], 'Prioridade': [], 'Preferencial': []}

        self.queue_size_history = []

    def log_queue_sizes(self):
        """Guarda o tamanho atual das filas para métricas/gráficos."""
        self.queue_size_history.append(
            (self.env.now, len(self.commom_line), len(self.priority_line), len(self.special_line))
        )

    def cycle_service(self, group):
        """Simula o trem com um grupo de passageiros."""
        service_time = random.normalvariate(ENTRY_EXIT_TIME, DEVIATION_ENTRY_EXIT) + JOURNEY_TIME
        yield self.env.timeout(max(0, service_time))

        for goer in group:
            time_in_system = self.env.now - goer['arrival_time']
            self.time_in_system[goer['type']].append(time_in_system)

    def choose_next_passenger(self):
        """Escolhe o próximo passageiro respeitando as regras."""

        # 1) Preferencial (SR) – prioridade mais alta
        if self.special_line and (self.counter_total_served >= LAW_SR):
            goer = self.special_line.pop(0)
            self.counter_total_served = 0
            return goer

        # 2) Prioridade (VIP)
        if self.priority_line and (self.counter_commom_line >= LAW_FIFO_PRI or not self.commom_line):
            goer = self.priority_line.pop(0)
            self.counter_commom_line = 0
            self.counter_total_served += 1
            return goer

        # 3) Comum
        if self.commom_line:
            goer = self.commom_line.pop(0)
            self.counter_commom_line += 1
            self.counter_total_served += 1
            return goer

        return None

    def manager_shipment(self):
        """Gerenciamento das três filas."""
        while True:
            if not (self.commom_line or self.priority_line or self.special_line):
                self.log_queue_sizes()
                yield self.env.timeout(1)
                continue

            with self.train.request() as req:
                yield req
                boarding_group = []

                while len(boarding_group) < TOTAL_CAPACITY and (self.commom_line or self.priority_line or self.special_line):
                    passenger = self.choose_next_passenger()
                    if passenger is None:
                        break

                    wait_time = self.env.now - passenger['queue_entry_time']
                    self.wait_queue[passenger['type']].append(wait_time)

                    boarding_group.append(passenger)

            self.log_queue_sizes()

            if not boarding_group:
                yield self.env.timeout(1)
                continue

            yield self.env.process(self.cycle_service(boarding_group))



#  PROCESSOS DE CHEGADA
def arrive_gears_FIFO(env, rollercoaster):
    """Chegadas para arquitetura FIFO."""
    gear_id = 0

    while True:
        wait_time = random.expovariate(1.0 / ENTRY_EXIT_TIME)
        yield env.timeout(wait_time)

        gear_id += 1
        customer = {
            'id': gear_id,
            'arrive_time': env.now
        }
        rollercoaster.boarding_line.append(customer)


def arrive_gears_FIFO_PRI(env, rollercoaster):
    """Gera os clientes e os coloca nas filas (FIFO+PRI)."""
    gear_id = 0

    while True:
        # Comuns
        commom_wait_time = random.expovariate(1.0 / FIFO_ARRIVAL_TIME)
        yield env.timeout(commom_wait_time)
        gear_id += 1

        customer_commom = {
            'id': gear_id,
            'type': 'Comum',
            'arrival_time': env.now,
            'queue_entry_time': env.now
        }
        rollercoaster.commom_line.append(customer_commom)

        # VIP com certa probabilidade
        if random.random() < (FIFO_ARRIVAL_TIME / PRI_ARRIVE_TIME):
            gear_id += 1
            customer_priority = {
                'id': gear_id,
                'type': 'Prioridade',
                'arrival_time': env.now,
                'queue_entry_time': env.now
            }
            rollercoaster.priority_line.append(customer_priority)


def arrive_gears_FIFO_PRI_SR(env, rollercoaster):
    """Chegadas para arquitetura FIFO+PRI+SR."""
    current_id = 0

    while True:
        commom_wait_time = random.expovariate(1.0 / FIFO_ARRIVAL_TIME)
        yield env.timeout(commom_wait_time)
        current_id += 1

        customer_commom = {
            'id': current_id,
            'type': 'Comum',
            'arrival_time': env.now,
            'queue_entry_time': env.now
        }
        rollercoaster.commom_line.append(customer_commom)

        # Probabilidade de chegar um VIP
        if random.random() < (FIFO_ARRIVAL_TIME / PRI_ARRIVE_TIME):
            current_id += 1
            customer_priority = {
                'id': current_id,
                'type': 'Prioridade',
                'arrival_time': env.now,
                'queue_entry_time': env.now
            }
            rollercoaster.priority_line.append(customer_priority)

        # Probabilidade de chegar preferencial
        if random.random() < (FIFO_ARRIVAL_TIME / SR_ARRIVE_TIME):
            current_id += 1
            customer_special = {
                'id': current_id,
                'type': 'Preferencial',
                'arrival_time': env.now,
                'queue_entry_time': env.now
            }
            rollercoaster.special_line.append(customer_special)


# =======================
#  GRÁFICOS
# =======================
def plot_metrics(rollercoaster):
    """Gráficos para FIFO+PRI+SR."""
    types = ['Comum', 'Prioridade', 'Preferencial']
    avg_queue = []
    avg_system = []

    for t in types:
        avg_queue.append(statistics.mean(rollercoaster.wait_queue[t]) if rollercoaster.wait_queue[t] else 0)
        avg_system.append(statistics.mean(rollercoaster.time_in_system[t]) if rollercoaster.time_in_system[t] else 0)

    # 1) Tempo na FILA
    plt.figure()
    plt.bar(types, avg_queue)
    plt.title("Tempo médio na FILA por tipo")
    plt.xlabel("Tipo")
    plt.ylabel("Tempo (min)")
    plt.show()

    # 2) Tempo no SISTEMA
    plt.figure()
    plt.bar(types, avg_system)
    plt.title("Tempo médio no SISTEMA por tipo")
    plt.xlabel("Tipo")
    plt.ylabel("Tempo (min)")
    plt.show()

    # 3) Evolução dos tamanhos das filas
    if rollercoaster.queue_size_history:
        times, fifo_sizes, pri_sizes, pref_sizes = zip(*rollercoaster.queue_size_history)

        plt.figure()
        plt.plot(times, fifo_sizes, label="Comum")
        plt.plot(times, pri_sizes, label="Prioridade")
        plt.plot(times, pref_sizes, label="Preferencial")
        plt.title("Tamanho das filas ao longo do tempo")
        plt.xlabel("Tempo (min)")
        plt.ylabel("Tamanho da fila")
        plt.legend()
        plt.show()


def plot_metrics_fifo_pri(rollercoaster):
    types = ['Comum', 'Prioridade']
    avg_queue = []
    avg_system = []

    for t in types:
        avg_queue.append(statistics.mean(rollercoaster.wait_queue[t]) if rollercoaster.wait_queue[t] else 0)
        avg_system.append(statistics.mean(rollercoaster.time_in_system[t]) if rollercoaster.time_in_system[t] else 0)

    # Fila
    plt.figure()
    plt.bar(types, avg_queue)
    plt.title("FIFO+PRI - Tempo médio na FILA")
    plt.xlabel("Tipo")
    plt.ylabel("Tempo (min)")
    plt.show()

    # Sistema
    plt.figure()
    plt.bar(types, avg_system)
    plt.title("FIFO+PRI - Tempo médio no SISTEMA")
    plt.xlabel("Tipo")
    plt.ylabel("Tempo (min)")
    plt.show()


def plot_metrics_fifo():
    if not WAIT_TIME:
        print("Sem dados para FIFO.")
        return

    avg_wait = statistics.mean(WAIT_TIME)
    plt.figure()
    plt.bar(['FIFO'], [avg_wait])
    plt.title("FIFO - Tempo médio na FILA")
    plt.ylabel("Tempo (min)")
    plt.show()



#  TESTES
def test_fifo():
    env = simpy.Environment()
    rollercoaster = Rollercoaster_FIFO(env)

    env.process(arrive_gears_FIFO(env, rollercoaster))
    env.process(rollercoaster.manage_shipment())

    env.run(until=SIMULATION_DURATION)

    if WAIT_TIME:
        average_waiting_time = statistics.mean(WAIT_TIME)
        waiting_max = max(WAIT_TIME)
        print(f"Total de frequentadores atendidos: {len(WAIT_TIME)}")
        print(f"Tempo médio de espera (FIFO): {average_waiting_time:.2f} minutos")
        print(f"Tempo máximo de espera: {waiting_max:.2f} minutos")
        print(f"Tamanho final da fila: {len(rollercoaster.boarding_line)}")
        plot_metrics_fifo()
    else:
        print("Nenhum frequentador foi atendido durante a simulação.")


def test_fifo_pri():
    env = simpy.Environment()
    rollercoaster = Rollercoaster_FIFO_PRI(env)

    env.process(arrive_gears_FIFO_PRI(env, rollercoaster))
    env.process(rollercoaster.menage_shipiment())

    env.run(until=SIMULATION_DURATION)

    plot_metrics_fifo_pri(rollercoaster)

    print(f"Total de clientes comuns atendidos: {len(rollercoaster.wait_queue['Comum'])}")
    print(f"Total de clientes prioridade (VIP) atendidos: {len(rollercoaster.wait_queue['Prioridade'])}")


def test_fifo_pri_sr():
    env = simpy.Environment()
    rollercoaster = Rollercoaster_FIFO_PRI_SR(env)

    env.process(arrive_gears_FIFO_PRI_SR(env, rollercoaster))
    env.process(rollercoaster.manager_shipment())

    env.run(until=SIMULATION_DURATION)

    plot_metrics(rollercoaster)

    if rollercoaster.queue_size_history:
        times, fifo_sizes, pri_sizes, pref_sizes = zip(*rollercoaster.queue_size_history)
        print(f"Tamanho médio fila comum: {statistics.mean(fifo_sizes):.2f}")
        print(f"Tamanho médio fila prioridade: {statistics.mean(pri_sizes):.2f}")
        print(f"Tamanho médio fila preferencial: {statistics.mean(pref_sizes):.2f}")


def main():
    print("=== FIFO TESTE ===")
    test_fifo()
    print("\n=== FIFO+PRI TESTE ===")
    test_fifo_pri()
    print("\n=== FIFO+PRI+SR TESTE ===")
    test_fifo_pri_sr()


if __name__ == "__main__":
    main()
