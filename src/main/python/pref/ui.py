from typing import Generator, Mapping

from .analyze import AnalysisResult
from .cards import Hand, Player, Position, Rank, Suite, Stack, Trick


def print_position(pos: Position) -> None:
    def _gen_lines(player: Player) -> Generator[str, None, None]:
        hand = pos.hands[player]
        if player == pos.turn:
            yield f'*{player.name}*'
        else:
            yield player.name
        for suite in Suite:
            yield f'{suite}: {hand.cards[suite]}'

    hand_width = 30
    for left, right in zip(_gen_lines(Player.West), _gen_lines(Player.East)):
        print(left.ljust(hand_width), right)
    for row in _gen_lines(Player.South):
        print(' ' * (hand_width // 2), row)


def print_trick(trick: Trick) -> None:
    print(' '.join(map(str, trick.cards)), '->', trick.winner.name)


def print_result(pos: Position, result: AnalysisResult) -> None:
    print(f'Tricks: {result.num_tricks}\n')
    for trick in result.gameplay:
        print_position(pos)
        print_trick(trick)
        print()
        pos = pos.play(trick)


def load_position(data: dict) -> Position:
    def _load_hands(data: dict) -> Mapping[Player, Hand]:
        return {
            player: _load_hand(data[player.name])
            for player in Player
        }

    def _load_hand(data: dict) -> Hand:
        return Hand({
            suite: _load_stack(data[suite.value])
            for suite in Suite
        })

    def _load_stack(data: list) -> Stack:
        return Stack(sorted(map(Rank, map(str, data))))

    return Position(
        _load_hands(data['hands']),
        getattr(Player, data['turn'])
    )


