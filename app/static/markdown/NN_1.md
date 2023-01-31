# NN_1 Algorithm

This is similar to NN_0, just that the way it connects the edges is a bit different.

Let's say that a problem is represented by a completed graph with **n** nodes with **m** edges. The following is its algorithm:

---

<pre style="padding-left: 30px">
Set a new graph NG with just the nodes of graph G
Set a nodes list of all-True array whose length is the number of nodes 
Set current_node to 0
Set candidates to all possible edges and distance between 
For edge-distance pair in candidates:
    if nodes in edges are not visited:
        Add edge to NG
        set nodes[edge.nodes] to True
If True in nodes:
    leftover_node = nodes.index(True)
    Add edge that connect leftover_node to any nodes in NG that has the minimum distance
Set partial to all segments in NG
Set nodes to a list of all-true array if the node has a degree less than 2 in partial
While NG is not connected:
    Connect any edge whose nodes have degree < 2
</pre>