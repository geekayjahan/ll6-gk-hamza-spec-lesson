#!/usr/bin/env python3
"""Checks a generated config.py against the boundaries in spec.json.

Reads the region and allow-list from spec.json and inspects config.py before
any code runs. Comments are ignored. A region read from AWS_REGION fails, even
with the right default, because the environment decides it. A host passes if
it is on the allow-list or carries the spec's region in its name. A region
read from spec.json counts as the spec's region. A Bedrock inference profile
prefixed eu./us./apac. fails, because it routes to other regions and the spec
pins one.

Usage: python checks/config_check.py path/to/config.py [spec.json]
"""
import json, re, sys
from pathlib import Path

DEFAULT_SPEC = Path(__file__).resolve().parent.parent / "spec.json"
REGION_RE = re.compile(r"\b([a-z]{2}-[a-z]+-\d)\b")
HOST_RE = re.compile(r"\b([a-z0-9.-]+\.amazonaws\.com)\b")
PROFILE_RE = re.compile(r"[\"']((?:eu|us|apac)\.[a-z0-9.-]+)[\"']")
SPEC_READ_RE = re.compile(r"spec\.json")
ENV_REGION_RE = re.compile(r"[\"']AWS_(?:DEFAULT_)?REGION[\"']")

def strip_comments(text):
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        out.append(line.split("#", 1)[0] if "#" in line and not re.search(r"[\"'][^\"']*#", line) else line)
    return "\n".join(out)

def main(cfg, spec_path):
    b = json.loads(Path(spec_path).read_text(encoding="utf-8"))["boundaries"]
    m = REGION_RE.search(b["region"])  # spec may say "eu-central-1 (Frankfurt)"
    want, allowed = (m.group(1) if m else b["region"]), list(b["allowed_hosts"])
    text = strip_comments(Path(cfg).read_text(encoding="utf-8"))
    regions = sorted(set(REGION_RE.findall(text)))
    hosts = sorted(set(HOST_RE.findall(text)))
    profiles = sorted(set(PROFILE_RE.findall(text)))
    reads_spec = bool(SPEC_READ_RE.search(text)) and "region" in text
    bad_regions = [r for r in regions if r != want]
    def host_ok(h):
        if h in allowed:
            return True
        m = REGION_RE.search(h)
        return bool(m) and m.group(1) == want
    bad_hosts = [h for h in hosts if not host_ok(h)]

    if not regions and not reads_spec:
        print(f"FAIL  {cfg}: no region pinned. Whatever the environment says on the day decides where the data goes.")
        return 1
    if ENV_REGION_RE.search(text):
        print(f"FAIL  {cfg}: region is only a default. AWS_REGION in the environment overrides it.")
        print(f"  {want} today, wherever the shell says tomorrow")
        print(f"Client data would leave {want} on any machine with AWS_REGION set.")
        return 1
    if bad_regions or bad_hosts:
        print(f"FAIL  {cfg} is outside {want}")
        for x in bad_regions + bad_hosts:
            print(f"  {x}")
        print(f"Client data would leave {want}.")
        return 1
    if profiles:
        print(f"FAIL  {cfg}: model routes across regions, not only {want}")
        for x in profiles:
            print(f"  {x}  (cross-region inference profile)")
        print(f"Client data would leave {want}.")
        return 1
    src = f"region {want}" if want in regions else f"region read from spec.json ({want})"
    print(f"PASS  {cfg}: {src}, {len(hosts)} host(s), all on allow-list")
    return 0

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else DEFAULT_SPEC))
