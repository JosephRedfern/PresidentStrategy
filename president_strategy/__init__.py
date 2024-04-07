import enum
from typing import Optional
from functools import total_ordering
import random

LOG = False
MAX_ITERS = 10_000


def log(string: str) -> None:
    if LOG:
        print(string)


class CardStrategyException(Exception):
    pass


class StartStrategy(enum.Enum):
    PLAY_LOWEST = 0


class MidgameStrategy(enum.Enum):
    PLAY_LOWEST = 0
    PLAY_HIGHEST = 1
    PLAY_RANDOM = 2


class Suit(enum.Enum):
    HEARTS = 0
    DIAMOND = 1
    SPADES = 2
    CLUBS = 3


class Value(enum.IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    JOKER = 15


@total_ordering
class Card:
    def __init__(self, suit: Suit, value: Value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return f"{self.value} of {self.suit}"

    def __eq__(self, other):
        return (self.suit == other.suit) and (self.value == other.value)

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    @classmethod
    def get_hand(cls) -> list["Card"]:
        hand = []
        for s in Suit:
            for v in Value:
                hand.append(cls(s, v))

        return hand


class Hand:
    def __init__(self, n):
        self.n = n
        self.cards = []

    def deal(self, card: Card) -> None:
        log(f"Hand {self.n} has been dealt: {card}")
        self.cards.append(card)

    def get_random(self, n: int = 1, current_card: Optional[Card] = None) -> Optional[int]:
        candidate_cards = self.cards if not current_card else [c for c in self.cards if c > current_card]

        if len(candidate_cards) > 0:
            return self.cards.index(random.choice(candidate_cards))

        # We can't play
        return None

    def get_highest(self, n: int = 1, current_card: Optional[Card] = None) -> Optional[int]:
        """Return index of highest card"""
        candidate_cards = self.cards if not current_card else [c for c in self.cards if c > current_card]

        log(f"{current_card=}, {self.cards=}, {candidate_cards=}")

        if len(candidate_cards) > 0:
            return self.cards.index(max(candidate_cards))

        # We can't play
        return None

    def get_lowest(self, n: int = 1, current_card: Optional[Card] = None) -> Optional[int]:
        """Return index of lowest card"""
        candidate_cards = self.cards if not current_card else [c for c in self.cards if c > current_card]

        log(f"{current_card=}, {self.cards=}, {candidate_cards=}")

        if len(candidate_cards) > 0:
            return self.cards.index(min(candidate_cards))

        # We can't play
        return None


def get_hands(hand_count: int) -> list[Hand]:
    hands: list[Hand] = [Hand(n) for n in range(hand_count)]

    hand = Card.get_hand()
    random.shuffle(hand)

    for n, card in enumerate(hand):
        hands[n % hand_count].deal(card)

    return hands


def random_game(hand_count: int, starter: int = 0):
    hands: list[Hand] = get_hands(hand_count)

    # Set up player strategies
    strategies = {hand: MidgameStrategy.PLAY_RANDOM for hand in hands}

    # strategies[hands[1]] = MidgameStrategy.PLAY_RANDOM
    # strategies[hands[2]] = MidgameStrategy.PLAY_HIGHEST

    for hand in hands:
        log(f"{hand.n}: {hand.cards}")

    active_hands = hands.copy()

    # Current deck. `None` is a special value used to indicate that any card is allowed (e.g start of round)
    heap = [None]

    # Iteration tracker
    iteration = 0

    # Current hand -- index into active hands, based on `starter` (defaulting to 1)
    current_hand = active_hands[starter]

    # `finishers` contains the hand index in order of completion.
    finishers = []

    # track the index of the last played hand
    last_played_hand_number = None

    # While there's more than one active hand, play the game.
    while len(active_hands) > 1 and iteration < MAX_ITERS:
        # If the current hand was the last to play, then it's a new round, so inject None into deck to trigger
        # arbitrary start card
        if last_played_hand_number == current_hand.n:
            print(f"{iteration}. Deadlock detected, triggering new game")
            heap.append(None)

        # For the current hand, determine next card to play.
        index = get_card_index(current_hand, strategies[current_hand], n=1, current_card=heap[-1])

        # If we were able to play, place the card down onto the heap, otherwise, move to next player.
        if index is not None:
            played_card = current_hand.cards.pop(index)
            log(f"Hand {current_hand.n} playing {played_card}")
            heap.append(played_card)
            last_played_hand_number = current_hand.n
        else:
            log(f"Hand {current_hand.n} cannot play!")
            # heap.append(None)

        if len(current_hand.cards) == 0:
            log(f"[!] Hand {current_hand.n} has finished!")
            active_hands.pop(active_hands.index(current_hand))
            finishers.append(current_hand.n)

        iteration += 1
        current_hand = active_hands[(starter + iteration) % len(active_hands)]

    if iteration == MAX_ITERS:
        log("Max iterations hit, something has happened...")

    loser = active_hands.pop()

    finishers.append(loser.n)

    return finishers


def get_card_index(
    hand: Hand,
    strategy: MidgameStrategy,
    n: int = 1,
    current_card: Optional[Card] = None,
) -> Optional[int]:
    match strategy:
        case MidgameStrategy.PLAY_LOWEST:
            log(f"Using PLAY_LOWEST MidgameStrategy")
            return lowest_card_strategy(hand, n, current_card)
        case MidgameStrategy.PLAY_HIGHEST:
            log(f"Using PLAY_HIGHEST MidgameStrategy")
            return highest_card_strategy(hand, n, current_card)
        case MidgameStrategy.PLAY_RANDOM:
            log(f"Using PLAY_RANDOM MidgameStrategy")
            return random_card_strategy(hand, n, current_card)
        case _:
            raise CardStrategyException("Invalid MidgameStrategy")


def lowest_card_strategy(hand: Hand, n: int = 1, current_card: Optional[Card] = None) -> Optional[int]:
    return hand.get_lowest(current_card=current_card, n=n)


def highest_card_strategy(hand: Hand, n: int = 1, current_card: Optional[Card] = None) -> Optional[int]:
    return hand.get_highest(current_card=current_card, n=n)


def random_card_strategy(hand: Hand, n: int = 1, current_card: Optional[Card] = None) -> Optional[int]:
    return hand.get_random(current_card=current_card, n=n)
