from scipy import stats
import random
import os
import random
import gym
from collections import deque

import numpy as np
import tensorflow as tf
from keras import Sequential
from keras.layers import Input, Dense, Lambda, concatenate
from keras.models import Model
from keras.optimizers import Adam
import keras.backend as K


class IPVNM():

    def __init__(self):
        self.GAMMA = 0.5
        self.actionQ = []

        self.matrix = [[0 for i in range(100)] for i in range(100)]
        self.degree_list = [0 for i in range(100)]
        self.degree_change_list = [0 for i in range(100)]
        self.posibility_list = [0 for i in range(100)]
        self.temp_posibility_list = [0 for i in range(100)]
        self.degree_change_list = [0 for i in range(100)]

        self.memory = deque(maxlen=4000)
        self.action_size = 120
        self.model = self._build_model()
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

    def ReadingActionSet(self):
        my_file = open('data/z3_V2.txt', 'r+')
        actionQ = []
        flow = []
        action_set = []
        action_select = []

        for i in range(9392):
            content = my_file.readline()
            if '#' in content:
                continue
            if '------' in content:
                flow_ = []
                for f in flow:
                    if f != '':
                        flow_.append(int(f))

                actionQ.append(flow_)
                flow = []
            line = content.replace('-', '')
            line = line.replace(' ', '')
            line = line.replace('>', ' ')
            line = line.strip()
            node = line.split(' ')
            flow.extend([x for x in node])
        while(len(action_set)<120):
            a = random.randint(0, 120)
            if a not in action_set:
                action_set.append(a)
                action_select.append(actionQ[a])
        print('len: ', len(action_set))
        print("action: ", action_select)



        # print(actionQ)
        self.actionQ = action_select

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

###

    def calculateDegree(self):  # 计算节点的度 （节点所连边的个数）

        self.matrix = self.importFigure()
        # print("matrix: ", self.matrix)
        global degree_list
        i = 0
        j = 0
        degree = 0
        while (i < 100):
            while (j < 100):
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
        while (i < 100):
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
        while (i < 100):
            sum = sum + self.degree_change_list[i]
            i = i + 1
        i = 0
        while (i < 100):
            self.posibility_list[i] = float(self.degree_change_list[i] / sum)
            i = i + 1

    def renewPossibilities(self, p):  # 根据权重分配已经消失的概率,消失的是0.8，0.8根据权重分配到每个元素中，权重计算为0.05/0.2,0.05/0.2,0.02/0.2,0.08/0.2
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

        pickingNodes = [0 for i in range(8)]
        selecting = 0
        selecting_list = [0 for i in range(100)]
        i = 0
        while (i < 100):
            selecting_list[i] = i
            i = i + 1
        selecting = 0
        x = 0

        for i in range(100):  # &&&&&&&
            self.temp_posibility_list[i] = self.posibility_list[i]  # $$$$$

        while (selecting < 8):
            x = self.random_pick(selecting_list)
            pickingNodes[selecting] = x
            p = selecting_list.index(x)
            # selecting_list.pop(p)
            self.renewPossibilities(p)
            selecting = selecting + 1

        for i in range(100):
            self.posibility_list[i] = self.temp_posibility_list[i]

        return pickingNodes
###



    def envfeedback(self, route_num):  # 这里算出reward, 并return 出来
        reward = 0
        hit = 0
        self.importFigure()
        self.calculateDegree()
        self.degreeChange()
        self.buildingModel()
        test_node = self.selectNodes()
        print("attack node: ", test_node)

        length = len(self.actionQ[route_num])

        for i in test_node:
            # if i==0:
            #     break
            for j in self.actionQ[route_num]:
                if i == j:
                    hit = hit + 1


        reward = (length - hit) / length * 100 - hit*10
        if hit == 0:
            reward = 150

        print(' route_num, hit num, reward:', route_num, hit, hit/length, reward)

        return reward, hit/length, length

    def _build_model(self):
        # Neural Net for Deep Q Learning
        # Sequential() creates the foundation of the layers.
        model = Sequential()
        model.add(Dense(140, name='Dense_1', input_dim=100, activation='relu'))
        model.add(Dense(160, name='Dense_2', activation='relu'))
        model.add(Dense(self.action_size, name='Dense_3', activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=0.001))
        return model

    def remember(self, state, action, reward, next_state):
        """add data to experience replay.

        Arguments:
            state: observation.
            action: action.
            reward: reward.
            next_state: next_observation.
            done: if game done.
        """
        item = (state, action, reward, next_state)
        self.memory.append(item)

    def update_epsilon(self):
        """update epsilon.
        """
        if self.epsilon >= self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def selectAction(self, state, episode):  # 选取动作  改成model.predict
        if episode <20:
            return random.randrange(self.action_size)

        elif episode > 380:
            act_values = self.model.predict(state)
            return np.argmax(act_values[0])
        else:
            if (random.random() > self.epsilon):
                act_values = self.model.predict(state)
                return np.argmax(act_values[0])
            else:
                return random.randrange(self.action_size)

    def selectAction_comp(self, state, episode):
        return random.randrange(self.action_size)

    def replay(self, batch_size):  # 抽取一个batch_size的样本进行训练
        minibatch = random.sample(self.memory, batch_size)  # 从memory里随机抽32个元素，作为片段返回

        for state, action, reward, next_state in minibatch:
            target = reward

            next_state = np.array(next_state)
            next_state = next_state.reshape(-1, 100)

            target = (reward + self.GAMMA *
                      np.amax(self.model.predict(next_state)[0]))

            target_f = self.model.predict(state)

            target_f[0][action] = target  # 更新再当前状态下当前action的值

            loss = self.model.fit(state, target_f, epochs=1, verbose=0)
            loss = np.mean(loss.history['loss'])
            return loss

    def state_process(self, action_num):
        node = []
        for i in range(100):
            node.append(0)
        for j in self.actionQ[action_num]:
            node[j] += 1
        print('state:', node)
        return node



if __name__ == '__main__':
    model = IPVNM()
    model.ReadingActionSet()
    model.importFigure()
    model.calculateDegree()

    episode = 400
    batch = 32

    for i in range(episode):
        print('********episode', episode, "*********")

        losses = []
        zero_sum = 0
        state_ = [0] * 100
        reward_sum = 0
        hit_sum = 0
        len_sum = 0

        for j in range(200):
            print('----step', j, "----")


            state = np.array(state_)

            state = state.reshape(-1, 100)
            action = model.selectAction(state, i)

            print('action: ', model.actionQ[action])

            reward, hit, route_len = model.envfeedback(action)
            reward_sum += reward
            hit_sum += hit
            len_sum += route_len

            next_state_ = model.state_process(action)
            next_state = np.array(next_state_)
            next_state = next_state.reshape(-1, 100)

            model.remember(state, action, reward, next_state)
            state_ = next_state_

            if len(model.memory) > batch:
                # loss = model.update_model(X1, X2, y)
                loss = model.replay(batch)
                model.update_epsilon()
                losses.append(loss)
                loss = np.mean(losses)

        file_name = 'data/reward_v4.txt'
        with open(file_name, 'a') as file_obj:
            file_obj.write("reward1: ")
            file_obj.write(str(reward_sum))
            file_obj.write("  hit: ")
            file_obj.write(str(hit_sum/200 + 0.01))
            file_obj.write("  len: ")
            file_obj.write(str(len_sum/200))
            file_obj.write("\n")


        #
        # print('Episode: {}/{} | reward: {} | loss: {:.3f}'.format(i, episode, reward, loss))

    # model.actor.save_weights('ddpg_actor.h5')
    # model.critic.save_weights('ddpg_critic.h5')
