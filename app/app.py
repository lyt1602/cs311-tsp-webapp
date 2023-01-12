from flask import Flask, render_template, request, redirect
import mypack

app = Flask(__name__)

MAX_JRNY = 100
MIN_NODE, MAX_NODE = 5,10
G, A, W, T, G, NODES, graph_path, solution_path, journey_path, tour_path, mst_path = [None for _ in range(11)]

MODELS = {
    f'NN_{i}': {
        'A': None,
        'T': None,
        'W': None,
        'H': None,
        'Solution': None,
        'Journey': None,
        'Tour': None
    }
    for i in range(3)
}

FUNC = {
    'NN_0': mypack.NN_0,
    'NN_1': mypack.NN_1,
    'NN_2': mypack.NN_2,
    'NX_CHRISTOFIDE': mypack.nx_christofide,
    'NX_GREEDY': mypack.nx_greedy_tsp
}

@app.route('/', methods=['GET', 'POST'])
def home():
    global G, NODES, FUNC, MODELS, A, W, T, H, graph_path, solution_path, journey_path, tour_path, mst_path
    print(NODES)

    if request.method == 'POST':
        request_args = list(request.form.to_dict().values())
        
        if request_args[1] == 'GO':
            try:
                NODES = int(request_args[0])
            except:
                NODES = 1
            
        func = request_args[1]
        if func == 'GO':
            G = mypack.getGraph(NODES)
            graph_path = mypack.saveGraph(G, 'mygraph')
            return render_template('index.html', graph_path=graph_path)
        
        elif func == 'REPORT':
            return redirect('/report')
        
        elif func == 'ALGO':
            return redirect('/algorithm')
        
        elif func == 'COMPARE':
            MST = mypack.getMST(G)
            if isinstance(MST, tuple):
                mst_path = mypack.saveGraph(MST[0], 'mst')
            
            for f in ['NN_0', 'NN_1', 'NN_2']:
                print(NODES)
                try:
                    NODES = len(list(G.nodes())) if NODES == None else NODES
                except AttributeError:
                    print(NODES)
                A0, T0, W0, H0 = FUNC[f](G, NODES)
                if len(H0) <= MAX_JRNY:
                    mypack.getJourneyFrames(G, H0)
                MODELS[f] = {
                    'A': A0,
                    'T': T0,
                    'W': W0,
                    'H': H0,
                    'Solution': mypack.saveTour(G, T0, f),
                    'Journey': mypack.saveVideo(f'journey_{f}') if len(H0) <= MAX_JRNY else None,
                    'Tour': ' -> '.join([str(t[0]) for t in T0]) + ' -> 0'
                }
            
            return render_template('index.html',
                                   graph_path=graph_path,
                                   mst_path=mst_path if isinstance(MST, tuple) else None,
                                   mst_w=MST[1] if isinstance(MST, tuple) else None,
                                   models=MODELS)
            
        # else:
        #     if func in ['NN_0', 'NN_1', 'NN_2']:
        #         A, T, W, H = FUNC[func](G, NODES)
        #     else:
        #         A, T, W = FUNC[func](G, NODES)
        #         H = None
        #     solution_path = mypack.saveTour(G, T, 'solution').replace('/app', '')
        #     mypack.getPathFrames(G, T)
        #     # tour_path = mypack.saveVideo('tour').replace('/app', '')
        #     tour_path = None
            
        #     if H != None and len(H) <= MAX_JRNY:
        #         mypack.getJourneyFrames(G, H)
        #         journey_path = None
        #         # journey_path = mypack.saveVideo('journey').replace('/app', '')
        #         # mypack.getPathFrames(G, T)
        #     else:
        #         journey_path = None
            
        #     return render_template('index.html',
        #                            graph_path=graph_path,
        #                            solution_path=solution_path,
        #                            algo=func,
        #                            tour=' -> '.join([str(t[0])
        #                                             for t in T]) + ' -> 0',
        #                            journey_path=journey_path,
        #                            tour_path=tour_path)
    NODES = mypack.random.randint(MIN_NODE, MAX_NODE)
    print(NODES)
    G = mypack.getGraph(NODES)
    graph_path = mypack.saveGraph(G, 'mygraph')
    return render_template('index.html', graph_path=graph_path)


@app.route('/report')
def report():
    return render_template('report.html', title='Report')

@app.route('/algorithm')
def algorithm():
    return render_template('algorithm.html', title='Algorithm')