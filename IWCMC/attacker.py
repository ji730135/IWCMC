'''
攻击模型
'''

import random
from typing import Deque
number_node  = 200

class IPVNM():
    def __init__(self):
        self.GAMMA = 0.5
        self.actionQ = []

        self.matrix = [[0 for i in range(number_node)]
                       for i in range(number_node)]
        self.degree_list = [0 for i in range(number_node)]
        self.degree_change_list = [0 for i in range(number_node)]
        self.posibility_list = [0 for i in range(number_node)]
        self.temp_posibility_list = [0 for i in range(number_node)]
        self.degree_change_list = [0 for i in range(number_node)]

        self.memory = Deque(maxlen=4000)
        self.action_size = 120
        # self.model = self._build_model()
        # discount rate for q value.
        self.gamma = 0.95
        # epsilon of action selection
        self.epsilon = 1.0
        # discount rate for epsilon.
        self.epsilon_decay = 0.9995
        # min epsilon of ε-greedy.
        self.epsilon_min = 0.01
        # actor learning rate
        self.a_lr = 0.0001
        # critic learining rate
        self.c_lr = 0.001

    def importFigure(self):  # 载入网络拓扑

        i = 0
        j = 0
        my_file = open('network.txt', 'r')
        content = my_file.readline()
        while (content):
            # content = my_file.readline()
            nodes = content.split()
            self.matrix[int(nodes[0])][int(nodes[1])] = 1
            self.matrix[int(nodes[1])][int(nodes[0])] = 1
            content = my_file.readline()
        # print("matrix", self.matrix)
        return self.matrix

    def calculateDegree(self):  # 计算节点的度 （节点所连边的个数）

        self.matrix = self.importFigure()
        # print("matrix: ", self.matrix)
        global degree_list
        i = 0
        j = 0
        degree = 0
        while (i < number_node):
            while (j < number_node):
                if (self.matrix[i][j] == 1):
                    degree = degree + 1
                j = j + 1
                self.degree_list[i] = degree
            i = i + 1
            j = 0
            degree = 0
        # print("degree list: ", self.degree_list)
        return self.degree_list

    def degreeChange(self):
        i = 0
        while (i < number_node):
            if (self.degree_list[i] >= 7):
                self.degree_change_list[i] = self.degree_list[i] * 10000
            if (self.degree_list[i] < 7 and self.degree_list[i] >= 6):
                self.degree_change_list[i] = self.degree_list[i] * 1000
            if (self.degree_list[i] < 6):
                self.degree_change_list[i] = self.degree_list[i] / 10000
            i = i + 1

    def buildingModel(self):
        sum = 0
        i = 0
        while (i < number_node):
            sum = sum + self.degree_change_list[i]
            i = i + 1
        i = 0
        while (i < number_node):
            self.posibility_list[i] = float(self.degree_change_list[i] / sum)
            i = i + 1

    def renewPossibilities(
        self, p
    ):  # 根据权重分配已经消失的概率,消失的是0.8，0.8根据权重分配到每个元素中，权重计算为0.05/0.2,0.05/0.2,0.02/0.2,0.08/0.2
        temp = self.posibility_list[p]
        for i in range(self.posibility_list.__len__()):
            # 先计算权重,如果不等于P，则计算公式为posibility_list[i] = posibility_list[i] + posibility_list[p]*(posibility_list[i]/(1-posibility_list[p])
            if (i == p):
                self.posibility_list[i] = 0
            else:
                self.posibility_list[i] = self.posibility_list[i] + \
                                          temp * (self.posibility_list[i] / (1 - temp))

    def random_pick(self, some_list):
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        for item, item_probability in zip(some_list, self.posibility_list):
            cumulative_probability += item_probability
            if x < cumulative_probability:
                break
        return item

    def selectNodes(self):  # 选取被攻击的点

        pickingNodes = [0 for i in range(int(number_node / 20))]
        selecting = 0
        selecting_list = [0 for i in range(number_node)]
        i = 0
        while (i < number_node):
            selecting_list[i] = i
            i = i + 1
        selecting = 0
        x = 0

        for i in range(number_node):  # &&&&&&&
            self.temp_posibility_list[i] = self.posibility_list[i]  # $$$$$

        while (selecting < int(number_node / 20)):
            x = self.random_pick(selecting_list)
            pickingNodes[selecting] = x
            p = selecting_list.index(x)
            # selecting_list.pop(p)
            self.renewPossibilities(p)
            selecting = selecting + 1

        for i in range(number_node):
            self.posibility_list[i] = self.temp_posibility_list[i]

        return pickingNodes

