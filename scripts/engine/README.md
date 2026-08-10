# 저장소 하네스 엔진

저장소에 기계적으로 검사 가능한 구조를 부여하는 세 개의 작은 모듈과,
그 구조를 강제하는 gate다. 이들은 프로젝트에 중립적이다. 엔진은 path,
selector, marker, exit code만 알며 파일이 무엇을 의미하는지는 전혀 알지
못한다. vocabulary는 주입하고, check는 연결한다.

| 모듈 | 역할 |
| --- | --- |
| `registry.py` | 구조 선언 문서를 fail-closed 방식으로 load하고, 모든 path를 정확히 하나의 declaration에 mapping하는 selector engine이다. |
| `markers.py` | 사람이 작성하는 파일 안의 generated region을 scan, extract, replace하며 atomic write를 수행한다. |
| `validate.py` | 하나의 command와 하나의 exit code로 project-neutral check series와 프로젝트 고유 check를 실행한다. |

third-party dependency는 없다. Python 3.10 이상이 필요하다(코드에서 `X | Y`
annotation을 사용한다).

**세 모듈은 bare name으로 서로를 import하므로** engine directory 자체가
`sys.path`에 있을 때만 resolve된다. 이들은 package가 아니다. `import
scripts.engine.validate`는 `validate.py` 자체의 `import markers`에서 실패한다.
따라서 아래의 모든 Python example은 먼저 해당 directory를 path에 추가하며,
제공되는 `scripts/check.sh`도 command line에서 같은 작업을 수행한다. 실제
package를 원한다면 `__init__.py`를 추가하고 세 sibling import를 relative
import로 다시 작성하라. 이는 setting이 아니라 engine의 fork다.

---

## 1. 구조 registry

### 필요한 이유

저장소에는 누구도 문서화하지 못할 만큼 빠르게 directory가 쌓인다. registry는
이를 뒤집는다. 하나의 문서가 tree의 각 부분을 어느 selector가 소유하는지
선언하고, 어떤 tracked path도 일치하지 않으면 gate가 실패한다. 그러면 새
directory는 누군가 그것이 무엇인지 명시하지 않고서는 나타날 수 없다.

### 문서

```yaml
schema_version: 1

declarations:
  - select: docs/**
    role: content
    disposition: ship
    overrides:
      - select: docs/internal/**
        disposition: skip
  - select: "*"
    role: support
    disposition: ship
  - select: src/
    role: content
    disposition: ship

exclusions:
  - select: build/**
    reason: compiler output, regenerated on every run
```

`schema_version`과 `declarations`는 필수다. `exclusions`는 schema가 요구하지
않는 한 선택 사항이다. 그 밖의 top-level key는 `extra_top_level_keys`에
이름이 있어야 한다. 그러면 engine은 이를 `Registry.extra` 아래에 verbatim으로
보존하고 그 의미는 사용자에게 맡긴다.

exclusion에는 작성된 reason이 필요하다. 이는 check를 끄는 유일한 declaration이며,
설명 없이 묵살된 check는 1년 뒤에는 도저히 정당화할 수 없다.

### Selector

여섯 가지 shape만 compile되며, 그 밖의 것은 허용되지 않는다.

| Shape | Kind | Reach |
| --- | --- | --- |
| `docs/guide.md` | exact | 해당 파일 하나 |
| `docs/` | direct | `docs` 바로 안의 파일이며, 더 깊은 곳은 제외 |
| `docs/**` | subtree | `docs` 아래 모든 depth의 모든 파일 |
| `*` | root | repository root 바로 아래에 있는 파일 |
| `docs/*` | single | `docs` 아래 한 segment(`direct`와 reach는 같지만 score는 더 낮음) |
| `**/name/**` | anysub | 어떤 depth에서든 이름이 `name`인 모든 directory |

specificity는 `(exactness, literal segment count, -wildcards)` triple이며 왼쪽부터
비교한다. Exact는 모든 glob보다 우선한다. glob끼리는 더 긴 literal prefix가
우선하며, 그것도 같으면 wildcard가 더 적은 쪽이 우선한다.

같은 path에 대해 두 declaration의 specificity가 동률이면 first-one-wins가 아니라
**error**다. order-dependent resolution은 문서의 line numbering에만 존재하며
누구의 머릿속에도 존재하지 않는 rule이다.

`overrides` entry는 parent보다 strictly more specific해야 하며 동시에 parent 안에
포함되어야 한다. 더 넓은 override는 모든 곳에서 parent를 shadow하고, 외부를
가리키는 override는 parent가 소유한 적 없는 path를 claim한다. 둘 다 load error다.

### Vocabulary 주입

engine은 구조를 validate한다. 의미는 `RegistrySchema`가 제공한다.

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("scripts/engine").resolve()))

from pathlib import Path
import registry

SCHEMA = registry.RegistrySchema(
    roles=("content", "support", "generated"),
    dispositions=("ship", "skip", "stub"),
    required_declaration_keys=("select", "role", "disposition"),
    optional_declaration_keys=("note", "overrides"),
    extra_top_level_keys=("project_block",),
    require_exclusions=True,
    max_key_depth=4,
)

reg = registry.load_registry(Path("schema/kernel/layout.yaml"), SCHEMA)
```

`roles` 또는 `dispositions`에 빈 tuple을 지정하면 *여기서는 constrain하지
않는다*는 뜻이다. 값은 여전히 비어 있지 않은 string이어야 하지만 membership은
사용자가 책임진다. `PERMISSIVE_SCHEMA`가 사용하는 방식이며, 독립 실행형 command
line도 이 방식으로 fallback한다. command line은 사용자의 enum을 알 수 없기
때문이다. 이는 의도적인 약화다. 가능하면 자신의 schema를 전달하여 disposition의
typo가 downstream으로 이동하지 않고 load 시점에 실패하게 하라.

### 질의하기

```python
reg.verdict("docs/guide.md")     # PathVerdict(status="declared", disposition="ship")
reg.verdict("build/out.js")      # status="excluded"
reg.verdict("stray/file.md")     # status="undeclared"

reg.disposition_of("docs/internal/plan.md")   # "skip" (from the override)
reg.disposition_of("build/out.js")            # None -- excluded, no disposition
reg.disposition_of("stray/file.md")           # raises KeyError

reg.resolve_one("a/x.md")        # the one owning Declaration, or None
                                 # raises AmbiguousPathError on a tie

reg.audit(tracked_paths)         # [PathIssue(kind="undeclared" | "ambiguous"), ...]
```

*Declared*, *excluded*, *undeclared*는 서로 다른 세 가지 answer다. 이를 하나의
nullable result로 collapse하면 "아무도 이 path를 declare하지 않았다"가 "이 path는
의도적으로 scope 밖이다"처럼 보이게 된다.

프로젝트에 자체 top-level block이 있다면 직접 validate하고 그 결과 declaration을
다시 주입하여 같은 resolution과 같은 duplicate check에 참여하게 하라.

```python
reg.extend([
    registry.Declaration(
        origin="project",
        label="project:tools",
        selector=registry.compile_selector("tools/**"),
        disposition="ship",
    )
])
```

### 실패 동작

`load_registry`는 수집된 **모든** message를 담은 `RegistryError`를 raise하며,
partial한 것은 아무것도 return하지 않는다. 절반만 load된 registry는 없는 것보다
나쁘다. caller가 일부 path는 올바르게 resolve하면서 나머지는 조용히 잘못
attribute할 수 있기 때문이다.

parser는 closed subset만 accept한다. block mapping, block list, single-line flow
shorthand만 허용한다. anchor, alias, merge key, type tag, block scalar, duplicate
key, tab character, `max_key_depth`를 넘는 nesting은 모두 hard error다. subset이
작으면 독자가 전체를 머릿속에 담을 수 있고 두 parser가 서로 다르게 해석할 수도 없다.

---

## 2. Generated region

generated region은 tool이 소유하는, 사람이 작성한 파일의 span이다.

```text
<!-- gen:begin key=index -->
... generator territory ...
<!-- gen:end key=index -->
```

whole-file generator는 그 대신 하나의 sentinel line을 사용한다.

```text
<!-- gen:file key=index -->
```

두 example이 의도적으로 fenced block 안에 있다. 아래의 near-miss rule은 이
파일을 포함하여 fenced block 밖에 있는 marker-like line을 모두 defect로
취급한다. 따라서 running prose에서 marker form을 그대로 적으면 documentation이
자체 gate에 실패한다. spelling은 `MarkerSyntax(token=..., open_delim=..., close_delim=..., key_word=...)`을 통해 configure할 수 있으므로 다른 language의
comment syntax나 repository가 이미 사용하는 spelling에 맞출 수 있다. plugin에서
한 번만 설정하라. marker가 `carrier=`라고 쓰인 repository는 그렇지 않으면 모든
올바른 marker를 near miss로 report하게 되고, false failure의 장벽은 gate가
독자를 잃게 되는 방식이다.

```python
import markers

body = markers.render_body("## Items", ["- alpha", "- beta"])
updated = markers.replace_section(text, "index", body)
markers.atomic_write(path, updated)

markers.check_text(text)          # [MarkerIssue(code=..., lineno=..., message=...)]
markers.extract_section(text, "index")
```

세 가지 behaviour는 타협할 수 없으며, 각각은 반대 behaviour가 조용히 실패하기
때문에 존재한다.

- **near-miss marker line은 error다.** space가 빠진 `key=index-->`도 독자에게는
  marker처럼 보이지만 어떤 generator도 절대 match하지 못한다. 따라서 region은
  마지막 content에서 조용히 freeze된다. silent staleness는 자신을 숨기는 데
  crash보다 뛰어나므로 더 나쁘다.
- **빈 body는 거부한다.** `replace_section`은 blank region을 쓰는 대신 raise하고,
  `check_text`는 기존 blank region을 report한다. 항상 header와 count를 emit하는
  `render_body`를 사용하라. 그래야 "아무것도 찾지 못함"과 "실행하지 않음"을
  구분할 수 있다.
- **write는 atomic하다.** rewrite 도중 interrupt된 generator가 old version도
  new version도 아닌 파일을 남겨서는 안 된다.

fenced code block 안의 line은 near-miss probe를 포함한 모든 검사에서 완전히
skip된다. 그렇지 않으면 marker form을 document하는 것이 불가능하다.

---

## 3. Gate

```
sh scripts/check.sh
```

이 wrapper가 지원되는 entry point다. engine을 path로 invoke하고, plugin import가
resolve되도록 `PYTHONPATH`를 설정하며, 개발 중에는 `worktree-clean`을 demote한다.
engine을 직접 호출해도 동작하지만, 그러면 이 세 가지를 올바르게 처리할 책임은
사용자에게 있다.

```
PYTHONPATH=. python3 scripts/engine/validate.py \
  --root . --registry schema/kernel/layout.yaml
```

| Option | Effect |
| --- | --- |
| `--root DIR` | repository root(default: current directory) |
| `--registry PATH` | registry를 load하고 `undeclared-path`를 enable함 |
| `--plugin module:attr` | 사용자의 check와 registry schema |
| `--warn CHECK_ID` | demotable check 하나를 warning으로 demote함(repeatable) |
| `--marker-suffix SUFFIX` | marker를 scan할 file suffix(repeatable) |
| `--strict` | warning을 failure로 취급함 |

output은 finding마다 한 line이며 마지막에 count가 나온다.

```text
WARN: [temp-file] docs/scratch.tmp: tracked file looks temporary
FAIL: [os-metadata] .DS_Store: tracked operating-system metadata
Validation complete: 1 failure(s), 1 warning(s).
```

exit code는 clean이면 `0`, finding이 있으면 `1`, usage 또는 configuration error면
`2`다.

### Check series

series는 closed다. 모든 id의 severity는 기본적으로 **error**다. finding의 기본값이
advisory인 gate는 사람들에게 scroll해서 지나치라고 가르치기 때문이다.

| Check id | Reports | Demotable |
| --- | --- | --- |
| `scan-source` | path universe를 enumerate할 수 없음(git이 없거나 repository가 아님) | no |
| `worktree-clean` | uncommitted change | yes |
| `merge-conflict` | unmerged index entry 또는 tracked file에 남은 conflict text | no |
| `os-metadata` | tracked operating-system junk file | no |
| `temp-file` | tracked scratch 또는 backup file(name heuristic) | yes |
| `marker-integrity` | malformed, unpaired, nested 또는 near-miss marker | no |
| `empty-state` | 비어 있는 path universe 또는 아무것도 report하지 않는 generated region | no |
| `undeclared-path` | declaration이 소유하지 않는 tracked path 또는 ambiguous tie | no |

`validate.py`의 `NON_DEMOTABLE`은 demotion을 거부하는 id를 나열한다. 그중 하나를
`--warn`에 전달하면 accept한 뒤 ignore하지 않고 configuration 시점에 exit `2`로
실패한다. 각각은 damage를 일으킬 때까지 보이지 않는 defect, 또는 report의 나머지를
신뢰할 수 없는 state를 report한다.

`scan-source`는 별도 설명이 필요하다. git이 없거나 root가 repository가 아니면
tracked path list가 비고, 그러면 validator가 읽은 적 없는 repository에서 모든
path-based check가 통과해 버린다. 대신 이 check는 크게 실패하며, 아래 check들이
실행되지 않았다고 알린다.

`undeclared-path`에는 `--registry`가 필요하다. 이 옵션이 없으면 check가 비교할
대상이 없으므로 실행되지 않았다는 `NOTE:` line을 출력한다. 아무것도 출력하지
않고 skip된 check는 통과한 check와 구별할 수 없고, 이 check가 아무도 declare하지
않은 directory를 잡아내는 유일한 check다.

marker scanning의 기본 suffix는 `.md`, `.markdown`, `.txt`, `.rst`다. source
file은 일상적으로 comment에서 marker를 다루며, 이를 flag하면 잘못 입력한 marker를
잡는 check를 무시하도록 사람들을 훈련하게 된다. 다른 file type에 generate한다면
`--marker-suffix`로 scope를 넓혀라.

### 자체 check 추가

하나의 plugin object가 사용자의 check, 이 check가 전제하는 registry vocabulary,
이 check가 읽는 marker spelling을 함께 운반한다. 따라서 loader가 들은 적 없는
enum을 전제하는 check와 함께 plugin을 load할 수 없다.

```python
# harness_plugin.py — at the repository ROOT, because the command below imports
# it as the top-level module `harness_plugin`. Saving it inside a package would
# make its module path `<package>.harness_plugin` and the command would look for
# a different file.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "scripts" / "engine"))

import markers
import registry
import validate


def check_headings(ctx):
    for relpath in ctx.tracked:
        if not relpath.endswith(".md"):
            continue
        text = ctx.read_text(relpath)
        if text is not None and not text.startswith("# "):
            yield validate.Finding("heading-required", "file does not open with a title", relpath)


PLUGIN = validate.Plugin(
    checks=(validate.Check("heading-required", check_headings),),
    registry_schema=registry.RegistrySchema(
        roles=("content", "support"),
        dispositions=("ship", "skip"),
    ),
    marker_syntax=markers.MarkerSyntax(key_word="carrier"),
)
```

```
# The plugin is imported by module path, so its package must be importable.
# Running validate.py by path puts only the engine directory on sys.path, which
# is why PYTHONPATH is set here: without it the import fails with
# "cannot import plugin module".
PYTHONPATH=. python3 scripts/engine/validate.py \
  --root . --registry schema/kernel/layout.yaml --plugin harness_plugin:PLUGIN
```

check는 `Context`(`root`, `tracked`, `registry`, `read_text`,
`git_available`)를 받고 `Finding(check_id, message, path="")`를 yield한다. file
read는 cache를 사용하고 decodable text가 아닌 대상에는 `None`을 return하는
`ctx.read_text`를 거친다.

closed series와 collide하는 plugin check id는 load 시 거부된다. 재사용된 id가
engine check를 조용히 replace하거나 한 report에서 하나의 id가 두 가지 의미를
가지게 할 수 있기 때문이다. plugin id는 기본적으로 demotable이다.
`NON_DEMOTABLE`은 engine series만 cover하며, project check를 절대 soften해서는
안 된다면 확장할 책임은 사용자에게 있다.

shell out 대신 gate를 embed할 수도 있다.

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("scripts/engine").resolve()))

import validate
from harness_plugin import PLUGIN

sys.exit(validate.main(sys.argv[1:], plugin=PLUGIN))
```

---

## 4. 이 engine이 의도적으로 하지 않는 일

누락 사항이 설계이며 backlog가 아니다. 아래 항목은 두 프로젝트에 동시에 올바를
수 없고, 반쯤 generic한 version은 없는 것보다 나쁘기 때문에 제외되었다.

- **file schema는 없다.** front-matter field, required section, heading order,
  naming convention, identifier format은 모두 프로젝트 자체의 vocabulary다.
  plugin check로 작성하라.
- **document-type knowledge는 없다.** engine은 읽는 document의 종류를 묻지
  않는다. path와, marker에 대해서는 text를 읽는다.
- **link 또는 reference checking은 없다.** cross-reference syntax는 프로젝트마다
  다르다. engine은 사용자가 어느 bracket dialect를 쓰는지 추측하지 않는다.
- **natural-language rule은 없다.** terminology, register, tone, word-choice
  check는 전적으로 프로젝트 자체 standard에 의존한다.
- **content generation은 없다.** `markers.py`는 region을 maintain한다. 그 안에
  *무엇이* 들어갈지는 generator의 일이다.
- **enum에 대한 opinion은 없다.** role과 disposition은 engine이 사용자가 제공한
  tuple과 비교하는 string이다. engine은 어떤 특정 value에도 behaviour를 부여하지
  않는다.
- **series를 넘어서는 severity policy는 없다.** 자체 check 중 무엇을 demote할 수
  있는지는 사용자의 결정이다. engine은 자신의 critical id를 조용히 soften할 수
  없다고 보장할 뿐이다.

경계는 단순하다. 다른 repository에서 rule의 wording을 바꿔야 한다면 그 rule은
여기가 아니라 plugin에 속한다.

## English brief

This document defines the repository-neutral harness engine: its structure registry, generated-region markers, and validation gate. It preserves the selector grammar, module APIs, commands, and failure semantics summarized by the Korean canonical text. Project-specific vocabulary and checks belong in plugins.
