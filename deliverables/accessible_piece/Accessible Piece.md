# Can a Cheap Cap Read the Deep Brain? What We Found on the First Try

*Dandelion Engineering — "EEG to LFP" Collaboration Station*
*A plain-language companion to the project's Technical Report. No background assumed.*

---

## The dream behind the project

Imagine a soft cap, the kind you could buy for a few hundred dollars, that you slip onto your head at home. It has a couple dozen little metal sensors that rest against your scalp. It doesn't touch your brain, doesn't inject anything, doesn't cost a fortune. And yet — somehow — it gives you a picture of what's happening *deep* inside your brain, in the structures that handle memory and emotion.

That's the long-term dream. We call it **"electrical fMRI."**

To unpack the name: an [**fMRI**](https://en.wikipedia.org/wiki/Functional_magnetic_resonance_imaging) (functional magnetic resonance imaging) is the machine that produces those famous "brain lighting up" images. It can see activity deep in the brain in three dimensions. But it's the size of a room, costs millions of dollars, requires you to lie perfectly still inside a giant magnet, and is booked solid at hospitals and universities. Almost nobody has casual access to one.

The cheap cap is called [**EEG**](https://en.wikipedia.org/wiki/Electroencephalography) (electroencephalography). It measures the brain's electrical activity from the scalp. It's portable, affordable, and already used in clinics and even in consumer headbands. But it has a reputation for only seeing the *surface* of the brain — the outer layer, the cortex — and being nearly blind to anything deep.

The dream of "electrical fMRI" is to close that gap: to use the cheap, accessible tool (EEG) plus modern AI to recover some of what only the expensive, inaccessible tool (fMRI) can normally show. If it worked, even a little, it would put a window into the deep brain within reach of ordinary people — for research, and eventually for monitoring health. That is exactly the kind of thing Dandelion exists to build.

This is a huge, multi-year goal. It will take many projects. **This project was the first rung on that ladder** — the smallest honest step we could take that would actually tell us something real and checkable.

---

## Why this is hard (and why there was reason for hope)

Here's the core problem. When brain cells fire, they create tiny electric fields. Those fields spread outward through brain tissue, then through the skull, then to the scalp where the EEG sensors sit. The trouble is that the **skull is a terrible conductor of electricity** — roughly a hundred times worse than brain tissue. So by the time a deep signal reaches the scalp, it's been smeared, weakened, and blended together with everything else. Picking out one faint deep voice from that blurred crowd is, on the face of it, nearly impossible. Scientists generally treat the deep brain as good as invisible to a scalp cap.

So why try at all? Because of one hopeful fact: **the deep brain doesn't work in isolation.** The deep structure we focused on is the [**medial temporal lobe (MTL)**](https://en.wikipedia.org/wiki/Medial_temporal_lobe), home of the [hippocampus](https://en.wikipedia.org/wiki/Hippocampus) — the brain's memory hub. When you're using your memory, the MTL is in constant conversation with the outer cortex. And the cortex is exactly the part EEG *can* see.

So even if the cap can't hear the deep brain directly, the deep brain's *influence* on the surface might leave a kind of fingerprint — an indirect trace that a smart enough method could learn to recognize. Prior research supports this: deep memory structures and the scalp do show measurable, coordinated rhythms during memory tasks. The bet of this project was that those traces are not just present but **learnable** by AI.

---

## The thing that made it testable: a rare dataset

A dream isn't science until you can check it against reality. The make-or-break ingredient here was finding the right **ground truth** — a way to know what the deep brain was *actually* doing, so we could check our guesses from the scalp against the real answer.

That ground truth is extraordinarily hard to get, because it means recording from inside a living human brain. It exists only in a special situation: epilepsy patients who, as part of their medical care, have electrodes placed deep in their brains to find the source of their seizures. With consent, some of these patients take part in research while those electrodes are in place.

We used an [**open dataset published by Boran and colleagues in 2020**](https://doi.org/10.12751/g-node.d76994) (freely available, licensed for reuse including commercial use). It is rare and valuable because it recorded, **at the same time, from the same nine patients:**

- the **scalp EEG** (the cheap signal — our input),
- the **deep intracranial recordings** from in and around the medial temporal lobe (the ground truth — what we're trying to infer), and
- even the firing of **individual neurons** deep in the brain.

"At the same time" is the whole point. It means we can take the scalp signal at a given moment, make an inference about what's happening deep down, and check it against what was *actually* recorded deep down in that same brain at that same instant. That simultaneity is what turns "guess the deep brain from the scalp" from speculation into a real, measurable test.

While the recordings were made, the patients did a memory task called the [**Sternberg task**](https://en.wikipedia.org/wiki/Sternberg_task): they were shown a small set of letters to hold in mind, waited a moment, then were asked whether a particular letter had been in the set. Sometimes they had to hold a few letters, sometimes more. How many things you're holding in mind at once is called your **working-memory load** — and that became our target.

---

## What we actually tested (the first rung)

We deliberately did *not* try to build the whole "electrical fMRI" dream in one go. We picked the smallest version that would still teach us something real.

The question, in plain terms:

> **Can a computer look only at the scalp EEG and tell whether the person was holding *a lot* in mind versus *a little* — on a person it has never seen before — and is whatever it's picking up genuinely tied to real deep-brain memory activity?**

Two parts to that question, and both matter:

1. **Can it read the load from the scalp, and does it generalize to a brand-new person?** (Reading it on someone the computer already practiced on is easy and doesn't prove much — see the next section on why.)
2. **If it can, is it actually using deep-brain memory signals — or just some unrelated shortcut?**

We chose "working-memory load" as the target on purpose: it's defined entirely by the task (how many letters you were told to hold), so it's honest and easy for anyone to check, with no circular reasoning.

---

## How we tested it honestly (this part matters most)

It's surprisingly easy to fool yourself in this kind of work. A lot of the project was about *not* fooling ourselves. Three safeguards did the heavy lifting.

**1. Test on people the computer has never seen.** The biggest trap in machine learning is letting the computer "memorize" rather than "understand." If you train and test on the same person, the computer can latch onto quirks of that one brain and look brilliant — while having learned nothing that transfers. The honest way to test a general claim is called [**leave-one-subject-out**](https://en.wikipedia.org/wiki/Cross-validation_(statistics)): train on eight patients, test on the ninth, and rotate so every patient gets a turn as the unseen test case. We treated this as a hard requirement. A claim about "reading the deep brain" only counts if it works on a person the method never trained on.

**2. Compare against sneaky shortcuts, not just against random guessing.** Beating a coin flip isn't impressive if there's an easier explanation lying around. So we built **controls** — deliberately "dumb" predictors that use *no brain signal at all*, only task bookkeeping (like reaction times, or which trial it was). If a control does as well as our brain-based method, then our method isn't really reading the brain; it's exploiting the same bookkeeping shortcut.

This safeguard earned its keep. One control turned out to be sneakily strong, and the reason is a beautiful little lesson in how hidden patterns creep in. **In this task, an incorrect answer was followed by an automatically easier (low-load) next trial.** So just by knowing "was the previous trial wrong?", you could guess the current load far better than chance — with zero brain data. When the previous trial was wrong, the next was low-load 98.5% of the time. That's not cheating by us; it's a real, built-in quirk of the task's design, and any honest method has to *beat* it, not just beat random guessing. We set our success bar above this strong shortcut, not above a coin flip.

**3. Decide what counts as success *before* looking at the answer.** We wrote down, in advance, exactly what would count as a win, a loss, or an inconclusive result. This is the scientific equivalent of calling your shot before you swing — it stops you from drawing the bullseye around wherever the arrow happened to land. Our bar: the brain method had to beat the best shortcut by a clear margin, do so for most of the nine patients, and *not* depend on any single lucky patient.

We also didn't just try one AI method. We climbed a **ladder of models**, from simple and cheap to more sophisticated — ending with a compact neural network designed for EEG. (We wrote even the heaviest method to run on an ordinary laptop, because affordability is part of the mission, not an afterthought.)

---

## What we found

The honest answer comes in two parts, and we'd written both down as possibilities ahead of time.

### Part A: A clean "no" — but a useful one

**Reading working-memory load from the scalp, in a way that transfers to a new person, did not clear our bar.** The simpler models all fell short of the strong shortcut. The most sophisticated model (the neural network) was the *only* one to beat the shortcut on average — but it failed the robustness test in exactly the way we'd designed that test to catch: **its entire advantage came from a single patient.** Remove that one person, and the advantage vanished. A result that rests on one lucky subject out of nine is not a real, general finding, and our pre-written rules correctly flagged it as a failure.

We also pinned down *why* it failed, which is the valuable part. It wasn't that our AI was too weak. We checked: the limiting factor is the **handful of scalp sensors shared across all patients, combined with the demand that one model work across different people.** Different brains are wired differently enough that, with only the few sensors every patient had in common, there simply wasn't a stable, shared "load fingerprint" to latch onto. Throwing fancier AI at it wouldn't help — so we didn't waste compute doing that. We found the wall and identified what the wall is made of.

**Why a "no" is genuinely worth something here.** This is the part that's easy to misunderstand. In real research, a clearly-established negative is not a failure — it's a map. We now know that *this* particular setup (a few shared scalp sensors, one model for everyone) can't carry the first claim. That redirects the whole long-term effort early and cheaply, before anyone sinks years into the wrong approach. A vague "it didn't quite work" teaches nothing; a *clean, well-understood* "no, and here's exactly why" is a real contribution. (Negative results being undervalued — and the [reproducibility problems](https://en.wikipedia.org/wiki/Replication_crisis) that follow when only positive results get reported — is a known issue across science. We're choosing to report ours plainly.)

### Part B: A tantalizing lead that didn't hold up

Here's where it got interesting. Two findings sat side by side:

- **The real deep-brain memory signal was there.** In the deep recordings, we confirmed the expected memory-load pattern in the MTL (a specific shift between two brain rhythms, "theta" and "alpha," as load went up). This showed up in 7 of the 9 patients — a solid, real effect. Good: the deep signal we hoped to eventually read really does exist in this data.

- **And our best scalp model seemed to be tracking it.** When we compared the neural network's scalp-based guesses against that real deep-brain pattern, they lined up — positively, in 7 of 9 patients — *while the simpler models showed no such alignment.* In other words, the one model that squeezed out a bit more load information was also the one that seemed to be echoing the genuine deep-brain rhythm. That was the first whiff of the actual dream: a scalp method faintly tracking a deep-brain signal.

It was exciting. So we did the responsible thing and tried hard to **kill it** — to check whether it was real or a mirage. We mathematically stripped out the task's bookkeeping structure (the same sneaky shortcuts from before) and asked whether the scalp–deep alignment *survived* on its own. **It didn't.** Once the load and task-schedule structure were removed, the alignment faded to essentially nothing. Codex, the other agent on this project, then ran a strict, pre-defined confirmatory test on exactly this question, and it failed cleanly.

What that means: with only nine patients, we **cannot tell the difference** between "the scalp is genuinely echoing a shared deep-brain memory state" and "both signals are independently riding the same task structure." The honest verdict is **exploratory, not proven.** We report it as a *lead worth chasing with more data* — explicitly not as a validated deep-brain readout. Calling a maybe a "yes" would be exactly the self-deception the whole project was built to avoid.

---

## So where does this leave the big dream?

Right where good first steps are supposed to leave it: **further along, and pointed in a clearer direction.**

We didn't reach "electrical fMRI" — we never expected to from one project. What we did was take an honest first measurement and come back with two concrete, useful things:

1. **We found the first wall and identified it.** A few shared scalp sensors plus one-model-for-everyone can't carry transferable deep-state decoding. The next rung should change *that* — richer sensor coverage, or methods tuned to each person, or both.

2. **We found the most promising signal to chase next.** The faint alignment between the best scalp model and the real deep-brain memory rhythm is the single most encouraging thread we found. It needs more patients to settle — enough to separate a genuine shared signal from a shared coincidence — and ideally a task without the sneaky "wrong answer leads to an easier next trial" quirk.

That's what a first rung is for. Not to finish the climb, but to test the ground, find where it's solid and where it gives way, and leave the next session — or the next project — a clear, honest place to put its foot.

---

## How you can check this yourself

You don't have to take our word for any of it. Everything above is backed by a **Reproducibility Packet** that ships with this project: the data is public (free to download from the link above), the code is included, and there's a **verification dashboard** — a single page that lays out, patient by patient, exactly what each method scored and how each result was reached. Anyone who wants to can download the same data, run the same code, and confirm every number for themselves. That's the standard we hold ourselves to: the work should be undeniable because anyone can check it, not because we said so.

---

*This piece is the plain-language companion to the project's full Technical Report, which contains the complete methods, tables, and statistics. Both were produced by the Dandelion Engineering "EEG to LFP" Collaboration Station — AI agents Claude and Codex, working with director Randy Crespo.*
