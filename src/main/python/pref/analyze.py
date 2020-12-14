import itertools

from operator import itemgetter
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    NamedTuple,
    Optional,
    Tuple,
)

from .cards import Card, Hand, Player, Position, Rank, Stack, Suite, Trick


CardGenerator = Generator[Card, None, None]


class AnalysisResult(NamedTuple):
    num_tricks: int
    gameplay: Tuple[Trick, ...]
    

class Analyzer:

    def __init__(self, trump: Optional[Suite], misere: bool) -> None:
        self.trump = trump
        self.declarer_goal = min if misere else max
        self.defender_goal = max if misere else min
        self._result_cache: Dict[str, AnalysisResult] = {}

    def analyze_position(self, pos: Position) -> AnalysisResult:
        if not pos:
            return AnalysisResult(0, ())

        if pos.hash_str not in self._result_cache:
            try:
                self._result_cache[pos.hash_str] = self._best_moves(
                    pos, (), pos.turn, None, None
                )
            except:
                from .ui import print_position
                print("HERE")
                print_position(pos)
                raise
        return self._result_cache[pos.hash_str]

    def _best_moves(
        self, pos: Position,
        moves_so_far: Tuple[Card, ...], turn: Player,
        top_player: Optional[Player],
        top_card: Optional[Card]
    ) -> AnalysisResult:
        if moves_so_far and turn == pos.turn:  # all moves are made
            assert top_card is not None
            assert top_player is not None
            trick = Trick(moves_so_far, top_player)
            num_tricks, gameplay = self.analyze_position(pos.play(trick))
            if top_player == Player.South:
                num_tricks += 1
            return AnalysisResult(num_tricks, (trick, ) + gameplay)

        hand = pos.hands[turn]
        if turn == Player.South:
            goal = self.declarer_goal
        else:
            goal = self.defender_goal
        if not moves_so_far:  # first card
            card_generator = self._gen_cards(hand)
            def new_top(card):
                return (turn, card)
        else:
            suite = moves_so_far[0].suite
            card_generator = self._gen_next_cards(hand, suite)
            def new_top(card):
                if self._compare_cards(suite, top_card, card) < 0:
                    return (turn, card)
                return (top_player, top_card)

        return goal(
            (
                self._best_moves(
                    pos, moves_so_far + (card, ), turn.next(), *new_top(card)
                ) for card in card_generator
            ),
            key=itemgetter(0)
        )

    def _compare_cards(self, suite: Suite, card1: Card, card2: Card) -> int:
        """Return 1 if card1 > card2 with given suite, -1 if card1 < card2."""
        def suite_rank(card):
            if card.suite == self.trump:
                return 2
            if card.suite == suite:
                return 1
            return 0

        suite_rank1 = suite_rank(card1)
        suite_rank2 = suite_rank(card2)
        if suite_rank1 < suite_rank2:
            return -1
        if suite_rank1 > suite_rank2:
            return 1
        if suite_rank1 == 0:
            return 0  # both are not in suite
        if card1.rank < card2.rank:
            return -1
        return 1

    def _gen_next_cards(self, hand: Hand, suite: Suite) -> CardGenerator:
        if hand.cards[suite]:
            return self._gen_cards(hand, [suite])
        if self.trump is not None and hand.cards[self.trump]:
            return self._gen_cards(hand, [self.trump])
        return self._gen_cards(hand)

    @classmethod
    def _gen_cards(
        cls, hand: Hand, allowed_suites: Iterable[Suite] = Suite
    ) -> CardGenerator:
        return (
            Card(suite, rank)
            for suite in allowed_suites
            for rank in cls._run_starts(hand.cards[suite])
        )

    @classmethod
    def _run_starts(cls, stack: Stack) -> Generator[Rank, None, None]:
        """Generate ranks that make difference for move."""
        prev: Optional[Rank] = None
        for cur in stack.ranks:
            if prev is None or not prev.is_adjacent(cur):
                yield cur
            prev = cur
