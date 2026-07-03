#!/usr/bin/env python3
"""LARRY v0.1 prototype tokenizer + recursive-descent parser.

Purpose: stress-test the abridged EBNF in larry-spec-v0.1.md §13 by parsing
every code example in the spec. Not a reference implementation — a probe.
Every place the EBNF alone was insufficient is marked with  # DISAMBIG.
"""
import re, sys

# ---------------- Tokenizer ----------------

TOKEN_RE = re.compile(r"""
    (?P<ws>\s+)
  | (?P<comment>\#[^\n]*)
  | (?P<pragma>%%?[a-z][a-z0-9_-]*)
  | (?P<string>"[^"]*")
  | (?P<arrow>->)
  | (?P<dbar>\|\|)
  | (?P<ref>[123]p(-any)?\b)                 # DISAMBIG: digit-initial refs (1p, 2p,
                                             # 3p-any) collide with the number rule;
                                             # the spec's lexical rules must call
                                             # this out explicitly.
  | (?P<num>\d+(\.\d+)?(b|deg|sps)?)
  | (?P<ident>[A-Za-z][A-Za-z0-9_.+-]*)      # signs, keys, zones, channels
  | (?P<sym>[{}()\[\]:~!@,>|+])
""", re.VERBOSE)

def tokenize(src):
    toks, i = [], 0
    while i < len(src):
        m = TOKEN_RE.match(src, i)
        if not m:
            raise SyntaxError(f"lex error at {src[i:i+20]!r}")
        i = m.end()
        kind = m.lastgroup
        if kind in ("ws", "comment"):
            continue
        toks.append((kind, m.group()))
    toks.append(("eof", ""))
    return toks

# ---------------- Parser ----------------

class P:
    def __init__(self, toks):
        self.toks, self.i = toks, 0
    def peek(self, k=0):
        return self.toks[min(self.i + k, len(self.toks) - 1)]
    def next(self):
        t = self.toks[self.i]; self.i += 1; return t
    def expect(self, val):
        t = self.next()
        if t[1] != val:
            raise SyntaxError(f"expected {val!r}, got {t[1]!r} (tok {self.i})")
        return t
    def at(self, val, k=0):
        return self.peek(k)[1] == val

    # document = { pragma } , [entities] , { item }
    def document(self):
        out = []
        while self.peek()[0] == "pragma":
            out.append(self.pragma())
        if self.at("@") and self.at("entities", 1):
            out.append(self.entities())
        while not self.at(""):
            out.append(self.item())
        return out

    def pragma(self):
        name = self.next()[1]
        args = []
        # DISAMBIG: pragmas are line-oriented in spirit but the grammar says
        # whitespace is insignificant. We consume args until next pragma/'@'/item
        # ... which is undecidable for '%dict core, medical.v2' followed by a
        # lowercase item. Works here only because no lowercase bare items exist
        # at top level. SPEC BUG: pragmas need explicit termination (newline).
        if name == "%%retract":
            self.expect("("); args.append(self.next()[1]); self.expect(")")
            return ("retract", args)
        while self.peek()[0] in ("num", "ident") or self.at(","):
            t = self.next()
            if t[1] != ",": args.append(t[1])
            if self.at("(") :  # handed(right)
                self.expect("("); args.append(self.next()[1]); self.expect(")")
        return ("pragma", name, args)

    def entities(self):
        self.expect("@"); self.expect("entities"); self.expect("{")
        ents = []
        while not self.at("}"):
            name = self.next()[1]
            cls = zone = None
            if self.at(":"):
                self.next(); cls = self.next()[1]
            if self.at("@"):
                self.next(); zone = self.next()[1]
            if self.at(","): self.next()
            ents.append((name, cls, zone))
        self.expect("}")
        return ("entities", ents)

    def item(self):
        t = self.peek()
        if t[1] == "[":
            return self.span()
        if t[1] == "par":
            return self.parblock()
        if t[1] == "rs":
            return self.roleshift()
        if t[1] == "def":
            return self.definition()
        if t[1] == "buoy":                      # v0.1.1 first-class buoys
            return self.buoy()
        if t[1] == "release":
            self.next(); self.expect("(")
            n = self.next()[1]; self.expect(")")
            return ("release", n)
        if t[1] in ("|",):
            self.next(); return ("minor-boundary",)
        if t[0] == "dbar":
            self.next(); return ("major-boundary",)
        return self.token()

    def token(self):
        stress = False
        if self.at("!"):
            # DISAMBIG: '!' is both stress prefix and start of '!est('.
            # Rule: '!' + 'est' + '(' => inflection (only legal after a sign,
            # so a leading bare '!est(' is an error we let surface later).
            self.next(); stress = True
        t = self.next()
        if t[1] in ("ix", "poss", "hon"):
            self.expect("(")
            refs = [self.next()[1]]
            while self.at("+"):                 # compound refs: 1p+2p
                self.next(); refs.append(self.next()[1])
            self.expect(")")
            base = (t[1], refs)
        elif t[1] == "num":                     # v0.1.1 numeral grammar
            base = ("num", self.optargs())
        elif t[1] == "fs":
            s = self.next()
            if s[0] != "string": raise SyntaxError("fs needs string")
            base = ("fs", s[1])
        elif t[0] == "ident" and t[1][0].isupper():
            base = ("sign", t[1])
        else:
            raise SyntaxError(f"not a sign token: {t[1]!r}")
        infl, sufx = [], []
        while True:
            if self.at(":"):
                self.next(); key = self.next()[1]
                args = self.optargs()
                infl.append((key, args))
            elif self.at("!") and self.at("est", 1) and self.at("(", 2):
                self.next(); self.next(); self.expect("(")
                ent = self.next()[1]; cls = None
                if self.at(":"):
                    self.next(); cls = self.next()[1]
                self.expect("@"); zone = self.next()[1]
                if self.at("("):                # finger(n) landmark
                    zone = (zone, self.optargs())
                self.expect(")")
                infl.append(("est", ent, cls, zone))
            elif self.at("~"):
                self.next(); key = self.next()[1]
                sufx.append((key, self.optargs()))
            else:
                break
        return ("token", base, stress, infl, sufx)

    def optargs(self):
        if not self.at("("):
            return None
        depth = 0; args = []
        while True:
            t = self.next()
            if t[1] == "(": depth += 1
            elif t[1] == ")":
                depth -= 1
                if depth == 0: return args
            else:
                args.append(t[1])

    def span(self):
        self.expect("["); key = self.next()[1]; self.expect("]"); self.expect("{")
        body = []
        while not self.at("}"):
            body.append(self.item())
        self.expect("}")
        return ("span", key, body)

    def roleshift(self):
        self.expect("rs"); self.expect("("); ref = self.next()[1]; self.expect(")")
        self.expect("{")
        affect, body = None, []
        if self.at("affect"):
            self.next(); self.expect(":"); affect = self.next()[1]
        while not self.at("}"):
            body.append(self.item())
        self.expect("}")
        return ("rs", ref, affect, body)

    def parblock(self):
        self.expect("par")
        dur = None
        if self.peek()[0] == "num":
            dur = self.next()[1]
        self.expect("{")
        stmts = []
        while not self.at("}"):
            stmts.append(self.chanstmt())
        self.expect("}")
        return ("par", dur, stmts)

    def chanstmt(self):
        chan = self.next()[1]          # dh, ndh, face.mouth, gaze, ...
        off = None
        if self.at("+"):               # offset '+0.5b'
            self.next(); off = self.next()[1]
        self.expect(":")
        val = self.chanvalue()
        sufx = []
        while self.at("~"):
            self.next(); sufx.append((self.next()[1], self.optargs()))
        return ("chan", chan, off, val, sufx)

    def chanvalue(self):
        t = self.peek()
        if t[1] == "cl" and self.at("{", 1):
            return self.phonblock("cl")
        if t[1] == "sign" and self.at("{", 1):
            return self.phonblock("sign")
        if t[1] in ("follow", "morpheme", "mouth", "brows", "head", "torso",
                    "eyes", "gaze", "cheeks", "nose"):
            name = self.next()[1]
            return (name, self.optargs())
        return self.token()

    def buoy(self):
        self.expect("buoy"); name = self.next()[1]; self.expect(":")
        signid = self.next()[1]; self.expect("{")
        binds = []
        while not self.at("}"):
            self.expect("!"); self.expect("est"); self.expect("(")
            ent = self.next()[1]; self.expect("@"); self.expect("finger")
            self.expect("("); d = self.next()[1]; self.expect(")"); self.expect(")")
            binds.append((ent, d))
        self.expect("}")
        return ("buoy", name, signid, binds)

    def definition(self):
        self.expect("def")
        name = self.next()[1]
        return ("def", name, self.phonblock("sign"))

    FIELDKEYS = {"hands", "hs", "orient", "loc", "mv", "nm"}

    def phonblock(self, kind):
        self.expect(kind); self.expect("{")
        fields = []
        while not self.at("}"):
            key = self.next()[1]
            self.expect(":")
            vals = []
            # DISAMBIG: a field's value list ends when the next tokens look like
            # 'fieldkey :' or '}'. The EBNF leaves fieldvalue undefined; without
            # a closed fieldkey set this needs 2-token lookahead over an open
            # vocabulary. SPEC BUG: field values should be comma- or
            # newline-terminated, or fieldkeys must be a closed set per profile.
            while not self.at("}") and not (
                self.peek()[0] == "ident"
                and self.peek()[1] in self.FIELDKEYS
                and self.at(":", 1)
            ):
                t = self.next()
                if t[1] == "(":
                    depth = 1
                    while depth:
                        u = self.next()
                        depth += (u[1] == "(") - (u[1] == ")")
                vals.append(t[1])
            fields.append((key, vals))
        self.expect("}")
        return (kind, fields)


def parse(src):
    return P(tokenize(src)).document()

# ---------------- Test corpus: every code example in the spec ----------------

EXAMPLES = {
 "§3 full document": '''
%lry 0.1 %lang asl.v1 %tempo 1.6sps
@entities { mother book }
YESTERDAY |
[topic] { poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
BOOK !est(book @ center-mid-near) |
GIVE :dir(mother -> 1p)
''',
 "§4.2 mid-utterance est": '''
[topic] { poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
CAR !est(car : vehicle @ contra-mid-near)
''',
 "§5.1 tokens": '''
HELLO
WEEK :num(3)
LOOK-AT :asp(iter)
GIVE :dir(1p -> mother)
SIT~fast
!WANT
''',
 "§5.2 deixis/fs": '''
ix(mother) ix(2p) poss(1p) hon(mother)
fs"KAFKA"
fs"KAFKA"~lexical
''',
 "§5.3 spans": '''
[ynq] { ix(2p) DEAF ix(2p) }
[whq] { STORE WHERE }
[neg] { ix(1p) LIKE COFFEE }
[topic] { BOOK } ix(1p) READ FINISH
[cond] { RAIN } [neg]{ GO PICNIC }
[mm] { DRIVE }
''',
 "§5.4 role shift": '''
rs(daughter) {
  affect: annoyed
  [neg] { ix(1p) WANT GO SCHOOL }
}
''',
 "§5.5 par/classifier": '''
par 3b {
  ndh: cl{ hs:open-B orient: palm(down) loc: contra-mid-near } ~hold
  dh:  cl{ hs:3 orient: palm(contra)
           loc: contra-low-near
           mv: path(spiral, to: ipsi-high-far) speed(0.7) }
  face.mouth: morpheme(mm)
  gaze: follow(dh)
}
''',
 "§6 discourse": '''
@entities { brother, denver : place }
[topic] { poss(1p) BROTHER !est(brother @ ipsi-mid-mid) } |
LIVE fs"DENVER" !est(denver @ ipsi-mid-far) ||
EVERY-MONTH ix(1p) VISIT :dir(1p -> brother)
''',
 "§7.1 defs": '''
def HELLO sign {
  hands: dh
  hs: open-B
  orient: palm(fwd) fingers(up)
  loc: temple-ipsi contact(light)
  mv: straight(dir: ipsi+fwd) size(small) end(release)
}
def BOOK sign {
  hands: both sym(mirror)
  hs: open-B
  orient: palm(contact)
  loc: center-mid-near
  mv: pivot(axis: pinky-edge, open: 120deg) end(hold)
}
''',
 "§11.1 ynq": '''
%lry 0.1 %lang asl.v1
[ynq] { ix(2p) DEAF ix(2p) }
''',
 "§11.2 cond+neg": '''
[cond] { TOMORROW RAIN } | [neg] { ix(1p) GO }
''',
 "§11.3 give chain": '''
@entities { mother, sister, book }
YESTERDAY |
[topic] { poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
BOOK !est(book @ center-mid-near) GIVE :dir(mother -> 1p) ||
poss(1p) SISTER !est(sister @ contra-mid-near) |
GIVE :dir(1p -> sister)
''',
 "§11.4 car uphill": '''
@entities { car : vehicle, hill : flat-surface }
[topic] { HILL } [topic] { CAR } ||
par 3b {
  ndh: cl{ hs: open-B orient: palm(down) fingers(contra)
           loc: contra-mid-near } ~hold
  dh:  cl{ hs: 3 orient: palm(contra) fingers(fwd)
           loc: contra-low-near
           mv: path(spiral, to: ipsi-high-mid) speed(0.6) }
  face.mouth: morpheme(mm)
  gaze: follow(dh)
}
''',
 "§11.5 role shift": '''
@entities { daughter }
[topic] { poss(1p) DAUGHTER !est(daughter @ ipsi-mid-near) } |
SAY ||
rs(daughter) {
  affect: exasperated
  [neg] { ix(1p) WANT !GO SCHOOL }
}
''',
 # --- adversarial, not from spec ---
 "ADV stress-then-est": 'MOTHER !est(mother @ ipsi-mid-near) !GO',
 "ADV buoy v0.1.1":     'buoy plans : LIST-3 { !est(coffee @ finger(1)) !est(tea @ finger(2)) } ix(tea) GOOD release(plans)',
 "ADV retract":         '%%retract(2) HELLO',
 "ADV numerals":        'YEAR num(1987) num(4.50, unit: dollar) num(25, unit: percent)',
 "ADV compound+each":   'ix(1p+2p) GIVE :dir(1p -> each(mother, sister))',
 "ADV chained asp":     'WAIT:asp(cont):asp(intense)',
 "ADV est-on-fs zone":  'fs"DENVER" !est(denver @ ipsi-mid-far)',
}

if __name__ == "__main__":
    failed = 0
    for name, src in EXAMPLES.items():
        try:
            parse(src)
            print(f"  OK    {name}")
        except SyntaxError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
    print(f"\n{len(EXAMPLES)-failed}/{len(EXAMPLES)} parsed")
    sys.exit(1 if failed else 0)
