import networkx as nx
from ortools.sat.python import cp_model
import typing

class CpSatTspSolverV1:
    def __init__(self, G: nx.Graph):
        self.graph = G
        self._model = cp_model.CpModel()

        # Variables
        edge_vars = dict()
        for u, v in G.edges:
            edge_vars[u, v] = self._model.NewBoolVar(f'edge_{u}_{v}')
            edge_vars[v, u] = self._model.NewBoolVar(f'edge_{v}_{u}')

        # Constraints
        # Because the nodes in the graph a indices 0, 1, ..., n-1, we can use the
        # indices directly in the constraints. Otherwise, we would have to use
        # a mapping from the nodes to indices.
        circuit = [(u,v,x) for (u,v),x in edge_vars.items()]
        self._model.AddCircuit(circuit)

        # Objective
        self._model.Minimize(sum(x*G[u][v]['weight'] for (u,v),x in edge_vars.items()))

    def solve(self, time_limit: float) -> typing.Tuple[float, float]:
        """
        Solve the model and return the objective value and the lower bound.
        """
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        #solver.parameters.log_search_progress = True
        status = solver.Solve(self._model)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            self.solution = solver
            return solver.ObjectiveValue(), solver.BestObjectiveBound()
        return float('inf'), 0.0