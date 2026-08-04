# I mined 91,606 cuneiform tablets for AI engineering insights. My own pipeline then killed most of what I found.

*Kristian Baer, Northtek. August 2026. The repo with every number, script, and retraction is
[here](https://github.com/NORTHTEKDevs/sumerian-agent-patterns). Nothing in this post is
peer-reviewed, and the post will tell you exactly which claims survived how much scrutiny.*

---

Four thousand years ago, Sumerian scribes ran what might be the largest document-processing
operation of the ancient world. Receipts, ledgers, ration lists, all pressed into clay in their
tens of thousands. When a scribe finished recording one transaction and started the next, he
often drew a physical line across the tablet.

Those lines survive. The [SumTablets corpus](https://aclanthology.org/2024.ml4al-1.20/)
(Simmons, Diehl Martinez and Jurafsky, ACL 2024) preserves 91,606 tablets as machine-readable
transliteration, with the ruling lines marked.

Here is why that matters to anyone building AI systems: those lines are chunk boundaries. Real
ones. Drawn by the document's author, for operational reasons, four millennia before anyone
needed to decide where one "retrievable unit" of agent memory ends and the next begins. Every
text-segmentation benchmark I could find uses boundaries that a modern annotator judged, or that
the text's own author wrote as section headers, or that researchers manufactured by concatenating
unrelated documents. A ruling on clay is none of those. The mark was drawn four thousand years
before chunking algorithms existed, which rules out the usual worry that the ground truth was
shaped by the methods being tested. It does not rule out transcription noise, since what I
actually evaluate against is the modern editorial record of those marks, and I come back to that
honestly in the caveats.

So I tested modern chunking signals against it. That part worked out. The part worth reading
about is everything that broke on the way.

## The part where my findings died

My original release claimed three statistical findings. A self-audit killed two of them.

The first said ruling boundaries were "statistically proven" to be logical row separators, with
p = 0.002. The problem: my null hypothesis shuffled all the tablet's tokens, which destroys the
local coherence that any real text has. Beating that null proves your text is text. When I built
a null that only moves the boundary positions, the effect reversed sign. The corrected,
full-corpus version of the test found something real, but it found the opposite of what I had
published: adjacent ruling-delimited chunks share fewer trigrams than arbitrary cuts, not more.

The second claimed Sumerian administrative text was "DSL-like" based on Zipf exponents.
That one turned out to be a stream-length artifact. At equal corpus sizes the genre differences
collapsed. The estimator was also the biased one that Clauset, Shalizi and Newman spent a famous
paper warning people about.

Then I audited my detection regexes against the
[Oracc ePSD2](http://oracc.org/epsd2/admin/ur3) expert lemmatisation, 3.6 million tokens of
published Assyriological annotation. My probe for the royal title "lugal" (king) turned out to
match personal names 41% of the time. Thousands of people in Ur III Mesopotamia were named
Lugal-something, the way people today are named Kingsley. No regex can tell them apart. Five of
my ten probes failed that audit badly enough that the data files now carry machine-readable
DO-NOT-CITE flags on them.

If you run regex or keyword scoring anywhere in your agent evals, I would take that last
paragraph personally. My probes looked completely authoritative until measured, and then the
worst of them came in at 6% precision at the construction level, and the royal-title probe at
58% against gold lemmatisation. Yours are unaudited too.

## The part that survived everything

After the retractions I rebuilt the whole thing with permutation tests, pre-registered
hypotheses, and an adversarial review gate (more on that below). One finding survived every
round, and got stronger each time:

**For record-structured text, sparse closing markers beat similarity signals at finding
boundaries. It is not close.**

The evaluation: give each method a document's lines with the boundaries removed, tell it how many
segments there are, and ask it to put the cuts back. Score with the standard segmentation metrics
(Pk, lower is better). Random cuts are the chance floor.

On 1,717 administrative tablets, cutting after validated record-closing formulae (the
"received" formula szu ba-ti, the seal formula kiszib) achieved Pk 0.208 on the tablets that
carry such a formula, against 0.408 for random cuts on those same tablets. Meanwhile the
similarity objective that "semantic chunking" descends from, minimising lexical overlap between
adjacent chunks, lost to random cuts 550 to 1,165 in paired comparisons, despite the underlying
boundary-similarity association being statistically robust. Knowing that boundaries correlate
with a signal does not mean the signal can find them. I now treat every "boundaries correlate
with X, therefore chunk on X" argument as unproven until X actually recovers boundaries.

Then the modern replication. Git commit histories are record streams with boundaries defined by
the version-control system, and some projects close every record with attribution trailers.
Signed-off-by is the modern szu ba-ti, and I do not mean that as a metaphor: it is a
formulaic closing line that attributes a record to a person. On 300 documents built from git/git
commit windows, cutting at trailers scored Pk 0.252 against 0.464 for random, winning 250 of 263
paired comparisons. The margin was larger than on the tablets.

Same result, two languages, two eras, four thousand years apart.

Embeddings earned a real but smaller place. Out-of-distribution on Sumerian they decisively beat
an identical algorithm running on trigrams (so they extract something n-grams miss, even on a
language no encoder ever saw), and on markerless tablets they were the only thing better than
chance. In-distribution on English commit messages they clearly beat random where records carry
enough text. But which embedding algorithm won flipped between corpora, so the honest guidance is
to probe on your own data rather than trust anyone's default, including mine.

And one of my tablet claims died in the modern replication, which is exactly what
pre-registration is for: fixed-size chunking was worse than random on the tablets, and I said so
loudly. On commit streams it beat random. The tablet result was a fact about how wildly uneven
Ur III record lengths are, not a fact about fixed-size chunking. Retracted and rescoped.

If you maintain an agent framework, the actionable version is one sentence: make your traces
carry explicit end-markers (tool-call terminations, confirmation lines, status closers), because
they cost nothing at generation time and they beat every post-hoc segmentation method I measured
by a wide margin. The Sumerians did this by convention on clay. Most agent traces today do not.

## The machinery that kept me honest

I do not fully trust myself after the first round of this project, so the repo now enforces
honesty mechanically:

- An integrity gate couples the prose to the generated data, and as of this post it covers this
  post: if a number in the paper or in this writeup drifts from the JSON the pipeline emits, the
  build fails. If a retracted claim loses the correction notice sitting next to it, the build
  fails. If a rerun flips a headline result, the build fails. (150 checks at the run before
  publishing; the literal count is printed by scripts/check_integrity.py, run it yourself.)
- Each check was validated by deliberately breaking it. One check turned out to be impossible to
  fail. It got rewritten, because a check that cannot fail proves nothing.
- The paper draft went through a five-reviewer adversarial gate before anyone saw it. The gate
  caught, among other things: a sign test that silently reported p = 1.0 whenever a method lost
  most comparisons, a transfer demo that was ingesting its own output file on rerun, and an
  abstract that advised against embedding-based chunking before any embedding had been tested.
- The follow-up experiments were pre-registered, with the criteria written in the script headers
  before the runs. The data then refuted several of my predictions, and the reports say so in
  those words. Two of three hypotheses in the embedding experiment failed. Two of five in the
  modern replication failed.

Every dead claim is preserved in [CORRECTIONS.md](CORRECTIONS.md) with the control that killed
it. If you want to attack this work, start there; the file is a ranked list of where I was wrong
and how it was caught, and hostile reading is the use case it was written for.

## What this is not

It is not peer-reviewed. No Assyriologist has checked my philology beyond what published
lemmatisation provides, and the ruling annotations I use as ground truth are inherited editorial
markup with no published accuracy figure. The tablet findings concern one maximally formulaic
genre. The commit-stream documents are same-project and same-era, which is gentler than a real
agent trace. Everything is one analyst plus a lot of adversarial tooling, which is not the same
thing as independent replication.

The historical observations, on their own, would not surprise a specialist. Assyriologists have
read rulings as entry separators for a century; what did not exist before, as far as a targeted
literature sweep could establish, was a statistical test of where rulings fall, a use of any
physical scribal mark as segmentation ground truth, or a boundary-recovery evaluation anywhere in
the RAG chunking literature, which evaluates on downstream metrics only.

If you are an Assyriologist, a segmentation researcher, or just someone who enjoys breaking
other people's statistics, the repo reproduces end to end from a clean clone in about ten
minutes for the core pipeline, and [REVIEWERS.md](REVIEWERS.md) lists the softest targets in
order. I would genuinely rather learn a fourth claim is wrong than have this circulate with an
error in it.

## The one-line version

A boundary drawn on clay in 2000 BCE turned out to be a working referee for one of the most
casually made decisions in modern AI systems, and the referee's verdict was that the oldest
solution on record, ending every record with a formulaic closing line, beat every post-hoc
method I measured against it: fixed windows, lexical similarity, and embedding similarity, on
clay and on commit streams alike. Also, check your regexes against ground truth. Mine were measuring people
named Lugal.

---

*Data: [SumTablets](https://aclanthology.org/2024.ml4al-1.20/) (CC BY 4.0),
[Oracc ePSD2](http://oracc.org/epsd2/admin/ur3) (CC BY-SA). Full methods and every number:
[PAPER.md](PAPER.md). Claims ranked by evidence strength: [FINDINGS.md](FINDINGS.md).
Everything retracted, and why: [CORRECTIONS.md](CORRECTIONS.md).*
