# 제1장 — 계층, 구조, 증거

## A1 — 출처 기반 계층 분리

**등급: CORE.** 이를 제거하면 "이 파일은 어디에 속하는가"에 원칙적으로 답할 방법이 없어지므로, 하네스의 다른 모든 메커니즘은 주소 체계와 무엇이 무엇을 편집할 수 있는지에 관한 개념을 잃는다.

### 정의

최상위 디렉터리는 콘텐츠가 무엇에 관한 것인지가 아니라 **콘텐츠가 어디에서 왔는지**에 따라 분리한다. 하네스는 네 가지 출처 클래스를 사용한다.

- **불변 입력** — 프로젝트 외부에서 수집한 자료(가져온 페이지, 업로드된 문서, 기록문, 내보낸 데이터). 바이트를 보존한다. 제자리에서 절대 편집하지 않는다.
- **파생 지식** — 모든 주장이 위치 지정자와 함께 불변 입력까지 추적되는, 에이전트가 유지·관리하는 콘텐츠.
- **생성 출력** — 에이전트가 추론으로 생성한 콘텐츠. 이를 뒷받침하는 수집 입력이 없으며 모델 역량에 의존한다.
- **운영 계약** — 에이전트가 저장소에서 작업할 때 따르는 규칙, 절차, 양식, 증거 기록.

주제는 이 분리와 직교한다. 출처가 다르면 같은 주제에 관한 두 문서는 서로 다른 계층에 놓이고, 하나의 계층은 흔히 프로젝트가 다루는 모든 주제에 걸쳐 있다.

세 가지 경계 규칙이 이 분리를 지탱한다. **파생 방향은 단방향이다**. 파생 콘텐츠가 입력을 가리키며 그 반대는 아니다. **수정 사항은 입력을 절대 편집하지 않는다**. 수정이 명백히 옳을 때도, 사용자가 직접 요청했을 때도 마찬가지다. 수정은 파생 계층에 기록하거나, 교정된 원본을 새 입력으로 수집하고 명시적인 지시가 있을 때만 이전 원본을 제거한다. 사례별 예외 경로는 없다. 규칙 자체의 변경은 변경 통제 사슬(B1, D3)을 거친다. **추론으로 생성한 출력은 파생 지식에 분류하지 않는다**. 둘 다 에이전트가 작성하지만, 근거와 실패 양상이 서로 다르기 때문이다.

두 규칙은 계층을 *읽는* 방법을 다루며, 쓰기 규칙만큼이나 이 메커니즘의 일부다.

**계층화는 읽기 순서다.** 질문에는 파생 계층에서 먼저 답하고, 파생 계층만으로 부족하거나 검증을 명시적으로 요청했을 때 불변 입력을 참조한다. 순서를 명시하지 않으면 모든 질문이 원본을 다시 읽고, 파생 계층이 존재하는 이유 전체가 활용되지 않으며, 더 나쁘게는 아무것도 파생 계층에 의존하지 않으므로 파생 계층이 낡았다는 사실을 아무도 알아차리지 못한다.

**기록된 주장과 모순되는 새 주장은 이를 조용히 대체하지 않는다.** 둘 다 남고 충돌이 드러난다. 덮어쓰려는 본능은 강하며 정리처럼 느껴진다. 대개 새 정보가 더 나은 정보이기 때문이다. 그러나 두 기록이 불일치한다는 사실 자체가 하나의 발견이고, 이전 주장이 기록된 *이유*, 즉 다른 내용을 말한 원본은 더 새로운 원본이 동의하지 않는다고 해서 사라지지 않는다. 근거가 빈약한 주장에는 단정적인 진술 대신 신뢰도 등급을 표시하여, 나중의 독자가 둘을 다시 파생하지 않고도 불확실한 주장과 확정된 주장을 구분할 수 있게 한다. (B3은 두 사용자 발언이 모순되는 *선호*에 같은 형태를 적용한다. 여기의 규칙은 콘텐츠에 관한 것이며, 둘은 하나의 원칙을 담는 서로 별개의 운반체다.)

### 존재 이유

입력 불변성이 없으면 에이전트가 수집한 원본의 "명백한 오타를 고친다." 몇 달 뒤 파생 주장과 원본은 완벽히 일치하지만, 그 일치가 충실한 파생의 결과인지 원본을 파생에 맞춰 편집한 결과인지 저장소 어디에서도 알 수 없다. 모든 입력의 증거 가치가 한꺼번에 무너지고, 텍스트 파일을 깔끔하게 편집한 결과는 올바른 편집과 구분할 수 없으므로 어떤 검사도 발동하지 않는다.

추론으로 생성한 출력을 원본에서 파생한 지식과 분리하지 않으면, 한 세션에서 에이전트가 수행한 추론이 이후 세션에서 확립된 사실로 다시 읽히고 재인용된다. 왕복할 때마다 겉보기 신뢰도는 높아지지만 기저 증거는 여전히 0이다. 이는 리뷰에서 보이지 않는다. 나중 문서는 원본을 잘 제시하며, 그 원본은 이전 문서다.

운영 계약을 콘텐츠와 분리하지 않으면 규칙 변경과 콘텐츠 편집이 같은 커밋에 들어오며, "이 산출물을 만들 때 어떤 규칙이 시행 중이었는가"라는 질문에 답할 수 없다. 주어진 출력이 어느 계약 버전에서 생성되었는지 식별할 수 없으므로 회귀 검사(E3)는 추측이 된다.

### 도입 방법

1. **프로젝트에 실제로 존재하는** 출처 클래스마다 최상위 디렉터리 하나를 선택한다. 일반적으로 세 개에서 다섯 개다. 외부에서 아무것도 수집하지 않는 프로젝트에는 불변 입력 계층이 없다. 목록에 네 개라고 쓰여 있다는 이유로 빈 디렉터리를 세우는 것은 디렉터리가 없는 것보다 나쁘다. 콘텐츠가 어디에서 왔는지가 아니라 빈 상자의 이름에 따라 분류되는데, 이는 이 분리가 막으려는 바로 그 일이다. 실제로 만드는 계층마다 무엇이 들어오고 누가 편집할 수 있으며 파생이 어느 방향으로 흐르는지 밝힌 한 문단짜리 헌장을 작성한다.
2. 불변성을 지향 사항이 아니라 기계적인 것으로 만든다. 입력 디렉터리 아래의 콘텐츠 편집을 금지한다. 모든 참조를 같은 변경에서 갱신하는 경로 정규화인 경우에만 이름 변경을 허용한다. 이를 강제하는 검사가 빌드 실패가 되게 한다(E1, E5).
3. 모든 파생 문서가 주장의 입력 경로와 문서 내 위치 지정자를 기록하도록 요구한다. 입력을 지목할 수 없는 파생 문서는 잘못 분류되었거나 근거가 없는 문서다.
4. 프로젝트가 추론 생성 콘텐츠를 조금이라도 만든다면 해당 계층에 자체 루트를 주고, 그 내용은 증거가 아니며 파생 계층에서 원본으로 인용할 수 없다고 헌장에 명시한다. 만들지 않는다면 루트를 생성하지 않는다. 빈 루트는 이 규칙이 막고자 하는 파생 계층으로의 재병합을 부추긴다.
5. 같은 변경에서 전체 집합을 구조 레지스트리에 선언한다(A2). 그전까지 계층화는 산문으로만 존재한다.

### 의존 대상 / 없을 때 깨지는 것

- **A2** — 관례로만 존재하는 계층화는 아무것도 강제하지 못한다. 레지스트리는 경계가 기계 검사로 바뀌는 곳이다. 레지스트리가 없으면 분리는 관례로 퇴화하고 몇 주 안에 드리프트한다. 모든 잘못된 분류가 개별적으로는 합리적이기 때문이다.
- **A3** — 계층 추가나 이동을 통제하는 게이트가 없으면 집합은 누적으로 침식되고 출처 기준은 구별력을 잃는다.
- **E1** — 불변성과 귀속 검사는 절차가 커밋 전에 이를 연결할 때만 실행된다.
- **E5** — 수집한 원문을 바이트 수준에서 보호하지 않으면 불변성은 어떤 에이전트든 평범한 편집으로 위반할 수 있는 정책이고, 그 뒤에는 교정된 입력과 충실한 입력을 구분할 수 없다.

### 변경할 경우

CORE. 클래스의 수와 이름은 프로젝트가 정할 수 있지만 기준은 바꿀 수 없다. 출처 대신 주제, 팀, 파일 유형에 따라 분리하면 계약이 아니라 분류 체계를 얻게 된다. 소속 여부에서 어떤 결과도 따라 나오지 않고 A2의 어떤 검사도 강제할 것이 없어진다.

## A2 — 구조 선언 레지스트리

**등급: CORE.** A1의 경계를 산문에서 기계 검사로 바꾸는 파일이다. 이것이 없으면 하네스의 모든 구조 규칙은 권고에 불과하다.

### 정의

하나의 선언 파일이 "이 저장소에 어떤 경로가 존재하며 각각 무엇을 위한 것인가"에 대한 답을 소유한다. 모든 tracked path는 **정확히 하나의** 선언 또는 명시적인 제외 항목으로 결정되어야 한다. 일치 항목이 없으면 hard failure다. 같은 구체성의 일치 항목이 둘이면 hard failure다. 둘 다 warning이 아니다.

이를 작동하게 하는 구체적인 형태는 다음과 같다.

- **닫힌 최상위 key 집합.** 인식되지 않는 key는 무시되는 데이터가 아니라 load error다. 레지스트리에 문서화되지 않은 차원이 늘어날 수 없다.
- **path group마다 선언 하나.** 각 선언은 최소한 안정적인 identifier, 하나의 path selector, role(content root, support 등), 그리고 **disposition**, 즉 하위 process가 path를 어떻게 다루는지, 특히 public distribution에 포함하는지를 담는다. 선언마다 disposition 하나가 reference engine이 구현하는 형태다. 서로 다른 규칙을 가진 distribution 두 개를 운영한다면 단일 field에 무리하게 넣지 않는다. 각 process에 자체 key를 부여하고 레지스트리 자체 comment에서 어느 key가 어느 process 소유인지 밝힌다. 소유 process가 모호한 disposition은 양쪽에서 읽히고 어느 쪽에서도 준수되지 않기 때문이다.
- **동결된 최소 selector grammar.** 여기서 사용하는 집합은 exact file, directory의 direct children, recursive subtree, root-level files, single path segment, any depth의 named directory다. 이 집합 밖의 것은 load error다. grammar 확장 자체가 decision gate를 거치는 registry change다. 누군가 selector를 고치면서 수행하는 code change가 아니다.
- **결정론적 specificity.** Exact가 longer literal prefix를 이기고, longer literal prefix가 fewer wildcards를 이긴다. equal-specificity double match는 coin flip이 아니라 error다. coin flip이면 귀속이 declaration order에 조용히 좌우되기 때문이다.
- **parent declaration보다 반드시 더 구체적이며 그 안에 포함되어야 하는 override.** 이를 위반한 override는 load error다. 그렇지 않으면 override가 조용히 두 번째 competing declaration이 된다.
- **비어 있지 않은 exclusions list** — 명시적인 untracked axis(build output, dependency directory, tool cache)이며 각각 사유를 명시한다. Exclusion은 선언된 결정이지 빈틈이 아니다.
- **fail-closed loader.** parse 또는 schema violation이 있으면 모두 raise하며, **어떤 것도 부분적으로 load하지 않는다**. loader는 의도적으로 엄격한 file format subset만 허용한다. anchor, alias, merge key, duplicate key, type tag, block scalar, tab을 금지하고 nesting depth를 제한한다. subset 밖의 모든 construct는 interpretation이 아니라 error다. loader는 같은 pass에서 enum membership, required-key presence, structural invariant(exactly N categories, path-to-category bijection)도 검증한다.
- **file content를 절대 읽지 않는 attribution.** path의 declaration은 path만으로 정한다. 따라서 파일은 자체 exemption을 선언할 수 없다. 해당 파일을 제외할 수 있는 것은 registry뿐이다.

레지스트리는 manifest inventory(A4)도 담고, 대규모 structural migration이 진행 중일 때는 frozen mapping table이 있는 topology state도 담는다. 따라서 "이동 중"이라는 사실이 기계에 보이며 migration 중에는 distribution 같은 downstream process를 차단할 수 있다.

레지스트리 변경은 decision gate(B2, C2)를 통해 한 명의 writer만 수행한다.

**여기서 일관된 원칙을 명시해야 한다. 이 원칙은 이 장 전체에서 반복된다. 선언의 부재는 실패이며 결코 통과가 아니다.** undeclared path는 build에 실패한다. judgment contract가 없는 hand-written index는 조용한 통과가 아니라 error다(A4). 어떤 classification rule에도 일치하지 않는 document는 "unclassified"가 아니라 error다. missing manifest file은 "검사할 것이 없음"이 아니다. fail-open hole이므로 file은 zero-count header와 함께 제자리에 남는다. 이 하네스를 warning으로 구현하는 도입자는 실패하지 않은 채 쇠퇴하는 버전을 만들게 된다.

### 존재 이유

**Undeclared-as-warning은 부패한다.** 실행할 때마다 발생하는 warning은 일주일 안에 읽히지 않게 된다. 그러면 attribution coverage는 build 실패 한 번 없이 0을 향해 퇴화하고, downstream process가 path의 disposition을 알아야 하는데 아무것도 없다는 사실을 발견할 때 비로소 누군가 알아차린다. hard failure이면 coverage는 구조적으로 100%를 유지한다. path를 추가할 때 무엇인지 밝히지 않으면 추가할 수 없기 때문이다.

**Registration과 intent는 같지 않으며 registry는 그 차이를 알 수 없다.** 이 하네스가 운영된 단 하나의 프로젝트에서 한 번 측정된 사례가 있다. path가 declared되어 모든 registry check가 통과했지만 disposition이 틀렸다. 절대 ship하면 안 되는 content가 public bundle에 조립되고, registry를 전혀 읽지 않는 두 번째 check만 이를 막는다. declaration이 well-formed이므로 registry는 불평할 것이 없다. 도입자가 가장 일관되게 과소평가하는 failure mode이므로 명시적으로 대비해야 한다. disposition은 single source of truth로서 registry에 둔다(distribution allowlist로 조립, undeclared = fail). **그리고** registry를 절대 읽지 않는 independent invariant layer가 distribution을 gate해야 한다. 어떤 disposition에서도 절대 ship하면 안 되는 것들의 짧은 hardcoded list와, 새 top-level private-looking path가 생기면 실패하는 canary로 구성한다. *disposition이 무엇인지*에는 하나의 source of truth를, *무엇이 절대 밖으로 나가면 안 되는지*에는 registry-blind second defense를 둔다.

**Wildcard declaration은 fail-open이다.** repository root의 "모든 root-level file" selector는 새 root file을 wildcard의 disposition에 조용히 편입한다. 누군가 root에 개인 scratch file을 놓으면 다음 distribution이 아무 signal 없이 이를 ship한다. 해결책은 root-level file과 tool-config file을 정확히 열거하고, root file 추가에 이제 registry edit가 필요하다는 점을 받아들이는 것이다. 그 마찰이 메커니즘이 작동하는 모습이다.

**Inference는 drift를 숨긴다.** registry가 category name에서 rule로 directory name을 추론한다면(pluralizing, suffix append), directory rename을 drift로 감지할 수 없다. inference가 그 자리에 있는 것을 그대로 재생성하기 때문이다. pattern이 명백해도 각 mapping을 정확히 선언한다.

**Self-declared exemption은 구조적으로 무효다.** attribution이 file content를 참조한다면 어떤 file이든 스스로 out of scope라고 주장하는 line을 추가할 수 있고 check는 이에 동의할 것이다. path-only attribution은 single-writer이며 gated인 registry를 건드리지 않고는 이를 불가능하게 만든다.

### 도입 방법

1. operating-contract layer 아래에 registry file 하나를 만든다. schema version과 closed key set을 부여한다.
2. 모든 tracked path group을 열거한다. unregistered-path check를 실행하면 실패할 것이므로 selector를 넓히지 말고 선언을 추가해 고친다. catch-all을 추가하려는 충동을 참는다. catch-all은 해결책이 아니라 failure mode다.
3. selector grammar를 declaration을 포괄하는 가장 작은 집합으로 동결한다. specificity ordering을 명문화하고 ambiguity를 error로 만든다.
4. loader를 fail-closed로 작성하고 자체 check id를 부여한다. registry에 general-purpose parser를 재사용하지 않는다. permissive parser는 merge key나 duplicate key를 받아들이고 저자가 작성한 것과 다른, 그럴듯해 보이는 document를 돌려준다.
5. 모든 declaration에 disposition field를 추가하고 undeclared = fail로 둔다. 그런 다음 별도의 registry-blind privacy defense를 만들고, fixture에서 private path를 일부러 잘못 선언해 second layer가 여전히 거부하는지 확인한다.
6. file을 만들거나 이동하는 모든 procedure에 registry check를 연결하고(E1), check catalogue에 error level로 id를 등록한다(E2).
7. registry edit는 owner-only로 만들고 decision record로 gate한다(B2, C2).

### 의존 대상 / 없을 때 깨지는 것

- **A1**은 registry가 선언하는 category를 제공한다. 이것이 없으면 registry는 semantics가 없는 file list다.
- **A3**는 변경을 gate한다. 이것이 없으면 directory가 늘어나는 만큼 declaration도 누적된다.
- **A4**는 registry의 manifest inventory를 소비하고 양방향으로 cross-check한다.
- **E1**은 commit 전에 check가 실제로 실행됨을 보장한다. 이 wiring이 없으면 registry는 누군가 볼 것을 기억할 때만 올바르다.
- **E2**는 check id를 govern한다. unregistered-path check를 warning으로 낮출 수 있거나 id가 catalogue에 binding된 closed-set member가 아니면 A2의 guarantee는 advisory다. 이는 도입한 registry가 decorative가 되는 가장 흔한 방법이다.
- **B2/C2**는 registry edit를 serialize한다. isolated workspace의 concurrent registry edit는 duplicate numbering과 같은 종류의 silent divergence를 만든다.

**전체 하네스의 최소 실행 가능 집합은 A1 + A2 + E1이다.** Layer separation은 boundary가 무엇인지 말하고, registry는 이를 machine-readable하게 만들며, producer wiring은 machine을 실제로 실행한다. 셋이 모두 없으면 이 specification의 나머지는 전부 실행되지 않는 paperwork다.

### 변경할 경우

CORE. file format, selector syntax, role vocabulary, disposition vocabulary는 모두 프로젝트가 정할 수 있다. 다음 네 가지 속성은 대체할 수 없다. exactly-one-declaration resolution, no-match와 ambiguity 모두에 대한 hard failure, error 발생 시 아무것도 load하지 않는 loader, file content를 절대 읽지 않는 attribution이다. 하나라도 버리면 registry는 repository를 제약하는 mechanism이 아니라 설명하는 document가 된다.

## A3 — 계층 추가 또는 이동 게이트

**등급: CORE.** 게이트가 없으면 A1과 A2가 의존하는 계층 집합이 누적으로 침식되어 결국 소속 여부가 아무것도 의미하지 않게 된다.

### 정의

최상위 계층을 추가하거나 이동하거나 두 계층 사이의 경계를 변경하려면 다음을 **모두** 충족해야 한다.

1. **구별되는 출처 또는 인식론적 범주** — 기존 계층 어디에도 실제로 속하지 않는 artifact kind. proposal은 가장 비슷한 layer를 지목하고 그 유사성으로 충분하지 않은 이유를 밝혀야 한다.
2. **지속적이고 복수인 artifact family** — 이번 주에 우연히 둘 곳이 필요한 일회성 deliverable이 아니라 축적되고 재사용되는 content.
3. **evidence chain을 거쳐 explicit human approval까지 통과**(B1, D3). approval의 후속 작업이 아니라 approval과 **같은 변경**에서 registry declaration과 validator의 new root recognition이 반영되어야 한다.

성격이 기존 계층과 겹치면 답은 새 루트가 아니라 해당 계층의 subtree다.

**계층 이동 또는 경계 이동에는 같은 게이트와 다른 실행 요구사항이 적용된다.** 새 category를 만드는 것이 아니므로 조건 1은 적용하지 않는다. 대신 의미, commit history, inbound link가 이동 후에도 보존되어야 하며, registry declaration change와 file move가 **같은 commit**에 반영되어야 한다. path가 물리적으로 새 layer에 있으면서 old layer로 attributed되는 commit은 단 하나도 존재해서는 안 된다. boundary shift는 기존 content에 적용되는 rule을 바꾸므로 approval과 decision record도 여전히 필요하다.

### 존재 이유

file-move-now, registry-later 방식의 relocation은 attribution이 단순히 틀리는데도 모든 check가 통과하는 구간을 만든다. registry 자체는 internally self-consistent하기 때문이다. registry가 더는 존재하지 않는 repository를 충실히 설명하는 상태다. 아무것도 실패하지 않고, 누군가 두 번째 commit을 할 때 구간이 닫힌다. 끝내 하지 않으면 mis-attribution이 새로운 표준이 된다.

게이트가 없으면 모든 새 output kind가 그 순간 가장 저항이 적은 경로인 top-level directory를 얻는다. 일 년 뒤 top level에는 오로지 역사적인 이유로만 구분되는 항목이 열두 개쯤 생기고, "어느 layer에 속하는가"라는 질문은 더는 확정적으로 답할 수 없으며, mechanical attribution(A2)은 모든 것을 classify하지만 아무것도 discriminate하지 못하는 catch-all로 퇴화한다.

반대 방향의 실패도 똑같이 해롭다. 계층 추가 절차가 없으면 실제로 출처가 다른 artifact family를 기존 layer에 욱여넣고, 해당 layer의 rule, 즉 immutability, one-way derivation, citation requirement가 그 subtree에는 틀리게 된다. rule은 그 subtree에서 조용히 위반되고, layer에 unenforced region이 하나 생기면 어디에서도 check를 신뢰하지 않게 된다.

### 도입 방법

세 조건을 산문이 아니라 checklist로 kernel document에 작성한다. proposal이 closest existing layer와 이를 부적합하게 만드는 specific property를 밝히도록 요구한다. registry declaration, layer charter, validator recognition 모두가 approving change의 일부가 되도록 요구한다. 나중에 "왜 이것이 root인가?"라는 질문에 답할 수 있도록 outcome을 decision(B1)으로 기록한다.

### 의존 대상 / 없을 때 깨지는 것

- **A1**은 layer가 무엇인지 정의하고, **A2**는 new layer를 선언해야 하는 곳이다.
- **D3**는 approval sequence, 즉 prose first, then structured questions, then explicit approval, then execution을 제공한다.
- **B1**은 evidence와 decision record를 운반한다. 이것이 없으면 gate는 기억을 갖지 못하고 같은 논쟁이 반복된다.

### 변경할 경우

CORE. 세 조건의 wording은 프로젝트가 정할 수 있다. 조건이 conjunctive여야 한다는 점은 바꿀 수 없다. 하나만 충족해도 되는 gate는 gate가 아니다. 누군가 제안하는 거의 모든 것에 "지속적인 family다"라는 말이 참이기 때문이다.

## A4 — Manifest와 generated-view 규율

**등급: CORE.** 이름이 명시된 owner가 없는 index는 확신에 찬 오정보가 되며, 이는 index가 없는 것보다 엄격히 더 나쁘다.

### 정의

index는 **manifest**다. 자신이 소유한 directory의 item, state, outward pointer를 열거한다. 다음 세 조건을 **모두** 만족할 때만 생성하고 유지한다.

1. **실제 consumer가 enumeration을 읽는다** — procedure step, machine parse, 또는 human browsing path. 추정하지 말고 측정한다.
2. **이름이 명시된 update owner가 존재한다.** owner는 정확히 세 종류의 typed string이다. procedure(`workflow:<name>`), script(`script:<path>#<anchor>`), contract clause(`contract:<id>#<anchor>`). multiple owner는 정상이다. validator-only owner는 실제 updater가 layer contract 또는 profile clause에 추가로 이름이 명시된 경우에만 허용한다. file을 읽는 check는 이를 update하는 party가 아니다.
3. **Auto-discovery로 같은 value를 제공할 수 없다.** directory listing, metadata scan, on-demand generated view로 같은 답을 얻을 수 있다면 manifest를 만들지 않는다.

path가 manifest의 identity이므로 manifest는 id 또는 version field를 갖지 않는다. frontmatter는 nature, mode, owner를 선언한다.

**Mode와 marker.** mode는 *manual*, *generated*(whole file), *mixed* 세 가지다. generated file은 generator를 지목하고 hand edit를 금지하는 top-of-file sentinel을 갖는다. mixed file은 각 generated region을 exact **paired marker**로 감싸며 네 가지 exclusivity rule을 적용한다. (a) marker 안은 generator-exclusive다. 그 안의 hand edit는 regeneration diff에서 드러나는 lint error다. (b) marker 밖은 generator-untouchable이다. 그곳에 쓰는 generator는 defective다. (c) marker 자체는 hand-owned이며, 하나를 추가·제거·이동할 때 inventory/design-change procedure를 거친다. (d) nesting은 금지한다. drift는 regenerate 후 diff하여 감지한다. exact form이 아닌 marker-*like* line은 무시할 것이 아니라 error다. near-miss marker는 generated region이 조용히 regeneration 대상에서 빠지는 방법이기 때문이다. token 뒤에 세 가지 올바른 spelling만 오는지를 찾지 말고 *어떤* keyword가 오든 탐지한다. keyword 자체의 typo는 좁은 probe에서 ordinary prose로 읽히는데, 바로 그것이 이 규칙이 잡으려는 경우다. checker가 out of scope로 취급하는 것(일반적으로 fenced example)은 모든 writer도 같은 방식으로 다뤄야 한다. 실제로는 각자 search하지 않고 같은 scan을 통해 marker를 찾는다는 뜻이다. checker는 fenced marker를 무시하면서 generator가 이를 rewrite한다면 clean document라고 보고하면서 example을 편집하게 된다.

**Carrier별 judgment contract.** 각 hand-written manifest는 자신의 currency contract를 선언한다. *orphan*(owned item은 있지만 row가 없음), *dead row*(row는 있지만 item이 없음)의 정의, 비교할 structured count, 그리고 결정적으로 check가 **flag하면 안 되는 것**을 선언한다. bulk item을 row 하나로 압축하는 series line, 다른 manifest를 가리키는 single pointer row, explicit zero-count sentence, row capsule 안의 prose가 그 예다. 그런 contract가 없는 hand-written manifest는 silent pass가 아니라 **error**다.

**Empty state.** item이 0개일 때도 file, header, explicit "0 items" statement를 모두 유지한다. empty input에 아무것도 출력하지 않는 generator는 defective다.

**Registry cross-check.** existence, mode, path는 registry에서 가져오고 owner와 detail은 manifest 자체 frontmatter에서 가져오며, check가 둘을 양방향으로 비교한다. 어느 쪽도 상대를 다시 진술하지 않는다. registry는 item instance를 절대 열거하지 않고, manifest는 structure 또는 path를 다시 진술하지 않으며 대신 registry에 link한다.

### 존재 이유

**Ownerless enumeration은 쇠퇴하며, named owner의 존재 여부가 다른 어떤 속성보다 쇠퇴를 잘 예측한다.** 누구에게도 update 의무가 없는 index도 current로 읽히므로 눈에 보이는 gap 대신 확신에 찬 오답을 만든다. 이 때문에 owner wiring은 manifest 생성과 **같은 commit**에 반영되어야 한다. ownerless index가 존재하는 repository state는 이미 decay가 시작된 state다.

**Missing file은 fail-open이다.** parser는 absent file을 조용히 skip하므로 manifest 삭제는 error로 드러나지 않고 그것을 읽던 check를 증발시킨다. 그래서 empty-state rule이 필요하며, 폐지 순서도 다음과 같아야 한다. retention condition의 상실을 기록하고, inventory를 수정하고, consumer를 re-wire한 뒤에야 file을 제거한다. consumer가 여전히 읽을 때 먼저 삭제하면 아무 signal 없이 enforced rule을 unenforced rule로 바꾼다.

**Generated region 안의 hand edit는 사라진다.** edit는 다음 regeneration까지 살아 있다가 흔적 없이 사라지고, author는 fix가 반영되었으며 reviewer가 그 반영을 봤다고 믿는다. marker discipline과 regeneration-diff check를 함께 적용해야만 이를 감지할 수 있다.

**Carrier별 contract가 없는 currency check는 추측해야 한다.** 추측하는 check는 legitimate compressed row를 끊임없이 flag하여 무시되게 되거나 모든 것을 통과시켜 decorative가 된다. undeclared carrier를 error로 만들면 check가 판단하기 전에 contract가 존재할 수밖에 없다.

**보존할 가치가 있는 반례.** Append-only record category에는 이 하네스에서 의도적으로 hand-written index를 **두지 않는다**. on-demand generated view가 같은 질문에 답하므로 세 번째 retention condition이 실패하여 manifest를 만들지 않는다. 이 규율은 manifest를 유지하는 것만큼이나 만들지 않는 것에 관한 규율이다.

### 도입 방법

1. 기존 index를 모두 나열한다. 각각에 세 조건을 정직하게 적용한다. 실패하는 것은 consumer를 re-wire한 뒤 삭제한다.
2. 살아남은 항목의 frontmatter에 typed owner string을 추가한다. owner를 지목할 수 없다면 그것이 답이다. 해당 index는 존재해서는 안 된다.
3. 살아남은 집합을 registry(A2)에 inventory canon으로 mode 및 disposition과 함께 선언하고 bidirectional cross-check를 추가한다.
4. exact paired marker와 regenerate 후 diff하는 drift check로 generator를 구현하고 기본값을 error로 둔다(E2).
5. 각 hand-written manifest에 exclusion list를 포함한 carrier별 judgment contract를 작성한다. undeclared carrier는 실패하게 한다.
6. manifest creation과 abolition이 decision gate를 거치게 하고 owner wiring을 같은 commit에 반영한다.

### 의존 대상 / 없을 때 깨지는 것

- **A2** — registry는 manifest inventory와 disposition을 보유한다. 이것이 없으면 어떤 manifest가 존재해야 하는지에 대한 canonical answer가 없고 cross-check는 비교할 것이 없다.
- **E1** — drift와 currency check를 producing procedure에 연결해야 한다.
- **E2** — drift check는 기본값이 error여야 하며 closed check set에 속해야 한다.
- **F1** — generated manifest와 generated procedure adapter 모두를 포괄하는 shared marker grammar와 단일 drift check가 없으면 각 generator가 자체 marker form을 만들고, 그중 하나의 near-miss form이 어떤 check도 알아차리지 못한 채 regeneration을 멈춘다.
- **B1** — retention condition의 상실과 abolition decision은 evidence chain으로 기록한다. 이것이 없으면 index가 사유 기록 없이 삭제되고 다음 agent가 다시 만든다.

### 변경할 경우

CORE. marker syntax, owner-string grammar, mode name은 자유롭게 정할 수 있다. 세 가지 retention condition, same-commit owner wiring, 네 가지 marker exclusivity rule, fail-closed empty state, "undeclared carrier = error"가 이 메커니즘이다.

## B1 — 이벤트 사슬

**등급: CORE**(여섯 갈래 분리와 그 category name은 **DEFAULT**). 지속적인 evidence chain이 없으면 repository의 모든 rule은 누군가 기억하는 rule에 불과하고, self-improvement는 drift와 구분할 수 없게 된다.

### 정의

다섯 종류의 record와 하나의 queue로 구성하며, 각각 `{category}-{number}-{slug}-{date}`라는 이름을 가진 개별 immutable-or-status-bearing file이고 filename은 identifier와 같다.

- **Run receipt** — run에서 읽고 만들고 수정한 것, 통과하거나 warning이 발생한 quality dimension, agent가 해결하지 못한 것을 기록한다. **발급된 뒤에는 immutable이며 status field 자체가 없다**. statelessness가 그 정의다. state가 바뀔 수 있는 receipt는 더는 실제로 일어난 일의 기록이 아니다. Quality는 **dimension마다 기록하고 하나의 score로 절대 합치지 않는다**. 단일 숫자로는 조치할 수 없기 때문이다. 정반대 이유로 실패한 두 artifact가 같은 value를 받고, aggregate는 어느 dimension이 변했는지 숨긴다. 하나의 숫자로 합치려는 압력은 실제로 존재한다. 숫자 하나는 sort하고 chart로 만들 수 있다. 그 대가는 receipt가 무엇을 고쳐야 하는지 알려주지 못하게 되는 것이다.
- **Verbatim feedback** — E5의 protected span 안에 바이트를 보존한 사용자 자신의 말. 절대 번역·요약·정규화하지 않는다. protected span 주변에는 scope, feedback type, status, 그리고 agent의 해석임을 명시적으로 표시한 optional interpretation note라는 agent의 classification을 둔다.
- **Interpretation / proposal** — 무엇이 변경되어야 하는지에 관한 agent의 해석. upstream evidence link를 적어도 하나 포함하며, evidence가 없으면 error다. 또한 **어떤 attempt도 수행하기 전에 동결한 success-criteria section**을 포함한다.
- **Evaluation** — 미리 등록한 criteria, 즉 proposal의 frozen section 또는 regression fixture identifier에 *reference로* 결속된 verdict. status는 running 또는 concluded이며 verdict는 concluded일 때만 존재한다.
- **Decision** — outcome만 담는다. 무엇을 결정했고 무엇에 영향을 주는지 기록한다. reasoning narrative는 담지 않으며 upstream에 남겨 link한다. rollback과 supersession은 삭제나 별도의 correction document가 아니라 **원래 decision의 status transition**이다. machine field는 actual diff와 registry에서 파생한 affected target(직관으로 선언해서는 안 됨), decision이 요구하는 check identifier, 그리고 verification-receipt identifier 또는 explicit not-applicable reason 중 정확히 하나다. validator가 인용한 receipt의 존재를 독립적으로 확인한다.
- **Deferred queue** — 인정했지만 지금은 실행하지 않는 item. status와 사용자가 자유롭게 쓸 수 있는 low-friction inbox를 포함한다. agent는 inbox entry를 queue item으로 바꾸면서 classification을 backfill하고 inbox를 비운다. item은 절대 삭제하지 않으며 done state로 이동한다.

여섯 범주가 공유하는 metadata는 filename stem과 같은 identifier, filename의 date와 동기화된 date, controlled vocabulary에서 가져온 layer 및 domain tag, producing procedure, document 작성에 사용한 form version이다.

### 존재 이유

**결과가 존재하기 전에 criteria를 동결한다.** attempt 뒤에 success criteria를 작성하면 evaluator는 벌어진 일을 보고 만든 criteria로 채점하며 모든 change가 통과한다. 누구도 이를 부정직함으로 경험하지 않는다. post-hoc criteria는 옳은 criteria처럼 느껴지며, 바로 result가 이를 형성했기 때문에 그렇다. freezing만이 유일한 방어이고, earlier separate document에 freeze되어 있을 때만 작동한다.

**Verbatim protection.** 보호되지 않은 correction은 선의로 agent가 이미 믿고 있던 내용으로 paraphrase된다. review에서는 compression이 보이지 않는다. summary는 괜찮아 보이지만 실제 constraint를 담고 있던 사용자의 특정 단어는 사라진다. byte preservation은 의식이 아니다. 나중에 correction을 다시 읽고 system이 결론 내린 의미와 실제 의미가 달랐음을 발견할 유일한 방법이다.

**Receipt와 state의 분리.** mutable receipt는 그 시점에 무엇이 참이었는지 더는 말할 수 없으므로 evidence가 아니게 된다. 반대로 decision이 full reasoning을 inline으로 담으면 supersede할 때 reasoning을 rewrite하게 되고, chain은 superseded decision이 당시에 옳아 보였던 이유를 보여줄 능력을 잃는다.

**Diff에서 파생한 machine field.** 직관으로 선언한 impact list에서는 작성자가 건드렸다는 사실을 잊은 file이 체계적으로 누락된다. actual change와 registry에서 affected target을 파생하면 regression selection(E3)이 의존하는 gap을 닫는다.

**"not now"를 위한 queue.** explicit deferral state가 없으면 "not now"와 "no"를 구분할 수 없다. 같은 defect가 다시 보고되고, 사용자는 자신의 어떤 요청이 버려졌는지 기억해야 하며, system은 backlog를 조용히 잃는다.

### 도입 방법

1. operating-contract layer 바로 아래에 category마다 directory 하나씩(여섯 개 또는 아래 설명에 따라 더 적게)을 sibling으로 만든다. shared parent 아래에 중첩하지 않는다. flat sibling arrangement는 각 category path가 registry에서 하나의 exact declaration으로 유지되게 한다.
2. category마다 blank form을 하나씩 작성하고 form version을 관리한다. record는 자신이 작성된 form version을 선언하므로 form change가 old record를 소급해 무효화하지 않는다.
3. proposal에서 frozen-criteria section을 required body section으로 만들고, evaluation의 criteria reference는 required이며 verdict가 반영된 뒤 편집할 수 없게 한다.
4. run receipt에 status field를 금지한다. 이 schema rule은 frontmatter check(E4)로 강제한다.
5. 각 producing procedure가 사후 작업이 아니라 procedure의 일부로 receipt를 내보내게 한다(E1).
6. deferred queue에 schema가 없는 plain-text inbox를 둔다. capture 시점의 마찰 때문에 backlog가 죽는다.

### 의존 대상 / 없을 때 깨지는 것

- **B2** — 모든 record는 numbered resource다. single-writer numbering이 없으면 chain에 duplicate identifier가 쌓이고 link가 ambiguous해진다.
- **E1** — 실제로 작동하는 procedure가 record를 작성하도록 wiring되어 있을 때만 chain이 일어난 일을 기록한다.
- **E4** — closed frontmatter schema가 category별 rule(status는 여기서는 forbidden, 저기서는 required)을 enforceable하게 만든다.
- **E5** — verbatim protection이 feedback record를 paraphrase가 아니라 evidence로 만든다.
- **B3** — promotion ladder가 이 chain을 소비한다. chain이 없으면 promotion에는 evidence가 없어지고 가장 최근에 주장한 사람을 따르는 것으로 퇴화한다.
- **A2** — 각 category directory는 exact declaration이다. category name에서 directory name을 추론하면 rename이 숨겨진다.

### 변경할 경우

여섯 갈래 분리와 category name은 **DEFAULT**다. 다음 다섯 경계가 살아 있다면 document를 병합할 수 있다. 예를 들어 evaluation을 decision에 합치거나 interpretation을 나중에 자체 verdict도 갖는 proposal에 합칠 수 있다.

1. 사용자의 말과 agent의 해석은 heading이 아니라 byte level에서 분리된다.
2. success criteria는 attempt보다 먼저 존재하는 record에 동결된다.
3. 그 criteria에 대한 verdict는 이를 실행한다는 decision과 구분할 수 있어야 한다. 최소한 verdict가 반영된 뒤 criteria reference가 immutable이어야 한다.
4. immutable하고 stateless한 run receipt는 mutable state carrier와 구분할 수 있어야 한다.
5. deferral은 absence가 아니라 explicit state다.

경계 1과 2는 single merged document로 보존할 수 없는 두 경계다. 둘 다 한 부분이 작성되고 봉인된 뒤 다른 부분이 존재하는 데 의존하기 때문이다. split의 다른 모든 것은 filing convenience다. 여기의 evidence는 프로젝트 하나에서 나왔고, 여섯 갈래 형태는 처음부터 설계된 것이 아니라 연속적인 splitting으로 도달했다. count는 incidental로, 다섯 boundary는 finding으로 취급한다.

## B2 — 번호 부여 규율

**등급: CORE**(digit width, date syntax, per-category versus single global sequence는 **PARAMETER**). evidence chain에서 identifier가 중복되면 다른 모든 mechanism이 읽는 link가 손상된다.

### 정의

보편적인 core는 정확히 세 가지다. **numbered resource의 single global writer, duplicate-issuance recovery procedure, guaranteed detection timing.**

**Single global writer.** owner session만 new number를 발급한다. delegated 및 isolated execution, 즉 subagent, isolated workspace, side branch는 **절대 발급하지 않는다**. 이들은 unnumbered draft를 반환한다. owner session은 active isolated workspace와 branch 전체에서 collision을 scan한 뒤 최신 mainline snapshot에서 identifier를 할당한다. mainline만 확인해서는 안 된다. 유일한 예외는 owner session이 자체 isolated workspace에서 작업할 때이며, 그때도 issuance는 C2의 serialized critical section 안에서만 수행할 수 있다.

**Derived next number.** next identifier는 issuance 시점에 계산한 category의 current maximum plus one이다. counter field는 유지하지 않는다. issuance를 rollback하거나 identifier를 수작업으로 복구하는 순간 counter가 reality와 drift하기 때문이다. (item이 directory 사이를 이동하는 queue는 합리적인 예외다. 그 경우 queue manifest의 counter가 두 directory를 scan하는 것보다 저렴하고 observed maximum과 대조한다.)

**Immutable identifier.** Filename stem은 frontmatter identifier와 같다. 일단 발급하면 number, slug, date를 포함한 whole identifier는 immutable하다. slug의 typo도 그대로 둔다. 유일한 예외는 duplicate recovery가 강제하는 renumbering이며, document의 previous name, renumbered time, reason을 기록한다.

**Recovery.** duplicate를 감지하면 **나중** issuance를 next free number로 renumber한다. first-add commit time으로 precedence를 정하고, 모호하면 context를 읽어 결정한다. earlier issuance와 그 모든 reference는 건드리지 않는다.

**Provenance-bounded reference rewiring.** 도입자가 잘못 이해하는 부분이다. old stem은 legitimate first issuance와 duplicate가 공유하므로 repository-wide substitution을 하면 올바르게 first issuance를 가리키던 reference까지 duplicate 쪽으로 조용히 다시 연결된다. 따라서 candidate reference는 duplicate의 first commit 이후에 추가된 것으로 제한한다. 그 commit 전에 작성한 것은 모두 반드시 first issuance를 가리켰다. 각 candidate를 history와 개별적으로 대조한다. **candidate 하나라도 구분할 수 없다면 automatic rewiring을 멈추고 manual judgment로 넘긴다.** 중단된 migration은 보이지만 잘못 연결된 reference는 보이지 않으므로, 잘못 연결하는 것보다 멈추는 것이 낫다.

**Detection timing.** global uniqueness check가 존재하며 producer wiring(E1)이 commit 전 실행을 보장한다. 누군가 기억해서 실행하는 것이 아니다. reference가 퍼지기 전에 detection해야 recovery candidate set을 commit 한두 개로 줄일 수 있다.

**Naming form(parameters).** `{category}-{zero-padded number}-{slug}-{date}`이며 date는 frontmatter field와 동기화하고 mismatch는 error로 처리한다.

### 존재 이유

**Isolated validation이 볼 수 없는 collision.** isolated working copy 두 개가 각각 "current maximum plus one"을 계산하고 서로 다른 slug에 같은 number를 발급한다. 어느 copy도 다른 copy를 볼 수 없으므로 각 copy의 validator는 통과한다. 두 문서를 integrate할 때까지 아무것도 실패하지 않는다. 그 시점에는 두 document가 각각의 workspace에서 작성된 다른 document에 이미 reference되었으므로, merge 결과 하나의 identifier를 가진 valid-looking record 두 개와 unique target으로 resolve되지 않는 link 집합이 생긴다. 이 하네스가 운영된 단 하나의 프로젝트에서 한 번 측정되었지만 우발적이 아니라 구조적인 문제다. partitioned view에서 평가하는 모든 maximum-plus-one scheme에 존재하며 per-workspace validation을 아무리 해도 감지할 수 없다.

**Mutable identifier는 모든 reference를 dangling risk로 만든다.** slug typo를 고칠 수 있다면 fix 전에 작성한 reference는 stale이며, "rename으로 link가 stale함"과 "link가 애초부터 틀렸음"을 구분할 방법이 없다. identifier를 freeze하면 보기 흉한 slug 하나를 대가로 영구적인 referential stability를 얻는다.

**Counter는 거짓말한다.** stored counter와 observed maximum은 abandoned issuance 첫 건에서 갈라지고, 누군가 number를 재사용할 때까지 divergence는 조용히 남는다.

### 도입 방법

1. naming form을 선택해 freeze한다. 이를 인식하는 anchored regular expression을 작성하되, slug의 last token 자체가 date처럼 보이면 안 된다는 rule도 포함한다. 그렇지 않으면 date segment가 ambiguous하다.
2. owner session만 발급한다는 rule과 delegated execution은 unnumbered draft를 반환한다는 rule을 작성한다. policy에만 두지 말고 delegation instruction에 명시한다. subagent는 contract tree가 아니라 prompt를 읽는다.
3. uniqueness check를 구현하고 issuance하는 모든 procedure에 wiring한다(E1). check catalogue에 error level로 등록한다(E2).
4. 필요해지기 전에 provenance bound와 stop-on-ambiguity rule을 포함한 recovery procedure를 기록한다. incident 중에는 아무도 provenance bound를 first principle에서 도출하지 않고 global substitution을 실행한다.
5. record schema에 "renumbered from" field를 추가하여 recovered document가 스스로 설명되게 한다.

### 의존 대상 / 없을 때 깨지는 것

- **C2** — serialized issuance critical section은 isolated workspace에서 일하는 owner가 안전하게 발급할 유일한 방법이다. 이것이 없으면 owner 자신의 isolation이 single-writer discipline을 무너뜨린다.
- **C1** — 처음부터 partitioned view를 만드는 것이 isolation이다. 두 mechanism은 함께 설계되어 있다.
- **E1** — detection timing은 희망이 아니라 wiring으로 보장한다. 이것이 없으면 reference가 퍼진 뒤 duplicate가 발견되어 recovery 비용이 커진다.
- **B1** — chain은 numbering의 대상이다. **A2**는 각 category path를 정확히 declare하므로 category directory가 조용히 rename될 수 없다.

### 변경할 경우

**Parameter.** *Digit width*: 여기서는 4를 사용했다. 다시 padding하지 말고 digit을 덧붙이는 방식으로 확장하여 이미 발급한 identifier가 유효하게 유지되게 한다. 더 좁은 width는 아무것도 절약하지 못하고 이른 migration을 강요한다. *Date syntax*: identifier에 creation date를 포함하면 record가 스스로 sort되고 slug collision이 드물어지지만 동기화해야 할 field가 하나 더 생긴다(mismatch = error). 이를 제거하면 chronological readability를 잃지만 synchronization surface 하나를 없앤다. *Per-category versus one global sequence*: per-category는 number를 작게 유지하고 reader가 category volume을 추론할 수 있게 하지만 serialize해야 할 sequence가 늘어난다. one global sequence는 critical section과 계산할 maximum이 하나지만 number가 빨리 커지고 number만으로 category를 읽을 수 없다.

**대체물이 보존해야 하는 것**은 다음과 같다. 어느 순간에도 issuing authority는 정확히 하나다. recovery procedure는 *later* issuance의 이름을 바꾸고 provenance로 reference rewiring 범위를 제한한다. detection point는 누군가 생각날 때 실행하는 것이 아니라 producing procedure에 wiring되어 있다.

정당한 대안으로 문제 종류 자체를 제거할 수 있다. content-hash 또는 random identifier에는 writer, critical section, recovery procedure가 필요 없다. 대가로 human-readable ordering과 "다음 것이 43번이다"라고 말할 가능성을 잃는다. 이 길을 택한다면 완전히 택한다. maximum-plus-one rule을 함께 유지하지 말고 버려야 한다. hybrid는 benefit 없이 collision을 다시 도입하기 때문이다.

## B3 — 승격 사다리와 선호 생명주기

**등급: CORE**(three-level scope split은 **DEFAULT**). promotion path가 없으면 verified knowledge가 binding되지 않거나 처음 발견되는 순간 모든 곳에서 binding된다.

### 정의

둘 다 세 단계인 사다리가 두 개 있으며, 서로 다른 사다리다.

**Promotion ladder — 지식이 enforcement가 되는 방법.**
1. **Non-binding technique note** — "violation"이라는 개념이 의미가 없는 knowledge. 한 번 도움이 된 craft, heuristic, pattern. 저장하고 version은 없으며 절대 check하지 않는다.
2. **Profile 또는 contract** — 위반이 실패가 되는 rule. versioned이며 적용 scope를 식별한다.
3. **Automated check** — closed check catalogue(E2)에 identifier를 두고 validator가 enforce하는 rule.

**Rung 2 옆에는 worked-example ledger가 필요하며, 도입자가 바로 이 부분을 건너뛴다.** judgment에 관한 rule, 즉 clear prose의 기준이나 adequate summary의 기준은 rule sentence 하나만으로 전달할 수 없다. 두 reader가 같은 sentence를 반대 verdict에 적용하고도 모두 자신이 준수했다고 믿는다. 해결책은 rejected form, accepted form, 둘을 구분하는 한 줄로 이루어진 matched pair ledger다. 꾸며내지 않고 실제 correction에서 자라나야 한다. review 때가 아니라 **작성 전에** 참고한다. review 시점에는 이미 artifact가 존재하고 reviewer가 이미 투입된 work와 논쟁하기 때문이다. ledger는 append-by-design이므로 rebuild counter(B4)에서 exempt이며 tidy를 위해 entry를 prune하지 않는다. 지금 명백해 보이는 pair는 ledger가 이를 가르쳤기 *때문에* 명백하다.

rule이 판단이 아니라 분류를 수행하는 경우(domain, kind, status의 controlled vocabulary)에는 이에 해당하는 규율이 있다. **vocabulary는 closed이며 이를 확장하려면 gate를 거친다.** 맞는 term이 없을 때 새 term을 추가할 수 있는 agent는 언제나 맞는 것이 없다고 결론 내리고, 몇 달 안에 author마다 value가 하나씩 생긴다. 분류를 거부하는 것이 올바른 결과이며, 이는 새 string이 아니라 vocabulary decision이 필요하다는 signal이다.

Knowledge는 반복적으로 검증될 때 rung 하나를 올라간다. verification 자체는 evidence chain의 일(proposal → evaluation)이며 storage layer는 단지 선반이다.

**Preference lifecycle — 사용자가 밝힌 희망이 rule이 되는 방법.** preference마다 하나의 file을 두며 statement, scope, event chain으로 연결되는 evidence link, candidate → active → superseded라는 status, 그리고 unresolved contradiction을 위한 **conflict**를 담는다. transition에는 다섯 규칙이 적용된다.

1. global rule을 요청하는 explicit user request는 **candidate**를 만든다. agent가 effect와 side effect를 설명하고, user가 confirm한 뒤에만 active가 된다.
2. 한 artifact에 대한 correction 한 건은 local record로 남는다. 그것만으로 global rule로 **절대** promote하지 않는다.
3. 서로 *다른* artifact에서 같은 preference가 recurring하면 candidate로 promote할 수 있다.
4. contradicting feedback은 **scope별로 split**한다. older preference를 삭제하지 않는다. contradiction을 resolve할 수 없으면 가장 최근에 말한 사람을 따라 해소하지 않고 preference를 `conflict` status로 유지한다.
5. explicit change가 있으면 old file은 `superseded`로 남기고 new file에서 link한다.

Scope는 this artifact, class of artifacts(profile 또는 document type), global의 세 level이다.

### 존재 이유

**Premature globalization이 이 mechanism이 방지하려는 failure이며, 구체적인 형태를 가진다.** 맥락에서는 실제로 옳은 correction 하나가 모든 것에 적용되는 rule이 된다. 몇 주 뒤 다른 맥락에서 contradicting feedback이 오고, 그것도 옳다. local과 global의 두 scope level만 있으면 "이 class에는 참이지만 모든 곳에는 그렇지 않다"를 둘 곳이 없으므로 누군가 새 rule을 넣기 위해 old rule을 삭제한다. old rule이 옳았던 case는 이제 사라지고, 이전에 옳았다는 record도 남지 않는다. 그러면 system은 oscillate한다. new correction마다 previous correction을 overwrite하고, user와 agent 모두 두 correction이 실제로 충돌한 것이 아니라 서로 다른 artifact class에 관한 것이었다는 사실을 볼 수 없다. middle scope tier가 해결책 전체다.

**Promotion ladder에 middle rung이 없으면** 반대 방향으로 같은 pathology가 생긴다. 모든 observation이 rule(그 결과 사소한 것까지 enforce되어 rule set이 unusable해짐)이거나 note(그 결과 verified finding이 advisory로 남음) 중 하나가 된다. machine rung에 도달하지 않는 rule은 읽히는 만큼만 준수되며, 몇 달이 지나면 거의 읽히지 않는다.

**Prose aggregate ledger는 item별 status를 담을 수 없다.** preference가 document 하나의 bullet point로 존재하면 한 entry의 supersession을 위해 shared file을 edit해야 한다. status transition은 edit에서 사라지고 evidence link는 cleanup 중 prune되며 conflict state를 둘 곳이 없다. preference마다 file 하나를 두어야 status와 evidence가 살아남는다.

**Conflict는 resolution이 아니라 status다.** contradiction의 패자를 삭제하면 나중 review에서 둘의 scope가 달랐다는 사실을 알아챌 evidence가 파괴된다. contradiction을 눈에 보이게 유지하는 것은 불편하지만 옳다.

### 도입 방법

1. non-binding technique note의 storage location을 만들고 그곳의 어떤 것도 enforce하지 않는다고 charter에 명시한다. finding을 넣을 다른 곳이 있어야 premature rule-making을 막을 수 있다.
2. preference마다 file 하나를 두고 statement, scope, evidence link, status를 저장한다. status enum에는 explicit conflict value를 포함한다.
3. 세 consumer를 wiring한다. feedback-recording procedure가 candidate를 만들고, periodic review procedure는 explicit user approval(D3)을 거치는 promotion 및 supersession gate이며, validator는 file shape를 enforce하고 active인 모든 것에 evidence link를 요구한다.
4. never-globalize-a-single-correction rule, 즉 "do not promote a single feedback event into a global rule"을 standing prohibition으로 approval boundary에 기록한다. 도움을 주려는 agent가 가장 자연스럽게 위반할 rule이기 때문이다.
5. rule이 third rung에 도달하면 closed catalogue에 해당 check를 error level로 등록하고 regression fixture를 binding한다(E2, E3).

### 의존 대상 / 없을 때 깨지는 것

- **B1** — evidence link는 event chain을 가리킨다. 이것이 없으면 promotion에는 substantiation이 없고 assertion으로 퇴화한다.
- **D3** — promotion은 approval boundary를 넘는다. approval sequence가 없으면 agent가 자신의 interpretation을 promote한다.
- **E2** — check가 govern될 때만 top rung이 존재한다. ungoverned check는 warning으로 낮출 수 있으며 promotion이 조용히 되돌아간다.
- **E3** — promoted rule이 나중에 변경되면 다시 실행할 fixture는 memory가 아니라 binding으로 선택한다.

### 변경할 경우

**three-level scope split은 DEFAULT**다. 대체물에는 최소한 "this document"와 "everything" 사이에 한 tier가 필요하다. two-level local/global split은 위에서 설명한 oscillation을 가끔이 아니라 확실하게 일으킨다. middle tier가 document type, profile, directory, task class 중 무엇인지는 프로젝트가 선택한다.

promotion rung의 number와 name 역시 유연하게 정할 수 있다. 대체물이 보존해야 하는 것은 failure가 될 수 없는 knowledge를 둘 곳, knowledge가 binding되고 versioned되는 explicit transition, machine이 enforce하는 terminal rung, storage format과 무관하게 preference마다 하나인 status carrier다. evidence base는 프로젝트 하나지만, style guide에 contradictory rule이 쌓이는 것을 본 사람이라면 누구나 이 mechanism이 막는 failure를 보고한다.

## B4 — 문서 재작성 임계값

**등급: DEFAULT**(threshold value는 **PARAMETER**). counter-and-threshold 형태에는 한 프로젝트의 evidence가 있으며 다른 trigger도 작동할 수 있다. 그러나 누적된 patching을 rebuild로 바꾸는 무언가는 반드시 필요하다. normal review에서는 이를 실행시키는 것이 전혀 없기 때문이다.

### 정의

policy가 적용되는 모든 document는 **마지막 full rebuild 이후의 semantic partial edit** 횟수를 나타내는 integer counter를 가진다.

**Transition.** New document: 0. Semantic partial edit(surgical fix, section added): +1이며 versioned contract는 version도 increment한다. sweep, move, rename, link rewiring, regeneration, metadata backfill 같은 mechanical work에서는 counter가 변하지 않는다. full rebuild는 0으로 reset한다. rollback은 그대로 둔다. policy 도입 전의 document를 처음 건드릴 때 측정할 수 있으면 measured value를 설정하고, 그렇지 않으면 threshold에서 saturate하고 이유를 기록한다.

**Gate.** threshold(원본 프로젝트에서는 3)에 도달하면 *다음* modification request에 대한 default response는 또 다른 patch가 아니라 **rebuild proposal**이다. user는 "just patch it this once"라고 override할 수 있고, 이 경우 date와 instruction의 요지를 담은 one-to-one **exception receipt**를 기록한다. threshold를 넘은 상태에서 receipt 수가 (level − threshold)보다 적으면 **validator failure**다. receipt는 counter를 절대 reset하지 않으며 rebuild만 reset한다.

**Exemption.** log, manifest, glossary, inventory, queue, example ledger, entry document처럼 정상 동작이 row를 append하는 document는 counter와 mutually exclusive인 literal boolean field로 exempt임을 선언한다. filename pattern은 first-pass classifier이며 self-declaration이 canonical이다. pattern은 technique note가 append-by-design이라는 사실을 볼 수 없기 때문이다.

**Class별 제외.** immutable input, event record, generated artifact는 policy 밖에 둔다. 앞의 둘에는 surgical edit 개념이 없고 세 번째는 canonical source에서 count한다.

**Rebuild protocol**에는 실제 risk가 존재한다.

- **rewriter는 original도 discarded candidate도 읽지 않은 independent agent**다. 입력은 frozen content requirement와 applicable contract뿐이다.
- **orchestrating agent는 rebuild를 절대 작성하지 않는다**. 원본에서 다른 agent 두 명이 독립적으로 추출한 **union inventory**를 기준으로 candidate의 omission을 확인하는 것이 역할이다.
- candidate는 temporary path에 stage하고 live document를 replace하기 전에 compare한다. 각 inventory item은 satisfied, repaired, deliberately dropped 중 하나로 표시한다. deliberate drop은 그렇게 명시한다.
- rebuild를 시작할 때 live document의 **baseline content hash**를 기록하고 landing 직전에 다시 비교한다. Mismatch = automatic stop이다. rebuild 중에 들어온 real modification이 rebuild에 우선한다. stale candidate와 inventory는 폐기하거나 new snapshot을 기준으로 다시 실행한다. arbitrary merge는 하지 않는다.
- receipt는 baseline 및 candidate hash, 두 inventory, item별 disposition, independent review verdict, re-verification result를 기록한다. machine-regenerable part는 전문 대신 count와 classification으로 기록할 수 있다. multi-document campaign에서는 중단된 campaign을 committed evidence에서 재개할 수 있도록 각 document의 receipt를 해당 document change와 함께 commit한다.

claim을 source까지 추적해야 하는 knowledge document에서는 inventory를 **claim별로** 추출한다. 각 item은 supporting reference, attribution class(source claim, agent inference, user statement), confidence를 binding한다. claim/source separation과 silent confidence inflation이 rebuild에서 일어나는 일급 손실이며, reference list가 단순히 여전히 존재하는지만으로는 어느 것도 감지하지 못하기 때문이다.

### 존재 이유

**Patch-on-patch decay는 edit별 review에서 보이지 않는다.** 각 edit는 개별적으로 올바르므로 아무것도 실패하지 않는다. 저하되는 것은 whole이다. section마다 tone과 detail level이 어긋나고, early paragraph와 late paragraph가 같은 rule을 다르게 진술하며, reader는 무엇이 current인지 알 수 없다. 다음 agent는 이를 해소하는 일이 request scope 밖이므로 confusion을 뚫고 고치는 대신 그 *주변을* patch한다. 단일 edit가 아니라 accumulation에서 발동하는 trigger가 없으면 이는 절대 드러나지 않는다.

**Original을 읽은 rewriter는 이를 물려받는다.** old document를 제공받은 agent는 rebuild 대신 restructure한다. section order를 보존하고 phrasing을 재사용하며 rebuild를 촉발한 바로 그 defect를 재생산하면서도 자신이 document를 rewrite했다고 정직하게 보고한다. blank-slate reconstruction을 얻을 수 있는 유일하게 신뢰할 만한 방법은 original을 주지 않는 것이다.

**Single inventory extractor는 rewriter도 놓치는 것을 놓친다.** independent extraction 두 개를 union하면 reader 한 명의 attention에서 빠진 item을 잡을 수 있다. 두 extraction의 disagreement 자체가 signal이다.

**Stale snapshot에 landing하는 rebuild는 real edit를 덮어쓴다.** rebuild가 진행 중일 때 누군가 live document의 error를 고치고, rebuild가 land하면서 그 fix가 사라진다. rebuild는 success를 보고하고 error가 다시 보고될 때까지 loss는 보이지 않는다. landing 직전 baseline-hash를 다시 비교해야 collision이 크게 드러난다.

### 도입 방법

1. metadata schema에 counter, receipt list, exemption boolean을 추가하고 exemption과 counter 사이의 mutual exclusion을 schema check(E4)로 enforce한다.
2. semantic change와 mechanical change를 명시적으로 정의한다. 이 boundary를 모호하게 두면 counter를 조작할 수 있게 된다.
3. threshold에서 aggregate warning을, 그 이후에는 hard failure를 구현한다. warning만 구현하지 않는다. warning은 reminder이고 failure가 mechanism이다.
4. history를 reconstruct하려 하지 말고 existing document를 threshold에서 backfill한다. 이는 counter를 retroactive accusation이 아니라 work queue로 바꾸며, 오래된 repository에서는 유일하게 감당할 수 있는 선택이다.
5. role split을 명시한 rebuild protocol을 procedure로 작성하고 staging step과 baseline comparison 없이는 실행할 수 없게 한다.

### 의존 대상 / 없을 때 깨지는 것

- **D1** — role split(rewriter, inspector, two inventory extractors)은 orchestration pattern이다. director/worker separation이 없으면 orchestrating agent가 rebuild를 직접 작성하여 protocol의 core가 무너진다.
- **C1** — live document를 real edit에 열어 둔 채 rebuild는 isolation에서 실행한다. 그것이 baseline gate를 필요하게 하고 가능하게 하는 바로 그 조건이다.
- **B1** — receipt는 event record다. chain이 없으면 이를 지속적으로 둘 곳이 없다.
- **E1**, **E4** — counter gate는 실제로 실행되어야 하는 metadata check다.

### 변경할 경우

**Threshold(PARAMETER).** 3 미만에서는 coherence damage가 보통 여전히 local이고 patch가 실제로 더 저렴하지만, 3에서는 edit가 서로 상호작용하기 시작하므로 3을 선택했다. 이를 높이면 decay가 되돌리기 비싸지고 rebuild도 그에 따라 커질 때까지 detection이 늦어진다. 낮추면 실제로 필요하지 않은 document에 protocol의 실질적인 비용(document마다 agent 3~4명)을 쓰게 되고, 예측 가능한 결과로 사람들이 gate를 따르지 않게 된다. threshold는 exemption rule과 상호작용한다는 점에 유의한다. 실제로 append-by-design인 document가 너무 많은데 exemption을 사용하지 않으면 낮은 threshold가 constant false trigger를 만든다.

**Mechanism(DEFAULT).** 대체물은 size growth, edit recency clustering, periodic review sweep, reviewer judgment call 같은 다른 trigger를 사용할 수 있다. 그러나 세 속성을 보존해야 한다. trigger는 누군가 decay를 알아차리는 데 의존하지 않고 **자동으로** 발동한다. exception path는 informal하지 않고 **machine-checked**되어 "just this once"가 standing practice가 될 수 없다. content-preservation protocol에는 **rewriter가 아닌 extractor**가 있다. 세 번째를 버리면 rebuild는 더 깔끔해 보이는 document를 만들면서 content를 잃는 효율적인 방법이 된다.

## English brief

This chapter defines the provenance layers, structure registry, layer-change gate, and manifest discipline that make repository structure enforceable rather than advisory. It also specifies the evidence chain, serialized identifier issuance and recovery, promotion and preference lifecycles, and an automatic threshold-driven document rebuild protocol. The Korean text preserves the original mechanism tiers, dependencies, break conditions, parameters, machine-facing tokens, and procedural constraints.
