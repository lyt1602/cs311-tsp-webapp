from flask import Flask, render_template, request, redirect
from markdown import markdown
import codecs
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

@app.before_first_request
def clear_media():
    mypack.clearDir()
    
@app.route('/', methods=['GET', 'POST'])
def home():
    global G, NODES, FUNC, MODELS, A, W, T, H, graph_path, solution_path, journey_path, tour_path, mst_path

    if request.method == 'POST':
        request_args = list(request.form.to_dict().values())
        if request_args[1] == 'GO':
            try:
                NODES = int(request_args[0])
            except:
                NODES = 5
            G = mypack.getGraph(NODES)
            graph_path = mypack.saveGraph(G, 'mygraph')
            return render_template('index.html', graph_path=graph_path)
        
        elif request_args[1] in ['NN_0', 'NN_1', 'NN_2', 'NX_CHRISTOFIDE', 'NX_GREEDY', 'COMPARE']:
            try:
                temp = int(request_args[0])
            except:
                temp = 0
                
            if temp > 0:
                NODES = temp
                G = mypack.getGraph(NODES)
                graph_path = mypack.saveGraph(G, 'mygraph')
                
        func = request_args[1]
        # if func == 'GO':
        #     G = mypack.getGraph(NODES)
        #     graph_path = mypack.saveGraph(G, 'mygraph')
        #     return render_template('index.html', graph_path=graph_path)
        
        if func == 'REPORT':
            return redirect('/report')
        
        elif func == 'ALGO':
            return redirect('/algorithm')
        
        elif func == 'COMPARE':
            MST = mypack.getMST(G)
            if isinstance(MST, tuple):
                mst_path = mypack.saveGraph(MST[0], 'mst')
            
            for f in ['NN_0', 'NN_1', 'NN_2']:
                if G == None:
                    G = mypack.getGraph(NODES)
                try:
                    NODES = len(list(G.nodes())) if NODES == None else NODES
                except AttributeError:
                    print('err', NODES)

                A0, T0, W0, H0 = FUNC[f](G, NODES)
                if len(H0) <= MAX_JRNY:
                    mypack.getJourneyFrames(G, H0)
                MODELS[f] = {
                    'A': A0,
                    'T': T0,
                    'W': W0,
                    'H': H0,
                    'Solution': mypack.saveTour(G, T0, f),
                    'Journey': mypack.saveVideo(f'journey_{f}'),
                    'Tour': ' -> '.join([str(t[0]) for t in T0]) + ' -> 0'
                }
                
            return render_template('index.html',
                                   graph_path=graph_path,
                                   mst_path=mst_path if isinstance(MST, tuple) else None,
                                   mst_w=MST[1] if isinstance(MST, tuple) else None,
                                   models=MODELS)
            
        else:
            if func in ['NN_0', 'NN_1', 'NN_2']:
                A, T, W, H = FUNC[func](G, NODES)
            else:
                A, T, W = FUNC[func](G, NODES)
                H = None
            
            solution_path = mypack.saveTour(G, T, 'solution')
            
            mypack.getPathFrames(G, T)
            tour_path = mypack.saveVideo(f'tour_{func}')
            
            mypack.getJourneyFrames(G, H)
            journey_path = mypack.saveVideo(f'journey_{func}')
            
            return render_template('index.html',
                                   graph_path=graph_path,
                                   solution_path=solution_path,
                                   algo=func,
                                   tour=' -> '.join([str(t[0])
                                                    for t in T]) + ' -> 0',
                                   journey_path=journey_path,
                                   tour_path=tour_path)
            
    NODES = mypack.random.randint(MIN_NODE, MAX_NODE)
    G = mypack.getGraph(NODES)
    graph_path = mypack.saveGraph(G, 'mygraph')
    return render_template('index.html', graph_path=graph_path)


@app.route('/report')
def report():
    return render_template('report.html', title='Report')

@app.route('/algorithm')
def algorithm():
    # test = {'NN_0': codecs.open("./app/static/markdown/NN_0.md", mode="r", encoding="utf-8")}
    algos = ['NN_0', 'NN_1', 'NN_2', 'NX_CHRISTOFIDE', 'NX_GREEDY']
    i_md = [codecs.open(f"./app/static/markdown/{name}.md", mode="r", encoding="utf-8") for name in algos]
    html = {algo: html_md for algo, html_md in zip(algos, [markdown(md.read()) for md in i_md])}
    return render_template('algorithm.html', title='Algorithm', html=html)