# Spec Engineering for FDEs: Blueprint for Zero-Shot Delivery

The kit from the lightning lesson GK and Hamza Farooq ran on 30 Oct 2026. Use it to rebuild the demo on your own kickoff notes.

## The demo in 1 paragraph

At the Nordlicht kickoff, Stefan from IT security said "claims data stays in Frankfurt" once, late in the call. We gave the same task to 2 builds. The raw-prompt build read its region from the environment, so it guessed Frankfurt on our machine, and one line of shell (`export AWS_REGION=us-east-1`) sent it to Virginia. The spec build wrote `REGION = "eu-central-1"` with Stefan's name above it, because `spec.json` says so, and the same shell line could not move it. The check below tells the 2 builds apart before a single call leaves the laptop.

## What is in the repo

| File | What it is |
|---|---|
| [03-spec-agent-prompt.md](03-spec-agent-prompt.md) | Turns kickoff notes into `spec.json` |
| [spec.json](spec.json) | The Nordlicht spec, every rule with its check |
| [checks/config_check.py](checks/config_check.py) | Fails on any region or host that is not on the allow-list, and on a region the environment can override |
| [sample-data/claims_notes.csv](sample-data/claims_notes.csv) | The sample claims notes from the demo |
| [sample-data/kickoff-notes.md](sample-data/kickoff-notes.md) | The kickoff notes the spec agent reads |
| [index.html](index.html) | The lesson deck. Download it and open it in a browser. |

Nordlicht, its people and its claims are fictional.

## Rebuild it on your own notes

1. Put your kickoff notes and a small sample of the client's data in an empty folder.
2. Run the prompt in [03-spec-agent-prompt.md](03-spec-agent-prompt.md) to get `spec.json`. Check that every client statement about data, region or compliance became a rule with a check.
3. Ask your coding agent to build from `spec.json`, and to write `config.py` (every setting the service starts from) before any other code.
4. Run the check on that config. It needs Python 3 and nothing else.

```
python checks/config_check.py path/to/config.py path/to/spec.json
```

A config that pins the spec's region passes:

```
PASS  config.py: region eu-central-1, 1 host(s), all on allow-list
```

A config that reads the region from the environment fails, even when its default is correct:

```
FAIL  config.py: region is only a default. AWS_REGION in the environment overrides it.
  eu-central-1 today, wherever the shell says tomorrow
Client data would leave eu-central-1 on any machine with AWS_REGION set.
```

The second spec argument is optional. Without it, the check reads [spec.json](spec.json) from the root of this repo.

## Go deeper

The [Product Builder Certification](https://maven.com/level-up-with-ai/product-builder-certification-spec-driven-ai-agents?promoCode=LAUNCH) covers the spec kit, the checks and the handover. Code LAUNCH.

Hamza Farooq runs FDE Builder Mode on Maven. GK writes at [aibarraiser.substack.com](https://aibarraiser.substack.com) and runs [flywheelbygk.com](https://flywheelbygk.com).
