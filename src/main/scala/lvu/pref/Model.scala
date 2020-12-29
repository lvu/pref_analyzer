package lvu.pref

import scala.collection.immutable.TreeSet

object Suite extends Enumeration {
  val Spades = Value("♠")
  val Clubs = Value("♣")
  val Diamonds = Value("♦")
  val Hearts = Value("♥")
}

object Rank {
  def apply(label: String): Rank = Rank(label match {
    case "A" => 14
    case "K" => 13
    case "Q" => 12
    case "J" => 11
    case _ => label.toInt
  })
}

case class Rank(value: Int) extends Ordered[Rank] {
  override def toString: String = value match {
    case 14 => "A"
    case 13 => "K"
    case 12 => "Q"
    case 11 => "J"
    case _ => value.toString
  }

  def compare(that: Rank): Int = this.value compare that.value

  def isAdjacent(that: Rank): Boolean = (this.value - that.value).abs == 1
}

case class Card(suite: Suite.Value, rank: Rank) {
  override def toString: String = suite.toString + rank.toString
}

case class Stack(ranks: TreeSet[Rank]) {
  def remove(card: Rank): Stack = {
    assert(ranks contains card)
    Stack(ranks - card)
  }
  
  def isEmpty: Boolean = ranks.isEmpty
}

case class Hand(cards: Map[Suite.Value, Stack]) {
  def remove(card: Card): Hand = Hand(
    cards + (card.suite -> cards(card.suite).remove(card.rank))
  )

  def isEmpty: Boolean = cards.values.forall(_.isEmpty)
}

object Player extends Enumeration {
  protected case class Val() extends super.Val {
    implicit def value2Val(value: Value) = value.asInstanceOf[Val]
    def next: Val = Player((id + 1) % values.size)
    private def iterateTo(end: Player.Value): Stream[Player.Value] = {
      this #:: {
        if (next == end) {
          Stream.empty
        } else {
          next.iterateTo(end)
        }
      }
    }
    def iterate: Stream[Player.Value] = iterateTo(this)
  }
  implicit def value2Val(value: Value) = value.asInstanceOf[Val]

  val East, West, South = Val()
}

case class Trick(
  cards: List[Card],  // starting from first who plays the card
  winner: Player.Value
)

case class Position(hands: Map[Player.Value, Hand], turn: Player.Value) {
  def play(trick: Trick): Position = {
    val newHands = turn.iterate.zip(trick.cards).map{
      case (player, card) => player -> hands(player).remove(card)
    }.toMap
    Position(newHands, trick.winner)
  }

  def isEmpty: Boolean = hands.values.forall(_.isEmpty)
}
