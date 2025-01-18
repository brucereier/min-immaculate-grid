from collections import defaultdict
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus

teams = [
    "crd", "atl", "rav", "buf", "car", "chi", "cin", "dal", "den", "det",
    "gnb", "htx", "clt", "jax", "kan", "rai", "sdg", "ram", "mia", "min",
    "nwe", "nor", "nyg", "cle", "nyj", "phi", "pit", "sfo", "sea", "tam",
    "oti", "was"
]


def load_players_from_file(file_path):
    """
    Loads players from a text file where each line is:
    player_href: connection1,connection2,...
    Returns a dict[str, set[str]] mapping each player to the connections they cover.
    """
    players = defaultdict(set)
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            player_href, connections = line.split(": ")
            players[player_href] = set(connections.split(","))
    return players


def greedy_cover(players_dict, teams):
    all_connections = set(
        f"{teams[i]}-{teams[j]}" for i in range(len(teams)) for j in range(i + 1, len(teams))
    )

    uncovered = set(all_connections)
    selected_players = []

    remaining_players = dict(players_dict)

    while uncovered:
        best_player = None
        best_coverage = 0

        for player, covers in remaining_players.items():
            coverage = len(covers & uncovered)
            if coverage > best_coverage:
                best_coverage = coverage
                best_player = player

        if not best_player or best_coverage == 0:
            print("No further coverage possible. Some connections remain uncovered:")
            print(uncovered)
            break

        selected_players.append(best_player)
        covered_connections = remaining_players[best_player] & uncovered
        uncovered -= covered_connections

        print(f"Selected player: {best_player}")
        print(f"Connections covered by this player: {
              len(covered_connections)}")
        print(f"Remaining uncovered connections: {len(uncovered)}")

        del remaining_players[best_player]

    if uncovered:
        print("Final uncovered connections:", uncovered)

    return selected_players


def optimal_cover(players_dict, teams):
    from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus

    all_connections = set(
        f"{teams[i]}-{teams[j]}" for i in range(len(teams)) for j in range(i + 1, len(teams))
    )

    problem = LpProblem("OptimalConnections", LpMinimize)

    player_vars = {
        player: LpVariable(f"player_{i}", cat="Binary")
        for i, player in enumerate(players_dict.keys())
    }

    problem += lpSum(player_vars[p]
                     for p in players_dict), "MinimizeNumberOfPlayers"

    for c in all_connections:
        covering_players = [player_vars[p]
                            for p in players_dict if c in players_dict[p]]
        problem += lpSum(covering_players) >= 1, f"Cover_{c}"

    problem.solve()

    if LpStatus[problem.status] != "Optimal":
        raise Exception(f"No optimal solution found. Status: {
                        LpStatus[problem.status]}")

    selected_players = []
    print("\n=== Selected Players and Their Coverage ===")
    for player in players_dict:
        if player_vars[player].varValue == 1:
            selected_players.append(player)
            print(f"{len(selected_players)}. {player}: {
                  len(players_dict[player])} connections")
            if len(selected_players) == 44:
                print("\nOptimal solution reached: 44 players selected.")
                break

    print("\n=== Final List of Selected Players and Their Coverage ===")
    for idx, player in enumerate(selected_players):
        print(f"{idx + 1}. {player}: {len(players_dict[player])} connections")

    return selected_players


if __name__ == "__main__":
    players_dict = load_players_from_file("players.txt")

    greedy_players = greedy_cover(players_dict, teams)
    print("\n=== GREEDY SET COVER RESULTS ===")
    print(f"Selected {len(greedy_players)} players")

    optimal_players = optimal_cover(players_dict, teams)
    print("\n=== OPTIMAL ILP RESULTS ===")
    print(f"Selected {len(optimal_players)} players")
