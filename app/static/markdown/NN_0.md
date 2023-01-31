# NN_0 Algorithm

NN stands for Nearest Neighbor as this function uses the Nearest Neighbor concept.

Let's say that a problem is represented by a completed graph with **n** nodes with **m** edges. The following is its algorithm:

---

<pre style="padding-left: 30px">
Set a new graph NG with just the nodes of graph G

Set a nodes list of all-True array whose length is the number of nodes 

Set current_node to 0

While True exists in nodes:

    Set candidates to all possible edges and distance between the current_node and its neighbors

    Set closest to the edge-distance pair that has the minimum distance

    Add closest edge to NG

    Set current_node to edge.next_node

Add the edge between current_node and 0 to NG
</pre>