import president_strategy
import tqdm

if __name__ == "__main__":
    n_games = 1000
    hands = 5

    results = []  # = [president_strategy.random_game(hands) for n in range(n_games)]

    prev_winner = 0
    for n in tqdm.tqdm(range(n_games)):
        res = president_strategy.random_game(hands, prev_winner)
        if len(results) == 0:
            print("Results for first game:", res)
        results.append(res)
        # print(f"Result for game {n}: {res}")
        prev_winner = res[0]

    """ We have a list of e.g. [1, 3, 0, 2, 4] to indicate that hand 1 came first, 3 second, 0 third etc in a single game.

    this dict horribleness needs refactoring, but will tell us how many times each player has come in each position
    across a number of games

    e.g. {0: 19, 1: 13, 2: 12, 3: 8, 4: 3} for player N would mean they came 1st 19 times, 2nd 13 times, 3rd 12 times.
    """

    # Create empty dict to store results
    scores = {n: {m: 0 for m in range(hands)} for n in range(hands)}

    for result in results:
        for place, hand in enumerate(result):
            scores[hand][place] += 1

    for hand, places in scores.items():
        print(f"Results for {hand}: {places}")
