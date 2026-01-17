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
        self.strategy = "Always picks a random move from all available valid moves. When checked, picks a random move from all valid moves that resolve the threat."
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "random player"

    def make_move(self, bord):
        zet_status, zetten = alle_geldige_zetten(bord, self.kleur)

        if zet_status == 4:
            if self.verbose:
                print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
            self.status = 0
            return bord, self.status, 0

        elif zet_status == 3:
            if self.verbose:
                print(f"\n{self.kleur} staat schaakmat.")
            self.status = 0
            return bord, self.status, 0

        else:
            zet = random.choice(zetten)
            bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
            return bord, self.status, 0


class score_player:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Always checks all available valid moves, also when checked, and then chooses randomly among the subset of moves that yields the highest 
        score. Score is 1 if a pawn is captured, 2 for a knight, 3 for a rook or a bishop and 4 for the queen. It is 2 when the opponent is checked, and 7 when he 
        is checkmated or can't make any valid move for another reason."""
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "score player"

    def make_move(self, bord):
        zet_status, zetten = alle_geldige_zetten(bord, self.kleur)

        if zet_status == 4:
            if self.verbose:
                print(f"\n{self.kleur} kan geen geldige zet meer uitvoeren.")
            self.status = 0
            return bord, self.status, -5

        elif zet_status == 3:
            if self.verbose:
                print(f"\n{self.kleur} staat schaakmat.")
            self.status = 0
            return bord, self.status, -5

        else:
            zetten_score = alle_geldige_zetten_score(bord, self.kleur)

            m = max([item[2] for item in zetten_score])
            beste_zetten = [item for item in zetten_score if item[2] == m]

            zet = random.choice(beste_zetten)
            bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)

            return bord, self.status, m


class thinking_one_ahead_player:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Assumes that the OTHER player is a 'score player', meaning that all available valid moves are listed, 
        and subsequently a random choice is made among the subset of moves that yields the highest score. Score is 1 if a pawn is 
        captured, 2 for a knight, 3 for a rook or a bishop, 4 for the queen, 2 when the move results in a check and 7 when he 
        is checkmated or can't make any valid move for another reason.
        
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
        zetten_score = alle_geldige_zetten_score(bord, self.kleur)

        if not zetten_score:
            if self.verbose:
                print(
                    f"\n{self.kleur} staat schaakmat of kan om een andere reden geen geldige zet meer uitvoeren."
                )
            self.status = 0
            return bord, self.status, -5

        else:
            m = max([item[2] for item in zetten_score])

            if m == 7:
                beste_zetten = [item for item in zetten_score if item[2] == m]
                zet = random.choice(beste_zetten)
                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status, 7

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

                return bord, self.status, m_n


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

        zetten_0_score = alle_geldige_zetten_score(bord, self.kleur)

        if not zetten_0_score:
            if self.verbose:
                print(
                    f"\n{self.kleur} staat schaakmat of kan om een andere reden geen geldige zet meer uitvoeren."
                )
            self.status = 0
            return bord, self.status, -5

        else:
            max_0 = max([item[2] for item in zetten_0_score])

            if max_0 == 7:
                beste_zetten = [item for item in zetten_0_score if item[2] == max_0]
                zet = random.choice(beste_zetten)

                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status, 7

            else:
                # 2 - Determine all countermoves and secondary moves with their scores

                change_color_map = {"zwart": "wit", "wit": "zwart"}

                for zet_0 in zetten_0_score:
                    bord_1 = doe_zet(
                        bord, self.kleur, zet_0[0], zet_0[1], controle=False
                    )
                    zetten_1_score = alle_geldige_zetten_score(
                        bord_1, change_color_map[self.kleur]
                    )

                    if not zetten_1_score:  # Betekent dat de andere speler niet schaakmat staat, maar toch geen geldige zet meer kan doen
                        bord = doe_zet(
                            bord, self.kleur, zet_0[0], zet_0[1], controle=False
                        )
                        return bord, self.status, 7

                    else:
                        for zet_1 in zetten_1_score:
                            bord_2 = doe_zet(
                                bord_1,
                                change_color_map[self.kleur],
                                zet_1[0],
                                zet_1[1],
                                controle=False,
                            )
                            zetten_2_score = alle_geldige_zetten_score(
                                bord_2, self.kleur
                            )

                            if not zetten_2_score:
                                zet_1.append(-20)
                            else:
                                zet_1.append(
                                    zet_0[2]
                                    - zet_1[2]
                                    + max([item[2] for item in zetten_2_score])
                                )

                        zet_0.append(min([item[3] for item in zetten_1_score]))

                max_cons = max([item[3] for item in zetten_0_score])
                beste_zetten = [
                    [item[0], item[1]] for item in zetten_0_score if item[3] == max_cons
                ]

                zet = random.choice(beste_zetten)

                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status, max_cons


class thinking_three_ahead_player_conservative:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Assumes nothing about the OTHER player.
        
        The player himself lists all valid moves. If the player himself is checked, only the valid primary moves (= moves that resolve the threat) are investigated. 
        
        For each valid primary move, all possible countermoves are determined with their scores for the opponent. For each countermove the highest scoring secondary move 
        is calculated and its corresponding tertiary move (the last one based on the 'score player' logic). The corresponding net score for the countermove + tertiary move 
        is stored. 

        In this way, for each primary move, the lowest net score can be determined across all possible countermoves. This is a conservative approach. 
        
        Subsequently, the primary move that has the highest 'lowest net score' is then chosen.

        When a move results in a checkmate of the opponent or another situation in which the opponent has zero possible moves left, that move is chosen (no countermove has to be determined). 
        
        """
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "conservative thinking 3 ahead player"

    def make_move(self, bord):
        # 1 - Determine primary moves with their scores

        zetten_0_score = alle_geldige_zetten_score(bord, self.kleur)

        if not zetten_0_score:
            if self.verbose:
                print(
                    f"\n{self.kleur} staat schaakmat of kan om een andere reden geen geldige zet meer uitvoeren."
                )
            self.status = 0
            return bord, self.status, -5

        else:
            max_0 = max([item[2] for item in zetten_0_score])

            if max_0 == 7:
                beste_zetten = [item for item in zetten_0_score if item[2] == max_0]
                zet = random.choice(beste_zetten)

                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status, 7

            else:
                # 2 - Determine all countermoves and secondary moves with their scores

                change_color_map = {"zwart": "wit", "wit": "zwart"}

                for zet_0 in zetten_0_score:
                    bord_1 = doe_zet(
                        bord, self.kleur, zet_0[0], zet_0[1], controle=False
                    )
                    zetten_1_score = alle_geldige_zetten_score(
                        bord_1, change_color_map[self.kleur]
                    )

                    if not zetten_1_score:  # Betekent dat de andere speler niet schaakmat staat, maar toch geen geldige zet meer kan doen
                        bord = doe_zet(
                            bord, self.kleur, zet_0[0], zet_0[1], controle=False
                        )
                        return bord, self.status, 7

                    else:
                        for zet_1 in zetten_1_score:
                            bord_2 = doe_zet(
                                bord_1,
                                change_color_map[self.kleur],
                                zet_1[0],
                                zet_1[1],
                                controle=False,
                            )
                            zetten_2_score = alle_geldige_zetten_score(
                                bord_2, self.kleur
                            )

                            if not zetten_2_score:
                                zet_1.append(-20)
                            else:
                                sub_player = thinking_one_ahead_player(
                                    self.kleur, verbose=False
                                )
                                bord_3, zet_status, score_2 = sub_player.make_move(
                                    bord_2
                                )
                                zet_1.append(zet_0[2] - zet_1[2] + score_2)

                        zet_0.append(min([item[3] for item in zetten_1_score]))

                max_cons = max([item[3] for item in zetten_0_score])
                beste_zetten = [
                    [item[0], item[1]] for item in zetten_0_score if item[3] == max_cons
                ]

                zet = random.choice(beste_zetten)

                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status, max_cons

    # def make_move(self, bord):
    #     # 1 - Determine primary moves with their scores

    #     primaire_zetten_score = alle_geldige_zetten_score(bord, self.kleur)

    #     if not primaire_zetten_score:
    #         if self.verbose:
    #             print(
    #                 f"\n{self.kleur} staat schaakmat of kan om een andere reden geen geldige zet meer uitvoeren."
    #             )
    #         self.status = 0
    #         return bord, self.status, -5

    #     else:
    #         primair_max = max([item[2] for item in primaire_zetten_score])

    #         if primair_max == 7:
    #             beste_zetten = [
    #                 item for item in primaire_zetten_score if item[2] == primair_max
    #             ]
    #             zet = random.choice(beste_zetten)
    #             bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
    #             return bord, self.status, 7

    #         else:
    #             # 2 - Determine all countermoves and secondary moves with their scores

    #             change_color_map = {"zwart": "wit", "wit": "zwart"}

    #             for zet in primaire_zetten_score:
    #                 bord_1 = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
    #                 zetten_score_1 = alle_geldige_zetten_score(
    #                     bord_1, change_color_map[self.kleur]
    #                 )

    #                 if zetten_score_1:  # Normaal gezien zijn er sowieso zetten, anders was primair_max = 7, dus in principe is deze check overbodig
    #                     for zet_1 in zetten_score_1:
    #                         bord_2 = doe_zet(
    #                             bord_1,
    #                             change_color_map[self.kleur],
    #                             zet_1[0],
    #                             zet_1[1],
    #                             controle=False,
    #                         )

    #                         secundaire_zetten_score = alle_geldige_zetten_score(
    #                             bord_2, self.kleur
    #                         )

    #                         if not secundaire_zetten_score:
    #                             zet_1.append(-20)
    #                         else:
    #                             sub_player = thinking_one_ahead_player(
    #                                 self.kleur, verbose=False
    #                             )
    #                             bord_3, zet_status, score = sub_player.make_move(bord_2)
    #                             zet_1.append(zet[2] - zet_1[2] + score)

    #                     zet.append(min([item[3] for item in zetten_score_1]))

    #             m = max([item[3] for item in primaire_zetten_score])

    #             beste_zetten = [
    #                 [item[0], item[1]] for item in primaire_zetten_score if item[3] == m
    #             ]

    #             zet = random.choice(beste_zetten)

    #             bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
    #             return bord, self.status, m


class thinking_four_ahead_player_conservative:
    def __init__(self, kleur, verbose=True):
        self.strategy = """Assumes nothing about the OTHER player.
        
        The player himself lists all valid moves. If the player himself is checked, only the valid primary moves (= moves that resolve the threat) are investigated. 
        
        For each valid primary move, all possible countermoves are determined with their scores for the opponent. For each countermove a 'thinking 2 ahead conservative player' is called that determines
        the highest scoring secondary move (taking into account 2 subsequent moves) and stores its net score across all 5 moves. 

        In this way, for each primary move, the lowest net score can be determined across all possible countermoves. This is a conservative approach. 
        
        Subsequently, the primary move that has the highest 'lowest net score' is then chosen.

        When a move results in a checkmate of the opponent or another situation in which the opponent has zero possible moves left, that move is chosen (no countermove has to be determined). 
        
        """
        self.kleur = kleur
        self.status = 1
        self.verbose = verbose
        self.name = "conservative thinking 3 ahead player"

    def make_move(self, bord):
        # 1 - Determine primary moves with their scores

        zetten_0_score = alle_geldige_zetten_score(bord, self.kleur)

        if not zetten_0_score:
            if self.verbose:
                print(
                    f"\n{self.kleur} staat schaakmat of kan om een andere reden geen geldige zet meer uitvoeren."
                )
            self.status = 0
            return bord, self.status, -5

        else:
            max_0 = max([item[2] for item in zetten_0_score])

            if max_0 == 7:
                beste_zetten = [item for item in zetten_0_score if item[2] == max_0]
                zet = random.choice(beste_zetten)

                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status, 7

            else:
                # 2 - Determine all countermoves and secondary moves with their scores

                change_color_map = {"zwart": "wit", "wit": "zwart"}

                for zet_0 in zetten_0_score:
                    bord_1 = doe_zet(
                        bord, self.kleur, zet_0[0], zet_0[1], controle=False
                    )
                    zetten_1_score = alle_geldige_zetten_score(
                        bord_1, change_color_map[self.kleur]
                    )

                    if not zetten_1_score:  # Betekent dat de andere speler niet schaakmat staat, maar toch geen geldige zet meer kan doen
                        bord = doe_zet(
                            bord, self.kleur, zet_0[0], zet_0[1], controle=False
                        )
                        return bord, self.status, 7

                    else:
                        for zet_1 in zetten_1_score:
                            bord_2 = doe_zet(
                                bord_1,
                                change_color_map[self.kleur],
                                zet_1[0],
                                zet_1[1],
                                controle=False,
                            )
                            zetten_2_score = alle_geldige_zetten_score(
                                bord_2, self.kleur
                            )

                            if not zetten_2_score:
                                zet_1.append(-20)
                            else:
                                sub_player = thinking_two_ahead_player_conservative(
                                    self.kleur, verbose=False
                                )
                                bord_3, zet_status, score_2 = sub_player.make_move(
                                    bord_2
                                )
                                zet_1.append(zet_0[2] - zet_1[2] + score_2)

                        zet_0.append(min([item[3] for item in zetten_1_score]))

                max_cons = max([item[3] for item in zetten_0_score])
                beste_zetten = [
                    [item[0], item[1]] for item in zetten_0_score if item[3] == max_cons
                ]

                zet = random.choice(beste_zetten)

                bord = doe_zet(bord, self.kleur, zet[0], zet[1], controle=False)
                return bord, self.status, max_cons
