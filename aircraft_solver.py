import cplex
import sys
import re


def solve_conflict_matrix(n, m, CM):
    # Inicjalizacja modelu
    model = cplex.Cplex()
    model.objective.set_sense(model.objective.sense.minimize)

    # Dodanie zmiennych decyzyjnych
    x = []
    for i in range(n):
        for j in range(m):
            var_name = "x_" + str(i) + "_" + str(j)
            x.append(var_name)
            model.variables.add(obj=[1], lb=[0], ub=[1], names=[var_name])

    # Dodanie ograniczeń
    for i in range(n):
        constraint_expr = [cplex.SparsePair(ind=[x[i * m + j] for j in range(m)], val=[1] * m)]
        model.linear_constraints.add(lin_expr=constraint_expr, senses=["E"], rhs=[1])

    for i in range(n):
        for j in range(m):
            for k in range(n):
                for l in range(m):
                    if i * m + j < k * m + l:
                        if CM[i * m + j][k * m + l] == 1:
                            constraint_expr = [cplex.SparsePair(ind=[x[i * m + j], x[k * m + l]], val=[1, 1])]
                            model.linear_constraints.add(lin_expr=constraint_expr, senses=["L"], rhs=[1])

    # Rozwiązanie modelu
    model.solve()

    # Pobranie wyniku
    result = []
    for i in range(n):
        for j in range(m):
            var_value = model.solution.get_values(x[i * m + j])
            result.append(str(int(var_value)))

    return " ".join(result)


if __name__ == "__main__":
    filename = sys.argv[1]
    pattern = r"CM_n=(\d+)_m=(\d+)\.txt"

    match = re.search(pattern, filename)

    if match:
        n = int(match.group(1))
        m = int(match.group(2))

        CM = []
        with open(filename) as f:
            for line in f.readlines():
                CM.append(list(map(int, line.split())))

        result = solve_conflict_matrix(n, m, CM)
        print(result)

        with open(f"wynik_{filename}", "w") as fr:
            fr.write(result)

    else:
        print("Podano zły plik lub nazwa pliku jest nieprawidlowa.")
