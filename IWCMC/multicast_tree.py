import networkx as nx
import matplotlib.pyplot as plt
from networkx.classes.function import is_empty
import numpy as np
from itertools import islice


def k_shortest_paths(G, source, target, k, weight=None):
    # TODO
    # 需要处理生成路径时的异常，设定松弛条件
    return list(
        islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))


'''
网络模型
'''
# 生成网络拓扑
number_node = 10
seed = 3
G = nx.random_internet_as_graph(number_node, seed)
nx.write_gml(G, "AS_topology.gml")
subax1 = plt.subplot(121)
nx.draw(G, with_labels=True, font_weight='bold')
plt.savefig("topology.png")
plt.clf()

rng = np.random.default_rng(seed)
# 链路赋延迟
random_delays = rng.uniform(10, 200, nx.number_of_edges(G)).tolist()
attrDelay_dict = dict(zip(nx.edges(G), random_delays))
nx.set_edge_attributes(G, attrDelay_dict, "delay")
# print(nx.get_edge_attributes(G, "delay"))

# 链路赋利用率
random_UtilizationRates = rng.triangular(0,
                                         0.2,
                                         1.0,
                                         size=nx.number_of_edges(G)).tolist()
# print(random_UtilizationRate)
attrUtilizationRate_dict = dict(zip(nx.edges(G), random_UtilizationRates))
nx.set_edge_attributes(G, attrUtilizationRate_dict, "UtilizationRate")
# print(nx.get_edge_attributes(G, "UtilizationRate"))

# 链路赋带宽
random_bandwidth = rng.uniform(32, 1024, nx.number_of_edges(G)).tolist()
attrBandwidth = dict(zip(nx.edges(G), random_bandwidth))
nx.set_edge_attributes(G, attrBandwidth, "bandwidth")
# print(nx.get_edge_attributes(G, "bandwidth"))
'''
生成组播树
'''
# 剪枝，去除不满足QoS约束的链路
bandwidth_ebunch = []
for edge, edge_attr in nx.get_edge_attributes(G, "bandwidth").items():
    if edge_attr < 33:
        bandwidth_ebunch.append(edge)
    # print(edge, edge_attr)
# G.remove_edges_from(bandwidth_ebunch)
# print(nx.get_edge_attributes(G, "bandwidth"))
UtilizationRate_ebunch = []
for edge, edge_attr in nx.get_edge_attributes(G, "UtilizationRate").items():
    if edge_attr > 0.99:
        UtilizationRate_ebunch.append(edge)
    # print(edge, edge_attr)
# G.remove_edges_from(UtilizationRate_ebunch)
# print(nx.get_edge_attributes(G, "UtilizationRate"))

# 指定组播源
server = 0
k = 4
# 指定组播接收集合
number_client = int(nx.number_of_nodes(G) / 5)
clients = rng.choice(np.array(list(G)), number_client, replace=False).tolist()
# print(clients)
k_shortest_paths_dict = {}
# 对每个client求k短路
for client in clients:
    k_shortest_paths_dict[client] = k_shortest_paths(G,
                                                     server,
                                                     client,
                                                     k,
                                                     weight="delay")
    # for path in k_shortest_paths_dict[client]:
    #     print("{0} to {1}: {2}".format(server, client, path))

# 得到备选树
alternative_trees = []
indexs_seq = []
for i in range(len(k_shortest_paths_dict[clients[0]])):
    stack = []
    stack.append((i, 0))
    cur_indexs = [[]]
    # 栈不空就是没有遍历完
    while len(stack) != 0:
        # 取出当前栈顶元素
        item, depth = stack.pop()
        temp_indexs = cur_indexs.pop()
        # 如果还没访问到最后一层
        if depth < len(clients) - 1:
            temp_indexs.append(item)
            depth += 1
            # 有子节点就是k个。这里入栈，所以倒着入栈，就可以正着出栈
            for i in range(
                    len(k_shortest_paths_dict[clients[depth]]) - 1, -1, -1):
                stack.append((i, depth))
                cur_indexs.append(temp_indexs.copy())
        else:
            temp_indexs.append(item)
            indexs_seq.append(temp_indexs.copy())
            # 到最后一层了就建立一个组播树
            G = nx.Graph(name="G({})".format(len(alternative_trees)))
            for client, path_index in zip(clients, temp_indexs):
                paths = k_shortest_paths_dict[client]
                nx.add_path(G, paths[path_index])
            alternative_trees.append(G)
# print(indexs_seq)

# 组播树去环
no_cycle = 0
for g in alternative_trees:
    if len(nx.cycle_basis(g)) > 0:
        # print("cycle in {0}.".format(nx.info(g)))
        continue
    else:
        no_cycle += 1
        print("!!!!!!!!!!!!!!!!!!!!!!!!!no cycle in {0}.".format(nx.info(g)))
print(no_cycle)
print(len(alternative_trees))