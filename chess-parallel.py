import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

from chess_base_functions import spel
from chess_players import (
    random_player,
    score_player,
    score_player_2,
    thinking_one_ahead_player,
    thinking_two_ahead_player_conservative,
)

speler_1 = thinking_one_ahead_player
speler_2 = random_player
N_games = 10_000
workers = 12
max_zetten = 300


def one_game(digit):
    speler_wit = (
        speler_1("wit", verbose=False) if digit == 1 else speler_2("wit", verbose=False)
    )
    speler_zwart = (
        speler_2("zwart", verbose=False)
        if digit == 1
        else speler_1("zwart", verbose=False)
    )

    bord, wit, zwart = spel(
        speler_wit, speler_zwart, max_zetten, verbose=False, toon=False
    )

    if wit == 1 and zwart == 1:
        return 0  # onbeslist

    elif digit == 1:
        if wit == 0:
            return 2  # speler_2 wint
        else:
            return 1  # speler 1 wint

    else:
        if wit == 0:
            return 1  # speler_1 wint
        else:
            return 2  # speler 2 wint


if __name__ == "__main__":
    digits = [1 if i % 2 == 0 else 0 for i in range(N_games)]
    results = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # results = list(executor.map(one_game, digits))
        futures = [executor.submit(one_game, digit) for digit in digits]

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing"
        ):
            results.append(future.result())

    onbeslist = len([x for x in results if x == 0])
    speler_1_wint = len([x for x in results if x == 1])
    speler_2_wint = len([x for x in results if x == 2])

    sp_1 = speler_1("wit")  # kleur maakt niet uit hier, is puur voor de naam
    sp_2 = speler_2("wit")

    print(
        f"\n{speler_1_wint} van de {N_games} spelletjes gewonnen door {sp_1.name}. \n{speler_2_wint} van de {N_games} spelletjes gewonnen door {sp_2.name}. \n{onbeslist} van de {N_games} spelletjes onbeslist na {max_zetten} zetten.\n"
    )
