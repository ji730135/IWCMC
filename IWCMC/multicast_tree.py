import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import shortest_paths
import numpy as np
from itertools import islice
from collections import defaultdict, deque
from heapq import *
import random


def k_shortest_paths(G, source, target, k, weight=None):
    return list(
        islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))


def prim(G, nbunch, start=0):
    adjacent_dict = defaultdict(list)  # 注意：defaultdict(list)必须以list做为变量
    # delays = nx.get_edge_attributes(G, "delay")
    for v1, v2 in nbunch:
        adjacent_dict[v1].append((G.edges[(v1, v2)]["delay"], v1, v2))
        adjacent_dict[v2].append((G.edges[(v1, v2)]["delay"], v2, v1))
    minu_tree = []  # 存储最小生成树结果

    visited = [start]  # 存储访问过的顶点，注意指定起始点
    adjacent_vertexs_edges = adjacent_dict[start]
    heapify(adjacent_vertexs_edges)  # 转化为小顶堆，便于找到权重最小的边
    while adjacent_vertexs_edges:
        weight, v1, v2 = heappop(adjacent_vertexs_edges)  # 权重最小的边，并同时从堆中删除。
        if v2 not in visited:
            visited.append(
                v2)  # 在used中有第一选定的点'A'，上面得到了距离A点最近的点'D',举例是5。将'd'追加到used中
            minu_tree.append((v1, v2))
            # 再找与d相邻的点，如果没有在heap中，则应用heappush压入堆内，以加入排序行列
            for next_edge in adjacent_dict[v2]:  # 找到v2相邻的边
                if next_edge[2] not in visited:  # 如果v2还未被访问过，就加入堆中
                    heappush(adjacent_vertexs_edges, next_edge)
    return minu_tree


def network(number_node=200, seed=36):
    '''
    网络模型
    生成网络拓扑
    返回值:networkx graph，无节点和边属性
    '''
    G = nx.random_internet_as_graph(number_node, seed)
    nx.write_gml(G, "AS_topology.gml")
    subax1 = plt.subplot(121)
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.savefig("topology.png")
    plt.clf()
    return G


def delay(G, seed=36, start=10, stop=200):
    rng = np.random.default_rng(seed)
    # rng = np.random.default_rng()
    # 链路赋延迟
    random_delays = rng.uniform(10, 200, nx.number_of_edges(G)).tolist()
    attrDelay_dict = dict(zip(nx.edges(G), random_delays))
    nx.set_edge_attributes(G, attrDelay_dict, "delay")
    # print(nx.get_edge_attributes(G, "delay"))
    return G


def UtilizationRate(G, seed=36, start=0, middle=0.2, stop=0.9):
    rng = np.random.default_rng(seed)
    # 链路赋利用率
    random_UtilizationRates = rng.triangular(
        0, 0.2, 0.9, size=nx.number_of_edges(G)).tolist()
    # print(random_UtilizationRate)
    attrUtilizationRate_dict = dict(zip(nx.edges(G), random_UtilizationRates))
    nx.set_edge_attributes(G, attrUtilizationRate_dict, "UtilizationRate")
    # print(nx.get_edge_attributes(G, "UtilizationRate"))
    return G


def bandwidth(G, seed=36, start=32, stop=1024):
    rng = np.random.default_rng(seed)
    # 链路赋带宽
    random_bandwidth = rng.uniform(32, 1024, nx.number_of_edges(G)).tolist()
    attrBandwidth = dict(zip(nx.edges(G), random_bandwidth))
    nx.set_edge_attributes(G, attrBandwidth, "bandwidth")
    # print(nx.get_edge_attributes(G, "bandwidth"))
    return G


def cut_branch(G, bandwidth_thor=48, UtilizationRate_thor=0.8):
    '''
    剪枝，去除不满足QoS约束的链路
    '''
    # 剪枝，去除不满足QoS约束的链路
    bandwidth_ebunch = []
    for edge, edge_attr in nx.get_edge_attributes(G, "bandwidth").items():
        if edge_attr < bandwidth_thor:
            bandwidth_ebunch.append(edge)
        # print(edge, edge_attr)
    G.remove_edges_from(bandwidth_ebunch)
    # TODO
    # 需要处理生成路径时的异常，设定松弛条件
    # print(nx.get_edge_attributes(G, "bandwidth"))
    UtilizationRate_ebunch = []
    for edge, edge_attr in nx.get_edge_attributes(G,
                                                  "UtilizationRate").items():
        if edge_attr > UtilizationRate_thor:
            UtilizationRate_ebunch.append(edge)
        # print(edge, edge_attr)
    G.remove_edges_from(UtilizationRate_ebunch)
    # print(nx.get_edge_attributes(G, "UtilizationRate"))
    return G


def get_clients(G, seed=36):
    rng = np.random.default_rng(seed)
    # 指定组播接收集合
    number_client = int(nx.number_of_nodes(G) / 5)
    clients = rng.choice(np.array(list(G)), number_client,
                         replace=False).tolist()
    return clients


def k_shortest_paths_dictionary(G, server=0, k=4):
    # print(clients)
    k_shortest_paths_dict = {}
    clients = get_clients(G)
    # 对每个client求k短路
    for client in clients:
        k_shortest_paths_dict[client] = k_shortest_paths(G,
                                                         server,
                                                         client,
                                                         k,
                                                         weight="delay")
        # for path in k_shortest_paths_dict[client]:
        #     print("k_shortest_paths for {0} to {1}: {2}".format(
        #         server, client, path))
    return k_shortest_paths_dict


def DFS(paths_dict, clients):
    # 得到备选图
    alternative_graphs = []
    indexs_seq = []
    for i in range(len(paths_dict[clients[0]])):
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
                for i in range(len(paths_dict[clients[depth]]) - 1, -1, -1):
                    stack.append((i, depth))
                    cur_indexs.append(temp_indexs.copy())
            else:
                temp_indexs.append(item)
                indexs_seq.append(temp_indexs.copy())
                # 到最后一层了就建立一个组播树
                gra = nx.Graph(name="G({})".format(len(alternative_graphs)))
                for client, path_index in zip(clients, temp_indexs):
                    paths = paths_dict[client]
                    nx.add_path(gra, paths[path_index])
                alternative_graphs.append(gra)
    # print(indexs_seq)
    return alternative_graphs


def random_pick(paths_dict, clients, number):
    alternative_graphs = []
    # 随机选择索引
    for i in range(number):
        rng2 = np.random.default_rng()
        temp_indexs = []
        for n in clients:
            temp_indexs.append(rng2.choice(np.arange(len(paths_dict[n]))))
        gra = nx.Graph(name="G({})".format(len(alternative_graphs)))
        for client, path_index in zip(clients, temp_indexs):
            paths = paths_dict[client]
            nx.add_path(gra, paths[path_index])
        alternative_graphs.append(gra)
    return alternative_graphs


def remove_cycle(G, graphs):
    # 组播树去环
    alternative_tree = []
    for g in graphs:
        if nx.is_tree(g) == False:
            minimum_spanning_tree = prim(G, g.edges, 0)
            remove_cycle_tree = nx.Graph(name=g.name)
            remove_cycle_tree.add_edges_from(minimum_spanning_tree)
            alternative_tree.append(remove_cycle_tree)
        else:
            alternative_tree.append(g)
    # for g in alternative_tree:
    #     if nx.is_tree(g) == False:
    #         print("!!!cycle in {0}.".format(nx.info(g)))
    #     else:
    #         print("no cycle in {0}.".format(nx.info(g)))
    return alternative_tree
