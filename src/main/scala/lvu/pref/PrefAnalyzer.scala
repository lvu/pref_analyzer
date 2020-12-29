package lvu.pref

import play.api.libs.json._

object PrefAnalyzer extends App {
  import CardsJson._

  val json = Json.parse(System.in)
  val maybePos = json.validate[Position]
  val maybeAnalyzer = maybePos.flatMap(_ => json.validate[Analyzer])
  (maybePos, maybeAnalyzer) match {
    case (JsSuccess(pos, _), JsSuccess(analyzer, _)) => println(analyzer.analyzePosition(pos))
    case (_, JsError(errors)) => println(errors)
  }
}
