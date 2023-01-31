# NN_2 Algorithm

This is a greedy version of previous NN algorithm.

Let's say that a problem is represented by a completed graph with **n** nodes with **m** edges. The following is its algorithm:

---

<pre style="padding-left: 30px">
Set a new graph NG with just the nodes of graph G
Set visited to []
Set candidates to a list of edge-distance pair with sorted distance
For edge-distance pair in candidates:
    If edge-distance pair not in visited:
        Add edge to NG
        Add edge-distance to visited

        If a node in edge has degree > 2:
            Set rm_flag = True
        Else:
            Set rm_flag = False

        Set partials to connected_components in NG
        If partials' length > 1:
            For partial in partials:
                If partial's length > 2 and has a cycle:
                    Set rm_flag = True
        
        If rm_flag:
            Remove last edge in NG
        
        If NG is connected:
            Add last edge that connect last 2 nodes with degree = 1
</pre>