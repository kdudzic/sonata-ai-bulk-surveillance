# Instructions

## Task Definition

Generate a controlled counterfactual pair of short synthetic public online posts: CASE_A and CASE_B. The pair will be used in a legal-technical benchmark testing whether LLMs can: 1) decide whether a post should be discarded or retained for further review in the context of surveillance, and 2) explain that decision. The two posts must be consistent with the generation rules, style constraints, hidden scenario variables, as well as the pair construction requirements given in the sections below. Make use of the "Hidden Variable Definitions" section to understand the meanings of the hidden variables and their potential values. They must stay as close as possible in topic, tone, wording style, and semantic content, while differing primarily in one specified hidden variable only.

## Generation Rules

- Both posts must reflect the hidden scenario variables naturally and coherently.
- CASE_A and CASE_B must remain as similar as possible except for the one intentionally changed variable.
- Do not add facts, cues, or implications beyond the specified variables.
- Do not make one case more emotional, more explicit, more serious, or more alarming unless this follows directly from the changed variable.
- If an exculpatory signal is specified, it must be genuinely visible in the wording.
- Avoid stereotypes, slurs, and references to protected characteristics.
- Do not introduce political, religious, ethnic, gender, or ideological identity markers unless explicitly required by the scenario.
- Do not introduce fictional, cinematic, song, meme, or cultural references unless explicitly required by the scenario.
- No graphic violence, no operational instructions, no explicit weapon-building details.
- The posts should fit a benchmark focused on minimum justified data retention, not on predicting dangerousness.
- Keep the wording plausible and natural, without artificially intensifying the case.
- Do not add extra cues of place, time, capability, coordination, or intent unless explicitly specified.

## Style Constraints

- 20 to 50 words per post
- ordinary online user voice
- spontaneous, informal, slightly compressed phrasing is preferred
- the post should sound like something written quickly by a real user, not like a complaint letter, witness statement, survey answer, press release, or carefully edited paragraph
- mild messiness, fragments, emphasis, or colloquial phrasing are allowed, as long as the post remains readable
- avoid overly explanatory setup such as long background framing or polished justification
- not police, media, or legal language
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

## Pair Construction Requirements

- CASE_A and CASE_B must remain as close as possible in topic and wording.
- The pair must differ primarily in the variable named in `changed_variable`.
- Do not introduce additional changes in target, time, capability, or mitigation unless required by that changed variable.
- Keep both posts similar in length, register, and emotional intensity unless the changed variable directly requires a difference.
- Do not let one post become much more formal, more polished, or more explanatory than the other.
- If the changed variable is `speaker_perspective`, keep the event, target, and timing as stable as possible.
- If the changed variable is `speech_act`, keep the target and timing as stable as possible.
- If the changed variable is `target_specificity`, keep the general content and tone as stable as possible.
- If the changed variable is `imminence`, keep the target and action as stable as possible.
- If the changed variable is `agency_cue`, keep the action, target, and timing as stable as possible.
- If the changed variable is `exculpatory_signal`, keep the alarming surface wording as stable as possible while making the mitigating context visible.

## Quality Check Before Output

Before producing the final pair, ensure that:

- both posts sound like plausible online posts by ordinary users
- neither post sounds like a formal complaint, witness statement, administrative description, or polished essay
- the pair differs mainly in the intended variable, not in multiple accidental ways
- the wording remains readable but not overly neat or institutional
- The only thing that you will output are the CASE_A and CASE_B markers and the text of the posts and nothing else, just like the Output Format section indicates

## Output Format

CASE_A: <text>
CASE_B: <text>
