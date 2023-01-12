import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from networkx.algorithms.approximation import christofides, greedy_tsp
import random
from itertools import combinations, product
import os
import glob
import re
import boto3
import botocore

# ---------------------------------------------------------------------------- #
#                                  GLOBAL VAR                                  #
# ---------------------------------------------------------------------------- #
_IMG_PATH = './app/static/images'
_VDO_PATH = './app/static/videos'

BUCKET_NAME = 'cs311-tsp-resources'
ACCESS_ID = 'DO00TX3KH7FDH4JLGFX9'
SECRET_KEY = 'q76iEzYPexj6xWT93GgrqfD9jLn/O+60YO8U+8uzsgE'
REGION_NAME = 'sgp1'
ENDPOINT_URL = 'https://sgp1.digitaloceanspaces.com'
ENDPOINT = 'https://cs311-tsp-resources.sgp1.digitaloceanspaces.com'

_RANDOM_SEED = 42
_GRAPH_TYPE = False
_MIN_INTV = 1
_MAX_INTV = 50

SESSION = boto3.session.Session()
CLIENT = SESSION.client('s3',
                        endpoint_url=ENDPOINT_URL,
                        config=botocore.config.Config(s3={
                            'addressing_style': 'virtual',
                        }),
                        region_name=REGION_NAME,
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY)
# ---------------------------------------------------------------------------- #
#                                HELPER FUNCTION                               #
# ---------------------------------------------------------------------------- #


def clearDir() -> None:
    for f in glob.glob(f'{_IMG_PATH}/*'):
        os.remove(f)
    for f in glob.glob(f'{_VDO_PATH}/*'):
        os.remove(f)


def pairs(*lists: list) -> tuple:
    """
    Get unique pairing between the given lists

    Yields:
        tuple: (a,b) which a and b are from different list
    """
    for t in combinations(lists, 2):
        for pair in product(*t):
            yield pair


def tryint(string: str) -> int | str:
    """
    Return  an  int  if  possible,  or  `string`  unchanged.
    """
    try:
        return int(string)
    except ValueError:
        return string


def alphanum_key(string: str) -> list:
    """
    Turn  a  string  into  a  list  of  string  and  number  chunks.

    >>>  alphanum_key("z23a")
    ["z",  23,  "a"]

    """
    return [tryint(c) for c in re.split('([0-9]+)', string)]


def human_sort(unsorted: list) -> None:
    """
    Sort  a  list  in  the  way  that  humans  expect.
    """
    unsorted.sort(key=alphanum_key)

# ---------------------------------------------------------------------------- #
#                                  ALGORITHMS                                  #
# ---------------------------------------------------------------------------- #


def getMST(graph: nx.classes.digraph.DiGraph) -> tuple:
    """
    Get the minimum spanning tree of a graph

    Args:
        graph (nx.classes.digraph.DiGraph): a graph

    Returns:
        tuple: (mst, weight)
    """
    try:
        mst = nx.minimum_spanning_tree(graph)
        return (mst, sum([mst.edges[u, v]['weight'] for (u, v) in mst.edges()]))
    except AttributeError:
        return 'Fail to get MSTs'


def getGraph(nodes: int, edges: int = 0) -> nx.classes.digraph.DiGraph:
    """
    Generate a complete graph with randomly generated weights applied to each edge

    Args:
        nodes (int): number of nodes
        edges (int, optional): number of edges. Defaults to 0. If nothing is given, it will be a complete graph

    Returns:
        nx.classes.digraph.DiGraph: a graph
    """
    G = nx.complete_graph(nodes) if edges == 0 else nx.gnm_random_graph(
        nodes, edges, seed=_RANDOM_SEED, directed=_GRAPH_TYPE)

    for (u, v) in G.edges():
        G.edges[u, v]['weight'] = random.randint(_MIN_INTV, _MAX_INTV)

    return G


def NN_0(graph: nx.classes.digraph.DiGraph, nodes: list) -> tuple:
    """
    Using the simplest solving technique. It will look for immediate closest node

    Args:
        graph (nx.classes.digraph.DiGraph): a complete graph
        nodes (list): list of the nodes

    Returns:
        tuple: (solved_graph, tour, weight, history)
    """

    history = []

    g = nx.Graph()
    g.add_nodes_from(nodes)

    nodes = [True for _ in range(len(graph.nodes))]
    current = 0
    nodes[current] = False

    while True in nodes:

        candidates = {i: graph.edges[current, i]['weight'] for i in range(
            len(nodes)) if nodes[i] and current in graph.neighbors(i)}

        closest_candidate = min(candidates, key=candidates.get)
        g.add_edge(current, closest_candidate,
                   weight=candidates[closest_candidate])

        nodes[closest_candidate] = False
        current = closest_candidate

        history.append(set(g.edges()))

    g.add_edge(current, 0, weight=graph.edges[current, 0]['weight'])
    history.append(set(g.edges()))

    tour = nx.find_cycle(g)
    total_weight = sum([g.edges[u, v]['weight'] for (u, v) in g.edges()])

    return (g, tour, total_weight, history)


def NN_1(graph: nx.classes.digraph.DiGraph, nodes: list) -> tuple:
    """
    Match any pairs with the least cost. Then match them all up together

    Args:
        graph (nx.classes.digraph.DiGraph): a complete graph
        nodes (list): list of nodes

    Returns:
        tuple: (solved graph, tour, weight, history)
    """
    g = nx.Graph()
    g.add_nodes_from(nodes)
    history = []

    nodes = [True for _ in range(len(graph.nodes))]

    candidates = sorted({(u, v): graph.edges[u, v]['weight'] for (
        u, v) in graph.edges()}.items(), key=lambda x: x[1])

    # match any nodes that have the least cost
    for ((u, v), w) in candidates:
        if nodes[u] and nodes[v]:
            g.add_edge(u, v, weight=w)
            nodes[u], nodes[v] = False, False
            history.append(set(g.edges()))

    # for odd leftover node
    if True in nodes:
        u = nodes.index(True)
        candidates = {n: graph.edges[u, n]['weight']
                      for n in [v for v in graph.neighbors(u)]}
        min_v = min(candidates, key=candidates.get)
        g.add_edge(u, min_v, weight=candidates[min_v])
        history.append(set(g.edges()))

    # connects all sections
    partial = [p for p in nx.connected_components(g)]
    avail_nodes = [[n for n in p if g.degree(n) < 2] for p in partial]
    nodes = [True for _ in range(max(sum(avail_nodes, []))+1)]
    potential_candidates = sorted({(u, v): graph.edges[u, v]['weight'] for (
        u, v) in pairs(*avail_nodes)}.items(), key=lambda x: x[1])
    for ((u, v), w) in potential_candidates:
        if nodes[u] and nodes[v]:
            g.add_edge(u, v, weight=w)
            nodes[u], nodes[v] = False, False
            history.append(set(g.edges()))

    tour = nx.find_cycle(g)
    total_weight = sum([g.edges[u, v]['weight'] for (u, v) in g.edges()])

    return (g, tour, total_weight, history)


def NN_2(graph: nx.classes.digraph.DiGraph, nodes: list) -> tuple:
    """
    Match any possible lowest cost that won't make the solved graph closed on itself

    Args:
        graph (nx.classes.digraph.DiGraph): a complete graph
        node (list): list of nodes

    Returns:
        tuple: (solved graph, tour, weight, history)
    """
    g = nx.Graph()
    g.add_nodes_from(nodes)

    visited, removed, history = [], [], []
    candidates = sorted({(u, v): graph.edges[u, v]['weight'] for (
        u, v) in graph.edges()}.items(), key=lambda x: x[1])

    for ((u, v), w) in candidates:

        if ((u, v), w) not in visited:
            g.add_edge(u, v, weight=w)
            visited.append(((u, v), w))
            history.append(set(g.edges()))

            rm_flag = True if g.degree(u) > 2 or g.degree(v) > 2 else False
            partial = [p for p in nx.connected_components(g)]

            if len(partial) > 1:
                for p in partial:
                    if len(p) > 2:
                        sub_g = g.subgraph(p).copy()
                        if len(nx.cycle_basis(sub_g)) != 0:
                            # print('raise',nx.cycle_basis(p))
                            rm_flag = True

            if rm_flag:
                removed.append(visited[-1])
                last_edge = visited[-1][0]
                last_u, last_v = last_edge[0], last_edge[1]
                g.remove_edge(last_u, last_v)
                history.append(set(g.edges()))

            if nx.is_connected(g):
                u, v = [n for n in g.nodes() if g.degree(n) == 1]
                g.add_edge(u, v, weight=graph.edges[u, v]['weight'])
                history.append(set(g.edges()))
                break

    tour = nx.find_cycle(g)
    total_weight = sum([g.edges[u, v]['weight'] for (u, v) in g.edges()])

    return (g, tour, total_weight, history)


def nx_christofide(graph: nx.classes.digraph.DiGraph, nodes: list) -> tuple:
    """
    1. find MST T
    2. Isolate set of odd-degree vertices S
    3. Find min weight M of S
    4. Combine T + M into multigraph G
    5. Find eucldiean tour of G
    6. Generate tsp tour from the euclidean tour

    Args:
        graph (nx.classes.digraph.DiGraph): a complete graph
        nodes (list): list of nodes

    Returns:
        tuple: (solved graph, tour, weight)
    """
    g = nx.Graph()
    g.add_nodes_from(nodes)

    cycle = christofides(graph)
    edge_list = [(*i, graph.edges[i]['weight'])
                 for i in list(nx.utils.pairwise(cycle))]

    g.add_weighted_edges_from(edge_list)

    tour = nx.find_cycle(g)
    total_weight = sum([g.edges[u, v]['weight'] for (u, v) in g.edges()])

    return (g, tour, total_weight)


def nx_greedy_tsp(graph: nx.classes.digraph.DiGraph, nodes: list) -> tuple:
    """
    greedy tsp from nx

    Args:
        graph (nx.classes.digraph.DiGraph): a complete graph
        nodes (list): list of nodes

    Returns:
        tuple: (solved graph, tour, weight)
    """
    g = nx.Graph()
    g.add_nodes_from(nodes)

    cycle = greedy_tsp(graph)
    edge_list = [(*i, graph.edges[i]['weight'])
                 for i in list(nx.utils.pairwise(cycle))]
    g.add_weighted_edges_from(edge_list)

    tour = nx.find_cycle(g)
    total_weight = sum([g.edges[u, v]['weight'] for (u, v) in g.edges()])

    return (g, tour, total_weight)


def saveGraph(graph: nx.classes.digraph.DiGraph, filename: str, txt: str = '') -> bool:
    """
    Save a graph as a png image

    Args:
        graph (nx.classes.digraph.DiGraph): a graph
        filename (str): name of the image file
        txt (str, optional): what to include in the image. Defaults to ''.
    Return:
        str: path of the image
    """
    if (len(graph.nodes()) > 12):
        plt.figure(figsize=(16, 9))
    else:
        plt.figure(figsize=(9, 6))
    plt.clf()
    pos = nx.spring_layout(graph)
    pos = nx.circular_layout(graph)
    nx.draw(graph, pos, with_labels=True, font_weight='bold')
    edge_weight = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_weight)
    plt.title(label=txt)
    try:
        plt.savefig(f'{_IMG_PATH}/{filename}.png')
        with open(f'{_IMG_PATH}/{filename}.png', 'rb') as f:
            CLIENT.upload_fileobj(f, BUCKET_NAME, f'images/{filename}.png', ExtraArgs={
                'ACL': 'public-read'
            })
    except FileNotFoundError:
        return os.path.exists(_IMG_PATH)
    

    # os.remove(f'{_IMG_PATH}/{filename}.png')
    
    return f'{ENDPOINT}/images/{filename}.png'


def saveTour(graph: nx.classes.digraph.DiGraph, tour: list, filename: str) -> str:
    """
    Save the solution graph with highlighted path

    Args:
        graph (nx.classes.digraph.DiGraph): original graph
        tour (list): path of the tour
        filename (str): name of the image

    Returns:
        str: path of the image in the space
    """
    plt.clf()
    tour = set(tour)

    all_edges = {e for e in graph.edges()}

    fig, ax = plt.subplots()
    ax.axis('off')
    # fig.tight_layout()
    edge_labels = {(u, v): graph.edges[u, v]['weight'] for (u, v) in tour}

    pos = nx.spring_layout(graph)
    pos = nx.circular_layout(graph)
    nx.draw_networkx_nodes(graph, pos, node_size=400)
    nx.draw_networkx_labels(
        graph, pos, {i: i for i in graph.nodes()}, font_size=16, font_color='w')
    nx.draw_networkx_edges(
        graph, pos, edgelist=all_edges-tour, alpha=0.1,
        edge_color='g', width=1
    )
    nx.draw_networkx_edges(
        graph, pos, edgelist=tour, alpha=1.0,
        edge_color='b', width=1
    )
    nx.draw_networkx_edge_labels(
        graph, pos, edge_labels=edge_labels
    )
    plt.title(f'weight - {sum(edge_labels.values())}')
    # plt.savefig(f'{_IMG_PATH}/{filename}.png')
    
    try:
        plt.savefig(f'{_IMG_PATH}/{filename}.png')
        with open(f'{_IMG_PATH}/{filename}.png', 'rb') as f:
            CLIENT.upload_fileobj(f, BUCKET_NAME, f'images/{filename}.png', ExtraArgs={
                'ACL': 'public-read'
            })
    except FileNotFoundError:
        return os.path.exists(_IMG_PATH)
    
    return f'{ENDPOINT}/images/{filename}.png'
    # return f'{_IMG_PATH}/{filename}.png'
    # plt.show()


def getJourneyFrames(graph: nx.classes.digraph.DiGraph, journey: list) -> None:
    """
    Generate picture frames to show the steps the algorithm takes

    Args:
        graph (nx.classes.digraph.DiGraph): the original complete graph
        journey (list): a list of edges at one point in time
    """
    plt.clf()
    for f in glob.glob(f'{_IMG_PATH}/f*'):
        os.remove(f)

    all_edges = {e for e in graph.edges()}

    for i, edges in enumerate(journey):
        fig, ax = plt.subplots()
        ax.axis('off')
        # fig.tight_layout()
        edge_labels = {(u, v): graph.edges[u, v]['weight'] for (u, v) in edges}

        pos = nx.spring_layout(graph)
        pos = nx.circular_layout(graph)
        nx.draw_networkx_nodes(graph, pos, node_size=400)
        nx.draw_networkx_labels(
            graph, pos, {i: i for i in graph.nodes()}, font_size=16, font_color='w')
        nx.draw_networkx_edges(
            graph, pos, edgelist=all_edges-edges, alpha=0.1,
            edge_color='g', width=1
        )
        nx.draw_networkx_edges(
            graph, pos, edgelist=edges, alpha=1.0,
            edge_color='b', width=1
        )
        nx.draw_networkx_edge_labels(
            graph, pos, edge_labels=edge_labels
        )
        plt.title(f'weight - {sum(edge_labels.values())}')
        plt.savefig(f'{_IMG_PATH}/f{i}.png')
        plt.close()
        # plt.show()


def getPathFrames(graph: nx.classes.digraph.DiGraph, path: set) -> None:
    """
    Generate picture frames to show the path to be taken

    Args:
        graph (nx.classes.digraph.DiGraph): the original complete graph
        path (set): a set of edges to be taken
    """
    plt.clf()
    for f in glob.glob(f'{_IMG_PATH}/f*'):
        os.remove(f)

    all_edges = {e for e in graph.edges()}
    edges = set()

    for i, edge in enumerate(path):
        edges.add(edge)

        fig, ax = plt.subplots()
        ax.axis('off')
        # fig.tight_layout()
        edge_labels = {(u, v): graph.edges[u, v]['weight'] for (u, v) in edges}

        pos = nx.spring_layout(graph)
        pos = nx.circular_layout(graph)
        nx.draw_networkx_nodes(graph, pos, node_size=400)
        nx.draw_networkx_labels(
            graph, pos, {i: i for i in graph.nodes()}, font_size=16, font_color='w')
        nx.draw_networkx_edges(
            graph, pos, edgelist=all_edges-edges, alpha=0.1,
            edge_color='g', width=1
        )
        nx.draw_networkx_edges(
            graph, pos, edgelist=edges, alpha=1.0,
            edge_color='b', width=1
        )
        nx.draw_networkx_edge_labels(
            graph, pos, edge_labels=edge_labels
        )
        plt.title(f'weight - {sum(edge_labels.values())}')
        plt.savefig(f'{_IMG_PATH}/f{i}.png')
        plt.close()
        # plt.show()


def saveVideo(vdo: str) -> str:
    """
    Generate the video after using either the getJourneyFrames or getPathFrames

    Args:
        vdo (str): the name of the video
    """
    fig = plt.figure("Animation")
    plt.clf()

    ax = fig.add_subplot()
    ax.axis('off')
    # fig.tight_layout()

    files = [f for f in os.listdir(_IMG_PATH) if 'f' in f]

    if len(files) == 0:
        return

    human_sort(files)

    img = [plt.imread(f'{_IMG_PATH}/{f}') for f in files]
    frames = []  # for storing the generated images
    for i in range(len(files)):
        frames.append([plt.imshow(img[i], animated=True)])

    ani = animation.FuncAnimation(fig, frames, interval=200, blit=True,
                                    repeat_delay=1000)
    FFwriter = animation.FFMpegWriter(fps=30)
    
    ani.save(f'{_VDO_PATH}/{vdo}.mp4',  writer=FFwriter)
    
    try:
        with open(f'{_VDO_PATH}/{vdo}.mp4', 'rb') as f:
            CLIENT.upload_fileobj(f, BUCKET_NAME, f'videos/{vdo}.mp4', ExtraArgs={
                'ACL': 'public-read'
            })
    except FileNotFoundError or botocore.exceptions.ClientError:
        return os.path.exists(_VDO_PATH)
    
    for f in glob.glob(f'{_IMG_PATH}/f*'):
        os.remove(f)
        
    return f'{ENDPOINT}/videos/{vdo}.mp4'


    # return f'{_VDO_PATH}/{vdo}.mp4'
