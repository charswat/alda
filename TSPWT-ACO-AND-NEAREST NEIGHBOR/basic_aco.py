import numpy as np
import random
from sptwt import Principal
from ants import Ant
import time


class BasicACO:
    def __init__(self, graph: Principal, ants_num, max_iter, beta, q0):
        super()
        # graph Información sobre la ubicación del nodo y el tiempo de servicio
        self.graph = graph
        # ants_num Numero de hormigas
        self.ants_num = ants_num
        # max_iter El número máximo de iteraciones
        self.max_iter = max_iter

        # beta La importancia de esclarecer la información
        self.beta = beta
        # q0 Indica la probabilidad de seleccionar directamente el siguiente punto con mayor probabilidad
        self.q0 = q0
        # mejor ruta
        self.best_path_distance = None
        self.best_path = None


    def run_basic_aco(self):
        """
       El algoritmo de colonias de hormigas más básico
        :return:
        """
        start_time_total = time.time()

        #El número máximo de iteraciones
        start_iteration = 0
        for iter in range(self.max_iter):

            # Establece la distancia de viaje actual y el tiempo actual para cada hormiga
            ants = list(Ant(self.graph) for _ in range(self.ants_num))
            for k in range(self.ants_num):

                # Las hormigas necesitan visitar a todos los las ciudades
                while not ants[k].index_to_visit_empty():
                    next_index = self.select_next_index(ants[k])
                    #Determine si las condiciones de restricción aún se cumplen después de unirse al puesto,
                    if not ants[k].check_condition(next_index):
                        next_index = self.select_next_index(ants[k])
                        if not ants[k].check_condition(next_index):
                            next_index = 0

                    # Actualizar la ruta de la hormiga
                    ants[k].move_to_next_index(next_index)
                    self.graph.local_update_pheromone(ants[k].current_index, next_index)

                # Finalmente regresa a la posición 0
                ants[k].move_to_next_index(0)
                self.graph.local_update_pheromone(ants[k].current_index, 0)

            # Calcule la longitud del camino de todas las hormigas
            paths_distance = np.array([ant.total_travel_distance for ant in ants])

            # Registra la mejor ruta actual
            best_index = np.argmin(paths_distance)
            if self.best_path is None or paths_distance[best_index] < self.best_path_distance:
                self.best_path = ants[int(best_index)].travel_path
                self.best_path_distance = paths_distance[best_index]
                start_iteration = iter

                print('\n')
                print("Recorrido Hormigas", self.best_path,"tiempo", (time.time() - start_time_total),'[iteration %d]: costo %f' % (iter, self.best_path_distance))

            # Actualizar tabla de feromonas
            self.graph.global_update_pheromone(self.best_path, self.best_path_distance)

            given_iteration = self.max_iter
            if iter - start_iteration > given_iteration:
                print('\n')
                print('iteration exit:no puede encontrar solucion en %d iteration' % given_iteration)
                break

        print('\n')
        print("El menor costo obtinido con hormigas es  ", (self.best_path_distance),  "en", (time.time() - start_time_total),"segundos")

    def select_next_index(self, ant):
        """
        Seleccione el siguiente nodo
        :param ant:
        :return:
        """
        current_index = ant.current_index
        index_to_visit = ant.index_to_visit

        transition_prob = self.graph.pheromone_mat[current_index][index_to_visit] * \
            np.power(self.graph.heuristic_info_mat[current_index][index_to_visit], self.beta)
        transition_prob = transition_prob / np.sum(transition_prob)

        if np.random.rand() < self.q0:
            max_prob_index = np.argmax(transition_prob)
            next_index = index_to_visit[max_prob_index]
        else:
            # Usa el algoritmo de la ruleta o numeros aleatorios
            next_index = BasicACO.stochastic_accept(index_to_visit, transition_prob)
        return next_index

    @staticmethod
    def stochastic_accept(index_to_visit, transition_prob):
        """
        Ruleta
        :param index_to_visit: a list of N index (list or tuple)
        :param transition_prob:
        :return: selected index
        """
        # calculate N and max fitness value
        N = len(index_to_visit)

        # normalize
        sum_tran_prob = np.sum(transition_prob)
        norm_transition_prob = transition_prob/sum_tran_prob

        # select: O(1)
        while True:
            # randomly select an individual with uniform probability
            ind = int(N * random.random())
            if random.random() <= norm_transition_prob[ind]:
                return index_to_visit[ind]
