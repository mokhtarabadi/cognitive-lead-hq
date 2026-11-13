#!/usr/bin/env python3
"""Refresh the zen-proxy allowlists from the live gateway catalogue.

Why this exists:
  The four allowlists in `proxy.py` are hand-verified model sets. They drift
  silently: the gateway adds a model and the proxy answers "not served here",
  or the gateway retires one and the proxy keeps offering a dead id. This
  script reports the drift and, on request, applies the safe half of it.

What it does:
  1. Reads the current sets out of `proxy.py` (no import, no side effects).
  2. Fetches the upstream catalogue per family with a GET, using the
     operator's key. The request is read-only: no inference is ever sent,
     so nothing is spent from the quota.
  3. Classifies every id as keep, gone or add-candidate.
  4. With `--apply` it rewrites only the allowlist literals, atomically.

Safety rules (the reason this is a script and not a habit):
  * A failed probe never removes anything. A timeout, a 429 or a 5xx means
    "unknown", not "gone".
  * A model missing from the catalogue is a CANDIDATE, not a verdict. The
    catalogue is not the served set: `crouton-alpha-free` is served by the
    Go tier and is not listed in its catalogue. A removal is written only
    when the operator confirms that exact id with `--confirm-remove`.
  * An id survives when it merely moved between the chat and the responses
    mount of its family.
  * A mount whose resulting set would be empty is never written.
  * New upstream ids are reported as candidates, never added automatically:
    the catalogue does not say which API style a model speaks, and guessing
    would put a model on a mount that cannot serve it.
  * The script never runs git and never writes a credential.

Attribution: the refuse-to-empty, keep-order and never-remove-on-transient
rules follow the catalogue-sync safety pattern of github.com/12errh/zen-proxy
(MIT, (c) 2026 12errh).

Usage:
  python zen-proxy/refresh_allowlists.py                 # report only
  python zen-proxy/refresh_allowlists.py \
      --confirm-remove /go/resp=some-model --apply       # apply that removal
  python zen-proxy/refresh_allowlists.py --add /go/resp=grok-4.8 --apply
"""

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://opencode.ai"
DEFAULT_KEY_ENV = "ZEN_PROXY_UPSTREAM_KEY"
PROXY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy.py")

# Mount prefix -> (family, upstream base, set name in proxy.py).
# A family is the credential tier: /zen/* is the free tier, /go/* is Go.
MOUNTS = {
    "/zen/chat": ("zen", "/zen/v1", "ZEN_CHAT"),
    "/zen/resp": ("zen", "/zen/v1", "ZEN_RESP"),
    "/go/chat": ("go", "/zen/go/v1", "GO_CHAT"),
    "/go/resp": ("go", "/zen/go/v1", "GO_RESP"),
}

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


class RefreshError(Exception):
    """Raised when the script must refuse to write."""


def read_sets(proxy_path=PROXY_PATH):
    """Parse the four allowlist literals out of proxy.py.

    The file is read as text and the literals are matched with a regex, so
    importing the module is never necessary and no side effect (no server,
    no environment read) can happen here.
    """
    with open(proxy_path, "r", encoding="utf-8") as handle:
        source = handle.read()
    sets = {}
    for _family, _base, name in MOUNTS.values():
        match = re.search(rf"^{name} = \{{(.*?)^\}}$", source, re.DOTALL | re.MULTILINE)
        if not match:
            raise RefreshError(f"could not find the {name} literal in {proxy_path}")
        ids = re.findall(r'"([^"]+)"', match.group(1))
        sets[name] = ids
    return sets


def merge_ids(current, removals, add=()):
    """Compute the new id list for one mount.

    Order is preserved for the ids that survive, additions are appended in
    alphabetical order, and only ids in `removals` are dropped — those are
    the ids the operator confirmed. An empty result is refused: a mount
    with no models serves nothing.
    """
    removal_set = set(removals)
    kept = [model for model in current if model not in removal_set]
    additions = sorted({model for model in add if model and model not in kept})
    merged = kept + additions
    if not merged:
        raise RefreshError("refusing to write an empty allowlist")
    return merged


def classify(current, family_observed, probe_ok):
    """Split the current ids into keep and removal candidates for one mount.

    `family_observed` is the union of the catalogue of every mount of the
    same family. An id that is absent from it is a candidate for removal,
    not a verdict: the catalogue and the served set are not the same thing.
    """
    if not probe_ok:
        return {"keep": list(current), "candidates": []}
    observed = set(family_observed)
    keep = [model for model in current if model in observed]
    candidates = [model for model in current if model not in observed]
    return {"keep": keep, "candidates": candidates}


def fetch_catalogue(base_url, upstream_base, key, timeout=30):
    """Fetch the upstream model catalogue of one family.

    Returns (ids, ok). `ok` is False when the catalogue could not be
    fetched; the ids are then empty and nothing may be removed.
    """
    url = base_url.rstrip("/") + upstream_base + "/models"
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        print(f"  catalogue {url} failed: HTTP {exc.code}", file=sys.stderr)
        return [], False
    except urllib.error.URLError as exc:
        print(f"  catalogue {url} failed: {exc.reason}", file=sys.stderr)
        return [], False
    except (ValueError, OSError) as exc:
        print(f"  catalogue {url} failed: {exc}", file=sys.stderr)
        return [], False
    ids = []
    for entry in payload.get("data", []) if isinstance(payload, dict) else []:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            ids.append(entry["id"])
    if not ids:
        # An empty catalogue is not an authoritative catalogue: the gateway
        # answers 200 with an error envelope or an empty list when the tier
        # is blocked. Treating that as "everything is gone" would empty an
        # allowlist on a quota error.
        print(
            f"  catalogue {url} returned no models: treated as unknown", file=sys.stderr
        )
        return [], False
    return ids, True


def render_literal(name, ids):
    """Render an allowlist literal in the same shape proxy.py uses."""
    lines = [f"{name} = {{"]
    for model in ids:
        lines.append(f'    "{model}",')
    lines.append("}")
    return "\n".join(lines)


def rewrite_sets(proxy_path, new_sets):
    """Rewrite the allowlist literals in proxy.py, atomically.

    Only the four literals are touched. The file is written to a temporary
    file in the same directory and moved into place, so a crash cannot leave
    a half-written module behind.
    """
    with open(proxy_path, "r", encoding="utf-8") as handle:
        source = handle.read()
    original = source
    for name, ids in new_sets.items():
        pattern = re.compile(rf"^{name} = \{{.*?^\}}$", re.DOTALL | re.MULTILINE)
        if not pattern.search(source):
            raise RefreshError(f"could not find the {name} literal in {proxy_path}")
        literal = render_literal(name, ids)
        source = pattern.sub(lambda _m, lit=literal: lit, source, count=1)
    if source == original:
        return False
    directory = os.path.dirname(os.path.abspath(proxy_path))
    # The temporary file is moved into place, so it is closed by hand.
    handle = tempfile.NamedTemporaryFile(  # noqa: SIM115
        "w",
        encoding="utf-8",
        dir=directory,
        prefix=".refresh_allowlists_",
        delete=False,
    )
    try:
        with handle:
            handle.write(source)
        os.chmod(handle.name, os.stat(proxy_path).st_mode & 0o777)
        os.replace(handle.name, proxy_path)
    except OSError:
        try:
            os.unlink(handle.name)
        except OSError:
            pass
        raise
    return True


def parse_additions(values):
    """Parse `--add /mount=id1,id2` arguments into {mount: [ids]}."""
    additions = {}
    for value in values or []:
        if "=" not in value:
            raise RefreshError(f"--add expects /mount=id[,id], got {value!r}")
        mount, ids = value.split("=", 1)
        mount = mount.strip()
        if mount not in MOUNTS:
            raise RefreshError(f"unknown mount {mount!r} in --add")
        additions[mount] = [item.strip() for item in ids.split(",") if item.strip()]
    return additions


def mount_set_name(mount):
    """The proxy.py set name behind a mount prefix."""
    return MOUNTS[mount][2]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--key-env",
        default=DEFAULT_KEY_ENV,
        help="environment variable holding the upstream key (default: %(default)s)",
    )
    parser.add_argument("--proxy", default=PROXY_PATH, help="path to proxy.py")
    parser.add_argument(
        "--add",
        action="append",
        metavar="/mount=id[,id]",
        help="add a verified model id to a mount (repeatable)",
    )
    parser.add_argument(
        "--confirm-remove",
        action="append",
        metavar="/mount=id[,id]",
        help="remove these ids from a mount, confirmed by the operator (repeatable)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write the confirmed removals and additions into proxy.py",
    )
    args = parser.parse_args(argv)

    key = os.environ.get(args.key_env, "").strip()
    if not key:
        print(
            f"zen-proxy: no key in ${args.key_env}; export the upstream key first.",
            file=sys.stderr,
        )
        return 2

    try:
        sets = read_sets(args.proxy)
        additions = parse_additions(args.add)
        confirmations = parse_additions(args.confirm_remove)
    except (RefreshError, OSError) as exc:
        print(f"zen-proxy: {exc}", file=sys.stderr)
        return 2

    families = {}
    for family in ("zen", "go"):
        bases = {base for fam, base, _name in MOUNTS.values() if fam == family}
        base = min(bases)
        ids, ok = fetch_catalogue(args.base_url, base, key)
        families[family] = {"ids": ids, "ok": ok, "base": base}
        state = "ok" if ok else "FAILED (no removals from this family)"
        print(f"family {family}: {len(ids)} upstream models, probe {state}")

    new_sets = {}
    removals = {}
    for mount, (family, _base, name) in MOUNTS.items():
        current = sets[name]
        family_ids = families[family]["ids"]
        probe_ok = families[family]["ok"]
        verdict = classify(current, family_ids, probe_ok)
        candidates = verdict["candidates"]
        # Only the ids the operator confirmed are removed. A catalogue
        # absence is a candidate, never a verdict: the catalogue and the
        # served set differ (crouton-alpha-free is served by Go and is not
        # listed in its catalogue).
        confirmed = [
            model for model in candidates if model in confirmations.get(mount, [])
        ]
        removals[name] = confirmed
        add = additions.get(mount, [])
        if candidates:
            print(
                f"{mount}: removal candidates (confirm with --confirm-remove): "
                f"{', '.join(candidates)}"
            )
        if confirmed:
            print(f"{mount}: removing {', '.join(confirmed)}")
        if add:
            print(f"{mount}: adding {', '.join(sorted(add))}")
        try:
            new_sets[name] = merge_ids(current, confirmed, add)
        except RefreshError as exc:
            # One mount that would end up empty must not block the report of
            # the others, and it must never be written.
            print(f"{mount}: keeping the current set ({exc})", file=sys.stderr)
            new_sets[name] = list(current)
    # Candidates are reported, never written: the catalogue does not say
    # which API style a model speaks.
    known = {model for ids in sets.values() for model in ids}
    for family, info in families.items():
        if not info["ok"]:
            continue
        candidates = sorted(set(info["ids"]) - known)
        if candidates:
            print(
                f"family {family}: unclassified upstream models (verify the API "
                f"style, then add with --add): {', '.join(candidates)}"
            )

    if not args.apply:
        print("report only; pass --apply to write the confirmed removals")
        return 0

    try:
        changed = rewrite_sets(args.proxy, new_sets)
    except (RefreshError, OSError) as exc:
        print(f"zen-proxy: {exc}", file=sys.stderr)
        return 2
    print(f"{args.proxy}: {'updated' if changed else 'unchanged'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
