# NX_GREEDY

The Greedy algorithm from networkx is an algorithm for finding approximate solutions to the travelling salesman problem. It doesn't always offer the best solution

The following is its algorithm:
---

<pre style="padding-left: 30px">
1. The algorithm adds a node to the solution at every iteration.
2. The algorithm selects a node not already in the cycle whose connection to the previous node adds the least cost to the cycle.
</pre>

Read more [here](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.approximation.traveling_salesman.greedy_tsp.html)