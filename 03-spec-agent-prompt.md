# 03. The spec agent prompt

This prompt turns 2 inputs into `spec.json`: the notes from a client kickoff and a sample of the data the build will read. In the lesson it ran on Nordlicht's notes and claims export, both in [sample-data/](sample-data/). The output it produced is [spec.json](spec.json).

## How to run it

Copy `sample-data/` into an empty folder, open Claude Code there, and paste the prompt below. In claude.ai, paste the prompt, then the kickoff notes, then the CSV.

Keep the folder empty apart from your inputs. The agent reads everything it can see, so a copy of this repo's `spec.json` or the deck would hand it the answer.

To use it on your own project, replace the 2 files with your own kickoff notes and a small export of the data your build will touch.

## The prompt

```
You are the spec writer for a forward deployed engineer. You have two inputs:
kickoff-notes.md, raw notes from the client call, and
sample-data/claims_notes.csv, the sample export the build will read.
Output: spec.json for the first slice only, the thing that has to work at
the Friday demo.

Output one JSON object with these keys, in this order:

- slice: one sentence. Who does what, and what they get back.
- boundaries: what the build may touch. region, allowed_hosts (exact
  hostnames), data (the files it may read, by path). If the client said
  anything about where data may live or travel, it becomes this list, not a
  sentence. Anything not on the list is out.
- rules: one entry per client statement the build must obey, each with
  said_by (name and meeting), heard (their words, as close to verbatim as the
  notes allow), rule (one sentence starting "Never" or "Always" that names
  the field or hostname to inspect), and check (the command or test case that
  verifies it, and what a pass looks like).
- response: the fields every answer returns. Include found_in_notes and
  outbound_calls (hostname and region of every call made to produce it).
- out_of_scope: parked and "later" items, each with asked_by, so the client
  sees they were heard.
- done_when: the build runs every check in rules on itself before it reports
  success.

Rules for you:
- Rules come only from what the client said in the notes. The CSV never
  creates a rule.
- Use the CSV to make the spec concrete: its columns name the fields an
  answer can cite, and its claim_ids give the test cases. A check that needs
  a claim that is not in the data must name one that is really absent.
- Every client statement about data, region or compliance becomes a boundary
  and a rule, even if it was said once in passing. Use the client's exact
  place, not a wider one.
- A rule without a check is not finished. Do not output one.
- Only what the inputs support. No best practices, no prose.
```

## What the CSV adds

- **Real test cases.** The sample has 12 notes across 5 claims: 4471, 4472, 4480, 4491 and 4493. A check for "say when you don't know" can name a claim the agent can see is missing, so the test case is a fact and not a guess.
- **Real fields.** `note_date` and `author` come from the CSV header, which is why the spec can promise an answer dated and naming who did what.
- **No new rules.** The notes are plainly German personal data, and a model left to itself will invent a residency rule from them. The prompt keeps every rule tied to what the client said. Stefan said Frankfurt, so the spec says `eu-central-1` and not "somewhere in the EU".

## What to look for in the output

Find Stefan's rule in `rules`. His sentence sits in `heard` with his name beside it, and the same entry carries the rule and the check. [checks/config_check.py](checks/config_check.py) reads the region and allow-list from this same file, so the build and the check answer to one source.
