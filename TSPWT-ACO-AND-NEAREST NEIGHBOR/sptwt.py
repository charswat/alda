import numpy as np
import copy
import time


class Node:
    def __init__(self, id:  int, x: float, y: float, ready_time: float, due_time: float):
        super()
        self.id = id

        if id == 0:
            self.is_depot = True
        else:
            self.is_depot = False

        self.x = x
        self.y = y
        self.ready_time = ready_time
        self.due_time = due_time


start_time_total = time.time()
class Principal:
    def __init__(self, file_path,tiempo):
        super()
        # node_num Número de nodos
        # node_dist_mat La distancia entre nodos (matriz)
        # pheromone_mat La densidad de información en la ruta entre nodos
        self.node_num, self.nodes, self.node_dist_mat, self.citys_num \
            = self.create_from_file(file_path)
        # rho  Tasa de volatilización de feromonas
        self.rho = 0.1
        # Crea una matriz de feromonas
        self.tiempo=tiempo
        self.nnh_travel_path, self.init_pheromone_val, _ = self.nearest_neighbor_heuristic()
        self.init_pheromone_val = 1/(self.init_pheromone_val * self.node_num)

        self.pheromone_mat = np.ones((self.node_num, self.node_num)) * self.init_pheromone_val
        # visibilidad
        self.heuristic_info_mat = 1 / self.node_dist_mat

        #Leer el archivo
    def create_from_file(self, file_path):

        node_list = []

        with open(file_path, 'rt') as f:
            flag = False
            count = 0
            node_list = []
            time = []
            citys_num = 0
            confLines = f.readlines()
            for line in confLines:
                if flag == False:
                    citys_num = int(line.strip())
                    flag = True
                else:
                    if count < citys_num:
                        node_list.append([float(x) for x in line.strip().split()])
                        count += 1
                    else:
                        time.append([float(x) for x in line.strip().split()])

        node_num = len(node_list)

        nodes= []
         #pasamos la informacion al objeto Node
        for i in range(node_num):
            nodes.append(Node(int(node_list[i][0]), float(node_list[i][1]), float(node_list[i][2]), float(time[i][0]), float(time[i][1])))


        # Crear matriz de distancias
        node_dist_mat = np.zeros((node_num, node_num))
        for i in range(node_num):
            node_a = nodes[i]
            node_dist_mat[i][i] = 1e-8
            for j in range(i+1, node_num):
                node_b = nodes[j]
                node_dist_mat[i][j] = Principal.calculate_dist(node_a, node_b)
                node_dist_mat[j][i] = node_dist_mat[i][j]
        return node_num, nodes, node_dist_mat, citys_num
    #calculamos la distancia
    @staticmethod
    def calculate_dist(node_a, node_b):
        return np.linalg.norm((node_a.x - node_b.x, node_a.y - node_b.y))

    def local_update_pheromone(self, start_ind, end_ind):
        self.pheromone_mat[start_ind][end_ind] = (1-self.rho) * self.pheromone_mat[start_ind][end_ind] + \
                                                  self.rho * self.init_pheromone_val

    def global_update_pheromone(self, best_path, best_path_distance):
        """
        Actualizar la matriz de feromonas
        :return:
        """
        self.pheromone_mat = (1-self.rho) * self.pheromone_mat

        current_ind = best_path[0]
        for next_ind in best_path[1:]:
            self.pheromone_mat[current_ind][next_ind] += self.rho/best_path_distance
            current_ind = next_ind
    #metodo el vecino mas cercano
    def nearest_neighbor_heuristic(self, max_city_num=None):
        index_to_visit = list(range(1, self.node_num))
        current_index = 0
        current_time = 0
        travel_distance = 0
        travel_path = [0]

        if max_city_num is None:
            max_city_num = self.node_num

        while len(index_to_visit) > 0 and max_city_num > 0:
            nearest_next_index = self._cal_nearest_next_index(index_to_visit, current_index, current_time)

            if nearest_next_index is None:
                travel_distance += self.node_dist_mat[current_index][0]

                current_time = 0
                travel_path.append(0)
                current_index = 0

                max_city_num -= 1
            else:

                dist = self.node_dist_mat[current_index][nearest_next_index]
                wait_time = max(self.nodes[nearest_next_index].ready_time - current_time - dist, 0)

                current_time += dist + wait_time
                index_to_visit.remove(nearest_next_index)

                travel_distance += self.node_dist_mat[current_index][nearest_next_index]
                travel_path.append(nearest_next_index)
                current_index = nearest_next_index
        #Finalmente regresa a deposito
        travel_distance += self.node_dist_mat[current_index][0]
        travel_path.append(0)

        citys_num = travel_path.count(0)-1

        print("Recorido vecino",travel_path,"costo", travel_distance, "tiempo",(time.time() - start_time_total))
        return travel_path, travel_distance, citys_num

    def _cal_nearest_next_index(self, index_to_visit, current_index, current_time):
        """
        Encuentre el siguiente index accesible más cercano
        :param index_to_visit:
        :return:
        """
        nearest_ind = None
        nearest_distance = None

        for next_index in index_to_visit:

            dist = self.node_dist_mat[current_index][next_index]
            wait_time = max(self.nodes[next_index].ready_time - current_time - dist, 0)

            # Verifique si puede regresar a la al nodo anterior
            if current_time + dist + wait_time +  self.node_dist_mat[next_index][0] > self.nodes[0].due_time:
                continue

            # No se puede atender fuera el horario.
            if current_time + dist > self.nodes[next_index].due_time:
                continue

            if nearest_distance is None or self.node_dist_mat[current_index][next_index] < nearest_distance:
                nearest_distance = self.node_dist_mat[current_index][next_index]
                nearest_ind = next_index

        return nearest_ind


