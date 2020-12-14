# from collections import Mapping as MappingABC
from enum import auto, Enum
from functools import cached_property, total_ordering
from typing import (
    Dict,
    Generator,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)


DECK_SIZE = 32
SUITE_SIZE = DECK_SIZE // 4
ACE_RANK = 14
MIN_RANK = ACE_RANK - SUITE_SIZE + 1


class Suite(Enum):
    Spades = '♠'
    Clubs = '♣'
    Diamonds = '♦'
    Hearts = '♥'

    def __str__(self):
        return self.value


@total_ordering
class Rank:
    
    display_map = {
        **{val: str(val) for val in range(MIN_RANK, 11)},
        11: 'J',
        12: 'Q',
        13: 'K',
        14: 'A',
    }

    reverse_map = {v: k for k, v in display_map.items()}

    def __init__(self, value):
        self.value = self.reverse_map[value]

    def __str__(self):
        return self.display_map[self.value]

    def __repr__(self):
        return f'<Rank: {self}>'

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def is_adjacent(self, other):
        return abs(self.value - other.value) == 1


class Card(NamedTuple):
    suite: Suite
    rank: Rank

    def __str__(self):
        return f'{self.rank}{self.suite}'

    @classmethod
    def from_str(cls, s: str) -> 'Card':
        return cls(Suite(s[0]), Rank(s[1:]))


class Stack:

    """Set of cards of the same suite."""

    def __init__(self, ranks):
        self.ranks = ranks  # should be sorted!

    @property
    def hash_str(self):
        return ''.join(map(str, self.ranks))

    def remove(self, card: Rank):
        pos = self.ranks.index(card)
        return type(self)(self.ranks[:pos] + self.ranks[pos + 1:])

    def __str__(self):
        return ' '.join(map(str, self.ranks))

    def __bool__(self):
        return bool(self.ranks)


class Hand:

    def __init__(self, cards: Mapping[Suite, Stack]) -> None:
        self.cards = cards

    @property
    def hash_str(self):
        return '|'.join(
            '' if suite not in self.cards else self.cards[suite].hash_str
            for suite in Suite
        )

    def remove(self, card) -> 'Hand':
        return type(self)({
            **self.cards,
            card.suite: self.cards[card.suite].remove(card.rank)
        })

    def __str__(self):
        return '\n'.join(
            f'{suite}: {cards[suite]}' for suite in Suite
        )

    def __bool__(self):
        return any(self.cards.values())


class Player(Enum):
    East = auto()
    West = auto()
    South = auto()

    @property
    def index(self):
        return self.value - 1

    def next(self) -> 'Player':
        return type(self)(self.value % len(type(self)) + 1)

    def iterate(self) -> Generator['Player', None, None]:
        player = self
        while True:
            yield player
            player = player.next()
            if player is self:
                break


class Trick(NamedTuple):
    cards: Tuple[Card, ...]  # starting from first who plays the card
    winner: Player


class Position:

    """
    Position representation; includes cards on all players' hands
    and a notion of a player whose turn it is currently.
    """

    def __init__(
        self,
        hands: Union[Mapping[Player, Hand], Iterable[Hand]],
        turn: Player
    ):
        self.hands: Mapping[Player, Hand]
        if isinstance(hands, Mapping):
            self.hands = hands
        else:
            self.hands = dict(zip(Player, hands))
        self.turn = turn

    @property
    def hands_tuple(self) -> Tuple[Hand, ...]:
        return tuple(self.hands[player] for player in Player)

    @property
    def hands_dict(self) -> Mapping[Player, Hand]:
        return self.hands

    @cached_property
    def hash_str(self):
        return '{0}:{1}'.format(
            self.turn.name,
            ':'.join(hand.hash_str for hand in self.hands_tuple)
        )

    def play(self, trick: Trick) -> 'Position':
        new_hands = {
            player: self.hands[player].remove(card)
            for player, card in zip(self.turn.iterate(), trick.cards)
        }
        return type(self)(new_hands, trick.winner)

    def __bool__(self):
        return any(self.hands.values())
