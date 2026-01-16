import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random
import time


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
    metadata_row = [
        [],  # en passant -> de positie waar een (virtuele) pion staat, gedurende 1 beurt
        True,  # rokade mogelijk voor WIT met de toren links
        True,  # rokade mogelijk voor WIT met de toren rechts
        True,  # rokade mogelijk voor ZWART met de toren links
        True,  # rokade mogelijk voor ZWART met de toren rechts
    ]

    bord = [
        [["zwart", p] for p in non_pawn_row],
        [["zwart", p] for p in pawn_row],
        empty_row,
        empty_row,
        empty_row,
        empty_row,
        [["wit", p] for p in pawn_row],
        [["wit", p] for p in non_pawn_row],
        metadata_row,
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


def geldige_zetten_pion(bord, kleur, van_rij, van_kol):
    geldige_zetten = []

    if kleur == "wit" and van_rij != 0:
        if bord[van_rij - 1][van_kol][0] == "leeg":
            geldige_zetten.append([van_rij - 1, van_kol])
            if van_rij == 6 and bord[van_rij - 2][van_kol][0] == "leeg":
                geldige_zetten.append([van_rij - 2, van_kol])
        if van_kol != 0 and (
            bord[van_rij - 1][van_kol - 1][0] == "zwart"
            or [van_rij - 1, van_kol - 1] == bord[8][0]
        ):
            geldige_zetten.append([van_rij - 1, van_kol - 1])
        if van_kol != 7 and (
            bord[van_rij - 1][van_kol + 1][0] == "zwart"
            or [van_rij - 1, van_kol + 1] == bord[8][0]
        ):
            geldige_zetten.append([van_rij - 1, van_kol + 1])

    if kleur == "zwart" and van_rij != 7:
        if bord[van_rij + 1][van_kol][0] == "leeg":
            geldige_zetten.append([van_rij + 1, van_kol])
            if van_rij == 1 and bord[van_rij + 2][van_kol][0] == "leeg":
                geldige_zetten.append([van_rij + 2, van_kol])
        if van_kol != 0 and (
            bord[van_rij + 1][van_kol - 1][0] == "wit"
            or [van_rij + 1, van_kol - 1] == bord[8][0]
        ):
            geldige_zetten.append([van_rij + 1, van_kol - 1])
        if van_kol != 7 and (
            bord[van_rij + 1][van_kol + 1][0] == "wit"
            or [van_rij + 1, van_kol + 1] == bord[8][0]
        ):
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


def geldige_zetten_koning_rokade(bord, kleur, van_rij, van_kol):
    geldige_zetten = []

    color_map = {"wit": 1, "zwart": 3}

    if bord[8][color_map[kleur]]:
        poss_castle = True
        for i in range(1, 4):
            if bord[van_rij][van_kol - i][0] != "leeg":
                poss_castle = False
                break
        if poss_castle:
            geldige_zetten.append([van_rij, van_kol - 2])

    if bord[8][color_map[kleur] + 1]:
        poss_castle = True
        for i in range(1, 3):
            if bord[van_rij][van_kol + i][0] != "leeg":
                poss_castle = False
                break
        if poss_castle:
            geldige_zetten.append([van_rij, van_kol + 2])

    return geldige_zetten


def geldige_zetten_koningin(bord, kleur, van_rij, van_kol):
    geldige_zetten = geldige_zetten_loper(
        bord, kleur, van_rij, van_kol
    ) + geldige_zetten_toren(bord, kleur, van_rij, van_kol)

    return geldige_zetten


def check(bord, kleur):
    found = False

    rij_k = 13
    kol_k = 13

    for i in range(8):
        for j in range(8):
            if bord[i][j] == [kleur, "koning"]:
                rij_k = i
                kol_k = j
                found = True
                break
        if found:
            break

    if rij_k == 13:
        toon_bord(bord)
        print(bord)

    bedreigingen = []

    pot_bedr = geldige_zetten_pion(bord, kleur, rij_k, kol_k)
    for b in pot_bedr:
        if (b[1] != kol_k) and bord[b[0]][b[1]][1] == "pion":
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


def checkmate(bord, kleur):
    bedreigingen = check(bord, kleur)

    if not bedreigingen:
        return False, []

    else:
        zetten = alle_geldige_zetten(bord, kleur)
        oplossingen = []

        for z in zetten:
            bord_v = doe_zet(bord, kleur, z[0], z[1], controle=False)
            bedr_v = check(bord_v, kleur)
            if not bedr_v:
                oplossingen.append(z)

        if oplossingen:
            return False, oplossingen
        else:
            return True, []


def alle_geldige_zetten(bord, kleur):
    geldige_zetten = []

    for i in range(8):
        for j in range(8):
            if bord[i][j][0] == kleur:
                function_name = f"geldige_zetten_{bord[i][j][1]}"
                function = globals().get(function_name)
                zetten = function(bord, kleur, i, j)

                for zet in zetten:
                    bord_v = doe_zet(bord, kleur, [i, j], zet, controle=False)
                    check_v = check(bord_v, kleur)
                    if not check_v:
                        geldige_zetten.append([[i, j], zet])

                if bord[i][j][1] == "koning" and geldige_zetten_koning_rokade(
                    bord, kleur, i, j
                ):
                    zetten = geldige_zetten_koning_rokade(bord, kleur, i, j)
                    for zet in zetten:
                        ch = check(bord, kleur)
                        bord_v = doe_zet(bord, kleur, [i, j], zet, controle=False)
                        ch_v = check(bord_v, kleur)
                        bord_v2 = doe_zet(
                            bord,
                            kleur,
                            [i, j],
                            [zet[0], int((zet[1] + j) / 2)],
                            controle=False,
                        )
                        ch_v2 = check(bord_v2, kleur)
                        if not ch and not ch_v and not ch_v2:
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

    def make_move(self, bord):
        ch = check(bord, self.kleur)

        if ch:
            ch_mt, oplossingen = checkmate(bord, self.kleur)
            if ch_mt:
                if self.verbose:
                    print(f"\n{self.kleur} staat schaakmat.")
                self.status = 0
            else:
                zet = random.choice(oplossingen)
                #check_koning = bord[zet[1][0]][zet[1][1]][1]
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                #if check_koning == "koning":
                    #print(ch)
                    #print("Koning veroverd! Something's wrong")

        else:
            zetten = alle_geldige_zetten(bord, self.kleur)

            if zetten:
                zet = random.choice(zetten)
                #check_koning = bord[zet[1][0]][zet[1][1]][1]
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                #if check_koning == "koning":
                    #print(ch)
                    #print("Koning veroverd without check! Something's wrong")

            else:
                if self.verbose:
                    print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
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
            if ch_mt:
                if self.verbose:
                    print(f"\n{self.kleur} staat schaakmat.")
                self.status = 0
            else:
                zet = random.choice(oplossingen)
                # check_koning = bord[zet[1][0]][zet[1][1]][1]
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                # if check_koning == "koning":
                # print(ch)
                # print("Koning veroverd! Something's wrong")

        else:
            zetten_score = alle_geldige_zetten_score(bord, self.kleur)

            if zetten_score:
                m = max([item[2] for item in zetten_score])
                beste_zetten = [item for item in zetten_score if item[2] == m]

                zet = random.choice(beste_zetten)
                # check_koning = bord[zet[1][0]][zet[1][1]][1]
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                # if check_koning == "koning":
                # print(ch)
                # print("Koning veroverd without check! Something's wrong")
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
            else:
                zet = random.choice(oplossingen)
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

        else:
            zetten_score = alle_geldige_zetten_score(bord, self.kleur)

            if zetten_score:
                m = max([item[2] for item in zetten_score])
                beste_zetten = [item for item in zetten_score if item[2] == m]

                if m == 6:
                    zet = random.choice(beste_zetten)
                    bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

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
                    beste_zetten = [
                        [item[0], item[1]]
                        for item in zetten_nettoscore
                        if item[2] == m_n
                    ]

                    zet = random.choice(beste_zetten)
                    bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

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


def doe_zet(bord, kleur, van, naar, controle=True):
    van_rij = van[0]
    van_kol = van[1]

    naar_rij = naar[0]
    naar_kol = naar[1]

    color_map = {"wit": 1, "zwart": 3}
    color_map_inv = {"wit": 3, "zwart": 1}

    if controle:
        geldige_zetten = alle_geldige_zetten(bord, kleur)
        if [van, naar] not in geldige_zetten:
            print("Ongeldige zet!")
            return bord

    volgend_bord = [rij[:] for rij in bord]

    if bord[van_rij][van_kol][1] == "pion":
        if (van_rij == 1 and kleur == "wit") or (van_rij == 6 and kleur == "zwart"):
            volgend_bord[naar_rij][naar_kol] = [f"{kleur}", "koningin"]
        else:
            volgend_bord[naar_rij][naar_kol] = volgend_bord[van_rij][van_kol]
        if abs(van_rij - naar_rij) == 2:
            volgend_bord[8][0] = [int((van_rij + naar_rij) / 2), van_kol]
        else:
            volgend_bord[8][0] = []
    else:
        volgend_bord[naar_rij][naar_kol] = bord[van_rij][van_kol]
        volgend_bord[8][0] = []

    if any(bord[8][1:5]):
        if bord[van_rij][van_kol][1] == "toren":
            if van_kol == 0:
                volgend_bord[8][color_map[kleur]] = False
            if van_kol == 7:
                volgend_bord[8][color_map[kleur] + 1] = False
        if bord[naar_rij][naar_kol][1] == "toren":
            if naar_kol == 0:
                volgend_bord[8][color_map_inv[kleur]] = False
            if naar_kol == 7:
                volgend_bord[8][color_map_inv[kleur] + 1] = False
        if bord[van_rij][van_kol][1] == "koning":
            volgend_bord[8][color_map[kleur]] = False
            volgend_bord[8][color_map[kleur] + 1] = False

    if naar == bord[8][0]:
        if naar[0] == 5:
            volgend_bord[naar_rij - 1][naar_kol] = ["leeg", 0]
        if naar[0] == 2:
            volgend_bord[naar_rij + 1][naar_kol] = ["leeg", 0]

    if (bord[van_rij][van_kol][1] == "koning") and (naar_kol - van_kol) == 2:
        volgend_bord[van_rij][5] = [kleur, "toren"]
        volgend_bord[van_rij][7] = ["leeg", 0]

    if (bord[van_rij][van_kol][1] == "koning") and (naar_kol - van_kol) == -2:
        volgend_bord[van_rij][3] = [kleur, "toren"]
        volgend_bord[van_rij][0] = ["leeg", 0]

    volgend_bord[van_rij][van_kol] = ["leeg", 0]

    return volgend_bord


def spel(player_white, player_black, aantal_zetten, verbose=True, toon=True):
    start = time.time()
    bord = nieuw_bord()
    #bord_replays = [bord]

    for i in range(aantal_zetten):
        #try:
        bord, status_white = player_white.make_move(bord)
        #except:
            #status_white = 13
            #status_black = 13
            #return bord_replays, status_white, status_black

        #bord_replays.append(bord)
        if status_white == 0:
            if verbose:
                print(f"\n{i + 1} zetten gespeeld.")
            break

        try:
        bord, status_black = player_black.make_move(bord)
        # except:
        #     status_white = 13
        #     status_black = 13
        #     return bord_replays, status_white, status_black

        # bord_replays.append(bord)
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

            #if (wit == 13) or (zwart == 13):
                #break

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

            #if (wit == 13) or (zwart == 13):
                #break

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

    #if (wit == 13) or (zwart == 13):
        #return bord

    speler_1 = player_1("wit")  # kleur maakt niet uit hier, is puur voor de naam
    speler_2 = player_2("wit")

    print(f"""\n{player_1_win} spelletjes gewonnen door {speler_1.name}. \n{player_2_win} spelletjes gewonnen door {speler_2.name}. 
    \n{onbeslist} spelletjes onbeslist na {max_zetten} zetten.""")
