Preferans position analyzer
===========================

Two implementations of recursive analyzer for [preferans](https://en.wikipedia.org/wiki/Preferans) game positions.

I wrote the Python one initially, but it was too slow, so I've reimplemented it in Scala. But I didn't want to throw the Python implementation away, so it's here too. Scala implementation is about 50 times faster.

Input format
------------

The input is a position description in JSON format; two samples are provided in files [kow_miser.json](./kow_miser.json) and [train.json](./train.json); the first one is the famous Sofia Kowalewskaya misère.

The format should be rather straightforward; some top-level fields to note:
* `misere`: Boolean, defaults to false;
* `turn`: `East`, `West` or `South`, the player making the first move;
* `trump`: Unicode symbol of trump suit; no trumps by default.

Invocation
----------

To launch the Python implementation, run

        python pref_analyzer.py < position.json

for Scala implementation:

        sbt run < position.json

or

        sbt package
        java -cp target/scala-2.12/pref_analyzer_2.12-0.1.0-SNAPSHOT.jar:$(cat target/streams/compile/dependencyClasspath/_global/streams/export) lvu.pref.PrefAnalyzer < position.json

(modify according to your Scala version etc).
