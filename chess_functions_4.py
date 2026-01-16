import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random
import time
import copy


# ----------------------------------------------------------------------------
# HOUSEKEEPING
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

    # Roster gridlines using spines - Hide all spines first
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
# CONTROLE
# Geldige zetten oplijsten, al dan niet met een score erbij
# Checken voor schaak en schaakmat
# ----------------------------------------------------------------------------


def geldige_zetten_pion(game, kleur, van_rij, van_kol):
    geldige_zetten = []
    bord = game.bord

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
            if van_rij == 1 and game.bord[van_rij + 2][van_kol][0] == "leeg":
                geldige_zetten.append([van_rij + 2, van_kol])
        if van_kol != 0 and game.bord[van_rij + 1][van_kol - 1][0] == "wit":
            geldige_zetten.append([van_rij + 1, van_kol - 1])
        if van_kol != 7 and game.bord[van_rij + 1][van_kol + 1][0] == "wit":
            geldige_zetten.append([van_rij + 1, van_kol + 1])

    return geldige_zetten


def geldige_zetten_paard(game, kleur, van_rij, van_kol):
    bord = game.bord
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


def geldige_zetten_toren(game, kleur, van_rij, van_kol):
    bord = game.bord
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


def geldige_zetten_loper(game, kleur, van_rij, van_kol):
    bord = game.bord
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


def geldige_zetten_koning(game, kleur, van_rij, van_kol):
    bord = game.bord
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


def geldige_zetten_koningin(game, kleur, van_rij, van_kol):
    geldige_zetten = geldige_zetten_loper(
        game, kleur, van_rij, van_kol
    ) + geldige_zetten_toren(game, kleur, van_rij, van_kol)

    return geldige_zetten


def check(game, kleur):
    found = False
    bord = game.bord

    for i in range(8):
        for j in range(8):
            if bord[i][j] == [kleur, "koning"]:
                rij_k = i
                kol_k = j
                found = True
                break
        if found:
            break

    bedreigingen = []

    pot_bedr = geldige_zetten_pion(game, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if (b[1] != kol_k) and bord[b[0]][b[1]][1] == "pion":
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_paard(game, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if bord[b[0]][b[1]][1] == "paard":
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_toren(game, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if (bord[b[0]][b[1]][1] == "toren") or (bord[b[0]][b[1]][1] == "koningin"):
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_loper(game, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if (bord[b[0]][b[1]][1] == "loper") or (bord[b[0]][b[1]][1] == "koningin"):
            bedreigingen.append(b)

    pot_bedr = geldige_zetten_koning(game, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if bord[b[0]][b[1]][1] == "koning":
            bedreigingen.append(b)

    return bedreigingen


def checkmate(game, kleur):
    bedreigingen = check(game, kleur)

    if not bedreigingen:
        return False, []

    else:
        zetten = alle_geldige_zetten(game, kleur)
        oplossingen = []

        for z in zetten:
            game_v = copy.deepcopy(game)
            doe_zet(game_v, kleur, z[0], z[1], controle=False)
            bedr_v = check(game_v, kleur)
            if not bedr_v:
                oplossingen.append(z)

        if oplossingen:
            return False, oplossingen
        else:
            return True, []


def alle_geldige_zetten(game, kleur):
    geldige_zetten = []
    bord = game.bord

    for i in range(8):
        for j in range(8):
            if bord[i][j][0] == kleur:
                function_name = f"geldige_zetten_{bord[i][j][1]}"
                function = globals().get(function_name)
                zetten = function(game, kleur, i, j)

                for zet in zetten:
                    game_v = copy.deepcopy(game)
                    doe_zet(game_v, kleur, [i, j], zet, controle=False)
                    check_v = check(game_v, kleur)
                    if not check_v:
                        geldige_zetten.append([[i, j], zet])

    return geldige_zetten


def alle_geldige_zetten_score(bord, kleur):
    score_map = {0: 0, "pion": 1, "paard": 2, "toren": 3, "loper": 3, "koningin": 4}
    change_color_map = {"zwart": "wit", "wit": "zwart"}

    geldige_zetten = alle_geldige_zetten(bord, kleur)
    geldige_zetten_score = []

    for zet in geldige_zetten:
        bord_v = doe_zet(bord, kleur, zet[0], zet[1], controle=False)

        check_v_other = check(bord_v, change_color_map[kleur])

        if check_v_other:
            ch_mt, oplossingen = checkmate(bord_v, change_color_map[kleur])

            if ch_mt:
                geldige_zetten_score.append([zet[0], zet[1], 7])  # schaakmat
                break
            else:
                score = 2 + score_map[bord[zet[1][0]][zet[1][1]][1]]
                geldige_zetten_score.append([zet[0], zet[1], score])  # schaak

        else:
            score = score_map[bord[zet[1][0]][zet[1][1]][1]]
            geldige_zetten_score.append([zet[0], zet[1], score])

    return geldige_zetten_score


# ----------------------------------------------------------------------------
# SPELERS
# definitie van spelers, met verschillende strategieën
# ----------------------------------------------------------------------------


class random_player:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Always picks a random move from all available valid moves. 
        When checked, picks a random move from all valid moves that resolve the threat."""
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "random player"

    def make_move(self, game):
        ch = check(game, self.kleur)

        if ch:
            ch_mt, oplossingen = checkmate(game, self.kleur)
            if ch_mt:
                if self.verbose:
                    print(f"\n{self.kleur} staat schaakmat.")
                setattr(game, f"status_{self.kleur}", 0)

            else:
                zet = random.choice(oplossingen)
                doe_zet(game, self.kleur, zet[0], zet[1], controle=False)

        else:
            zetten = alle_geldige_zetten(game, self.kleur)

            if zetten:
                zet = random.choice(zetten)
                doe_zet(game, self.kleur, zet[0], zet[1], controle=False)

            else:
                if self.verbose:
                    print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
                setattr(game, f"status_{self.kleur}", 0)


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
            if ch_mt:
                if self.verbose:
                    print(f"\n{self.kleur} staat schaakmat.")
                self.status = 0
                return bord, self.status
            else:
                zet = random.choice(oplossingen)
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
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
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status

            else:
                if self.verbose:
                    print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
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
            if ch_mt:
                if self.verbose:
                    print(f"\n{self.kleur} staat schaakmat.")
                self.status = 0
                return bord, self.status
            else:
                zet = random.choice(oplossingen)
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
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
                    bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                    return bord, self.status

                else:
                    change_color_map = {"zwart": "wit", "wit": "zwart"}
                    zetten_nettoscore = []

                    for zet in zetten_score:
                        bord_v = doe_zet(
                            bord, self.kleur, zet[0], zet[1], controle=False
                        )
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
                    bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                    return bord, self.status

            else:
                if self.verbose:
                    print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
                self.status = 0
                return bord, self.status


# ----------------------------------------------------------------------------
# ACTIE
# Zet doen, met of zonder controle
# Spel spelen (enkelvoudig)
# Reeks spelen (meervoudig)
# ----------------------------------------------------------------------------


def doe_zet(game, kleur, van, naar, controle=True):
    van_rij = van[0]
    van_kol = van[1]

    naar_rij = naar[0]
    naar_kol = naar[1]

    if controle:
        geldige_zetten = alle_geldige_zetten(game, kleur)
        if [van, naar] not in geldige_zetten:
            print("Ongeldige zet!")

    volgend_bord = [rij[:] for rij in game.bord]
    en_passant = game.en_passant
    castle = game.castle

    if volgend_bord[van_rij][van_kol][1] == "pion":
        if (van_rij == 1 and kleur == "wit") or (van_rij == 6 and kleur == "zwart"):
            volgend_bord[naar_rij][naar_kol] = [f"{kleur}", "koningin"]
        else:
            volgend_bord[naar_rij][naar_kol] = volgend_bord[van_rij][van_kol]
        if abs(van_rij - naar_rij) == 2:
            en_passant = [int((van_rij + naar_rij) / 2), van_kol]
        else:
            en_passant = []
    else:
        volgend_bord[naar_rij][naar_kol] = volgend_bord[van_rij][van_kol]
        en_passant = []

    if castle[f"{kleur}"]["left"] or castle[f"{kleur}"]["right"]:
        if volgend_bord[van_rij][van_kol][1] == "toren":
            if van_kol == 0:
                castle[f"{kleur}"]["left"] = False
            if van_kol == 7:
                castle[f"{kleur}"]["right"] = False
        if volgend_bord[van_rij][van_kol][1] == "koning":
            castle[f"{kleur}"]["left"] = False
            castle[f"{kleur}"]["right"] = False

    volgend_bord[van_rij][van_kol] = ["leeg", 0]

    game.bord = volgend_bord
    game.en_passant = en_passant
    game.castle = castle


class game:
    def __init__(self, speler_wit, speler_zwart, max_zetten, verbose=True):
        self.speler_wit = speler_wit
        self.speler_zwart = speler_zwart
        self.bord = nieuw_bord()
        self.max_zetten = max_zetten
        self.verbose = verbose
        self.aantal_zetten_wit = 0
        self.aantal_zetten_zwart = 0
        self.status_wit = 1
        self.status_zwart = 1
        self.en_passant = {
            "wit": [],
            "zwart": [],
        }  # De positie waar een (virtuele) pion staat, gedurende 1 beurt
        self.castle = {
            "wit": {
                "left": True,
                "right": True,
            },
            "zwart": {
                "left": True,
                "right": True,
            },
        }

    def play_game(self):
        start = time.time()

        for i in range(self.max_zetten):
            self.speler_wit.make_move(self)
            if self.status_wit == 0:
                if self.verbose:
                    print(f"\nZwart wint na {2 * i} zetten.")
                break
            self.aantal_zetten_wit += 1

            self.speler_zwart.make_move(self)
            if self.status_zwart == 0:
                if self.verbose:
                    print(f"\nWit wint na {2 * i + 1} zetten.")
                break
            self.aantal_zetten_zwart += 1

            if self.verbose and i == (self.max_zetten - 1):
                print(f"Spel onbeslist na {self.max_zetten} zetten.")

        stop = time.time()

        if self.verbose:
            print(f"Speltijd: {round(stop - start, 2)} seconden.")
            toon_bord(self.bord)


def N_games(player_1, player_2, N, max_zetten):
    start = time.time()

    onbeslist = 0
    player_1_win = 0
    player_2_win = 0

    for i in range(N):
        if i % 2 == 0:
            speler_wit = player_1("wit", verbose=False)
            speler_zwart = player_2("zwart", verbose=False)

            spel = game(speler_wit, speler_zwart, max_zetten, verbose=False)
            spel.play_game()

            if spel.status_wit == 0:
                player_2_win += 1
            elif spel.status_zwart == 0:
                player_1_win += 1
            else:
                onbeslist += 1

        else:
            speler_wit = player_2("wit", verbose=False)
            speler_zwart = player_1("zwart", verbose=False)

            spel = game(speler_wit, speler_zwart, max_zetten, verbose=False)
            spel.play_game()

            if spel.status_wit == 0:
                player_1_win += 1
            elif spel.status_zwart == 0:
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
