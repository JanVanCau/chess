import random
from chess_base_functions import (
    alle_geldige_zetten,
    alle_geldige_zetten_score,
    check,
    checkmate,
    doe_zet,
)


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
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

        else:
            zetten = alle_geldige_zetten(bord, self.kleur)

            if zetten:
                zet = random.choice(zetten)
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

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
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

        else:
            zetten_score = alle_geldige_zetten_score(bord, self.kleur)

            if zetten_score:
                m = max([item[2] for item in zetten_score])
                beste_zetten = [item for item in zetten_score if item[2] == m]

                zet = random.choice(beste_zetten)
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

            else:
                if self.verbose:
                    print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
                self.status = 0

        return bord, self.status


class score_player_2:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Always checks all available valid moves, also when checked, and then chooses randomly among the subset of moves that
        yields the highest score. Score is 1 if a pawn is captured, 2 for a knight, 3 for a rook or a bishop and 4 for the queen.
        It is 2 when the opponent is checked, and 6 when he is checkmated."""
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "score player version 2"

    def make_move(self, bord):
        zetten_score = alle_geldige_zetten_score(bord, self.kleur)

        if not zetten_score:
            if self.verbose:
                print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
            self.status = 0

        else:
            ch = check(bord, self.kleur)

            if ch:
                ch_mt, oplossingen = checkmate(bord, self.kleur)
                if ch_mt:
                    if self.verbose:
                        print(f"\n{self.kleur} staat schaakmat.")
                    self.status = 0
                    return bord, self.status
                else:
                    zetten_score = [
                        item
                        for item in zetten_score
                        if [item[0], item[1]] in oplossingen
                    ]

            m = max([item[2] for item in zetten_score])
            beste_zetten = [item for item in zetten_score if item[2] == m]

            zet = random.choice(beste_zetten)
            bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

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

    def make_move_old(self, bord):
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

    def make_move(self, bord):
        zetten_score = alle_geldige_zetten_score(bord, self.kleur)

        if not zetten_score:
            if self.verbose:
                print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
            self.status = 0

        else:
            if check(bord, self.kleur):
                ch_mt, oplossingen = checkmate(bord, self.kleur)

                if ch_mt:
                    if self.verbose:
                        print(f"\n{self.kleur} staat schaakmat.")
                    self.status = 0
                    return bord, self.status
                else:
                    zetten_score = [
                        item
                        for item in zetten_score
                        if [item[0], item[1]] in oplossingen
                    ]

        m = max([item[2] for item in zetten_score])
        beste_zetten = [item for item in zetten_score if item[2] == m]

        if m == 6:
            zet = random.choice(beste_zetten)
            bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

        else:
            change_color_map = {"zwart": "wit", "wit": "zwart"}
            zetten_nettoscore = []

            for zet in zetten_score:
                bord_v = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
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
                [item[0], item[1]] for item in zetten_nettoscore if item[2] == m_n
            ]

            zet = random.choice(beste_zetten)
            bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

        return bord, self.status


class thinking_two_ahead_player_conservative:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Assumes nothing about the OTHER player.
        
        The player himself lists all valid moves. If the player himself is checked, only the valid primary moves (= moves that resolve the threat) are investigated. 
        
        For each valid primary move, all possible countermoves are determined with their scores for the opponent. For each countermove the highest scoring secondary move 
        is calculated and the corresponding net score for the player is stored. 

        In this way, for each primary move, the lowest net score can be determined (across all possible countermoves). This is a conservative approach. The primary move 
        that has the highest 'lowest net score' is then chosen.

        When a move results in a checkmate of the opponent or another situation in which the opponent has zero possible moves left, that move is chosen (no countermove has to be determined). 
        
        """
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "conservative thinking 2 ahead player"

    def make_move(self, bord):
        # 1 - Determine primary moves with their scores

        primaire_zetten_score = alle_geldige_zetten_score(bord, self.kleur)

        if not primaire_zetten_score:
            if self.verbose:
                print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
            self.status = 0

        else:
            ch = check(bord, self.kleur)

            if ch:
                ch_mt, oplossingen = checkmate(bord, self.kleur)
                if ch_mt:
                    if self.verbose:
                        print(f"\n{self.kleur} staat schaakmat.")
                    self.status = 0
                    return bord, self.status
                else:
                    primaire_zetten_score = [
                        item
                        for item in primaire_zetten_score
                        if [item[0], item[1]] in oplossingen
                    ]

            primair_max = max([item[2] for item in primaire_zetten_score])

            if primair_max == 6:
                beste_zetten = [
                    item for item in primaire_zetten_score if item[2] == primair_max
                ]
                zet = random.choice(beste_zetten)

            else:
                # 2 - Determine all countermoves and secondary moves with their scores

                change_color_map = {"zwart": "wit", "wit": "zwart"}
                z_ult = []

                for z in primaire_zetten_score:
                    bord_o = doe_zet(bord, self.kleur, z[0], z[1], controle=False)
                    zetten_score_o = alle_geldige_zetten_score(
                        bord_o, change_color_map[self.kleur]
                    )

                    if zetten_score_o:
                        for z_o in zetten_score_o:
                            bord_p = doe_zet(
                                bord_o,
                                change_color_map[self.kleur],
                                z_o[0],
                                z_o[1],
                                controle=False,
                            )
                            secundaire_zetten_score = alle_geldige_zetten_score(
                                bord_p, self.kleur
                            )

                            if not secundaire_zetten_score:
                                z_o.append(-20)
                            else:
                                z_o.append(
                                    z[2]
                                    - z_o[2]
                                    + max([item[2] for item in secundaire_zetten_score])
                                )

                        z.append(min([item[3] for item in zetten_score_o]))

                    else:
                        z_ult = z
                        break

                if not z_ult:
                    m = max([item[3] for item in primaire_zetten_score])
                    beste_zetten = [
                        [item[0], item[1]]
                        for item in primaire_zetten_score
                        if item[3] == m
                    ]

                    zet = random.choice(beste_zetten)

                else:
                    zet = z_ult

            bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

        return bord, self.status
