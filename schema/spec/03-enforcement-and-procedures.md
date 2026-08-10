# 제3장 — 강제, 검증, 절차

이 장은 하네스의 나머지 부분을 실제로 *실행되게 하는* 메커니즘을 다룬다. 계층과 evidence 장의 모든 내용은 무엇이 참이어야 하는지를 설명한다. 이 장의 내용은 무엇이 참이어야 하는지를 설명하지 않는다. 여기에는 참이 아닌 상태를 보장된 시점에 탐지할 수 있게 하는 메커니즘과, 시간이 지나도 계속 발견 가능하고 drift하지 않는 절차가 있다.

E1부터 읽어라. 하네스의 최소 실행 가능 집합은 세 가지 메커니즘, 즉 provenance 기반 계층 분리(A1), 구조 선언 registry(A2), producer wiring 의무(E1)로 이루어진다. A1과 A2는 tree에 관해 무엇이 참인지 알려 준다. 그것이 더는 참이 아닐 때 누군가 이를 알게 되는 유일한 이유가 E1이다. A1과 A2를 이식하면서 E1을 생략한 도입자는 하네스가 아니라 파일 정리 체계를 만든 것이다.

아래의 모든 메커니즘에 적용되는 표본 크기 주의사항: 이 하네스는 agent가 주된 committer인 정확히 하나의 프로젝트에서 실행되었다. 주장이 단 한 번 관찰된 실패에 근거할 때는 본문에 그렇게 명시한다.

---

## E1 — Producer wiring 의무

**Tier: CORE.** 이것이 없으면 이 장의 다른 모든 check는 작동하지 않는다. 탐지 시점은 오직 이 wiring의 속성이므로, 이를 제거하면 enforcement 계층 전체가 문서로 전락한다.

### 정의

governed artifact를 만들거나 변경하는 모든 canonical 절차는 끝부분에 다음과 같은 명시적 번호 단계가 있어야 한다. *commit 전에 validator를 실행한다. 실패하면 commit하지 않는다. 수정하고 다시 실행한다.* "유효한지 확인한다"거나 "적절히 lint한다"는 표현이 아니다. 실제 command를 commit 단계 바로 앞에 놓고 실패 분기까지 적어야 한다.

역할 분담은 의도적이다. check catalogue(E2)는 어떤 check가 존재하고, 무엇을 판단하며, severity가 무엇인지를 소유한다. 강제력은 전혀 소유하지 않는다. 강제력은 서로 다른 14개의 절차 문서가 각각 validator 실행을 단계로 명시하여, 그 절차를 따르는 agent가 별도의 결정을 내리지 않고도 validator를 실행한다는 사실에서 나온다. 따라서 탐지 시점은 구조적 속성이다. governed artifact가 canonical 절차를 거쳐 commit에 이르는 동안 validator 실행을 건너뛸 수 없다.

여기에는 도입자가 곧바로 의문을 품을 의도적인 미채택 사항이 있다. commit hook과 CI 강제를 검토했지만 채택하지 않았고, 강제는 절차 본문 수준에 남겼다. 이유는 실행자가 행동 전에 절차 문서를 읽는 agent이므로, 그 실행자에게는 절차 본문이 곧 실행 경로이며 hook을 추가하면 첫 번째 강제 지점과 불일치할 수 있는 두 번째 강제 지점이 생기기 때문이다. trade-off를 솔직히 밝혀야 한다. 사람이 commit하거나 절차를 우회하는 경로가 있는 저장소에서는 사람이 매 commit 전에 절차를 읽지 않으므로, 절차 본문 wiring은 hook보다 엄격히 약하다. committer가 사람이라면 hook을 추가하되 wiring도 유지하라. hook 실패를 이해할 수 있게 하는 것이 wiring이다.

원본 프로젝트의 coverage는 절차 spec 17개 중 14개였다. 그 단계가 없는 세 문서는 external-collector 절차, session-archiving 절차, 그리고 아무것도 생산하지 않는 reference annex다. 깔끔한 100%는 아니며, 이 빈틈은 시사하는 바가 크다. 생략된 절차는 산출물이 가장 덜 governed된다고 느껴진 절차들인데, 바로 그런 곳에서 도입자는 첫 drift를 예상해야 한다.

### 존재 이유

저장소에 구조 registry와 check 60개가 쌓였지만 아무도 실행하지 않는 상황이 생긴다. 실행은 따로 기억해야 하는 행동이고, 기억은 실제 작업과 경쟁한다. tree는 몇 주 동안 drift한다. 마침내 누군가 validator를 실행하면 한꺼번에 수백 개 finding이 나오는데, 운영상 이는 noise와 구별되지 않는다. 어느 finding이 오늘의 실수이고 어느 것이 6주 동안 쌓인 침전물인지 아무도 알 수 없다. 300줄짜리 보고서에 대한 합리적 반응은 이를 억제하거나 무시하는 것이며, 두 반응 모두 check catalogue를 영구히 죽인다. catalogue의 실제 출력은 누구도 해소하지 않을 backlog가 되고, registry는 더는 존재하지 않는 tree를 설명하는 문서가 된다.

두 번째 실패는 더 미묘하며, 메커니즘 이름에 단순한 *실행*이 아니라 *시점*이 들어가는 이유다. 예측할 수 없는 시점에 실행되는 check에는 다른 어떤 메커니즘도 의존할 수 없다. identifier collision scan은 번호가 history에 들어가기 전에 실행될 때만 유용하고, manifest drift check는 오래된 manifest를 다음 agent가 읽기 전에 실행될 때만 유용하다. 보장이 필요한 메커니즘인 serialized issuance 절차(C2)와 manifest discipline(A4)은 실행 시점이 정의된 check 위에 세워진다. "누군가 주기적으로 validator를 실행한다"로는 아무것도 뒷받침할 수 없다.

세 번째로 측정된 실패가 있다. 검증 command를 commit command와 chain하면 실패가 gate 없이 통과할 수 있다. `validate && commit`이라고 쓰면 gate처럼 보이고 실제로 gate이기도 하지만, 반대 순서로 chain하거나 이미 메시지를 작성한 commit에 검증 출력을 chain하는 것은 gate가 아니다. 검증, 검증 출력 확인, commit은 서로 분리된 세 가지 행위여야 한다. bulk migration에서 chain된 형태 때문에 실패한 실행이 landing한 사례가 한 번 관찰되었다.

### 도입 방법

- validator entry point는 하나만 둔다. command 하나, exit code 하나, 저장소 전체 scan 하나다. 호출자가 조립해야 하는 script 모음으로 만들지 않는다. 조립은 결정이고 결정은 생략된다.
- 저장소 전체 실행을 빠르게 유지한다. 초 단위 실행은 어디에나 wiring되지만, 분 단위 실행은 "PR 전"으로, 이어서 "release 전"으로, 끝내는 어디에도 없는 곳으로 옮겨 간다.
- 모든 절차 문서에 실패 분기를 명시한 단계를 넣는다. 절차 directory에서 command 이름을 grep하라. 그 command를 포함한 파일 수가 실제 coverage이며, 그 수를 알고 있어야 한다.
- 해당 단계를 commit 단계 바로 앞에 놓고 verify / inspect / commit을 서로 분리된 세 instruction으로 유지한다. 이를 chain하는 절차를 절대 만들지 않는다.
- generator가 있는 메커니즘에서는 generate-then-validate 순서로 작성한다. 먼저 모든 derived view를 재생성하고 나서 validate하여, generator가 곧 고칠 drift를 보고하는 대신 생성 후의 tree를 validator가 판단하게 한다.
- 항상 load되는 entry document에 validator를 producer duty로 가리키는 routing row를 추가하여, 이름 붙은 절차 밖에서 작업하는 agent도 그 의무를 발견하게 한다.

### 의존 대상 / 없을 때 파손되는 조건

- **A2** — validator의 가장 강력한 check는 모든 tracked path가 declaration에 포함되는지를 묻는다. registry가 없으면 이 질문에는 답이 없고 validator는 syntax checker로 전락한다.
- **E2** — E1은 시점을, E2는 내용을 제공한다. catalogue 없는 E1은 구현에 따라 severity가 drift하는 미지정 check 집합을 실행한다.
- **A4, E3, F1**은 각각 enforcement를 "check가 validator 실행에 wiring된다"고 표현한다. 이 문장은 E1에 관한 주장이다. E1이 없으면 세 메커니즘 모두 convention으로 전락한다.
- **C2**는 issuance와 관련해 정의된 시점에 collision scan이 실행되는 것에 의존한다. 그 보장은 E1의 것이다.

---

## E2 — Check catalogue governance

**Tier: CORE.** 자체적으로 governed되지 않는 check 집합은 severity와 identity가 drift하여, 결국 enforcement 계층의 동작이 어떤 decision이 아니라 구현의 속성이 된다. 그 시점부터 그 위에 있는 어느 것도 신뢰할 수 없다.

### 정의

값싸고 모두 핵심적인 네 가지 하위 메커니즘이 있다.

**닫힌 identifier family.** check id는 엄격한 kebab-case grammar를 따르고 첫 token은 닫힌 집합에서 가져온 *family*다. 원본 프로젝트의 family는 대략 version-control hygiene, parser and schema, document-class classification, naming, frontmatter discipline, machine-field references, body links, manifests, generated-artifact comparison, registry and paths, event chain이었다. 여기에 이 catalogue의 관할 밖에 있는 인접 도구의 check를 위해 예약했지만 구현하지 않은 family 하나가 더 있었다. reserved namespace 개념은 복제할 가치가 있다. check가 존재하지 않는 척하지 않으면서 "이 id들은 다른 주체의 것이다"라고 말할 수 있기 때문이다. self-check fixture는 catalogue의 모든 id가 grammar로 parse되고 그 family가 집합에 속하며 self-violation은 0개임을 assert한다.

**3방향 binding.** check id는 정확히 세 위치에 나타난다. catalogue table의 row, decision record의 `required_checks` list 값, 구현의 registration constant다. catalogue table이 canonical이며, cross-check lint는 이를 구현의 registration constant와 *양방향으로* 비교한다. 구현이 없는 catalogue row와 row가 없는 구현 check는 똑같이 error다. 세 곳 사이의 불일치 자체가 lint finding이다. binding은 바람이 아니라 check다.

**Severity discipline.** 기본 severity는 error다. schema, naming, uniqueness, dangling reference, manifest currency, path ownership 같은 contract violation은 모두 기본적으로 error이며, 성능은 이를 완화할 수 있는 허용 사유가 아니다. warning은 열거된 네 조건에서만 허용되고, 이 조건은 contract에 작성하여 "이것을 warning으로 만들자"는 말이 목록에 비추어 정당화해야 할 주장이 되게 한다.

1. **Heuristic checks** — 판단이 확률적 신호여서 구조적으로 오판할 수 있다. 이는 nudge이지 contract violation이 아니다.
2. **Acknowledged debt** — 문서 자체 frontmatter에 명시적으로 표시된 알려진 결함이다. 조용한 suppression은 금지되며 marker가 있어야 warning이 허용된다.
3. **Agreed two-stage rollout** — 먼저 warning, 나중에 error로 바꾸며 promotion 시점을 특정 decision에 결속한다. 무기한 warning 상태는 금지된다. 6개월 동안 "일단 warning"이었던 check는 영원히 error가 되지 않을 check다.
4. **Release-only escalation** — default mode에서는 warning, release 또는 strict gate에서는 error다.

그리고 **no-downgrade list**가 있다. warning으로 낮추는 행위 자체가 contract violation인, 절대 warning으로 낮출 수 없는 이름 붙은 check 집합이다. 원본 프로젝트에서는 manifest currency, global uniqueness check 둘, dangling 및 ambiguous reference, parser schema gate, single-classification check, unregistered-path check, decision-receipt check가 여기에 포함되었다.

**Parser unification.** frontmatter parser, registry loader, protected-span extractor는 공유 module에 있고 validator와 모든 generator가 같은 module을 import한다. 두 번째 parser는 금지된다. parser는 strict subset parser다. 수용하는 shape(scalar, flat array, top-level block literal)를 열거하고, duplicate key, 인식하지 못하는 shape, integer가 아닌 version field, malformed array, 빈 selector list를 즉시 error로 처리한다. Markdown frontmatter와 standalone YAML document는 하나의 schema로 판단한다. 문서의 carrier format이 규칙을 바꾸지 않는다.

parser unification에는 **fail-open 금지**가 함께 온다. schema를 위반한 파일은 error로 보고하며, 한 위반 때문에 같은 scan set에 대한 다른 check가 조용히 통과해서는 안 된다. generator input이 손상되면 해당 carrier는 중단한다. 문서가 손상되면 그 파일의 downstream check는 억제하되 *전체 실행은 실패한다*. 실패 없는 suppression은 망가진 tree 위의 green build가 취하는 모양이다.

catalogue가 실제로 작동하려면 두 가지가 더 필요하다. **rename에는 successor id와 같은 commit에 landing하는 read-side alias가 필요하다.** alias는 기존 record를 읽거나 fixture를 match할 때 허용되지만 새 write에는 절대 유효하지 않다. alias key는 check id가 아니므로 family self-check에서 제외하지만, alias table 자체는 rename mapping과 cross-check한다. **Retirement timing:** migration이 check target 자체를 제거할 때는 제거 commit과 successor check의 activation이 같은 commit이어야 한다. 그렇지 않으면 jurisdiction gap(어떤 것도 invariant를 지키지 않는 기간)이나 double-red(두 check가 같은 조건에서 모두 발화하여 모든 실행에 noise가 생기고 결국 둘 다 무시되는 상태)가 생긴다.

마지막으로 catalogue는 lint가 *flag하지 말아야 할 것*도 규정한다. code span과 fence, protected verbatim region, 완전성을 목표로 하지 않고 의도적으로 선별한 manifest section, retired identifier가 plain text에 역사적으로 언급된 경우, reserved sentinel value 같은 false-positive exclusion은 공유 module에서 한 번만 정의하고 check마다 다시 구현하지 않는다. check별 exclusion logic은 두 check가 code fence의 정의에 관해 불일치하게 되는 경로다.

### 존재 이유

**downgrade는 check를 약하게 만드는 것이 아니라 invariant를 삭제한다.** "이 check들은 중요하다"라는 말은 오후 6시에 아무도 설득하지 못하므로, 이것이 도입자에게 제시할 논거다. 각 no-downgrade check는 *다른 메커니즘이 전제하는* invariant를 지킨다.

- currency check가 warning 수준이면 manifest는 *때때로* 참이라는 뜻이다. 이는 manifest가 없는 것보다 나쁘다. 독자는 manifest를 신뢰하고 스스로 열거하기를 멈추기 때문이다. 신뢰할 수 없다고 알려진 manifest라면 적어도 다시 derive하지만, 신뢰할 수 있다고 믿는 manifest는 그대로 읽는다.
- global-uniqueness check가 warning 수준이면 tree에 duplicate id가 존재한다. 그러면 id 기반 reference는 모두 잠재적으로 ambiguous하며, 문서가 path 대신 id로 다른 문서를 인용하게 하는 전체 reference-resolution model은 더는 well-defined가 아니다. "대체로 unique"인 id란 있을 수 없다. resolution rule은 total이거나 존재하지 않는다.
- unregistered-path check가 warning 수준이면 registry는 더는 tree의 닫힌 설명이 아니다. "이 path가 선언되었는가?"라는 모든 질문은 사람에게 되돌아가고 A2는 조용히 advisory가 된다.

**한 파일에 두 parser를 적용하면 error 없이 두 개의 truth가 생긴다.** 문서에 duplicate key가 있다고 하자. 한 parser는 first-wins, 다른 parser는 last-wins를 택한다. validator는 자신이 읽은 값을 승인하고 generator는 *자신이* 읽은 값을 내보낸다. 둘은 서로 다른 값이다. 각 도구의 관점에서는 파일이 정상이었으므로 아무것도 실패하지 않는다. silent-skip 변형은 더 나쁘다. 한 도구가 parse할 수 없다고 보는 파일이 그 도구의 scan set에서 그냥 빠지고, absence는 조용하다. check는 실패했어야 할 파일 하나를 조용히 제외한 집합에 대해 finding 0개를 보고한다.

**govern되지 않은 catalogue는 무엇이 강제되는지 아무도 모르는 상태로 drift한다.** 누군가는 migration을 위해 check를 warning으로 내리고 다시 올리지 않는다. 누군가는 구현에서 check 이름을 바꾸고, 예전 id를 적은 decision record는 이제 아무것도 가리키지 않는다. 누군가는 기존 family와 개념적으로 충돌하는 id의 check를 추가한다. 세 위치가 각자 내부적으로는 일관되어 보이므로, 3방향 binding 없이는 어느 것도 보이지 않는다.

### 도입 방법

- catalogue를 id, target, criterion, severity, 구현 위치, 아직 active인지 여부를 담은 table로 작성한다. 마지막 column은 보기보다 중요하다. check를 구현하기 전에 specification으로 landing할 수 있게 하므로 jurisdiction gap 없이 enforcement를 단계화할 수 있다.
- check가 20개가 되기 전에 family set을 고정한다. 나중에 닫힌 family set을 소급 도입하면 rename이 필요하고, rename에는 alias가 필요하며, alias에는 위의 alias machinery가 필요하다.
- self-check를 test로 작성한다. 모든 id가 parse되고, 모든 family가 집합에 속하며, catalogue와 구현 registration constant가 양방향으로 일치하고, rename mapping과 alias table이 일치해야 한다.
- warning 허용 조건 네 가지와 no-downgrade list를 contract에 작성하여 작성자가 반론을 제시해야 할 prose로 만든다.
- parser를 module 하나에 두고 두 번째 parser를 금지한다. strict-subset acceptance list를 명시한다. 목록에 없는 모든 것은 best-effort parse 대상이 아니라 error다.
- severity 변경을 다른 contract 변경과 같은 decision gate로 보낸다. 구현이 자체적으로 severity를 바꾸는 것은 drift이며 cross-check가 이를 잡아야 한다.

### 의존 대상 / 없을 때 파손되는 조건

- **E1** — 아무도 실행하지 않는 catalogue는 문서다. 이 장에서 가장 날카로운 경계이며 한 방향만 가리킨다. E1 없는 E2는 저장소에 미치는 효과가 0이다.
- **A2** — unregistered-path check는 registry query다. registry가 없으면 이 check와 path-ownership family 전체에는 referent가 없다.
- **E5** — false-positive rule이 의존하는 exclusion-zone 정의는 protected-span extractor에서 온다. "protected"의 정의가 둘이면 prose check와 substitution driver가 어느 byte를 건드릴 수 없는지에 대해 불일치한다.
- **B1** — 3방향 binding의 `required_checks` leg는 decision record에 있다. machine-readable check list를 지닌 record가 없으면 binding에는 leg가 둘뿐이고 catalogue는 어떤 decision에도 묶이지 않은 채 떠다닌다.

---

## E3 — Regression fixture gate

**Tier: CORE.** 이 메커니즘이 막는 실패는 자체 선언한 regression scope이며, 이 실패는 사후에 탐지할 수 없다. 잡아냈어야 할 fixture를 생략한 contract 변경은 실행할 fixture가 없었던 변경과 똑같아 보인다.

### 정의

기존 artifact의 작은 이름 붙은 집합을 regression baseline으로 지정한다. 각 fixture entry는 artifact, 그것이 exercise하는 contract, role tag(시스템에 실제로 있었던 bug를 encode한 artifact에는 `known-failure-regression-case`, 현재의 올바른 동작을 encode한 artifact에는 `representative-current-case`), 기대 속성의 prose list, 사람이 실제로 review했는지를 나타내는 flag, 마지막 regression 실행을 가리키는 pointer를 기록한다. 마지막 값은 *날짜가 아니라 event id*로 기록하여, 누구나 입력할 수 있는 timestamp가 아니라 evidence를 담은 record까지 실행을 trace할 수 있게 한다.

gate의 핵심은 **fixture selection이 declaration이 아니라 binding으로 이루어진다**는 것이다. fixture contract에는 selector, 즉 layer tag와 path glob을 담은 `targets:` field가 있다. decision record에는 변경 대상 범위를 설명하는 `affected_targets`와 반드시 실행할 것을 나열하는 `required_checks`가 있다. decision의 `affected_targets`가 fixture contract의 `targets:`와 match하면 그 fixture set이 자동으로 `required_checks`에 들어간다. 작성자는 선택하지 않는다. 작성자는 자신이 알고 있는 변경 대상을 설명하고, 메커니즘은 작성자가 대개 알지 못하는 재검증 대상을 derive한다.

두 번째 독립 check는 receipt를 강제한다. 모든 decision record는 verification receipt pointer 또는 verification이 적용되지 않는다고 명시한 이유 중 하나를 반드시 가져야 한다. 둘은 mutually exclusive이고 둘 다 없으면 error다. validator는 선언된 receipt가 실제로 존재하는지를 독립적으로 검사한다. 자체 declaration만으로는 gate를 통과할 수 없다. receipt를 선언할 수는 있지만 check가 직접 찾아가 확인한다.

artifact 수준 fixture 옆에는 **code-level fixture directory**가 있다. check family마다 input file directory 하나(frontmatter shape, generator behaviour, registry state, document structure, protected-span extraction)와 runner script를 둔다. 일반적인 unit test지만 두 속성은 복제할 가치가 있다. check가 조용히 발화하지 않게 되는 상황을 탐지할 수 있도록 반드시 실패해야 하는 *negative* case를 포함한다. 그리고 acceptance condition을 check catalogue에 hand-over specification으로 작성한다. 그러면 validator 재구현에는 "기존 test를 통과한다"가 아니라 명확한 기준이 생긴다. test를 구현하지 않으면 재구현이 기존 test를 자명하게 통과하기 때문이다.

evaluation 절차 자체에도 제약이 있다. candidate output을 임시 위치에 재생성하고 live artifact와 diff한 뒤 human approval을 gate로 삼는다. evaluation 중 immutable input을 overwrite하지 말고 unrelated live artifact도 건드리지 않는다. 평가 대상을 변경하는 evaluation은 자신의 baseline을 파괴한 것이다.

### 존재 이유

**contract를 변경하는 작성자는 정확히 무엇이 그 contract에 의존하는지 열거할 수 없는 사람이다.** 이는 부주의가 아니라 상황의 정의다. dependents를 열거할 수 있다면 변경은 위험하지 않을 것이다. 어떤 fixture를 실행할지 선언하라고 하면 작성자는 변경하는 동안 생각했던 fixture를 선언한다. 이는 이미 머릿속에 있던 dependent 집합이며, 위험에 놓인 적이 없는 바로 그 집합이다.

**declaration에는 incentive 문제도 있다.** fixture를 선언하면 실행해야 하고, 실행하면 실패할 수 있으며, 실패하면 지금 일이 늘어난다. 시간 압박을 받으면 정직한 declaration이 가장 먼저 축소되고, 그 축소는 보이지 않는다. 짧은 `required_checks` list는 실제로 scope가 좁은 변경과 구별되지 않는다. binding은 선택지를 없앤다. 작성자는 여전히 scope를 설명하지만, scope 설명은 결과에 관한 주장(어디에서도 검사할 수 없음)이 아니라 변경에 관한 주장(diff와 대조 가능)이다.

**사람들이 정직하게 통과할 수 없는 gate는 우회된다.** receipt check가 명시적인 non-applicability 사유를 허용하는 이유다. 유일한 통과 상태가 "fixture를 실행했다"라면 진정으로 적용되지 않는 변경은 실행을 조작하거나 check를 disable한다. 서로 배타적인 두 exit를 모두 기록하며 어느 쪽도 silence가 아니다.

### 도입 방법

- fixture set을 작게 유지한다. 원본은 총 9개의 artifact를 사용했다. 큰 fixture set은 아무도 다시 실행하지 않는다. fixture는 corpus coverage가 아니라 *contract surface* coverage를 위해 선택한다.
- known-failure case를 명시적으로 포함하고 label한다. 이미 고친 bug를 encode한 artifact가 그 fix가 아직 작동하는지를 알려 준다.
- selector shape를 이식 가능한 부분으로 만든다. fixture contract의 `targets:`에는 tagged selector(`layer:<name>`, `path:<glob>`)를 두고 change record의 `affected_targets`와 match한다. 두 field 모두 prose가 아니라 machine-readable frontmatter여야 한다.
- 모든 decision record에 서로 배타적인 두 exit receipt field를 요구하고, 둘 다 없으면 error로 처리한다. validator가 pointer를 신뢰하지 말고 참조된 receipt가 존재하는지를 검증하게 한다.
- check family마다 negative case를 포함한 code-level fixture directory를 추가하고, 그 pass condition을 재구현 기준으로 check catalogue에 작성한다.
- 마지막 regression 실행은 날짜가 아니라 evidence record를 가리키는 pointer로 기록한다.

### 의존 대상 / 없을 때 파손되는 조건

- **B1** — 자동 선택에는 machine-readable scope field가 있는 decision record가 필요하다. decision이 prose로 작성되면 match할 대상이 없어 selection은 declaration으로 되돌아간다.
- **E1** — receipt check는 정의된 시점에 실제로 실행되어야 한다. 가끔 실행되는 receipt check는 아무것도 잡지 못한다.
- **E2** — `required_checks` 값은 check catalogue의 controlled vocabulary에서 온다. free-text check name을 허용하면 decision이 존재하지 않는 check를 요구해도 아무도 알아차리지 못한다.
- **F5** — 기록된 profile version이 있어야 contract 변경으로 어떤 기존 artifact가 어떤 규칙 아래 생성되었는지 식별할 수 있다. 이것이 없으면 binding이 있어도 "이 변경은 무엇에 영향을 주는가"라는 질문에 query 가능한 답이 없다.

---

## E4 — 닫힌 frontmatter schema

**Tier: DEFAULT.** unknown field에 warning을 내는 열린 schema도 비용을 감수하면 작동하므로 이 구체적 형태는 대체할 수 있다. 그러나 닫힘 자체가 모든 downstream 메커니즘이 field의 존재를 신뢰할 수 있게 한다.

### 정의

각 governed document는 정확히 하나의 document class에 속한다. class는 self-declaration이 아니라 위에서 아래로 평가하는 **ordered decision list**로 정한다. list는 fail-closed다. 어느 rule과도 match하지 않으면 error이며, 해당 문서 series에 허용된 deviation set 밖의 self-declared class도 error다. 정확히 하나의 class가 나와야 하며 ambiguity는 finding이다. classification boundary는 반드시 *out of jurisdiction*으로 결정되어야 하는 case를 포함한 boundary fixture 집합으로 고정한다. classifier가 올바르게 분류를 거부함을 입증하는 fixture는 분류함을 입증하는 fixture만큼 중요하다.

각 class별로 schema는 **닫힌 field set**을 선언한다. unknown key는 warning이 아니라 error다. enum-valued field는 controlled vocabulary와 대조한다. reference-valued field는 link markup이 섞이지 않은 plain identifier만 담아야 한다. 별도 check가 참조한 identifier의 존재를 검증하고, mandatory reference field는 absence 역시 error다. version field는 integer여야 한다. selector list는 비어 있으면 안 된다.

닫힌 집합을 감당할 수 있게 하는 두 가지 허용 장치가 있다.

**strict loader가 문서를 보기 전에 block literal을 byte-verbatim으로 먼저 추출한다.** 그렇지 않으면 닫힌 schema와 strict parser가 사용자가 작성한 text를 byte-immutable하게 유지해야 한다는 요구와 정면으로 충돌한다. parser가 quotation 내부 whitespace를 normalize할 것이기 때문이다. top-level block literal만 허용하며 다른 block-scalar shape는 계속 hard parse error다.

**legacy acceptance flag.** naming 또는 field migration 이전 문서는 configuration flag 아래에서 legacy로 허용한다. strict parse도 새 형식 field enforcement도 적용하지 않으며, flag를 전환하는 것이 cutover다. 이것이 있어서 corpus 전체가 한 번에 준수하도록 요구하지 않고도 strict schema를 먼저 설치할 수 있다.

specification이 침묵하는 곳에서는 구현이 취한 interpretation을 기록하고 rule을 발명하는 대신 gap을 보고한다. module docstring에 interpretation이 쌓이는 것은 대응할 가치가 있는 smell이다. 각각은 contract에 문장 하나가 필요한 지점이다.

### 존재 이유

닫힘이 없으면 field name이 drift하고 모든 consumer에 synonym table이 필요해진다. 두 record가 동일한 정보를 같은 key의 서로 다른 두 spelling으로 담는다. 한 spelling을 query하면 corpus의 절반만 찾고, 찾지 못한 절반은 보이지 않는다. 각 spelling은 따로 보면 올바르게 보이므로 아무도 알아차리지 못한다. 비용은 미래의 모든 consumer에게 영구히 전가되고 누적된다. 누군가 첫 두 spelling을 grep한 뒤 field가 optional이라고 결론 내리기 때문에 세 번째 spelling이 생긴다.

fail-closed classifier가 없으면 문서가 자신의 class를 선언하고 이미 만족하는 rule을 가진 class를 고른다. 이는 부정직이 아니라 저항이 가장 적은 경로이며, class membership을 문서 자체가 아니라 편의에 관한 statement로 만든다.

byte-verbatim carve-out이 없으면 strict parser는 다음 round-trip에서 인용된 human text를 조용히 다시 쓴다. schema 메커니즘이 protection 메커니즘을 무너뜨리는데 어디에서도 error가 나지 않는다.

### 도입 방법

- class decision list를 ordered rule로 작성하고 맨 아래에 명시적인 no-match error를 둔다.
- class별 field table을 code branch가 아니라 data에 둔다. 편집하게 될 것은 table이고, 편집하기를 잊게 될 것은 branch다.
- unknown key를 reject한다. 알려진 legacy key는 이름으로 감지하고 *unknown*이 아니라 *migration needed*로 보고한다. 둘의 차이가 고칠 수 있는 finding과 이해하기 어려운 finding을 가른다.
- parse 전에 protected literal block을 추출하고 정확히 하나의 block shape만 허용한다.
- schema가 corpus 준수보다 먼저 landing할 수 있도록 첫날부터 legacy-acceptance flag를 제공한다.
- negative case와 out-of-jurisdiction case를 포함한 boundary fixture로 classifier를 고정한다.

### 변경할 때

synonym-table 비용을 받아들이고 near-duplicate key name을 드러내는 주기적 field-census check를 추가하면 열린 schema도 작동할 수 있다. 대체 메커니즘이 무엇이든 세 가지는 보존해야 한다. unknown key가 silence가 아니라 *finding*을 낸다. 문서가 declaration이 아니라 rule에 따라 정확히 하나의 class로 결정된다. class별 field requirement를 validator code를 읽지 않고도 사람이 읽을 수 있는 data로 선언한다.

### 의존 대상 / 없을 때 파손되는 조건

- **E2** — strict parser와 schema는 같은 module이다. 분리하면 두 구현이 문서란 무엇인지에 대해 불일치한다.
- **E5** — byte-verbatim pre-extraction은 schema validation이 protected text를 건드리지 못하게 하려고 존재한다. E5의 extractor 정의가 없으면 carve-out에 boundary가 없다.
- **A2** — classifier의 jurisdiction, 즉 애초에 어느 path를 분류할지는 registry declaration이다. classifier jurisdiction 밖의 path는 단지 unmatched되어서는 안 되고 *out of jurisdiction으로 등록*되어야 한다. 그렇지 않으면 "분류되지 않음"과 "발견되지 않음"이 같은 상태다.
- **F7** — 닫힌 field set은 field마다 spelling이 하나라고 전제한다. working language가 English가 아닐 때 metadata key를 English로 고정하는 axis가 이 전제를 지킨다. 이것이 없으면 working language로 된 key가 들어오고 닫힌 집합은 unknown으로 reject하며, key를 고치는 대신 집합을 열라는 압력이 생긴다.

---

## E5 — Protected span

**Tier: CORE.** 사람이 실제로 쓴 text는 저장소에서 재생성할 수 없는 유일한 artifact다. 이를 손상시키는 메커니즘은 evidence를 파괴하며, 위의 모든 evidence 기반 메커니즘은 verbatim record가 실제로 verbatim이라는 데 의존한다.

### 정의

structural extractor가 tree에서 사용자가 작성한 원문을 담는 모든 region을 열거하고, mechanical operation 중 그 region의 byte를 불변으로 유지한다. protection은 heuristic이 아니라 *recognized carrier*로 정의한다.

- 어느 문서에서든 verbatim content용으로 예약된 이름 붙은 frontmatter key. top-level block literal과 single-line scalar라는 두 shape를 인식한다. 해당 key에서 다른 shape가 나오면 raise한다.
- user-feedback record의 quotation payload. recognized carrier는 reserved frontmatter key, marker word를 case-insensitive하게 포함하는 heading(날짜 및 suffix 변형 포함)이 있는 verbatim-marked section 중 body에 fenced block이나 blockquote run이 있는 것, 또는 둘 다다. 인식 가능한 carrier가 없는 record는 실패한다.
- archived conversation file의 모든 blockquote run과 모든 fenced block. prompt text가 그 방식으로 보존되기 때문이다. blockquote가 하나도 없거나 끝나지 않은 fence가 있는 conversation file은 실패한다.

이 모든 실패는 skip이 아니라 **abort**다. unknown layout은 extractor가 protected byte의 위치를 모른다는 뜻이며, 계속하면 human text 내부에서 substitution이 일어난다. fail-closed가 이 태도의 전부다.

over-protection은 의도적이다. 우연히 quotation이나 fence 안에 놓인 agent 작성 text도 보호하며 이를 받아들인다. false positive는 나중 pass가 찾아낼 수 있는 stale string을 남길 뿐이지만, false negative는 사람이 쓴 말을 다시 써서 artifact만으로는 복원할 수 없게 하기 때문이다.

immutable input 계층에는 protection보다 더 강한 규칙이 적용된다. **아예 processing하지 않는다.** caller가 그 path 중 하나를 넘기기만 해도 extractor가 raise한다. "protected"는 도구가 검사했지만 그대로 두었다는 뜻이고, "never processed"는 도구가 실수할 기회 자체가 없다는 뜻이다. immutable input에는 두 번째를 적용한다.

extractor가 만든 exclusion-zone 정의는 공유한다. prose check, link check, naming check는 모두 substitution driver와 동일한 정의를 읽고 protected span을 jurisdiction 밖으로 취급한다. 정의 하나, consumer 여러 개다.

### Bulk-substitution 절차(이 하위 부분은 `OPTIONAL`)

**Precondition:** protected span을 포함한 tree 전체에서 body-text reference까지 포함하여 identifier를 rename하거나 path를 move해야 한다.

choreography — **freeze → map → protect → apply → verify → thaw**:

1. **Freeze.** clean tree의 base commit을 고정하고 hash를 mapping table에 bind한다. mapping table은 그 frozen tree만으로 재생성할 수 있어야 하고 regeneration은 idempotent해야 한다. freeze 뒤에 발급된 것은 *cargo가 아니다*. count guard는 live total이 아니라 mapping table의 cargo를 기준으로 계산해야 한다.
2. **Map.** 모든 item의 old→new를 set hash에 bind된 파일로 만든다. ambiguous adjudication은 별도 table로 분리하고 *그 table의 byte hash*를 mapping table에 embed한다. judgment의 reproducibility가 judgment를 assertion이 아니라 evidence로 만든다.
3. **Protect.** 어떤 것도 건드리기 전에 모든 protected span을 추출하고 byte signature를 기록한다. unknown layout은 campaign을 abort한다. substitution 뒤 모든 signature를 비교한다.
4. **Apply.** 실행 자체의 artifact를 tree 밖에서 만들고 실행한 뒤 artifact를 commit으로 들여온다. 그러면 mapping table의 hash가 실행이 곧 수정할 파일을 포함하는 self-hash cycle을 피할 수 있다. 먼저 dry-run하고 target count, substitution count, protected-span violation 0개, fixpoint violation 0개라는 네 숫자를 assert한다. bulk rewrite는 명시적인 human approval gate를 통과해야 한다.
5. **Verify.** frozen commit으로부터의 idempotent regeneration, category별 total, 전체 reference resolution, validator failure 0개를 확인한다. Verify, inspect, commit은 서로 분리된 세 행위로 수행한다.
6. **Thaw.** state-machine flip은 별도 commit으로 만들고, 이어서 모든 gate와 success path의 live exercise 한 번을 수행한다. working file을 버리기 전에 evidence table과 hash를 durable receipt로 promote한다.

**Pitfall ledger — 아래의 모든 항목은 가설이 아니라 측정된 것이다.**

- **Tool self-contamination.** substitution driver가 자신의 input, 즉 자신의 fixture, override table, adjudication table을 다시 쓴다. 한 campaign에서 서로 다른 세 번 발생했다. 도구, fixture, evidence file을 substitution universe에서 명시적으로 제외하고 진행하는 동안 byte-hash gate로 evidence file을 감시한다.
- **Restore-then-checkout.** contaminated file을 고친 뒤 commit 전에 checkout을 실행하면 contaminated index copy로 되돌아간다. repair를 즉시 commit하거나 index를 update한다.
- **Undeclared hash universe.** set hash는 *무엇의 집합인지*에 대한 declaration에 bind되어야 한다. freeze가 풀리면 새로운 issuance가 destination 쪽 total을 부풀리고, filter하지 않은 count guard는 파괴된다.
- **Stem-set blind spot.** 한 move에 서로 다른 path에서 같은 name stem을 공유하는 item이 여럿 있으면 stem-set guard가 개별 손실을 숨긴다. cargo를 path별로 bind한다.
- **Case-only renames.** case-insensitive filesystem에서는 capitalization만 바꾸는 rename에 관해 existence test와 version-control detection이 불일치한다. case-exact comparison을 사용한다.
- **Post-move check semantics.** "live source 쪽과 비교한다"라고 표현한 check는 move 전까지만 유효하다. move 뒤에는 table에 embed된 hash와 비교하도록 semantics를 고쳐야 한다. 그렇지 않으면 완전히 정직한 declaration이 실패하고 누군가 check를 disable한다.
- **Document the exclusion list itself.** code fence, inline span, frontmatter, historical verbatim, fixture shadow는 judgment universe에서 제외하며 exclusion rule을 문서화한다. 문서화되지 않은 exclusion은 bug와 구별할 수 없다.

규모를 가늠할 기준으로, 약 400개 파일을 rename하고 약 2,000개의 body substitution을 수행했으며 protected-span violation은 0개였다. campaign 하나, 프로젝트 하나의 수치다.

### 존재 이유

사람이 작성한 quotation이 있는 저장소에서 mechanical substitution을 충분히 많이 실행하면 그중 하나를 결국 다시 쓰게 된다. rewrite는 작다. 누군가 입력한 문장 안의 rename된 identifier 하나 정도이며, 손상된 text도 well-formed이고 그럴듯하므로 사후에 탐지할 수 없다. evidence chain의 전체 가치는 verbatim record가 사용자가 실제로 말한 것이라는 주장에 달려 있다. 조용한 substitution 하나만 있어도 어느 record가 건드려졌는지 알 수 없으므로 그 주장은 모든 곳에서 거짓이 된다.

unknown layout에서 skip 대신 abort하는 이유는 skip 자체가 실패이기 때문이다. skipped file은 driver가 protected region의 위치를 모른 채 substitution한 파일이다. "protected span을 찾지 못했으므로 계속했다"는 태도는 정확히 거꾸로이며, 이 규칙 없이 작성한 code가 자연스럽게 취하는 동작이다.

### 도입 방법

- carrier를 명시적으로 열거한다. heuristic으로 protected text를 탐지하지 말고 이를 담는 key, heading, file class를 선언한다.
- 인식할 수 없는 shape가 있으면 raise한다. exception type을 구별하여 caller가 일반 parse error와 함께 삼키지 못하게 한다.
- 위험해 보이는 pass만이 아니라 모든 mechanical pass에서 사전에 byte signature를 추출하고 사후에 비교한다.
- immutable input 계층은 아예 processing을 거부한다. caller가 아니라 extractor에서 이를 강제한다.
- 이 module이 exclusion zone을 publish하여 prose check와 link check가 동일한 정의를 사용하게 한다.
- 이를 촉발한 campaign이 끝난 뒤에도 extractor를 permanent module로 유지한다. one-shot driver는 version-control history로 retire할 수 있지만 extractor는 상시 asset이다.

### 변경할 때

일괄 rename을 전혀 하지 않는 프로젝트에는 bulk-substitution 절차가 필요 없으므로 `OPTIONAL`이다. 대체물을 만든다면 frozen base commit과 mapping의 binding, live가 아니라 cargo 기반인 count guard, operation 전후 byte-signature 비교, unknown layout에서의 abort, substitution universe에서 driver 자체 input 제외, verify / inspect / commit의 세 가지 분리된 행위를 보존해야 한다. 어느 하나라도 빼면 campaign의 guarantee는 claim으로 전락한다.

byte-immutability core는 대체할 수 없다. 달라질 수 있는 것은 corpus에 존재하는 carrier의 종류다.

### 의존 대상 / 없을 때 파손되는 조건

- **A1** — protection은 immutable input이 *선언된 계층*임을 전제로 한다. provenance split이 없으면 어떤 text가 human-authored인지에 원칙적인 답이 없고 protection은 파일별 판단이 된다.
- **B1** — verbatim user-feedback record가 주된 protected carrier다. event chain이 없으면 보호할 것이 훨씬 적어지고 이 메커니즘의 tier는 실제로 내려간다.
- **E2** — false-positive exclusion rule은 이 extractor의 zone definition에 의존한다. protected의 정의가 둘이면 prose check와 substitution driver가 어느 byte를 건드릴 수 없는지에 대해 불일치한다.
- **E4** — schema validation이 protected text를 normalize해서는 안 된다. 그래서 parse 전에 block literal을 verbatim으로 pre-extract한다.

---

## F1 — Canonical 절차 → adapter 생성

**Tier: CORE.** 여러 도구는 각자 다른 위치에서 절차를 load하므로 generation과 drift check가 없으면 도구들이 조용히 갈라지고, "그 절차"를 따르는 agent들이 서로 다른 절차를 따르면서도 모두 같은 절차를 따른다고 믿게 된다.

### 정의

절차마다 canonical specification 하나를 단일 directory에 둔다. sync script가 각 canonical file을 모든 도구의 예상 위치로 copy한다. script에는 두 mode가 있다. `sync`는 deploy하고 `check`는 배포된 모든 copy를 canon과 diff하여 차이가 있으면 실패한다. `check` mode는 validator *내부에서 subprocess로* 실행되므로, drift는 따로 기억해야 하는 의식이 아니라 다른 모든 것과 같은 gate에서 탐지된다.

두 세부 사항이 대부분의 역할을 한다.

**deployment는 directory glob이 아니라 선언된 exact set으로 한정한다.** script는 배포할 procedure name을 열거한다. canon 옆에 있지만 집합에는 없는 file은 절대 배포하지 않는다. 원본 프로젝트에서는 input-format handling을 문서화하는 reference annex가 procedure spec 옆에 있지만 의도적으로 procedure로 배포하지 않는다. agent가 workflow로 routing받을 문서가 아니라 reference material이기 때문이다. glob은 이를 배포하고, agent는 결국 procedure인 것처럼 실행할 것이다.

**현재 copy는 byte-identical하며, 더는 그렇지 않게 되는 순간 difference를 generator에 넣는다.** 한 도구가 다른 frontmatter를 필요로 하게 되면 script에 명시적인 tool별 adapter 단계를 두어 고친다. generated file을 직접 편집해서는 안 된다. hand edit는 바로 drift check가 보고하는 대상이고, 편집자는 이어서 drift check를 더 조용하게 만들고 싶은 유혹을 받게 된다.

**F1과 A4는 서로 다른 scope에 적용한 같은 원리다.** 이름 붙은 canonical source 하나 → mechanical generation → validator 실행에 wiring된 drift check라는 구조다. A4는 marker로 경계를 정한 *hand-owned file 내부 region*을 생성하고 주변 prose는 사람이 유지한다. F1은 whole file을 생성한다. invariant는 동일하다. generated thing은 절대 edit point가 아니며, generator는 idempotent하고, drift check는 optional이 아니다. 이 대칭을 도입자에게 명시하라. 이를 알아보면 서로 다른 메커니즘 둘을 구현하는 대신 한 pattern을 두 번 구현할 수 있다.

### 존재 이유

절차를 고치라는 요청을 받은 agent는 자기 도구가 load한 copy를 편집한다. context에 들어 있는 데다 도구가 기대하는 정확한 위치에 있는 완전하고 올바르게 보이는 procedure document이므로 authoritative해 보이기 때문이다. canon은 stale한 채 남는다. 그러면 두 결과 중 하나가 생긴다. 다음 sync가 fix를 조용히 되돌리고 나중 agent가 같은 bug를 다시, 또다시 고친다. 또는 sync가 실행되지 않아 두 tool copy가 갈라지고, 같은 저장소의 두 agent가 실질적으로 다른 절차를 따르면서도 둘 다 canon을 따른다고 믿는다. 각 agent의 위치에서는 비교할 대상이 없으므로 어느 쪽도 알아차리지 못한다.

scope 실패는 별개이며 더 조용하다. glob 기반 deployment는 canon 옆의 모든 file을 배포한다. reference material, draft, annex가 모두 invoke 가능한 procedure가 된다. file이 well-formed이므로 아무것도 error를 내지 않고 agent는 따르도록 만든 적 없는 문서를 따른다.

### 도입 방법

- canonical directory는 하나만 둔다. generated location은 절대 edit point가 아니며 generator 맨 위 comment에 그렇게 적는 두 줄은 충분히 가치가 있다.
- `sync`와 `check` mode가 있는 generator를 두고 drift 시 non-zero로 exit한다. failure message는 drift한 file과 일치해야 할 canon을 모두 지목하고, 가능한 두 fix(regenerate하거나 의도한 edit를 canon으로 이동)를 알려야 한다.
- `check`를 validator 실행에 wiring한다. 누군가 따로 기억해야 하는 command에 넣지 않는다.
- deployment set을 명시적으로 선언한다. canon 옆의 file을 배포하면 안 된다면 어떤 field가 다르기 때문이 아니라 집합에 없어야 한다.
- missing canonical source는 skip이 아니라 hard error로 다룬다.

### 의존 대상 / 없을 때 파손되는 조건

- **E1** — drift check의 가치는 실행 시점만큼만 존재한다. wiring되지 않으면, 알려 줬어야 할 drift를 누군가 이미 알아차린 뒤 실행하는 command가 된다.
- **A4** — 동일한 pattern이다. 두 메커니즘은 vocabulary와 failure-message style을 공유하여 저장소에서 "drift"가 한 가지 뜻만 갖게 해야 한다.
- **F2** — routing table은 canonical procedure의 frontmatter에서 생성된다. canon이 단일 edit point가 아니면 routing table은 어떤 도구도 실제로 load하지 않는 문서를 index한다.

---

## F2 — Trigger-routed 절차

**Tier: DEFAULT.** discoverability는 다른 방식으로도 얻을 수 있지만, *상황*으로 index되지 않은 procedure library는 발견되지 않고 다시 발명된다.

### 정의

각 procedure는 자체 frontmatter에 **trigger condition sentence** list, 즉 "이러이러한 상황이 발생할 때" 형식의 완전한 문장과 status 및 bind할 tool을 선언한다. generated routing table은 그 field만으로 derive한다. procedure마다 link, trigger, status, bound tool을 담은 row 하나를 만든다. table은 update owner로 generator를 명시하고 hand-editing을 금지한 generated view다(A4 적용).

table을 catalogue에서 router로 바꾸는 규칙은 항상 load되는 entry document에 있는 문장 하나다. **task가 procedure trigger와 match하면 그 procedure를 따른다.** 이 문장이 없으면 table은 보기 좋은 list다. 있으면 matching은 의무가 된다.

trigger sentence는 topic이 아니라 situation으로 작성한다. "사용자가 작성한 text를 byte-for-byte로 보존하면서 저장소 전체에서 identifier를 rename해야 할 때"는 trigger다. "Migration"은 topic이어서 쓸모가 없다. agent는 아직 자신이 migration 중임을 모르며, 어떤 것들의 이름을 바꾸라는 요청을 받았다는 것만 알기 때문이다.

### 존재 이유

procedure가 쌓이면 어느 수를 넘어선 뒤 아무도 무엇이 있는지 모르게 된다. procedure의 존재를 모르는 agent는 이를 다시 발명한다. 잘못되고 매번 다른 방식으로 말이다. 구체적인 손실이 가장 나쁘다. 성숙한 procedure의 가치는 pitfall ledger, 즉 잘못된 일과 그에 따라 추가된 guard의 누적 list에 집중된다. 재발명에는 정확히 그 ledger가 없으므로 같은 pitfall을 같은 순서로 겪고 두 번째 통과에도 첫 번째만큼 비용이 든다.

topic 기반 organization은 이를 고치지 못한다. discovery가 반대쪽 끝에서 일어나기 때문이다. agent는 자신의 situation을 알지 그 situation이 속한 topic은 모른다. situation을 기준으로 index하면 query와 같은 vocabulary로 index하게 된다.

### 도입 방법

- trigger를 procedure 자체 frontmatter에 condition sentence list로 넣는다. edit point는 하나다.
- routing table을 생성하고 절대 손으로 유지하지 않는다. retired procedure가 조용히 사라지지 않고 listed된 채 visibly retired 상태로 남도록 status를 포함한다.
- binding sentence를 항상 load되는 entry document에 추가하고 suggestion이 아니라 obligation으로 만든다.
- tool도 frontmatter에서 bind한다. procedure를 발견한 agent가 같은 row에서 script도 발견해야 한다.
- 아직 자신이 무엇을 하는지 모르는 사람의 관점에서 trigger를 작성한다.

### 변경할 때

정직한 규모 주의사항: 원본 프로젝트에는 routed procedure가 6개 있었다. 이 규모에서 generated routing table은 거의 필요하지 않다. 이 메커니즘의 가치는 성장에 대해 주장된 것이지 load 아래에서 측정된 것이 아니다. procedure가 한 줌보다 적다면 hand-written list로 충분하다.

search-indexed procedure library나 도구 자체가 situation을 procedure description과 match하는 tool-native routing 같은 대체물도 세 속성을 보존해야 한다. trigger가 procedure와 함께 있어 edit point가 하나여야 한다. routing view는 유지되는 것이 아니라 생성되어야 한다. trigger match가 procedure를 단지 읽는 것이 아니라 따를 의무를 부여하는 binding instruction이 있어야 한다.

### 의존 대상 / 없을 때 파손되는 조건

- **F1** — trigger는 canonical procedure spec에 있다. canon이 단일 edit point가 아니면 routing table은 아무도 load하지 않는 문서로 routing한다.
- **A4** — routing table은 generated view이므로 marker-and-drift discipline이 필요하다. 그렇지 않으면 늘 하던 대로 stale해진다. 누군가 row를 손으로 추가하고 generator가 overwrite하며, row는 error 없이 사라진다.

---

## F3 — Onboarding discipline과 doc-gap loop

**Tier: DEFAULT.** 구체적인 세 문서 분리는 작동 가능한 구성 하나일 뿐이지만, entry document는 durable mechanism을 설명하고 discovery failure는 불편이 아니라 evidence라는 기본 규칙이 문서의 부패를 막는다.

### 정의

**역할이 엄격히 분리된 세 entry document.**

- *principles guide* — newcomer가 가장 먼저 읽는 문서다. core operating model, quick start, 대표 scenario 몇 가지를 담는다. principle 수준만 다룬다.
- *operating map* — 항상 load되는 contract document로, situation → contract routing table을 담는다. row에는 "이 상황에서는 먼저 이 canon을, 다음으로 저 canon을 참조한다"고 적는다. rule body를 절대 복제하지 않고 상황별 pointer를 정리한다.
- *capability manifest* — 저장소가 할 수 있는 모든 것에 관한 완전한 discovery map으로, 모든 capability와 모든 directory role을 **복제가 아니라 link를 통해 두 hop 이내에** 도달할 수 있다고 약속한다.

**boundary clause가 세 문서가 세 개의 stale document가 되는 것을 막는다.** 각 문서는 자신이 *담지 않는 것*을 선언한다. capability manifest는 capability와 usage path만 열거하고 structure를 재진술하지 않는다. structure는 registry의 역할이고, operating map의 역할은 operating model이며, principle은 guide의 역할이다. entry document 사이의 overlap은 drift를 만드는 메커니즘이다. 겹치는 fact가 한 곳에서만 update되기 때문이다.

**같은 exclusivity를 한 단계 아래의 모든 directory에도 적용한다.** 위 clause는 top-level entry document 세 개를 지배한다. 그 아래 directory에는 보통 guide와 manifest라는 자체 file 두 개가 있고, 각각을 따로 정의하는 대신 *서로에 대비하여* 정의한다. guide는 그 directory를 위한 guide, 즉 무엇을 위한 곳이며 어떻게 작성하는지를 다루고 그 외에는 다루지 않는다. manifest는 directory가 소유한 item, 그 state, 바깥으로 향하는 pointer를 열거하며, update owner가 명시되어 있다는 precondition 아래 작동한다(A4가 그 부분을 소유하므로 여기서 재진술하지 않는다). 따로 정의하면 각각 다른 쪽으로 drift한다. guide에는 작성 당일에는 맞지만 한 달 뒤에는 틀릴 불완전한 item list가 쌓이고, manifest에는 설명이 쌓여 독자가 두 문서 중 어느 것이 directory content의 정본인지 구별할 수 없게 된다. 두 문제를 막는 규칙은 각 file에 다른 file이 무엇을 담는지 명시하는 한 문장이다.

**changelog를 두지 않는다.** entry document는 durable mechanism 수준에 머문다. 국소적인 fix, 일회성 formatting technique, migration history는 명시적으로 제외한다. 그것들은 evidence chain과 procedure에 속한다. entry document는 어떤 것이 고쳐질 때가 아니라 core mechanism이 바뀔 때 update한다.

**이름 붙은 update owner**를 둔다. 원본은 복제할 가치가 있는 방식을 사용한다. capability manifest의 owner는 사람이나 script가 아니라 *contract clause*다. owner field는 doc-gap duty 자체를 가리킨다. 불완전함을 발견한 누구나 이를 고쳐야 한다는 규칙이 문서를 유지한다. generated section에는 generator라는 두 번째 owner가 있으며 file은 mixed-mode다.

**doc-gap loop.** 일반 작업 중 entry document에서 발견할 수 *있었어야 하지만* 찾을 수 없었던 fact, 예를 들어 directory role, capability, usage path를 사용자나 agent가 필요로 했다면 이는 gap이다. 그때 한 가지가 아니라 세 가지를 수행한다.

1. 명백한 local repair를 즉시 적용한다. missing role이나 entry point를 추가한다.
2. gap을 evidence chain에 기록한다. 사용자가 말했다면 verbatim으로, 그렇지 않다면 observation으로 기록한다.
3. structural 또는 contract-level gap이면 proposal을 열고 review cycle로 보낸다. contract 변경은 approval 뒤에만 적용한다.

### 존재 이유

모든 도입자가 물을 질문은 **그냥 고치고 넘어가면 왜 안 되는가**이며, 답은 두 부분이다.

local repair는 symptom을 고치고 evidence를 파괴한다. recurrence는 "독자 한 명이 주의 깊게 찾지 않았다"와 "이 entry document의 shape가 틀렸다"를 구별하는 유일한 signal이며 promotion ladder는 rule을 정당화하기 전에 recurrence count를 필요로 한다. fix-and-move-on을 따르면 이후 모든 독자가 같은 gap을 영원히 다시 발견하고, 각자 local fix를 하면서 아무 trace도 남기지 않는다. 저장소가 같은 discovery를 수십 번 받아들이고도 보여 줄 것이 전혀 없을 수 있다.

둘째, 그 순간 명백하게 느껴지는 repair는 거의 언제나 *table에 row 하나 더 추가하기*다. 세 번 반복되는 gap은 보통 table이 잘못된 shape라는 뜻이다. 독자가 table의 조직 기준과 다른 dimension으로 lookup하고 있는 것이다. record가 없으면 이를 볼 수 없어 계속 row를 추가하고, 각각의 추가는 올바르게 보였지만 table은 쓸모가 없어질 때까지 커진다.

설계상의 가치는 loop가 **새 machinery를 추가하지 않는다**는 데 있다. 기존 evidence chain과 promotion ladder를 재사용한다. 새로운 store도, workflow도, 기억할 discipline도 없다. 별도의 doc-quality process였다면 가장 먼저 버려졌을 것이므로 바로 이 점 때문에 살아남는다.

### 도입 방법

- entry document를 역할별로 분리하고 각 문서에 boundary clause를 작성한다. 모든 entry document에는 자신이 다루지 않는 것과 그 내용이 있는 곳을 명시한 문장이 있어야 한다.
- directory마다 같은 pair rule을 적용한다. 해당 directory만 다루는 guide, 열거하고 가리키는 manifest, 그리고 서로의 역할을 명시하는 문장을 각각에 둔다.
- reachability promise를 숫자(two hops)로 명시하여 "manifest가 완전한가?"를 검사 가능한 질문으로 만든다.
- changelog content를 entry document에서 금지한다고 명시하고 그 content가 대신 갈 곳도 밝힌다. 목적지 없는 금지는 압력을 옮길 뿐이다.
- 각 entry document의 update owner를 명시한다. contract clause는 적법한 owner지만 "the team"은 아니다.
- 항상 load되는 문서에 세 부분의 doc-gap response를 작성하며, *record* 단계는 optional이 아니고 repair만으로 충족되지 않는다고 명시한다.
- approval gate를 보존한다. loop는 entry document를 조용히 restructure할 권한을 주지 않는다.

### 변경할 때

대체물은 다음을 보존해야 한다. entry document가 overlap하지 않는다. 완전성 promise가 검사 가능하다. incident history가 쌓이는 것을 금지하는 명시적 규칙이 있다. discovery failure가 단순한 fix가 아니라 durable record를 만든다. 문서 수와 hop count는 프로젝트가 정할 수 있다.

### 의존 대상 / 없을 때 파손되는 조건

- **B1** — record 단계는 event chain에 쓴다. 이것이 없으면 "gap을 기록한다"에는 destination이 없고 loop는 fix-and-move-on으로 되돌아간다.
- **B3** — promotion ladder는 기록된 gap 세 개를 structural change로 바꾼다. promotion path 없는 기록은 아무도 읽지 않는 archive를 만든다.
- **A4** — manifest에는 generated section이 있어 mixed-mode다. 같은 marker-and-drift discipline을 적용한다.
- **D3** — entry document에 대한 structural repair는 다른 contract 변경과 똑같이 approval sequence를 거친다.

---

## F4 — Volatile workspace 계층

**Tier: OPTIONAL.** Precondition: 여러 session에 걸치며 확정되지 않은 design question과 실행 가능한 task가 섞인 work unit이 있다. 하네스는 이것 없이도 완전하다. evidence chain만으로 전체 workflow를 수행할 수 있으며, 이는 특정 형태의 작업을 위한 management optimization이다.

그 subsidiarity statement 자체도 이식할 가치가 있다. 계약 자체에서 계층을 optional로 선언하고 그것이 없을 때 시스템이 무엇을 하는지 밝히면, 다음 독자가 optional 계층을 mandatory로 취급하지 않는다.

### 정의

큰 work unit마다 volatile workspace(원본에서는 "camp") 하나를 두며 여섯 요소를 담는다. goal과 resume procedure가 있는 manifest, *departure* ledger, open question별 file 하나, 근거를 verbatim으로 담은 settled decision별 file 하나, work item별 file 하나, drafts area다.

**state canon은 file location과 frontmatter이며 manifest에 절대 복제하지 않는다.** workspace를 *떠나는* item만 ledger row를 얻고 existence, final state, destination을 기록한다. resident item은 directory 자체가 추적한다. 이 한 규칙이 ledger가 workspace state의 두 번째 diverging copy가 되는 것을 막는다.

**Question→decision conversion.** question에 답이 생기면 그 file은 다음 decision number로 *convert*되어 이동하며 origin pointer가 question identity를 보존한다. questions directory에는 copy를 남기지 않는다. question number와 decision number는 독립적으로 증가한다.

**local id는 global event sequence와 구조적으로 분리한다.** workspace item id는 짧고 workspace-local이며 owning session만 발급한다. 별도 counter 없이 resident file과 ledger 전체에서 max-plus-one으로 derive하고 single-owner assumption 아래에서만 유효하다. workspace는 close할 때 삭제되므로 그 id는 절대 permanent reference가 되어서는 안 된다. promotion할 때 workspace decision은 globally issued number가 있는 실제 event로 *regenerate*한다. event로 rename하지 않는다.

**Ownership.** workspace manifest는 owner session key를 선언한다. 다른 session은 active workspace를 read-only로 취급한다. 자유롭게 reference하되 절대 modify하지 않으며, 자신의 작업이 scope와 겹치면 사용자에게 escalate한다. successor session은 resume procedure를 수행한 뒤 해당 workspace에 대한 첫 write commit에 ownership update를 함께 담는다. 그 commit이 *handover declaration*이며 그 전에는 아무것도 modify할 수 없다.

하나의 원칙, 즉 떠나는 file은 남겨 두지 않고 management를 transfer한다는 원칙 아래에 **두 가지 mid-life optimization**이 있다.

- *Consume*: 별도 작업이 필요 없고 다른 session에 필요하며 지금 action할 수 있는 item은 도중에 convert하여 permanent layer로 올려 보낸다. completion은 rule이 in force라는 뜻이다. 항상 load되는 entry document에 wiring이 필요한지 판단하고 필요하면 수행하는 것도 포함한다.
- *Spin-off*: 서로 합의된 work cluster가 남은 open question과 mutually exclusive하면 provenance pointer와 명시적인 scope boundary가 있는 자체 workspace가 되어 parallel 실행할 수 있다.

이 경우 commit binding은 *file type이 아니라 provenance*를 따른다. promote된 document, original 제거, 그 item에서 derive된 entry-document wiring은 모두 하나의 commit에 속하며, history는 각 edit가 어느 item에서 왔는지 보여 준다. shared bookkeeping은 자체 unit으로 close한다.

**Close.** residue는 고정 mapping에 따라 convert한다. contract에 영향을 주는 decision은 permanent event가 되고, unresolved question은 deferred-queue entry가 되며, adopted design은 canonical home으로 이동한다. execution tracking은 promote하지 않고 closing receipt에 summarize한다. close gate는 local id에서 promoted location으로 가는 *drain map*을 만들고, live normative document가 promotion을 가리키도록 다시 쓰며, historical reference는 그대로 둔다. 그리고 **live normative document에서 workspace를 가리키는 남은 reference가 0개**여야 하며 scan universe는 workspace가 아니라 저장소 전체다.

### 존재 이유

그렇지 않으면 여러 session에 걸친 structural work는 state를 conversation에 보관한다. session이 끝나면 successor는 합의된 question을 다시 논의하거나, 더 나쁘게는 조용히 뒤집는다. message로만 존재하는 decision에는 location이 없어 누구도 내려진 결정인지 확인할 수 없기 때문이다.

numbering separation이 막는 실패는 구체적이고 관찰되었다. workspace-local id가 permanent document로 샌다. workspace가 존재하는 동안에는 실제 identifier처럼 보이고 resolution도 잘 된다. close 때 workspace를 삭제하면 이 reference들은 모두 dangling이 되어, 단순히 존재하지 않을 뿐 아니라 존재하지 않도록 설계된 무언가를 가리킨다. drain map과 zero-live-references close gate는 이 cleanup이 optional이 아니며 저절로 일어나지 않기 때문에 존재한다.

### 변경할 때

Precondition을 다시 말한다. work unit이 session 하나에 들어간다면 이것을 전부 생략하라. 대체물은 다음을 보존해야 한다. state는 conversation이 아니라 file에 산다. workspace id를 permanent id로 오인할 수 없다. close 시 정의된 conversion mapping이 있다. close gate가 살아 있는 어떤 것도 삭제될 workspace를 가리키지 않는지 검증한다.

### 의존 대상 / 없을 때 파손되는 조건

- **B2** — local numbering과 global numbering의 분리 자체가 메커니즘이다. 분리할 global issuance discipline이 없으면 local id가 permanent document로 drift하고 close gate는 강제할 대상이 없다.
- **C1, C3** — workspace ownership은 session isolation과 session-per-work-unit boundary를 전제한다. 이것이 없으면 "owning session"은 아무것도 식별하지 못한다.
- **B1** — close mapping의 destination은 permanent event store다. 이것이 없으면 close 시 promote할 곳이 없고 workspace는 permanent가 되거나(목적을 무너뜨림) 사라진다.
- **A4** — departure ledger는 manifest이며 manifest discipline을 따른다.

---

## F5 — Profile composition

**Tier: OPTIONAL.** Precondition: input 특성에 따라 올바른 shape가 달라지는 한 family의 artifact를 많이 생성하여, 고정 template가 유용하기에는 너무 느슨하거나 input의 상당 부분에 틀린 경우다.

### 정의

output은 template로 찍는 것이 아니라 compose한다.

```
artifact = core contract + shape profile + presentation profile + confirmed user override
```

core contract는 해당 family의 모든 artifact가 만족해야 할 requirement를 담는다. shape profile은 input이 *구조적으로 무엇인지*에 따라 선택한다. presentation profile은 결과의 layout을 지배한다. user override는 확인된 경우에만 적용한다.

**axis orthogonality가 실질적 주장이다.** input이 *무엇에 관한 것인지*와 *어떤 shape인지*는 독립적이며, subject matter만으로 structure를 선택해서는 안 된다. 세 번째 axis인 consumer가 artifact를 어떻게 사용할지는 명시되었을 때만 적용하고, 추론한 purpose를 input에 관한 fact처럼 기록해서는 안 된다.

**profile은 config가 아니라 versioned artifact다.** 각 profile은 integer version, status, selection signal("input이 이런 특성을 지니면 이것을 선택한다"), core contract 위에 추가하는 structure, 어느 presentation profile을 기본값으로 삼는지에 관한 note, **known exception**("input이 실제로 X라면 profile Y를 대신 사용한다"), bump마다 한 line이 있는 version history를 담는다. known-exceptions section은 가치가 가장 크지만 도입자가 생략하는 부분이다. profile set을 menu가 아니라 decision procedure로 유지하기 때문이다.

**profile이 structure가 아니라 prose를 지배하는 경우 paired-example ledger를 붙이고 작성 전에 반드시 읽게 한다.** register profile은 rule을 정확히 명시하고도 그 뒤의 judgment를 전달하지 못할 수 있다. rule이 degree, 즉 hedging이 어느 정도면 지나친지, metaphor가 언제부터 역할을 하지 못하는지에 관한 것이며 degree에 관한 문장은 경계가 어디인지 알려 주지 못하기 때문이다. matched pair ledger는 알려 준다. reject된 passage, accepted revision, 그 사이에서 무엇이 변했는지에 관한 한 line을 담는다. profile과는 별도 asset이다. 서로 다른 rule로 자라기 때문이다. 각 pair는 실제 disagreement였을 때만 들어갈 자격을 얻으므로 ledger는 누적 record인 반면 profile은 versioned standard다. 핵심은 *언제* 참고하는지다. composition procedure의 한 단계로서 writing 전에 읽는다. review 때까지 미루면 judgment가 이미 contest된 경우에만 읽는 appeals file이 되며, writing cost를 이미 지불했고 author에게는 방어할 대상까지 생긴 뒤다.

**generated artifact는 어떤 profile과 version이 자신을 만들었는지 기록하며**, machine-readable field로 기록하고 validator가 check한다. declared profile은 registry에 존재해야 하고(error), version이 없으면 warning이며, 어떤 declaration도 하지 않는 registry entry는 error다. superseded version을 계속 선언하는 artifact는 artifact별 finding이 아니라 count와 sample을 포함한 aggregated row 하나로 보고한다.

### 존재 이유

기록된 profile version이 없으면 profile을 개선한 뒤 기존 artifact 중 어느 것이 예전 rule 아래 만들어졌는지 알 수 없다. 그러면 모든 quality question에 corpus 전체를 다시 읽어야 하고, 아무도 그렇게 하지 않으므로 정직한 답은 "모른다"가 된다. two-stage severity rollout에서는 이 문제가 첨예해진다. 예전 profile로 만든 artifact가 새 check를 한꺼번에 실패하며, *아직 migrate하지 않음*과 *실제로 망가짐*을 구별할 방법이 없다. aggregated-row reporting은 정확히 이 때문에 존재한다. 아직 migrate하지 않은 artifact 100개를 개별 보고하면 실제 실패 3개가 묻히고, 일반적 반응은 check를 downgrade하는 것인데 E2가 타당한 이유로 금지한다.

axis orthogonality가 없으면 subject로 structure를 선택하게 되고, 같은 subject지만 shape가 완전히 다른 input 두 개가 동일한 skeleton을 받는다. 하나에는 심하게 맞지 않는다. symptom은 모든 것에 맞을 때까지 optional section이 늘어나 결국 아무것도 제약하지 않는 template다.

known-exceptions section이 없으면 profile selection은 매번 새로 내리는 취향 판단이 되고, 같은 input shape가 처리자에 따라 다른 profile에 놓인다.

### 도입 방법

- invariant contract와 variable profile을 분리한다. 해당 family의 모든 artifact에 참인 것은 contract에 속한다. requirement에 exception이 있다면 profile material이다.
- shape axis와 presentation axis를 독립적으로 만들고 orthogonality rule을 명시한다. 직관에 어긋나므로 기본적으로 위반된다.
- 각 profile에 명시적인 selection signal과 sibling profile을 가리키는 known-exceptions section을 둔다.
- profile을 integer로 versioning하고 version-history section을 두며, generated artifact frontmatter에 profile id와 version을 기록한다.
- registry check를 양방향으로 추가한다. declared-but-unregistered는 error이고 registered-but-never-declared도 error다.
- 이전 version의 straggler는 artifact별 finding이 아니라 aggregated row 하나로 보고한다.

### 변경할 때

artifact family가 실제로 shape 하나만 가진다면 template를 사용하고 이를 생략하라. 대체물은 invariant/variable 분리, author preference가 아니라 input characteristic에 따른 selection, 어느 rule version이 output을 만들었는지에 대한 기록된 provenance, version straggler를 artifact별이 아니라 aggregate로 보고하는 방식을 보존해야 한다.

### 의존 대상 / 없을 때 파손되는 조건

- **E3** — 기록된 profile version이 있어야 contract 변경의 blast radius를 계산할 수 있다. 이것이 없으면 fixture auto-selection은 *어느 contract*가 바뀌었는지는 식별하지만 *어느 artifact가 그 contract를 구현하는지*는 알 수 없다.
- **B4** — rebuild threshold는 artifact의 accumulated-patch counter를 읽는다. profile-version field도 같은 frontmatter에 있고 같은 discipline으로 유지한다. 둘 다 "이 artifact는 여전히 현재 rule이 만들어 낼 것인가?"에 답한다.
- **E4** — profile과 version field가 닫힌 field set에 포함되고 enum-check되어야 한다. 그렇지 않으면 free text로 drift하여 registry cross-check가 신뢰할 만한 비교 대상을 잃는다.
- **B3** — profile은 promotion ladder의 중간 rung에 있다. technique은 profile이 되고 profile은 automated check가 된다. 위로 이어지는 ladder가 없는 profile system은 절대 enforce되지 않는 prose를 쌓는다.

---

## F6 — 도구 entry point: canon 하나, 얇은 link

**Tier: CORE.** 모든 agent tool은 자체 entry file을 auto-load하므로 둘 이상의 도구가 작업하는 저장소에는 항상 load되는 instruction file도 둘 이상 있다. 중복 instruction은 조용히 갈라지고, 각 도구의 agent는 서로 다른 contract를 따르면서도 모두 같은 것을 따른다고 믿게 된다.

### 정의

각 agent tool은 무언가를 하기 전에 자신이 선택한 filename의 instruction file을 자동으로 읽는다. 따라서 두 도구가 작업하는 저장소에는 이런 file이 둘 있고 어느 도구도 다른 도구의 file을 읽지 않는다.

규칙은 convenience가 아니라 *nature*에 따라 분리한다.

- **한 file이 canonical**이며 layer, gate command, evidence chain, parallel rule, approval boundary 등 tool-agnostic instruction을 모두 담는다.
- **다른 모든 tool entry file에는 canon link와 해당 tool에 진정으로 고유한 것만 넣는다.** model tier name, subagent interface, 자체 switch 같은 것이다. 어느 도구가 실행하든 참인 rule은 거기에 두지 않는다.
- **긴 procedure는 compatibility file에 절대 복제하지 않는다.** compatibility file은 가리키고 canon이 담는다.

**canonical file 자체가 어떤 tool의 entry point라는 점은 예외가 아니라 규칙 안의 한 case다.** canon으로 선택한 filename은 이미 어떤 tool이 load하기 때문에 선택한 것이다. 따라서 그 tool이 실행할 때 canon은 그 tool의 entry file이기도 하며 tool-specific content가 살 다른 file은 없다. 이 case를 명시하라. canonical이라고 선언된 document 안에서 이 case를 허용하는 clause 없이 tool-specific table을 발견한 독자는 boundary가 이미 깨졌다고 읽는다. 그래서 tool에 필요한 content를 삭제하거나 boundary가 장식이라고 결론 낸다. clause는 한 문장이면 된다. 이 file을 직접 읽는 tool에 고유한 content는 여기에 속한다. 그 tool에는 이 file이 thin file이기도 하기 때문이다.

**role은 canon에, name은 tool file에 둔다.** task class에서 tier *role*로 가는 mapping, 즉 어느 work class가 가능한 가장 강한 model을 필요로 하고 어느 것이 더 가벼운 model에서도 무난히 degrade하는지는 어느 tool이 실행해도 참이다. 따라서 tool-agnostic하게 한 번만 적으며, 이는 이 메커니즘이 아니라 D4의 rule이다. tool에 따라 달라지는 것은 각 role을 채우는 *identifier*다. 따라서 각 tool entry file은 role-to-name table을 담고 그 reasoning은 전혀 담지 않는다. 이 분리 덕분에 tool file이 짧게 유지되고 model name이 rule 안에 들어가지 않는다. rule은 role을 이름 붙이며 role은 name보다 오래 살아남는다. 앞 문단에 따라 canon을 직접 읽는 tool은 자신의 row를 canon에 넣는다.

어떤 line이 tool file에 속하는지 판단하는 test는 이것이다. 다른 tool이 이 저장소에서 작업해도 여전히 참인가? 그렇다면 canon에 속한다.

이는 F1과 같은 shape, 즉 하나의 canonical source와 얇은 generated 또는 linked copy를 procedure가 아니라 tool이 load하는 file에 한 단계 위에서 적용한 것이다. tool file이 pointer와 tool-specific setting을 넘어 커지면 손으로 유지하지 말고 생성하며 그 결과에 drift check를 둔다(A4).

### 존재 이유

중복 instruction은 중복 상태로 머물지 않는다. 누군가는 자기 tool이 load한 file에서 rule을 바로잡는다. 앞에 놓인 authoritative-looking file이기 때문이다. 다른 tool의 file에는 이전 rule이 남는다. 두 file 모두 내부적으로 coherent하여 어느 쪽에서도 이상해 보이지 않고 check도 발화하지 않는다. 누구도 비교할 생각이 없는 두 문서를 diff해야만 divergence가 보인다. 나중에는 같은 저장소의 두 agent가 서로 다른 contract를 enforce하면서 각각 자신의 instruction file을 근거로 든다.

거울상 실패는 두 번째 canon으로 자란 compatibility file이다. pointer로 시작하고 유용한 summary가 붙고 clarification이 붙다가, 마침내 다른 어디에도 없는 rule을 담는다. 이때 삭제하면 content를 잃고 유지하면 canon이 더는 canonical이 아니다.

단순한 비용도 있다. 매 실행마다 load되는 instruction은 저장소에서 가장 비싼 text다. 두 번 쓴 rule의 비용은 영원히 두 번 지불한다.

**적용 대상 object 없이 principle만 배포하는 것이 세 번째 실패이며, 이 specification 자체가 그 실패를 commit했다.** 이 하네스의 이전 packaging은 F6을 CORE tier로 담았지만 entry file은 canon도 thin file도 전혀 배포하지 않았다. rule을 읽은 도입자는 적용하기 전에 artifact를 발명해야 했고, 그들이 발명하는 shape는 바로 이 rule이 막기 위해 존재하는 shape다. tool-agnostic content가 처음 작성된 곳, 즉 도입자의 tool이 load하는 어느 file에 들어가고, 나중에 결코 neutral하지 않았던 file에서 canon을 재구성한다. 이 하네스 자체 packaging에서 한 번 측정되었고, repair는 설명에 그치지 않고 채워진 entry file을 배포하는 것이었다. 일반형은 보존할 가치가 있다. 도입으로 *file*이 생기는 메커니즘은 시작 artifact로 그 file이 존재하기 전까지 도입된 것이 아니다.

### 도입 방법

1. canonical file을 지정하고 그 file 안에서 canonical임을 밝힌다. implicit하게 두지 않는다.
2. 다른 모든 tool entry file에는 canon link와 다른 tool에서는 참이 아닐 내용만 둔다. file 안에 이 금지를 명시하여 다음 agent가 내용을 추가하기 전에 boundary를 보게 한다.
3. 위 test로 기존 content를 분류한다. tool-agnostic한 것은 모두 canon으로 옮기고 남은 것은 한눈에 읽힐 만큼 짧아야 한다.
4. 모두 structure registry(A2)에 선언하여 새 tool entry file이 undeclared 상태로 나타날 수 없게 한다.
5. 둘보다 많으면 template에서 thin file을 생성하고 drift check를 추가한다(F1, A4). 그보다 적으면 discipline이 generator보다 저렴하다.
6. 두 file을 같은 commit에 채워진 상태로 만든다. canon을 만들고 tool file을 나중으로 미루는 것은 위 실패의 느린 형태다. 그 사이 들어오는 모든 rule은 실행 중인 tool이 볼 수 있는 곳에 작성되고, thin file이 생길 즈음에는 넣을 것이 아무것도 남지 않는다.
7. canonical name에 이미 file이 있는 저장소에 도입할 때는 overwrite하지 않는다. 하네스 content를 exact paired marker region 안에 둔다. marker 안은 하네스가 replace할 영역이고 밖은 adopter의 영역이므로 update가 건드리지 않는다. 이후 version은 file을 merge하지 말고 region을 replace하여 받는다. marker form, exclusivity rule, near-miss failure는 A4의 것이며, 여기서는 하네스가 소유하지 않는 file에 그 discipline을 적용한다. boundary가 없으면 다음 version은 hand-merge할 수밖에 없고, 항상 load되는 instruction file을 hand-merge하면 양쪽 절반이 서로 불일치하기 시작한다.

### 의존 대상 / 없을 때 파손되는 조건

- **F1** — 동일한 one-canon-many-copies 원리다. 함께 도입하고 vocabulary를 공유해야 한다. 그렇지 않으면 한 저장소 안에서 "drift"가 서로 다른 두 의미를 갖는다.
- **F2, F3** — trigger와 match한 procedure를 bind하는 routing sentence와 entry-document boundary rule은 모두 canon에 있으며 가장 먼저 복제되는 내용이다.
- **A2** — entry file도 다른 path와 같아서 선언해야 한다. 그렇지 않으면 새 tool file이 unnoticed 상태로 나타난다.
- **A4** — adopter가 소유한 entry file 내부 transplant region은 다른 주체의 지붕 아래 있는 marker-bounded region이다. marker discipline이 없으면 하네스가 유지하는 영역과 adopter가 작성한 영역 사이에 찾을 수 있는 boundary가 없고, 다음 version은 replacement가 아니라 merge conflict로 온다.
- **D4** — tool file이 model name을 채우는 role에 관한 메커니즘이다. class-to-tier rule이 tool-agnostic한 어딘가에 명시되지 않으면 각 tool file이 어느 work에 어느 tier가 필요한지에 대한 자체 reasoning을 키우고, 한 저장소의 두 tool이 서로 다른 rule로 delegate하면서 모두 자신의 instruction file을 근거로 든다.

### 변경할 때

CORE. 다만 tool file 수는 프로젝트가 아니라 toolchain이 정한다. 대체물은 세 속성을 보존해야 한다. tool-agnostic rule의 canonical file은 정확히 하나다. 다른 모든 entry file은 pointer와 진정한 tool-specific content로 한정된다. 긴 procedure를 compatibility file에 재진술하지 않는다. full copy를 손으로 동기화하는 것은 대체물이 아니다. 그것이 실패이지 rule의 구현이 아니다.

---

## F7 — Working-language 정책

**Tier: OPTIONAL.** Precondition: 저장소의 working language가 English가 아니다. English라면 아래 axis는 아무 해 없이 합쳐진다. 모든 것이 이미 English여서 분리해 둘 것이 없고, 메커니즘은 아무도 필요로 하지 않는 문단 하나의 비용을 낸다. F4처럼 이 precondition을 note가 아니라 메커니즘 자체에 명시하라. 생략 가능한 조건을 이름 붙이지 않은 optional mechanism은 다음 독자가 그것이 생략 가능했음을 알 방법이 없어 ceremony로 도입한다.

### 정의

항상 load되는 canonical entry document(F6)에 네 axis를 각각 자체 값과 함께 따로 선언한다.

- **사용자에게 보내는 reply** — working language.
- **저장소 안의 human-readable prose** — working language이며, 위 line과 독립적으로 설정한다. 저장소가 한 언어로 답하고 durable prose는 다른 언어로 보관할 수 있다. audience가 다른 별개의 decision이다.
- **file과 directory name** — 위 두 axis와 관계없이 고정 casing convention의 English.
- **metadata key** — frontmatter field, registry key, machine field는 위 두 axis와 관계없이 English.

**separation이 formatting choice가 아니라 메커니즘이다.** "이 저장소는 언어 X로 작업한다"라는 declaration 하나로 합치면 prose rule이 조용히 filename rule이 된다. prose에 관해서는 합친 문장이 참이고 독자가 기본적으로 이를 확장하므로 그 순간에는 아무도 이의를 제기하지 않는다. 나중에는 English로 작성한 glob이 match할 수 없는 path, 두 filesystem에서 서로 다르게 sort되는 identifier, 닫힌 field schema(E4)가 받아들이기 위해 넓어져야 하는 metadata key가 들어온다. 각각을 하나씩 고치지만 어느 것도 원인이 된 declaration을 가리키지 않는다.

**cross-language brief.** working language가 English가 아니면 모든 durable document에 짧은 English summary section을 둔다. working language를 모르는 독자는 가상의 존재가 아니다. newcomer, 질문 하나 때문에 참여한 reviewer, 자체 operating vocabulary가 English인 모든 tool이 그 독자다. brief가 지원해야 할 것은 *reading*이 아니라 *routing*이다. 내가 필요한 문서가 이것인지, 무엇을 주장하는지를 알게 하면 된다. 문서의 translation인 brief는 유지해야 할 두 번째 문서여서 stale해진다. 몇 문장의 orientation인 brief는 그렇지 않다.

**rule은 자체 mechanical coverage가 끝나는 곳을 명시한다.** check로 enforce되는 language 또는 terminology rule은 그 check가 scan하는 path에 대해서만 enforce되고 그 밖에는 enforce되지 않는다. 보통 일부 directory만 포함하고 다른 곳은 포함하지 않으며, agent가 사용자에게 하는 발화에는 대개 전혀 적용되지 않는다. rule body에 boundary를 작성한다. check가 도달하는 곳을 이름 붙이고, 그 밖에서는 읽히는 만큼만 rule이 유효하다고 말한다. E1이 coverage를 procedure spec 17개 중 14개라고 밝히고 그 gap을 시사점으로 부르는 것과 같은 조치다. 이것이 막는 실패는 구체적이다. check가 붙은 rule은 완전히 enforce되는 것처럼 읽히므로 check가 닿지 않는 곳은 unguarded로 취급되지 않고 아예 고려되지 않는다. 나중에 gap을 발견한 사람은 이를 시스템에 관한 뜻밖의 발견으로 경험하고 check를 불신한다. 정직한 형태였다면 처음부터 명시된 한계였을 것이다.

**의미를 담은 phrasing을 보존한다. 그리고 의도적으로 두 계층 중 더 약한 계층이다.** E5는 recognized carrier 안에서 사람이 쓴 byte를 mechanical operation으로부터 보호하며 fail-closed이므로 unknown layout에서 abort한다. F7은 다른 actor에게 더 부드러운 요구를 한다. agent가 쓰는 prose, 즉 summary, paraphrase, constraint를 rule로 옮긴 translation을 지배하며 constraint를 담은 단어 하나가 compression을 견뎌야 한다고 요구한다. carrier도 mechanical operation도 check도 없으며, enforcement는 rule이 읽힌다는 것뿐이다. 둘을 모두 작성할 때 방향을 명시하라. 합치는 것은 실제 error이기 때문이다. 이 specification 자체의 coverage audit도 처음에 soft rule이 byte-level rule로 충족되었다고 기록했고, 실제로 cover된 적 없는 rule을 retire하는 결과를 낳았다.

### 존재 이유

**합쳐진 language declaration은 선언한 곳에서 멀리 떨어진 failure를 만든다.** declaration은 한 문장이며 명백히 올바르게 읽힌다. 몇 달 뒤 저장소에는 English-language glob으로 접근할 수 없는 directory name과 서로 다른 두 spelling의 frontmatter key가 생기며, 모두 agent가 읽은 문장을 올바르게 따라서 작성한 것이다. rule이 깨진 순간은 없으므로 symptom이 아니라 declaration에서 repair해야 한다.

**prose가 한 언어로 된 저장소는 다른 모든 사람에게 reading 수준보다 routing 수준에서 먼저 읽을 수 없게 된다.** prose를 읽을 수 없는 독자는 reading 수준에서 그 사실을 안다. routing 수준에서는 filename, heading, structure를 보고 각 document가 무엇인지 짐작하지만 틀리며, 이를 알려 주는 것은 없다. brief는 문서를 읽을 수 없는 상태는 복구 가능하지만 문서를 식별했다고 잘못 믿는 상태는 그렇지 않기 때문에 존재한다.

**enforced rule은 모든 곳에서 enforce된다고 여겨진다.** check의 존재는 rule이 읽히는 방식을 "이를 따라라"에서 "이는 처리된다"로 바꾸며, rule이 이름 붙인 전체 scope에 그렇게 적용된다. check가 cover하는 더 작은 scope에만 적용되지 않는다. boundary를 명시해야 uncovered part가 agent가 실제로 수행해야 하는 것의 범주에 남는다.

### 도입 방법

- 네 axis를 canonical entry document에 네 줄로 따로 선언한다. 두 값이 같더라도 네 줄이다. redundancy가 collapse를 막는다.
- working language와 관계없이 file-name axis와 metadata-key axis를 English로 정하고 본문에 *관계없이*라고 쓴다. independence를 추론해야 하는 독자는 dependence를 추론한다.
- 모든 durable document class에 짧은 English section을 요구하고 translation이 아니라 orientation이라고 명시하여 실제로 작성할 만큼 저렴하게 만든다.
- wiring하는 각 language 또는 terminology check마다 covered path를 rule 바로 옆 body에 적고, 그 밖에서는 무엇이 어떤 근거로 유효한지 한 문장으로 쓴다.
- agent-prose preservation rule과 byte-level protection(E5)을 text상 분리하고 어느 것이 더 강한지 밝히는 문장을 둔다. 비슷하게 들리지만 강도가 다른 두 rule은 다음 사람이 문서를 정리할 때 합쳐진다.

### 의존 대상 / 없을 때 파손되는 조건

- **F6** — axis declaration은 어느 tool이 실행해도 참이므로 canonical entry document에 속한다. 대신 tool file에 선언하면 다른 tool 아래의 agent는 undeclared language로 작업한다.
- **E5** — 이 soft layer 아래의 strong layer다. 이것이 없으면 soft preservation rule만 mechanical pass와 사람이 쓴 text 사이를 지키게 되는데 감당할 수 없는 역할이다.
- **E4** — metadata-key axis가 닫힌 field set의 각 field를 하나의 spelling으로 유지한다.
- **E1** — coverage statement는 어느 check가 어느 path에서 실행되는지에 관한 주장이다. wired validator가 없으면 경계를 정할 mechanical jurisdiction이 없고 전체 rule은 read-only 절반으로 축소된다.

### 변경할 때

precondition이 거짓이면 메커니즘 전체를 생략한다. 이것이 여기서 뜻하는 tier는 OPTIONAL — 선택 사항이다. 생략 전 check는 하나의 질문이다. 이 저장소의 durable prose 중 English가 아닌 언어로 작성된 것이 있는가? 유지한다면 대체물은 네 가지를 보존해야 한다. axis는 서로 derive하지 않고 따로 선언한다. identifier와 machine key는 prose language와 독립적인 한 언어로 고정한다. working language를 모르는 독자도 읽지 않고 routing할 수 있다. 부분적인 mechanical enforcement가 있는 모든 rule은 enforcement가 끝나는 곳을 명시한다.

---

## F8 — 사용자 보고

**Tier: DEFAULT.** item list는 작동 가능한 집합 하나이며 프로젝트의 목록은 달라도 된다. 대체할 수 없는 것은 사람을 대상으로 한 channel이 저장소 자체 record와 별도로 존재한다는 점이다. 유일한 reporting surface가 자체 evidence chain인 저장소에서 operator는 무슨 일이 있었는지 보려면 그 chain의 독자가 되어야 한다.

### 정의

meaningful operation 뒤 agent는 사용자에게 고정된 item 집합을 보고한다.

- 읽은 file,
- 만든 file,
- 수정한 file,
- conflict와 open question,
- hash와 subject로 나타낸 commit.

핵심은 fixed라는 점이다. 매번 새로 조립하는 report는 그 run이 어떻게 *느껴졌는지*를 바탕으로 조립되며, run에 대한 느낌은 보통 가장 어려웠던 일에 좌우된다. 그것은 대개 사용자가 알아야 할 것이 아니다. 고정된 집합은 slot이 비어 있어도 답할 수 있고, 빈 slot 자체가 정보다.

**absence는 absence로 보고한다.** source를 찾지 못했다면 그렇게 말한다. 읽은 내용으로 뒷받침할 수 없는 claim이 있다면 그렇게 말한다. 요청 scope의 일부를 하지 않았다면 어느 부분인지 말한다. 언급하지 않은 gap은 cover된 것으로 읽힌다. 독자는 "문제가 없어서 언급하지 않음"과 "전혀 보지 않아서 언급하지 않음"을 구별할 수 없고 silence는 기본적으로 첫 번째 의미로 읽힌다. 다른 모든 item은 수행한 work의 record인 반면 이것은 하지 않은 work의 record이므로 가장 자주 누락된다.

**세 reporting channel이 있으며 각각 다른 독자에게 필요한 것을 누락한다.** 겹치는 fact를 담아 서로 바꿀 수 있어 보이지만 그렇지 않다. 구분 기준은 각 channel이 무엇을 빼도 되는가다.

- **run receipt(B1)**는 저장소 자체의 memory다. immutable하고 stateless하며, 나중에 도착한 agent가 과거 unit이 무엇을 했는지 재구성하도록 작성한다. 수정할 수 없다는, 좋은 evidence를 만드는 바로 그 속성 때문에 지금 기다리며 여전히 움직이는 state를 묻는 사람에게는 답으로 쓸 수 없다.
- **orchestrator에게 보내는 report(D1)**는 길이가 제한되고 verifiable value만 허용하며 narrative, reasoning, alternative는 의도적으로 제외한다. orchestrator의 judgment capacity가 scarce resource이고 report volume은 decision보다 먼저 이를 소비하기 때문이다. uncertainty, blocker, significant finding, clarification request, final status는 **누락하지 않는다**. D1은 길이를 이유로 이를 억제하는 것을 금지하며 이 문서도 약화하지 않는다. cap이 적법하게 제거하는 것은 reader가 *route*하지 않고 *judge*할 수 있게 하는 모든 것이다. agent가 왜 uncertain한지, 무엇을 검토하고 기각했는지, 잘못 판단했을 때 불확실한 대상이 초래할 비용이다. orchestrator는 question이 존재함을 알아야 routing할 수 있다. 답해야 할 사람에게는 잘려 나간 부분이 필요하다.
- **사용자에게 보내는 report**는 ephemeral하며 한 사람의 즉각적인 decision에 맞춘다. durable trace를 전혀 남기지 않으므로 receipt를 대체하지 않는다.

둘 중 어떤 두 channel을 합쳐도 한 독자는 다른 독자에 맞춘 문서를 받는다. 흔한 collapse는 receipt를 report로 취급하는 것이다. fact가 모두 있으니 report가 pointer가 되고, 사용자는 저장소에 방금 무슨 일이 있었는지 알려고 record store를 열어야 한다.

**아무것도 이를 check하지 않는다.** enforcement는 항상 load되는 entry document와 procedure text뿐이다. validator는 agent가 사람에게 무엇을 말했는지 판단할 수 없고, check가 읽을 수 있는 artifact는 report 여부에 따라 달라지지 않는다. rule이 있는 곳에 이 사실을 명시한다. 명시되지 않은 enforcement absence는 F7의 jurisdiction clause가 막는 것과 같은 결함이다. 한 absence의 공개를 요구하면서 다른 absence를 숨기는 문서는 이상할 것이다.

### 존재 이유

**operation이 완료되어도 사용자는 무엇이 바뀌었는지 말할 수 없다.** work는 올바르고 저장소는 좋은 상태지만, 사용자가 직접 file을 읽어야만 두 fact를 알 수 있다. 뒤따르는 것은 complaint가 아니라 oversight의 느린 철회다. agent가 한 일을 싸게 볼 수 없는 사용자는 확인하려는 시도를 멈추고, 잘못된 변경 하나를 잡았을 review도 사라진다.

**partial result가 whole result처럼 읽힌다.** 요청한 다섯 item 중 네 개를 끝내고 그 네 개를 보고한 agent는 거짓을 말한 것이 아니다. 확인할 list가 없는 사용자는 완료된 요청으로 읽는다. 이는 집합에서 가치가 가장 높은 단일 item이자 report가 가장 먼저 누락하는 item이다. 네 개는 work지만 다섯 번째는 admission이기 때문이다.

**"receipt에 있다"는 report가 아니라 pointer다.** evidence chain은 나중에 질문을 갖고 도착하는 독자를 위해 작성한다. 앞에 있는 사용자의 질문은 "방금 무엇을 했는가"라는 다른 질문이며, location으로 답하면 그 사람을 희생해 다른 독자의 질문에 답하는 셈이다.

### 도입 방법

- 항상 load되는 canonical entry document에 item list를 fixed set으로 작성하고 빈 slot을 포함해 모두 보고한다.
- absence item을 명시적으로 넣고 missing source, unsupportable claim, unfinished scope라는 세 형태를 이름 붙인다. 정직하라는 일반 지시만으로는 이 항목들이 나오지 않는다.
- 같은 곳에서 이 channel이 durable receipt와 orchestrator report와 구별된다고 명시하고 각각의 목적을 한 줄로 설명한다. 그 문장이 없으면 다음 사람이 문서를 정리할 때 둘을 합친다.
- 아무것도 이를 check하지 않는다고 말한다. procedure-text-only rule은 적힌 곳마다 procedure-text-only라고 label해야 한다.
- 읽을 수 있을 만큼 report를 짧게 유지한다. gate는 사용자가 file을 열지 않고도 무슨 일이 있었는지 알 수 있는가이지, report가 receipt처럼 완전한가가 아니다.

### 의존 대상 / 없을 때 파손되는 조건

- **B1** — 같은 fact의 durable half다. receipt가 없으면 user-facing report가 유일한 record가 되며 ephemeral하므로, 저장소는 report한 것처럼 보이면서도 run의 memory를 잃는다.
- **D1** — verifiable-values-only rule과 length cap이 있는 orchestrator-facing report다. 둘은 reader로 구별한다. orchestration channel만 정의되어 있으면 그 economy rule이 사용자에게 적용되어 사용자가 필요로 하는 signal을 정확히 제거한다.

### 변경할 때

DEFAULT: item set은 프로젝트가 정할 수 있으며 사용자가 commit을 직접 읽는 프로젝트에는 더 적은 항목으로 충분할 수 있다. 대체물은 세 속성을 보존해야 한다. 집합은 run마다 조립하지 않고 사전에 고정한다. absence가 item이며 unfinished scope를 그 형태로 명시한다. channel은 저장소의 durable record와 구별할 수 있어야 한다. fact를 기록한 위치만 가리키는 report는 report가 아니라 화제를 바꾸는 것이다.

---

## English brief

This chapter defines the enforcement and procedural mechanisms that make harness invariants detectable at guaranteed moments and keep canonical workflows discoverable without drift. It covers E1–E5 and F1–F8, including validator wiring, governed checks and fixtures, protected spans, generated adapters, routing, onboarding, volatile workspaces, profile composition, tool entry points, language policy, and user reporting. The Korean body is the canonical prose; machine keys, paths, code, tier tokens, markers, and commands remain unchanged.
