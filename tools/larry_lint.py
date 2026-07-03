#!/usr/bin/env python3
"""larry_lint — reference semantic linter for LARRY v0.1.1.

Validates what the parser cannot: the discourse registry (§4.2, §6),
buoy lifecycle (§5.7), role-shift binding (§5.4), span keywords (§10.4-.5),
and modifier-chain rules (§5.1). Emits (severity, code, message) findings.

Usage:  python3 larry_lint.py file.lry   |   import and call lint(src)
"""
import sys
from larry_parser_prototype import parse

ASL_SPANS = {"ynq", "whq", "rhq", "neg", "topic", "cond",
             "mm", "cha", "oo", "th", "pah", "pow", "cs", "puff", "ps",
             "intense"}
RESERVED = {"1p", "2p", "3p-any"}
NM_CHANNELS = {"gaze", "head", "torso", "affect"}


def edit1(a, b):
    """True if edit distance between a and b is exactly 1 (typo guard, §6)."""
    if a == b:
        return False
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        if sum(x != y for x, y in zip(a, b)) == 1:
            return True
        # adjacent transposition (Damerau): the classic typo
        for i in range(len(a) - 1):
            if a[:i] + a[i+1] + a[i] + a[i+2:] == b:
                return True
        return False
    if len(a) > len(b):
        a, b = b, a
    for i in range(len(b)):
        if a == b[:i] + b[i+1:]:
            return True
    return False


class Entity:
    def __init__(self, name, cls=None, zone=None):
        self.name, self.cls = name, cls
        self.zone = zone                 # zone name, ("finger", n), or None
        self.established = zone is not None
        self.referenced_since_est = False
        self.ever_referenced = False


class Linter:
    def __init__(self):
        self.reg = {}                    # name -> Entity
        self.live_buoy = None            # (buoyname, {finger->entity})
        self.findings = []               # (sev, code, msg)

    def err(self, code, msg):  self.findings.append(("error", code, msg))
    def warn(self, code, msg): self.findings.append(("warn", code, msg))

    # ---- registry ----
    def declare(self, name, cls=None, zone=None):
        for other in self.reg:
            if edit1(name, other):
                self.warn("E-NEARDUP",
                          f"entity '{name}' is edit-distance 1 from '{other}'"
                          " — possible auto-declaration typo (§6)")
        self.reg.setdefault(name, Entity(name, cls, zone))
        if cls:
            self.reg[name].cls = cls

    def establish(self, name, cls, zone):
        if name not in self.reg:
            self.declare(name, cls)
        ent = self.reg[name]
        # zone eviction rule (§4.2)
        if not isinstance(zone, tuple):
            for other in self.reg.values():
                if other is not ent and other.established and other.zone == zone:
                    if other.referenced_since_est:
                        self.err("Z-EVICT",
                                 f"'{name}' establishes at {zone}, evicting"
                                 f" referenced entity '{other.name}' —"
                                 " rebind explicitly instead (§4.2)")
                    other.established = False
        ent.zone = zone
        ent.established = True
        ent.referenced_since_est = False

    def reference(self, name, where):
        if name in RESERVED:
            return
        ent = self.reg.get(name)
        if ent is None or not ent.established:
            self.err("R-UNEST",
                     f"reference to '{name}' in {where} before establishment"
                     " (§4.2/§6)")
        else:
            ent.referenced_since_est = True
            ent.ever_referenced = True

    def refs_in_args(self, args):
        """Pull candidate entity refs from opaque modifier args (dir, etc.)."""
        out = []
        for a in args or []:
            if a in ("->", ",", "each") or not a[:1].isalpha() and a not in RESERVED:
                continue
            if a in RESERVED or (a.islower() and a.isidentifier()
                                 or "-" in a and a.islower()):
                # zones look like refs; exclude the grid vocabulary
                if not any(a.startswith(p) for p in
                           ("ipsi", "contra", "center", "neutral")):
                    out.append(a)
        return out

    # ---- walkers ----
    def walk(self, items, in_rs=None):
        for it in items:
            kind = it[0]
            if kind == "entities":
                for name, cls, zone in it[1]:
                    self.declare(name, cls, zone)
            elif kind == "token":
                self.token(it)
            elif kind == "span":
                _, key, body = it
                if key not in ASL_SPANS:
                    self.err("S-KEY", f"unknown span keyword [{key}] for"
                                      " asl.v1 (§10.4–10.5)")
                self.walk(body, in_rs)
            elif kind == "rs":
                _, ref, _affect, body = it
                self.reference(ref, "rs()")
                if in_rs is not None:
                    self.warn("RS-NEST", "role shift nested at depth 2 —"
                                         " legal but rare (§5.4)")
                self.walk(body, in_rs=ref)
            elif kind == "par":
                self.par(it)
            elif kind == "buoy":
                self.buoy(it)
            elif kind == "release":
                self.release(it)
            # boundaries, pragmas, defs: no registry effect

    def token(self, it):
        _, base, _stress, infl, sufx = it
        if base[0] in ("ix", "poss", "hon"):
            refs = base[1] if isinstance(base[1], list) else [base[1]]
            refs = [r for part in refs for r in part.split("+")]
            if len(refs) > 3:
                self.err("R-COMPOUND", "compound reference exceeds 3 atoms (§4.2)")
            for r in refs:
                self.reference(r, base[0] + "()")
        keys = [m[0] for m in infl] + [s[0] for s in sufx]
        for k in set(keys):
            if keys.count(k) > 1 and k != "est":
                self.err("M-DUP", f"modifier '{k}' repeated in one chain (§5.1)")
        for m in infl:
            if m[0] == "est":
                _, ent, cls, zone = m
                if isinstance(zone, tuple):     # finger(n) landmark
                    self.finger_bind(ent, zone)
                else:
                    self.establish(ent, cls, zone)
            elif m[0] == "dir":
                for r in self.refs_in_args(m[1]):
                    self.reference(r, ":dir()")

    def par(self, it):
        _, _dur, stmts = it
        for st in stmts:
            _, chan, _off, val, _sufx = st
            if chan == "ndh" and self.live_buoy:
                self.err("B-NDH", f"par addresses 'ndh' while buoy"
                                  f" '{self.live_buoy[0]}' is live (§5.7)")
            if isinstance(val, tuple) and val and val[0] == "token":
                self.token(val)

    def finger_bind(self, ent, zone):
        if not self.live_buoy:
            self.err("B-NOBUOY", f"'{ent}' bound to {zone[0]}({','.join(zone[1] or [])})"
                                 " with no live buoy (§5.7)")
            return
        self.declare(ent)
        e = self.reg[ent]
        e.zone, e.established, e.referenced_since_est = zone, True, False
        self.live_buoy[1][tuple(zone[1] or [])] = ent

    def buoy(self, it):
        _, name, _signid, binds = it
        if self.live_buoy:
            self.err("B-DOUBLE", f"buoy '{name}' raised while"
                                 f" '{self.live_buoy[0]}' is live —"
                                 " one at a time in v0.1.1 (§5.7)")
        self.live_buoy = (name, {})
        for ent, digit in binds:
            self.finger_bind(ent, ("finger", [digit]))

    def release(self, it):
        _, name = it
        if not self.live_buoy or self.live_buoy[0] != name:
            self.err("B-RELEASE", f"release({name}) but that buoy is not live (§5.7)")
        else:
            for ent in self.live_buoy[1].values():
                self.reg[ent].established = False
            self.live_buoy = None

    def finish(self):
        if self.live_buoy:
            self.warn("B-UNRELEASED",
                      f"buoy '{self.live_buoy[0]}' never released —"
                      " auto-released at stream end (§5.7)")
        for e in self.reg.values():
            if not e.ever_referenced:
                self.warn("E-UNUSED", f"entity '{e.name}' established but never"
                                      " referenced — possible typo (§6)")


def lint(src):
    ast = parse(src)
    L = Linter()
    L.walk(ast)
    L.finish()
    return L.findings


# ------------------------- self-test -------------------------

CASES = [
 # name, source, expected codes (subset match)
 ("clean give-chain", '''
   YESTERDAY | [topic]{ poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
   BOOK !est(book @ center-mid-near) GIVE :dir(mother -> 1p) ||
   ix(book) GOOD
 ''', []),
 ("ref before est", 'ix(mother) MOTHER !est(mother @ ipsi-mid-near)',
  ["R-UNEST", "E-UNUSED"]),
 ("evict referenced entity", '''
   MOTHER !est(mother @ ipsi-mid-near) ix(mother) |
   STORE !est(store @ ipsi-mid-near)
 ''', ["Z-EVICT", "E-UNUSED"]),
 ("evict unreferenced entity ok", '''
   MOTHER !est(mother @ ipsi-mid-near) |
   STORE !est(store @ ipsi-mid-near) ix(store)
 ''', ["E-UNUSED"]),          # mother evicted silently, but never referenced -> warn
 ("near-duplicate typo", '''
   MOTHER !est(mother @ ipsi-mid-near) ix(mother) |
   MOTHER !est(mothre @ contra-mid-near) ix(mothre)
 ''', ["E-NEARDUP"]),
 ("unknown span key", '[zzz]{ HELLO }', ["S-KEY"]),
 ("rs unbound referent", 'rs(daughter) { HELLO }', ["R-UNEST"]),
 ("duplicate modifier", 'WAIT:asp(cont):asp(intense)', ["M-DUP"]),
 ("buoy lifecycle clean", '''
   buoy plans : LIST-3 { !est(coffee @ finger(1)) !est(tea @ finger(2)) }
   ix(tea) GOOD | ix(coffee) [neg]{ WANT } || release(plans)
 ''', []),
 ("double buoy", '''
   buoy alpha : LIST-3 { !est(coffee @ finger(1)) } ix(coffee)
   buoy beta : LIST-2 { !est(soda @ finger(1)) } ix(soda)
 ''', ["B-DOUBLE", "B-UNRELEASED"]),
 ("unreleased buoy", 'buoy a : LIST-3 { !est(x @ finger(1)) } ix(x)',
  ["B-UNRELEASED"]),
 ("ndh during buoy", '''
   buoy a : LIST-3 { !est(x @ finger(1)) } ix(x)
   par { ndh: HELLO } release(a)
 ''', ["B-NDH"]),
 ("release unknown buoy", 'HELLO release(ghost)', ["B-RELEASE"]),
 ("dir to unestablished", 'GIVE :dir(1p -> mother)', ["R-UNEST"]),
 ("compound ref ok", '''
   MOTHER !est(mother @ ipsi-mid-near) SISTER !est(sister @ contra-mid-near)
   ix(mother+sister) GOOD
 ''', []),
]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        findings = lint(open(sys.argv[1]).read())
        for sev, code, msg in findings:
            print(f"{sev:5}  {code:12}  {msg}")
        sys.exit(1 if any(s == "error" for s, _, _ in findings) else 0)

    passed = 0
    for name, src, expect in CASES:
        try:
            got = [c for _, c, _ in lint(src)]
        except SyntaxError as e:
            print(f"  PARSE-FAIL {name}: {e}"); continue
        missing = [c for c in expect if c not in got]
        spurious = [c for c in got if c not in expect]
        if not missing and not spurious:
            passed += 1
            print(f"  OK    {name}  {got or '(clean)'}")
        else:
            print(f"  FAIL  {name}: expected {expect}, got {got}")
    print(f"\n{passed}/{len(CASES)} lint cases passed")
    sys.exit(0 if passed == len(CASES) else 1)
