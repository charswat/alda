from sptwt import Principal
from basic_aco import BasicACO
import os

if __name__ == '__main__':
    for file_name in os.listdir('./SolomonPotvinBengio'):
        file_path = os.path.join('./SolomonPotvinBengio', file_name)
        print('-' * 100)
        print('file_path: %s' % file_path)
        print('\n')
        #file_path = './SolomonPotvinBengio/rc_208.3.txt'
        ants_num = 10
        beta = 2
        q0 = 0.1
        max_iter = 200
        time =600

        graph = Principal(file_path,time)
        graph.create_from_file(file_path)
        basic_aco1 = BasicACO(graph, ants_num=ants_num, max_iter=max_iter, beta=beta, q0=q0)
        basic_aco1.run_basic_aco()




