from networkx.algorithms import shortest_paths
import multicast_tree
import networkx as nx
import attacker
# 获取当前网络拓扑，对节点实施攻击，攻击的效果为使链路的利用率升高，延迟升高
# 先考虑域内的攻击情况
'''
对于域内来说，如果一个攻击者以一定概率随机选择节点进行攻击，使链路利用率和时延增大，那么如果我随机跳变了，整个组播树理论上是不太会受到持续的影响的
，就是说我的时延和链路利用率表现和攻击之前的差距不大或者几乎没有。画一个没有攻击时的时延和链路利用率变化图，再画一个受到攻击时的时延和链路利用率变化图。

攻击成功率也可以算，定义为攻击到了组播树上所含的网络节点的百分比

'''


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

alternative_graphs = multicast_tree.random_pick(
    multicast_tree.k_shortest_paths_dictionary(G), clients, 30)
alternative_trees = multicast_tree.remove_cycle(G, alternative_graphs)
for round in range(30):

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

    SPT_delay_without_attack = delay_of_multicast_tree(G, spt)
    print("delay of the spt without attack: {}".format(SPT_delay_without_attack))

    attacked_G = nx.Graph(attacker_G)
    nx.write_edgelist(attacked_G, "network.txt", data=False)
    attack_model = attacker.IPVNM()
    attack_model.importFigure()
    attack_model.calculateDegree()
    attack_model.degreeChange()
    attack_model.buildingModel()
    test_node = attack_model.selectNodes()
    print("attacked node: ", test_node)
    attacked_edges = attacked_G.edges(test_node)

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
    delay_with_attack = delay_of_multicast_tree(attacked_G, spt)
    print("delay of the spt with attack: {}".format(delay_with_attack))


    # 被攻击之前的组播树延迟情况
    # 选定组播树
    # multicast_tree = nx.Graph(random.choice(alternative_tree))
    tree = alternative_trees[round]
    delay_without_attack = delay_of_multicast_tree(G, tree)
    print("delay of the multicast tree without attack: {}".format(
        delay_without_attack))

    # 被攻击之后的组播树延迟情况
    delay_with_attack = delay_of_multicast_tree(attacked_G, tree)
    print("delay of the multicast tree with attack: {}".format(
        delay_with_attack))
    print()