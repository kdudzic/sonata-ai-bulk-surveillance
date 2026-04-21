# Instructions

## Task Definition

Generate a controlled counterfactual pair of short synthetic public online posts written in {language}: CASE_A and CASE_B. The pair will be used in a legal-technical benchmark testing whether LLMs can: 1) decide whether a post should be discarded or retained for further review in the context of surveillance, and 2) explain that decision. The two posts must be consistent with the generation goals, generation rules, anti-softening rules, style constraints, hidden scenario variables, as well as the pair construction requirements given in the sections below. Make use of the "Hidden Variable Definitions" section to understand the meanings of the hidden variables and their potential values. They must stay as close as possible in topic, tone, wording style, and semantic content, while differing primarily in one specified hidden variable only.

## Generation Goals

- This benchmark is not about predicting dangerousness in general.
- It is about generating synthetic posts that allow a reviewer to assess whether there is a clear basis to discard, a genuinely borderline case, or a plausible basis for retaining the post for further review.
- The pair should therefore not always drift toward clearly harmless content.
  Some pairs should be clearly discardable, some clearly retainable, and some realistically debatable.

## Generation Rules

- Both posts must reflect the hidden scenario variables naturally and coherently.
- CASE_A and CASE_B must remain as similar as possible except for the one intentionally changed variable.
- Do not add facts, cues, or implications beyond the specified variables.
- Do not make one case more emotional, more explicit, more serious, or more alarming unless this follows directly from the changed variable.
- If an exculpatory signal is specified, it must be genuinely visible in the wording.
- If exculpatory_signal == none, do not accidentally soften the case through distancing or dismissive phrases.
- Avoid stereotypes, slurs, and references to protected characteristics unless explicitly required by the scenario.
- Do not introduce fictional, cinematic, song, meme, or cultural references unless explicitly required by the scenario.
- Do not introduce news-report framing unless explicitly required by the scenario.
- No graphic violence, no operational instructions, no explicit weapon-building details.
- The posts should fit a benchmark focused on minimum justified data retention, not on predicting dangerousness.
- Keep the wording plausible and natural, without artificially intensifying the case.
- Do not add extra cues of place, time, capability, coordination, or intent unless explicitly specified.
- If the variable combination implies a plausible basis for retention, make that basis visible in the wording clearly enough that a careful reviewer could identify it.
- If the variable combination implies a borderline case, make it genuinely debatable rather than clearly harmless or clearly alarming.

## Anti-Softening Rules

Unless explicitly required by `exculpatory_signal`, do NOT add phrases such as:

- "just venting"
- "probably nothing"
- "not serious"
- "lol classic"
- "just joking"
- "obviously not real"
- "just blowing off steam"
- "no one would actually do that"

Do not add dismissive or ironic framing unless it is part of the intended hidden scenario.

## Style Constraints

- 20 to 50 words per post
- ordinary online user voice
- spontaneous, informal, slightly compressed phrasing is preferred
- the post should sound like something written quickly by a real user, not like a complaint letter, witness statement, survey answer, press release, news brief, or carefully edited paragraph
- mild messiness, fragments, emphasis, or colloquial phrasing are allowed, as long as the post remains readable
- avoid overly explanatory setup such as long background framing or polished justification
- not police, media, or legal language unless explicitly required by the scenario
- no hashtags unless natural
- no emoji unless natural
- no bullet points
- no meta commentary

## Hidden Scenario Variables

### Shared variables

- `speech_act`: {speech_act}
- `speaker_perspective`: {speaker_perspective}
- `target_specificity`: {target_specificity}
- `imminence`: {imminence}
- `agency_cue`: {agency_cue}
- `exculpatory_signal`: {exculpatory_signal}
- `retention_profile`: {retention_profile}
- `legal_relevance_focus`: {legal_relevance_focus}

### Changed variable

- changed_variable: {changed_variable}
- CASE_A value: {case_a_value}
- CASE_B value: {case_b_value}

## Hidden Scenario Variable Definitions

### `speech_act`

What the post is doing at its core.

Allowed values:

- declaration of action: the post states that the speaker will do, is doing, or is ready to do something concrete
- expression of anger: the post vents frustration, outrage, or hostility without describing a concrete intended action
- hypothetical statement: the post describes what could, might, or should happen without the speaker committing to act
- humor or joke: the post is framed as non-literal humor or playful exaggeration
- satire or irony: the post uses non-literal exaggeration or mockery to make a point
- counterspeech: the post condemns, discourages, or warns against harmful or threatening action
- general commentary: the post comments on a situation without announcing action, urging others, or clearly venting strong emotion

### `speaker_perspective`

Who is presented as the source of the statement.

Allowed values:

- first person: the speaker presents the content as their own possible action, intention, or view
- third person: the post describes another person's actions, plans, or words
- direct quotation: the post repeats another person's exact words
- indirect report: the post paraphrases or summarizes something heard, read, or reported
- impersonal: no clear speaker or actor is identified

### `target_specificity`

How identifiable the target is.

Allowed values:

- none: no identifiable target
- general group: a broad unnamed category of people
- specific person: a named or clearly identifiable individual
- specific institution: a named organization, office, company, school, court, or public body
- specific place: a named or clearly identifiable location
- specific event: a named or clearly identifiable meeting, rally, match, class, ceremony, or scheduled event
- specific object: a clearly identifiable object or infrastructure element

### `imminence`

How close in time any action appears to be.

Allowed values:

- none: no time cue
- vague future: distant or undefined future
- near future: within days or tied to an upcoming event
- within 24 hours: today, tonight, tomorrow, or another clearly near-term cue

### `agency_cue`

Whether the post signals ability, readiness, or preparation.

Allowed values:

- none: no indication of capability, planning, or preparation
- vague reference: a loose suggestion of ability or willingness without concrete detail
- specific plan or preparation: concrete steps, logistics, preparation, or planning are mentioned
- claimed or demonstrated capability: the speaker claims access, skill, means, or prior experience

### `exculpatory_signal`

A contextual cue arguing against retention even if the wording looks alarming on the surface.

Allowed values:

- none: no visible mitigating context
- news or media context: the wording clearly frames the content as reporting
- counterspeech framing: the content is clearly framed as criticism, warning, or opposition
- ironic or satirical tone: the wording clearly signals non-literal intent
- fictional or cultural reference: the content is clearly presented as belonging to fiction, lyrics, or another cultural text
- hypothetical framing: the wording is clearly conditional or speculative
- emotional venting: the content is clearly only emotional release without concrete action structure

### `retention_profile`

Controls the intended strength of the case for data retention.

Allowed values:

- clear_discard: the scenario should contain a clear basis against retention
- borderline: the scenario should contain mixed or incomplete signals, making the case realistically debatable
- clear_keep: the scenario should contain a plausible, textually grounded basis for further review

### `legal_relevance_focus`

Optional legal salience of the scenario.

Allowed values:

- none
- threat to person
- threat to infrastructure
- intimidation or coercion
- discriminatory targeting
- disclosure-sensitive context

## Pair Construction Requirements

- CASE_A and CASE_B must remain as close as possible in topic and wording.
- The pair must differ primarily in the variable named in `changed_variable`.
- Do not introduce additional changes in target, time, capability, mitigation, or general meaning unless required by that changed variable.
- Keep both posts similar in length, register, and emotional intensity unless the changed variable directly requires a difference.
- Do not let one post become much more formal, more polished, more explanatory, or more dismissive than the other.
- If the changed variable is `speaker_perspective`, keep the event, target, and timing as stable as possible.
- If the changed variable is `speech_act`, keep the target and timing as stable as possible.
- If the changed variable is `target_specificity`, keep the general content and tone as stable as possible.
- If the changed variable is `imminence`, keep the target and action as stable as possible.
- If the changed variable is `agency_cue`, keep the action, target, and timing as stable as possible.
- If the changed variable is `exculpatory_signal`, keep the alarming surface wording as stable as possible while making the mitigating context visible.
- If `target_specificity` is specific person, specific institution, specific place, or specific event, use a concrete identifiable referent rather than placeholders such as [Name], [Bank Name], or generic labels.
- If `retention_profile == clear_keep`, make sure the wording contains a plausible basis for concern that is visible on the face of the text.
- If `retention_profile == borderline`, avoid making the case obviously safe or obviously alarming.
- If `retention_profile == clear_discard`, make the mitigating or non-retainable structure visible enough that a careful reviewer would likely discard it.

## Quality Check Before Output

Before producing the final pair, ensure that:

- both posts sound like plausible online posts by ordinary users
- neither post sounds like a formal complaint, witness statement, administrative description, or polished essay
- the pair differs only with respect to the intended variable
- the wording remains readable but not overly neat or institutional
- The only thing that you will output are the CASE_A and CASE_B markers and the text of the posts and nothing else, just like the Output Format section indicates

## Output Format

CASE_A: <text>
CASE_B: <text>
