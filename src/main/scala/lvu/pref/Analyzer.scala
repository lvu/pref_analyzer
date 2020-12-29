package lvu.pref

import scala.collection.mutable.{Map => MutableMap}

case class AnalysisResult(numTricks: Int, gameplay: List[Trick])

case class Top(player: Player.Value, card: Card)

object Analyzer {
  def genRunStarts(stack: Stack): Iterator[Rank] = {
    stack.ranks
      .sliding(2)
      .map(_.toList)
      .zipWithIndex
      .filter { case (pair, idx) =>
        idx == 0 || !(pair(0) isAdjacent pair(1))
      }
      .map(_._1(0))
  }

  def genCards(hand: Hand, allowedSuites: Iterable[Suite.Value]): Iterator[Card] = {
    allowedSuites
      .map {suite =>
        genRunStarts(hand.cards(suite)).map(Card(suite, _))
      }
      .reduce(_ ++ _)
  }
}

case class Analyzer(trump: Option[Suite.Value], misere: Boolean) {
  import Analyzer._
  private val resultsCache = MutableMap.empty[Position, AnalysisResult]

  val resultOrdering = Ordering by {res: AnalysisResult => res.numTricks}
  val declarerGoal = if (misere) resultOrdering.reverse else resultOrdering
  val defenderGoal = if (misere) resultOrdering else resultOrdering.reverse

  def analyzePosition(pos: Position): AnalysisResult = {
    if (pos.isEmpty) {
      AnalysisResult(0, List.empty[Trick])
    } else {
      if (!resultsCache.contains(pos)) {
        resultsCache.put(pos, bestMoves(pos, List.empty[Card], pos.turn, None))
      }
      resultsCache(pos)
    }
  }

  def bestMoves(
    pos: Position, movesSoFar: List[Card], turn: Player.Value,
    top: Option[Top]
  ): AnalysisResult = {
    if (turn == pos.turn && !movesSoFar.isEmpty) {  // all moves are made
      val trick = Trick(movesSoFar, top.get.player)
      analyzePosition(pos.play(trick)) match {
        case AnalysisResult(numTricks, gameplay) => AnalysisResult(
          numTricks + (if (top.get.player == Player.South) 1 else 0),
          trick +: gameplay
        )
      }
    } else {
      val hand = pos.hands(turn)
      val goal = if (turn == Player.South) declarerGoal else defenderGoal
      val cardGenerator = movesSoFar match {
        case Nil => genFistCard(hand)
        case x::_ => genNextCard(hand, x.suite)
      }
      val newTop: Card => Top = movesSoFar match {
        case Nil => Top(turn, _)
        case x::_ => {
          val cardOrdering = makeCardOrdering(x.suite)
          val topOrdering = Ordering.by{t: Top => t.card}(cardOrdering)

          {card => topOrdering.max(Top(turn, card), top.get)}
        }
      }

      cardGenerator
        .map(card => bestMoves(pos, movesSoFar :+ card, turn.next, Some(newTop(card))))
        .max(goal)
    }
  }

  def genFistCard(hand: Hand): Iterator[Card] = genCards(hand, Suite.values)

  def genNextCard(hand: Hand, leadSuite: Suite.Value): Iterator[Card] = {
    if (!hand.cards(leadSuite).isEmpty) {
      genCards(hand, Seq(leadSuite))
    } else if (trump.isDefined && !hand.cards(trump.get).isEmpty) {
      genCards(hand, Seq(trump.get))
    } else {
      genCards(hand, Suite.values)
    }
  }

  def makeCardOrdering(leadSuite: Suite.Value): Ordering[Card] = Ordering.by {card: Card =>
    val trumpOrLead = trump.getOrElse(leadSuite)
    val suiteRank = if (trump.isDefined && card.suite == trump.get) 3 else if (card.suite == leadSuite) 2 else 1
    (suiteRank, card.rank)
  }
}
