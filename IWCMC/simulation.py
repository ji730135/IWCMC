import random
from networkx.algorithms.centrality.current_flow_betweenness import approximate_current_flow_betweenness_centrality
import multicast_tree
import networkx as nx
import attacker
import time

# 获取当前网络拓扑，对节点实施攻击，攻击的效果为使链路的利用率升高，延迟升高
# 先考虑域内的攻击情况


# 计算组播树总延迟之和
def delay_of_multicast_tree(graph, multicast_tree):

    sum_delay = 0.0
    for edge in multicast_tree.edges:
        sum_delay += graph.edges[edge]["delay"]
    return sum_delay


G = multicast_tree.network()
G = multicast_tree.delay(G)
G = multicast_tree.UtilizationRate(G)
G = multicast_tree.bandwidth(G)

clients = multicast_tree.get_clients(G)

# 攻击者视角下的网络拓扑
attacker_G = nx.Graph(G)
multicast_tree.DFS(multicast_tree.k_shortest_paths_dictionary(G),clients)
alternative_graphs = multicast_tree.random_pick(
    multicast_tree.k_shortest_paths_dictionary(G), clients, 50)
alternative_trees = multicast_tree.remove_cycle(G, alternative_graphs)
times = []
for round in range(50):
    begin = time.time()*100000
    multicast_tree.DFS(multicast_tree.k_shortest_paths_dictionary(G),clients)
    end = time.time()*100000
    times.append(end-begin)
print(times)

spt_delays_without_attack = []
spt_delays_with_attack = []
delay_without_attack = []
delay_with_attack = []

for round in range(50):

    shortest_paths_dict = {}
    # 对每个client求k短路
    shortest_paths_dict = multicast_tree.k_shortest_paths_dictionary(G, k=1)
    sptG = nx.Graph(name="SPT")
    for client in clients:
        paths = shortest_paths_dict[client]
        nx.add_path(sptG, paths[0])
    t = multicast_tree.prim(G, sptG.edges, 0)
    spt = nx.Graph(name="spt")
    spt.add_edges_from(t)

    spt_delays_without_attack.append(delay_of_multicast_tree(G, spt))
    # print("delay of the spt without attack: {}".format(SPT_delay_without_attack))

    attacked_G = nx.Graph(attacker_G)
    nx.write_edgelist(attacked_G, "network.txt", data=False)
    attack_model = attacker.IPVNM()
    attack_model.importFigure()
    attack_model.calculateDegree()
    attack_model.degreeChange()
    attack_model.buildingModel()
    attack_nodes = attack_model.selectNodes()
    # print("attacked node: ", test_node)
    attacked_edges = attacked_G.edges(attack_nodes)

    # 链路赋新延迟
    for edge in attacked_edges:
        # print("attacked edge: {}".format(edge))
        attacked_G.edges[edge]["delay"] *= 2

    # 链路赋新利用率
    for edge in list(attacked_edges):
        attacked_G.edges[edge]["UtilizationRate"] *= 2
        if attacked_G.edges[edge]["UtilizationRate"] >= 1:
            attacked_G.edges[edge]["UtilizationRate"] = 1

    # 被攻击之后的组播树延迟情况
    spt_delays_with_attack.append(delay_of_multicast_tree(attacked_G, spt))
    # print("delay of the spt with attack: {}".format(delay_with_attack))

    # 被攻击之前的组播树延迟情况
    # 选定组播树
    tree = alternative_trees[round]
    delay_without_attack.append(delay_of_multicast_tree(G, tree))
    # print("delay of the multicast tree without attack: {}".format(
    #     delay_without_attack))

    # 被攻击之后的组播树延迟情况
    delay_with_attack.append(delay_of_multicast_tree(attacked_G, tree))
    # print("delay of the multicast tree with attack: {}".format(
    #     delay_with_attack))
    # print()

# print(spt_delays_without_attack)
# print(spt_delays_with_attack)
# print(delay_without_attack)
# print(delay_with_attack)
for item in list(
        zip(spt_delays_without_attack, delay_without_attack,
            spt_delays_with_attack, delay_with_attack)):
    print(item)

defense_timeslot = 0.5
success_rates = []
attacked_G = nx.Graph(attacker_G)
nx.write_edgelist(attacked_G, "network.txt", data=False)
attack_model = attacker.IPVNM()
attack_model.importFigure()
attack_model.calculateDegree()
attack_model.degreeChange()
attack_model.buildingModel()
attack_nodes = attack_model.selectNodes()
# print("attacked node: ", test_node)
attacked_edges = attacked_G.edges(attack_nodes)
for i in range(50):
    tree = random.choice(alternative_trees)
    # rng = np.random.default_rng()
    # tree = rng.choice(alternative_trees)
    success_rates.append(
        len(set(tree.nodes).intersection(set(attack_nodes))) /
        len(attack_nodes))
print(success_rates)

import numpy as np
import matplotlib.pyplot as plt

# x1 = list(range(len(spt_delays_without_attack)))
# y1 = spt_delays_without_attack
# x2 = list(range(len(delay_without_attack)))
# y2 = delay_without_attack
# x3 = list(range(len(spt_delays_with_attack)))
# y3 = spt_delays_with_attack
# x4 = list(range(len(delay_with_attack)))
# y4 = delay_with_attack
# l1 = plt.plot(x1, y1, 'r--', label='spt_delays_without_attack')
# l2 = plt.plot(x2, y2, 'g--', label='delay_without_attack')
# l3 = plt.plot(x3, y3, 'b--', label='spt_delays_with_attack')
# l4 = plt.plot(x4, y4, 'm--', label='delay_with_attack')
# plt.plot(x1, y1, 'r-', x2, y2, 'g-', x3, y3, 'b-',x4, y4, 'm-')
# plt.title('Delays in four conditions')
# plt.xlabel('iteration')
# plt.ylabel('delay (second)')
# plt.legend()
# plt.savefig("simulation_1")
# plt.show()


DFS_delay = times
random_pick_delay = [16.8125, 8.8125, 8.21875, 7.875, 7.5625, 7.625, 13.09375, 8.59375, 8.1875, 8.3125, 8.28125, 8.09375, 8.375, 8.0625, 8.15625, 8.03125, 8.25, 10.8125, 8.46875, 8.3125, 8.375, 10.84375, 8.90625, 8.46875, 8.40625, 8.1875, 8.53125, 8.25, 8.53125, 9.625, 8.28125, 8.28125, 11.375, 9.09375, 8.125, 8.375, 8.21875, 8.15625, 8.53125, 8.15625, 9.75, 8.5, 8.21875, 10.1875, 8.75, 8.46875, 9.4375, 8.0625, 7.96875, 7.96875]

x5 =  list(range(len(DFS_delay)))
l5 = plt.plot(x5, DFS_delay, 'r--', label='DFS')
l6 = plt.plot(x5, random_pick_delay, 'b--', label='random pick')
plt.plot(x5, DFS_delay, 'r-',x5, random_pick_delay, 'b-')
plt.title('Two types of algorithms for generating multicast trees')
plt.xlabel('iteration')
plt.ylabel('time of generating multicast trees (second)')
plt.legend()
plt.savefig("simulation_3")
plt.show()
