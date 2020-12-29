package lvu.pref

import play.api.libs.json._
import play.api.libs.json.Reads._
import play.api.libs.functional.syntax._

import scala.collection.immutable.TreeSet

object CardsJson {
  implicit val rankReads: Reads[Rank] = __.read[String].map(Rank.apply _)
  implicit val stackReads: Reads[Stack] = __.read[List[Rank]].map(s => Stack(TreeSet(s:_*)))
  implicit val handReads: Reads[Hand] = __.read[Map[String, Stack]]
    .map(_.map{case (k, v) => Suite.withName(k) -> v})
    .map(Hand.apply _)
  implicit val hadsReads: Reads[Map[Player.Value, Hand]] = __.read[Map[String, Hand]]
    .map(_.map{case (k, v) => Player.withName(k) -> v})
  implicit val playerReads: Reads[Player.Value] = __.read[String].map(Player.withName)
  implicit val suiteReads: Reads[Suite.Value] = __.read[String].map(Suite.withName)
  implicit val positionReads: Reads[Position] = (
    (__ \ "hands").read[Map[Player.Value, Hand]] and
    (__ \ "turn").read[Player.Value]
  )(Position.apply _)
  implicit val analyzerReads: Reads[Analyzer] = (
    (__ \ "trump").readNullable[Suite.Value] and
    (__ \ "misere").readWithDefault[Boolean](false)
  )(Analyzer.apply _)
}
