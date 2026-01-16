import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random
import time


# ----------------------------------------------------------------------------
# Nieuw bord creëren
# Bestaand bord visualiseren
# ----------------------------------------------------------------------------


def nieuw_bord():
    non_pawn_row = [
        "toren",
        "paard",
        "loper",
        "koningin",
        "koning",
        "loper",
        "paard",
        "toren",
    ]

    pawn_row = ["pion" for _ in range(8)]
    empty_row = [["leeg", 0] for _ in range(8)]

    bord = [
        [["zwart", p] for p in non_pawn_row],
        [["zwart", p] for p in pawn_row],
        empty_row,
        empty_row,
        empty_row,
        empty_row,
        [["wit", p] for p in pawn_row],
        [["wit", p] for p in non_pawn_row],
    ]

    return bord


def toon_bord(board):
    images = []

    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece[0] == "leeg":
                images.append(Image.open("icons/leeg.png"))
            else:
                images.append(Image.open(f"icons/{piece[0]}_{piece[1]}.png"))

    rows, cols = 8, 8

    row_labels = ["8", "7", "6", "5", "4", "3", "2", "1"]
    col_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(0.5 * cols, 0.5 * rows),
        gridspec_kw=dict(wspace=0, hspace=0),
    )

    axes = np.array(axes)

    # Show images, remove ticks
    for idx, img in enumerate(images):
        r, c = divmod(idx, cols)
        ax = axes[r, c]
        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks([])

    # row lavels
    for r in range(rows):
        ax = axes[r, 0]
        ax.set_ylabel(
            row_labels[r],
            rotation=0,
            labelpad=20,
            va="center",
            ha="center",
        )

    # column labels
    for c in range(cols):
        ax = axes[rows - 1, c]
        ax.set_xlabel(
            col_labels[c],
            labelpad=20,
            ha="center",
            va="center",
        )

    # Roster gridlines using spines
    # Hide all spines first
    for ax in axes.ravel():
        for s in ax.spines.values():
            s.set_visible(False)

    # Turn on only the necessary ones
    for r in range(rows):
        for c in range(cols):
            ax = axes[r, c]

            # outer border
            if r == 0:
                ax.spines["top"].set_visible(True)
            if r == rows - 1:
                ax.spines["bottom"].set_visible(True)
            if c == 0:
                ax.spines["left"].set_visible(True)
            if c == cols - 1:
                ax.spines["right"].set_visible(True)

            # inner grid lines (each one drawn once)
            if r < rows - 1:
                ax.spines["bottom"].set_visible(True)
            if c < cols - 1:
                ax.spines["right"].set_visible(True)

    # Style visible borders
    for ax in axes.ravel():
        for s in ax.spines.values():
            if s.get_visible():
                s.set_linewidth(2)
                s.set_edgecolor("black")

    plt.show()


# ----------------------------------------------------------------------------
# Geldige zetten
#
# ----------------------------------------------------------------------------


def geldige_zetten_pion(bord, kleur, van_rij, van_kol):
    geldige_zetten = []

    if kleur == "wit" and van_rij != 0:
        if bord[van_rij - 1][van_kol][0] == "leeg":
            geldige_zetten.append([van_rij - 1, van_kol])
            if van_rij == 6 and bord[van_rij - 2][van_kol][0] == "leeg":
                geldige_zetten.append([van_rij - 2, van_kol])
        if van_kol != 0 and bord[van_rij - 1][van_kol - 1][0] == "zwart":
            geldige_zetten.append([van_rij - 1, van_kol - 1])
        if van_kol != 7 and bord[van_rij - 1][van_kol + 1][0] == "zwart":
            geldige_zetten.append([van_rij - 1, van_kol + 1])

    if kleur == "zwart" and van_rij != 7:
        if bord[van_rij + 1][van_kol][0] == "leeg":
            geldige_zetten.append([van_rij + 1, van_kol])
            if van_rij == 1 and bord[van_rij + 2][van_kol][0] == "leeg":
                geldige_zetten.append([van_rij + 2, van_kol])
        if van_kol != 0 and bord[van_rij + 1][van_kol - 1][0] == "wit":
            geldige_zetten.append([van_rij + 1, van_kol - 1])
        if van_kol != 7 and bord[van_rij + 1][van_kol + 1][0] == "wit":
            geldige_zetten.append([van_rij + 1, van_kol + 1])

    return geldige_zetten


def geldige_zetten_pion_aanv(bord, kleur, van_rij, van_kol):
    geldige_zetten = []

    if kleur == "wit" and van_rij != 0:
        if van_kol != 0 and bord[van_rij - 1][van_kol - 1][0] == "zwart":
            geldige_zetten.append([van_rij - 1, van_kol - 1])
        if van_kol != 7 and bord[van_rij - 1][van_kol + 1][0] == "zwart":
            geldige_zetten.append([van_rij - 1, van_kol + 1])

    if kleur == "zwart" and van_rij != 7:
        if van_kol != 0 and bord[van_rij + 1][van_kol - 1][0] == "wit":
            geldige_zetten.append([van_rij + 1, van_kol - 1])
        if van_kol != 7 and bord[van_rij + 1][van_kol + 1][0] == "wit":
            geldige_zetten.append([van_rij + 1, van_kol + 1])

    return geldige_zetten


def geldige_zetten_paard(bord, kleur, van_rij, van_kol):
    zetten = [
        [van_rij - 2, van_kol - 1],
        [van_rij - 2, van_kol + 1],
        [van_rij + 2, van_kol - 1],
        [van_rij + 2, van_kol + 1],
        [van_rij - 1, van_kol + 2],
        [van_rij - 1, van_kol - 2],
        [van_rij + 1, van_kol + 2],
        [van_rij + 1, van_kol - 2],
    ]

    geldige_zetten = []

    for zet in zetten:
        if (
            (zet[0] >= 0)
            and (zet[0] <= 7)
            and (zet[1] >= 0)
            and (zet[1] <= 7)
            and bord[zet[0]][zet[1]][0] != kleur
        ):
            geldige_zetten.append(zet)

    return geldige_zetten


def geldige_zetten_toren(bord, kleur, van_rij, van_kol):
    geldige_zetten = []

    if van_rij != 7:
        for i in range(7 - van_rij):
            if bord[van_rij + i + 1][van_kol][0] == "leeg":
                geldige_zetten.append([van_rij + i + 1, van_kol])
            elif bord[van_rij + i + 1][van_kol][0] == kleur:
                break
            else:
                geldige_zetten.append([van_rij + i + 1, van_kol])
                break

    if van_rij != 0:
        for i in range(van_rij):
            if bord[van_rij - i - 1][van_kol][0] == "leeg":
                geldige_zetten.append([van_rij - i - 1, van_kol])
            elif bord[van_rij - i - 1][van_kol][0] == kleur:
                break
            else:
                geldige_zetten.append([van_rij - i - 1, van_kol])
                break

    if van_kol != 7:
        for i in range(7 - van_kol):
            if bord[van_rij][van_kol + i + 1][0] == "leeg":
                geldige_zetten.append([van_rij, van_kol + i + 1])
            elif bord[van_rij][van_kol + i + 1][0] == kleur:
                break
            else:
                geldige_zetten.append([van_rij, van_kol + i + 1])
                break

    if van_kol != 0:
        for i in range(van_kol):
            if bord[van_rij][van_kol - i - 1][0] == "leeg":
                geldige_zetten.append([van_rij, van_kol - i - 1])
            elif bord[van_rij][van_kol - i - 1][0] == kleur:
                break
            else:
                geldige_zetten.append([van_rij, van_kol - i - 1])
                break

    return geldige_zetten


def geldige_zetten_loper(bord, kleur, van_rij, van_kol):
    geldige_zetten = []

    rij = van_rij + 1
    kol = van_kol + 1

    while rij < 8 and kol < 8:
        if bord[rij][kol][0] == "leeg":
            geldige_zetten.append([rij, kol])
            rij += 1
            kol += 1
        elif bord[rij][kol][0] == kleur:
            break
        else:
            geldige_zetten.append([rij, kol])
            break

    rij = van_rij + 1
    kol = van_kol - 1

    while rij < 8 and kol >= 0:
        if bord[rij][kol][0] == "leeg":
            geldige_zetten.append([rij, kol])
            rij += 1
            kol -= 1
        elif bord[rij][kol][0] == kleur:
            break
        else:
            geldige_zetten.append([rij, kol])
            break

    rij = van_rij - 1
    kol = van_kol - 1

    while rij >= 0 and kol >= 0:
        if bord[rij][kol][0] == "leeg":
            geldige_zetten.append([rij, kol])
            rij -= 1
            kol -= 1
        elif bord[rij][kol][0] == kleur:
            break
        else:
            geldige_zetten.append([rij, kol])
            break

    rij = van_rij - 1
    kol = van_kol + 1

    while rij >= 0 and kol < 8:
        if bord[rij][kol][0] == "leeg":
            geldige_zetten.append([rij, kol])
            rij -= 1
            kol += 1
        elif bord[rij][kol][0] == kleur:
            break
        else:
            geldige_zetten.append([rij, kol])
            break

    return geldige_zetten


def geldige_zetten_koning(bord, kleur, van_rij, van_kol):
    zetten = [
        [van_rij - 1, van_kol - 1],
        [van_rij - 1, van_kol],
        [van_rij - 1, van_kol + 1],
        [van_rij, van_kol - 1],
        [van_rij, van_kol + 1],
        [van_rij + 1, van_kol - 1],
        [van_rij + 1, van_kol],
        [van_rij + 1, van_kol + 1],
    ]

    geldige_zetten = []

    for zet in zetten:
        if (
            (zet[0] >= 0)
            and (zet[0] <= 7)
            and (zet[1] >= 0)
            and (zet[1] <= 7)
            and bord[zet[0]][zet[1]][0] != kleur
        ):
            geldige_zetten.append(zet)

    return geldige_zetten


def geldige_zetten_koningin(bord, kleur, van_rij, van_kol):
    geldige_zetten = geldige_zetten_loper(
        bord, kleur, van_rij, van_kol
    ) + geldige_zetten_toren(bord, kleur, van_rij, van_kol)

    return geldige_zetten


def doe_zet_simpel(bord, kleur, van, naar):
    van_rij = van[0]
    van_kol = van[1]

    naar_rij = naar[0]
    naar_kol = naar[1]

    volgend_bord = [rij[:] for rij in bord]

    if (bord[van_rij][van_kol][0] != kleur) or (bord[naar_rij][naar_kol][0] == kleur):
        print("Ongeldige zet!")

    else:
        function_name = f"geldige_zetten_{bord[van_rij][van_kol][1]}"  # Is eigenlijk dubbele check, in principe komen geen ongeldige zetten binnen
        function = globals().get(function_name)
        geldige_zetten = function(bord, kleur, van_rij, van_kol)

        if [naar_rij, naar_kol] in geldige_zetten:
            volgend_bord[naar_rij][naar_kol] = bord[van_rij][van_kol]
            volgend_bord[van_rij][van_kol] = ["leeg", 0]

        else:
            print("Ongeldige zet")

    return volgend_bord


def check(bord, kleur):
    found = False

    for i in range(8):
        for j in range(8):
            if bord[i][j] == [kleur, "koning"]:
                rij_k = i
                kol_k = j
                found = True
                break
        if found == True:
            break

    bedreigingen = []

    pot_bedr = geldige_zetten_pion_aanv(bord, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if bord[b[0]][b[1]][1] == "pion":
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_paard(bord, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if bord[b[0]][b[1]][1] == "paard":
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_toren(bord, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if (bord[b[0]][b[1]][1] == "toren") or (bord[b[0]][b[1]][1] == "koningin"):
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_loper(bord, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if (bord[b[0]][b[1]][1] == "loper") or (bord[b[0]][b[1]][1] == "koningin"):
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_koning(bord, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if bord[b[0]][b[1]][1] == "koning":
            bedreigingen.append(b)

    return bedreigingen


def alle_geldige_zetten(bord, kleur):
    geldige_zetten = []

    for i in range(8):
        for j in range(8):
            if bord[i][j][0] == kleur:
                function_name = f"geldige_zetten_{bord[i][j][1]}"
                function = globals().get(function_name)
                zetten = function(bord, kleur, i, j)

                for zet in zetten:
                    bord_v = doe_zet_simpel(bord, kleur, [i, j], zet)
                    check_v = check(bord_v, kleur)
                    if not check_v:
                        geldige_zetten.append([[i, j], zet])

    return geldige_zetten


def checkmate(bord, kleur):
    bedreigingen = check(bord, kleur)

    if not bedreigingen:
        return False, []

    else:
        zetten = alle_geldige_zetten(bord, kleur)
        oplossingen = []

        for z in zetten:
            bord_v = doe_zet_simpel(bord, kleur, z[0], z[1])
            bedr_v = check(bord_v, kleur)
            if not bedr_v:
                oplossingen.append(z)

        if oplossingen:
            return False, oplossingen
        else:
            return True, []


def spel(player_white, player_black, aantal_zetten, verbose=True, toon=True):
    start = time.time()
    bord = nieuw_bord()

    for i in range(aantal_zetten):
        bord, status_white = player_white.make_move(bord)
        if status_white == 0:
            if verbose:
                print(f"\n{i + 1} zetten gespeeld.")
            break

        bord, status_black = player_black.make_move(bord)
        if status_black == 0:
            if verbose:
                print(f"\n{i + 1} zetten gespeeld.")
            break

    stop = time.time()

    if verbose:
        print(f"\nGame took {round(stop - start, 2)} seconds.")

    if toon:
        print("\n")
        toon_bord(bord)

    return bord, status_white, status_black


def alle_geldige_zetten_score(
    bord, kleur
):  # Waarschijnlijk sneller indien eerst functie alle_geldige_zetten oproepen, en dan scores toevoegen
    score_map = {0: 0, "pion": 1, "paard": 2, "toren": 3, "loper": 3, "koningin": 4}
    change_color_map = {"zwart": "wit", "wit": "zwart"}

    geldige_zetten_score = []

    for i in range(8):
        for j in range(8):
            if bord[i][j][0] == kleur:
                function_name = f"geldige_zetten_{bord[i][j][1]}"
                function = globals().get(function_name)
                zetten = function(bord, kleur, i, j)

                for zet in zetten:
                    bord_v = doe_zet_simpel(bord, kleur, [i, j], zet)
                    check_v_own = check(bord_v, kleur)

                    if not check_v_own:
                        check_v_other = check(bord_v, change_color_map[kleur])

                        if check_v_other:
                            ch_mt, oplossingen = checkmate(
                                bord_v, change_color_map[kleur]
                            )

                            if ch_mt:
                                geldige_zetten_score.append(
                                    [[i, j], zet, 6]
                                )  # schaakmat
                            else:
                                geldige_zetten_score.append([[i, j], zet, 2])  # schaak

                            # Hier kan eventueel een break om de functie sneller te maken

                        else:
                            score = score_map[bord[zet[0]][zet[1]][1]]
                            geldige_zetten_score.append([[i, j], zet, score])

    return geldige_zetten_score


def N_games(player_1, player_2, N, max_zetten):
    start = time.time()

    onbeslist = 0
    player_1_win = 0
    player_2_win = 0

    for i in range(N):
        if i % 2 == 0:
            speler_wit = player_1("wit", verbose=False)
            speler_zwart = player_2("zwart", verbose=False)

            bord, wit, zwart = spel(
                speler_wit, speler_zwart, max_zetten, verbose=False, toon=False
            )

            if wit == 0:
                player_2_win += 1
            elif zwart == 0:
                player_1_win += 1
            else:
                onbeslist += 1

        else:
            speler_wit = player_2("wit", verbose=False)
            speler_zwart = player_1("zwart", verbose=False)

            bord, wit, zwart = spel(
                speler_wit, speler_zwart, max_zetten, verbose=False, toon=False
            )

            if wit == 0:
                player_1_win += 1
            elif zwart == 0:
                player_2_win += 1
            else:
                onbeslist += 1

        if (i + 1) % 50 == 0:
            print(f"{round(100 * (i + 1) / N, 2)} % done.")

    stop = time.time()
    print(f"\nThis took {round(stop - start, 2)} seconds.")

    speler_1 = player_1("wit")  # kleur maakt niet uit hier, is puur voor de naam
    speler_2 = player_2("wit")

    print(f"""\n{player_1_win} spelletjes gewonnen door {speler_1.name}. \n{player_2_win} spelletjes gewonnen door {speler_2.name}. 
    \n{onbeslist} spelletjes onbeslist na {max_zetten} zetten.""")


class random_player:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Always picks a random move from all available valid moves. 
        When checked, picks a random move from all valid moves that resolve the threat."""
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "random player"

    def make_move(self, bord):
        ch = check(bord, self.kleur)

        if ch:
            ch_mt, oplossingen = checkmate(bord, self.kleur)
            if ch_mt == True:
                if self.verbose:
                    print(f"\nSpel beëindigd: {self.kleur} staat schaakmat.")
                self.status = 0
                return bord, self.status
            else:
                zet = random.choice(oplossingen)
                bord = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                return bord, self.status

        else:
            zetten = alle_geldige_zetten(bord, self.kleur)

            if zetten:
                zet = random.choice(zetten)
                bord = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                return bord, self.status

            else:
                if self.verbose:
                    print(
                        f"\nSpel beëindigd: {self.kleur} kan geen geldige zet meer uitvoeren."
                    )
                self.status = 0
                return bord, self.status


class score_player:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Always checks all available valid moves, and then chooses randomly among the subset of moves that 
        yields the highest score. Score is 1 if a pawn is captured, 2 for a knight, 3 for a rook or a bishop and 4 for the queen.
        It is 2 when the opponent is checked, and 6 when he is checkmated.
        
        If the player himself is checked, he picks a random move from all valid moves that resolve the threat."""
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "score player"

    def make_move(self, bord):
        ch = check(bord, self.kleur)

        if ch:
            ch_mt, oplossingen = checkmate(bord, self.kleur)
            if ch_mt == True:
                if self.verbose:
                    print(f"\nSpel beëindigd: {self.kleur} staat schaakmat.")
                self.status = 0
                return bord, self.status
            else:
                zet = random.choice(oplossingen)
                bord = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                return bord, self.status

        else:
            zetten_score = alle_geldige_zetten_score(bord, self.kleur)

            if zetten_score:
                m = max([item[2] for item in zetten_score])
                beste_zetten = []

                for item in zetten_score:
                    if item[2] == m:
                        beste_zetten.append([item[0], item[1]])

                zet = random.choice(beste_zetten)
                bord = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                return bord, self.status

            else:
                if self.verbose:
                    print(
                        f"\nSpel beëindigd: {self.kleur} kan geen geldige zet meer uitvoeren."
                    )
                self.status = 0
                return bord, self.status


class thinking_one_ahead_player:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Assumes that the OTHER player is a 'score player', meaning that all available valid moves are listed, 
        and subsequently a random choice is made among the subset of moves that yields the highest score. Score is 1 if a pawn is 
        captured, 2 for a knight, 3 for a rook or a bishop, 4 for the queen, 2 when the move results in a check and 6 when it 
        results in a checkmate.
        
        The player himself lists all valid moves and, for each of them, determines (based upon the strategy explained in the previous
        paragraph) what the countermove will be. For each valid move the 'net score' is calculated: score own move minus score countermove.
        From all valid moves with the highest net score, a random move is chosen. 

        When a move results in a checkmate of the opponent, that move is chosen (no countermove has to be determined).
        
        If the player himself is checked, he picks a random move from all valid moves that resolve the threat."""
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "thinking 1 ahead player"

    def make_move(self, bord):
        ch = check(bord, self.kleur)

        if ch:
            ch_mt, oplossingen = checkmate(bord, self.kleur)
            if ch_mt == True:
                if self.verbose:
                    print(f"\nSpel beëindigd: {self.kleur} staat schaakmat.")
                self.status = 0
                return bord, self.status
            else:
                zet = random.choice(oplossingen)
                bord = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                return bord, self.status

        else:
            zetten_score = alle_geldige_zetten_score(bord, self.kleur)

            if zetten_score:
                m = max([item[2] for item in zetten_score])

                beste_zetten = []

                for item in zetten_score:
                    if item[2] == m:
                        beste_zetten.append([item[0], item[1]])

                if m == 6:
                    zet = random.choice(beste_zetten)
                    bord = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                    return bord, self.status

                else:
                    change_color_map = {"zwart": "wit", "wit": "zwart"}
                    zetten_nettoscore = []

                    for zet in zetten_score:
                        bord_v = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                        tegenzetten_score = alle_geldige_zetten_score(
                            bord_v, change_color_map[self.kleur]
                        )

                        if tegenzetten_score:
                            tegenscore = max([item[2] for item in tegenzetten_score])
                        else:
                            tegenscore = -7

                        zetten_nettoscore.append([zet[0], zet[1], zet[2] - tegenscore])

                    m_n = max([item[2] for item in zetten_nettoscore])
                    beste_zetten = []

                    for item in zetten_nettoscore:
                        if item[2] == m_n:
                            beste_zetten.append([item[0], item[1]])

                    zet = random.choice(beste_zetten)
                    bord = doe_zet_simpel(bord, self.kleur, zet[0], zet[1])
                    return bord, self.status

            else:
                if self.verbose:
                    print(
                        f"\nSpel beëindigd: {self.kleur} kan geen geldige zet meer uitvoeren."
                    )
                self.status = 0
                return bord, self.status
