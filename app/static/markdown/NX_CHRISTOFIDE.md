# NX_CHRISTOFIDE

The Christofides algorithm is an algorithm for finding approximate solutions to the travelling salesman problem. It's an approximating algorithm from networkx library. 

It's best approximation ratio that has been proven for the traveling salesman problem on general metric spaces, although better approximations are known for some special cases

The following is its algorithm:
---

<pre style="padding-left: 30px">
1. Find a minimum spanning tree (T)
2. Find vertexes in T with odd degree (O)
3. Find minimum weight matching (M) edges to T
4. Build an Eulerian circuit using the edges of M and T
5. Make a Hamiltonian circuit by skipping repeated vertexes
</pre>

Read more [here](https://github.com/Retsediv/ChristofidesAlgorithm)