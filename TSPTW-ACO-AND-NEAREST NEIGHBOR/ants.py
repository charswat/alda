import numpy as np
import copy
from sptwt import Principal
from threading import Event


class Ant:
    def __init__(self, graph: Principal, start_index=0):
        super()
        self.graph = graph
        self.current_index = start_index
        self.city_travel_time = 0
        self.travel_path = [start_index]
        self.arrival_time = [0]

        self.index_to_visit = list(range(graph.node_num))
        self.index_to_visit.remove(start_index)

        self.total_travel_distance = 0

    def clear(self):
        self.travel_path.clear()
        self.index_to_visit.clear()

    def move_to_next_index(self, next_index):
        # Actualizar la ruta de la hormiga
        self.travel_path.append(next_index)
        self.total_travel_distance += self.graph.node_dist_mat[self.current_index][next_index]

        dist = self.graph.node_dist_mat[self.current_index][next_index]
        self.arrival_time.append(self.city_travel_time + dist)

        if self.graph.nodes[next_index].is_depot:


            self.city_travel_time = 0

        else:

            # Si es anterior a la ventana de tiempo requerida por el cliente (ready_time), debe esperar

            self.city_travel_time += dist + max(self.graph.nodes[next_index].ready_time - self.city_travel_time - dist, 0)
            self.index_to_visit.remove(next_index)

        self.current_index = next_index

    def index_to_visit_empty(self):
        return len(self.index_to_visit) == 0

    def get_active_citys_num(self):
        return self.travel_path.count(0)-1

    def check_condition(self, next_index) -> bool:
        """

        Verifique si moverse al siguiente punto satisface las restricciones
        :param next_index:
        :return:
        """

        dist = self.graph.node_dist_mat[self.current_index][next_index]
        wait_time = max(self.graph.nodes[next_index].ready_time - self.city_travel_time - dist, 0)

        # Verifique si puede regresar a la tienda de servicio después de visitar a un pasajero determinado
        if self.city_travel_time + dist + wait_time + self.graph.node_dist_mat[next_index][0] > self.graph.nodes[0].due_time:
            return False

        # No se puede atender a los pasajeros fuera del horario establecido
        if self.city_travel_time + dist > self.graph.nodes[next_index].due_time:
            return False

        return True

