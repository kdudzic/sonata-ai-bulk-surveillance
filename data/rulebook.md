# RULEBOOK

## Purpose and Scope

This rulebook defines a structured and transparent framework for how a large language model (LLM) should assess textual inputs to determine whether limited data retention is justified.

The model’s task is strictly limited to deciding between two outcomes:

- DISCARD: no sufficient basis for further data retention
- KEEP_FOR_REVIEW: limited retention is justified for human review

This framework does not assess individuals, predict behavior, or perform risk profiling. It evaluates only the content of the text (or short interaction).

## Core Principle: Least Intrusive Decision-Making

The model should follow the least intrusive decision-making core principle. In practice, this means that it should not read more into the text than there is or assume a threat that has not been clearly expressed. Strong or emotional language on its own is not enough to justify keeping the data. As a rule, retaining data should be rare and clearly justified, not something done by default. In case of doubt, the model should choose DISCARD.

Guiding sub-principles:

- No speculation: do not infer threats in the text
- No overreaction to tone: emotional or harsh language is insufficient
- Retention as exception: KEEP_FOR_REVIEW must remain rare
- Evidence-based reasoning: Decisions must rely on explicit signals

## Unit of Analysis

The model may be made to assess a single statement or a short interaction (a few messages). The full context must be considered, but the decisive element must be identified. No external information may be used.

## Decision Types

If the model decides to DISCARD, it means there are not enough grounds to justify keeping the data any longer. The material can be treated as insufficient to warrant even limited retention for further analysis.

If the model decides to KEEP_FOR_REVIEW, it means the text contains enough signals to justify keeping it for a limited time. This does not mean that any threat has been established - it simply indicates that the content should be passed on for human review.

The decision to DISCARD means that there are no sufficient signals. Its consequence is no retention.

The decision to KEEP_FOR_REVIEW means that there are sufficient signals present. Its consequence is limited retention plus human review.

## Analytical Framework: Signals

### Signals supporting KEEP_FOR_REVIEW

#### First-person intent

Explanation: This is not merely a comment about the world, but a potential declaration of action.

Suggestion of action:

- I'll come
- I'll do it
- I'll go in
- you'll see
- I'll be there tomorrow

#### Specific target

Explanation: The more specific the target, the stronger the basis for KEEP_FOR_REVIEW.

Identifiable place, person, event:

- a specific place
- a specific institution
- a specific event
- a specific person or group
- a specific object

#### Temporal proximity

Explanation: The closer and more clearly defined the timeframe, the stronger the signal.

Near-term timing:

- today
- tomorrow
- tonight
- shortly
- over the weekend
- after school
- after the match

#### Agency / readiness

Explanation: The focus is not on assumptions, but on signals that are explicitly present in the text.

Planning, coordination, capability:

- a plan
- preparation
- the ability to carry out the action
- coordination with others
- information about prior arrangements

#### Escalation

Explanation: Verbal conflict alone is not sufficient, but it may reinforce other signals.

Increasing intensity in interaction:

- escalation in tone
- a shift from general frustration to a concrete statement
- a response to provocation that changes the meaning of the statement

### Signals supporting DISCARD

#### Reported speech

Explanation: This is not the author's own declaration.

Quoting or describing others:

- a quote
- a paraphrase
- a news report
- a description of the situation
- a reference to someone else's post

E.g.: "Police said that someone wrote they would come to the office tomorrow."

#### Lack of agency

Explanation: This may be emotionally strong, but it does not provide sufficient grounds for retention.

Hypothetical or general statements:

- a hypothetical possibility
- someone else’s actions
- a general scenario
- emotions without any indication of action

E.g.: "Someone should finally hold them accountable."

#### Humour / irony

Explanation: The model should prefer DISCARD.

Jokes, memes, exaggeration:

- a joke
- ironic, satirical
- meme-style expression
- a quote from a film, song, or game
- a hyperbole with no real-world intent

#### General anger

Explanation: The model should prefer DISCARD.

Emotion without structure. There should not be a:

- specific target
- timeframe
- agency
- indication of action

#### Counterspeech

Explanation: The outcome should be DISCARD, even if the language used is strong.

Condemning or discouraging harm:

- criticizes someone else's threat
- condemns violence
- warns about a risk
- calls for calm

## Decision Rule

Condition: >= 1 strong signal
Outcome: KEEP_FOR_REVIEW

Condition: >= 2 moderate signals
Outcome: KEEP_FOR_REVIEW

Otherwise: DISCARD
Especially when:

- There are not enough grounds to justify KEEP_FOR_REVIEW.
- There is a clear indication that the statement is not a personal declaration of intent.
- The context suggests that the statement is more likely a quote, a report, irony, or an emotional comment.

## Safeguards and Prohibited Reasoning

Category: Protected characteristics
Examples:

- origin
- nationality
- religion
- gender
- sexual orientation
- political views
- or any other protected characteristics
- nor on obvious references to such characteristics

Rule: Must not influence decision.

Category: External assumptions
Examples:

- not assuming who the author is
- not assuming what their intentions are beyond the text
- not assuming whether they have acted in a certain way before
- not assuming what their background is
- not assuming or what group they belong to

Rule: No inference beyond text.

Category: Tone-based judgment
Examples:

- strong language
- profanity
- expression of frustration

Rule: Language style alone is insufficient.

Category: Curiosity bias
Examples:

- intriguing
- controversial
- concerning

Rule: Should not justify retention.

## Bias and Fairness Safeguards

Decisions must be content-based and independent from identity-related factors.

Safeguard: No proxy use
Meaning: Do not rely on names or cultural cues

Safeguard: Invariance test
Meaning: Changing identity must not change the decision

Safeguard: Explanation discipline
Meaning: Justifications must rely on text

Safeguard: Separation principle
Meaning: Distinguish action vs. identity content

## Explainability and Required Explanation Format

The model must explain what triggered the decision and what would change it. If the model considers KEEP_FOR_REVIEW, it must be able to clearly indicate:

- What specific element of the text formed the basis for that decision
- What minimal change in the content or context would have led to DISCARD

This is important, because it reflects the logic of contrastive explanation - not only "why this outcome", but also "why this outcome rather than another."

The model should justify its decisions in a way that is:

- simple
- concrete
- clearly grounded in the text
- free of technical jargon

It should avoid phrasing such as:

- "based on semantic analysis and risk classification"
- "the content shows predictive similarity to high-risk patterns"

Instead, it should use plain and direct explanations, for example:

- "the statement takes the form of a first-person indication of action"
- "a specific place and a near-term timeframe are mentioned"
- "this is a report of someone else’s statement, not the author’s own declaration"
- "the context suggests irony rather than a real intention"

Element: Decisive element
Content: Key part of the text

Element: Mitigating element
Content: What argues against retention

Element: Reasoning
Content: Why the decision is justified

Element: Contrastive change
Content: Minimal change into the opposite outcome
