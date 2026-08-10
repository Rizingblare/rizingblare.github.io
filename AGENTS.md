# 범용 에이전트 하네스 운영 계약

<!-- harness:begin v1 -->

<!-- harness:registry-locator schema/kernel/layout.yaml -->

## 계약의 경계와 bootstrap

이 문서는 범용 운영 계약의 정본인 동시에 도구가 자동으로 읽는 완성된 AGENTS entry다. exact harness marker 안의 범용 운영 의미와 bootstrap 순서를 소유하며 bootstrap에 필요한 exact fixed registry locator를 위 machine marker로 직접 제공한다. generated projection용 envelope, whole-file sentinel과 deterministic provenance를 이 entry에 덧붙이지 않는다.

실제 directory·file·charter·entry document·gate의 path와 구조 role은 layout registry가 유일하게 소유한다. project Manifest는 프로젝트 목적과 non-goal, 언어 정책의 정확한 값, 실행 기본값, task class와 tool별 binding 값을 소유한다. approved generator config는 `harness-sync`와 `harness-lint` 두 canonical skill을 각각 다른 tool adapter의 동명 skill로 투영하는 mapping, projection envelope와 deterministic provenance만 소유한다. 실행 때마다 달라지는 task·dispatch·terminal·worktree 식별자와 launch 결과는 runtime record가 소유하며 registry, Manifest, generator config나 이 계약에 복사하지 않는다.

실행 주체는 auto-load된 이 AGENTS entry의 machine marker가 제공하는 exact locator로 layout registry를 정확히 하나 찾는다. registry의 `canonical_contract` pointer가 가리키는 target이 auto-load된 entry와 같은 AGENTS bytes인지 검증하고, `project_manifest` pointer가 가리키는 project Manifest를 읽는다. canonical contract pointer 검증은 별도 source를 다시 load하는 단계가 아니며 bootstrap dependency를 순환시키지 않는다. 그 뒤 다음 순서를 따른다.

1. auto-load된 이 canonical contract entry
2. machine marker가 가리키는 layout registry
3. registry가 가리키는 project Manifest
4. registry가 현재 작업에 대해 선언한 charter, entry document와 적용 대상 schema
5. 현재 절차에 필요한 blank form, skill, tool adapter

뒤 단계는 앞 단계의 의미를 바꿀 수 없다. 다만 실제 path와 구조 role은 registry에서, 프로젝트별 값은 Manifest에서, 두 skill projection의 mapping·envelope·provenance는 approved generator config에서만 읽는다. 정적 `@AGENTS.md` 포인터는 generated projection이 아니며 이 bootstrap을 canonical entry로 전달하기만 한다. 같은 사실이 다른 source나 projection에 반복되어 다르면 어느 한쪽을 우선하는 것으로 봉합하지 말고 drift로 실패시킨다.

이 AGENTS entry의 exact fixed registry locator, layout registry, `canonical_contract` pointer, `project_manifest` pointer 중 하나라도 없거나 읽을 수 없거나, 무결성 검사를 통과하지 못하거나, 각각 정확히 하나의 repository-contained target을 결정하지 못하면 project-aware 작업을 시작하지 않는다. 특히 저장소 쓰기, identifier 발급, stage, commit, push, 구조 변경은 금지한다. 누락 사실은 사용자에게 명시한다.

## Registry, Manifest와 projection의 책임

layout registry는 tracked structure의 단일 정본이다. 실제 path, path group과 owner, adopted provenance layer, charter와 entry document, schema, public exposure 대상과 gate를 선언하고, harness entry와 skill의 각 path를 공통 `contract` role로 닫힌 형태로 선언한다. canonical·static·generated 세부 구분은 registry top-level pointers와 approved generator mapping이 소유한다. registry에 없는 실제 path를 Manifest나 adapter가 새로 정의할 수 없다. `canonical_contract`와 `project_manifest`는 각각 정확히 하나의 상대 pointer여야 하며 repository 밖으로 벗어나거나 서로의 source 역할을 대신할 수 없다.

project Manifest는 다음 프로젝트별 값의 단일 정본이다.

- 프로젝트 목적과 non-goal
- 사용자 reply, durable prose, naming, metadata와 protected text에 대한 언어 정책의 정확한 값
- harness, supervisor, worktree와 opt-out의 실행 기본값
- task class와 model tier, tool별 model·effort, delegation·supervision capability와 launch record field binding

approved generator config는 `harness-sync`와 `harness-lint` 각각의 canonical skill에서 다른 tool adapter의 동명 skill로 가는 두 projection의 mapping, source ownership, envelope, sentinel과 deterministic provenance field만 소유한다. 두 canonical skill은 source이고 두 adapter skill만 generated projection이며, 별도의 규칙, 실제 path 또는 프로젝트 기본값을 소유하지 않는다. generator는 AGENTS entry나 정적 `@AGENTS.md` pointer entry를 render하지 않고 registry locator도 소유하지 않으며, canonical skill을 임의로 해석하거나 고치지 않고 승인된 mapping대로 감싼다.

이 canonical AGENTS entry와 정적 pointer entry에는 generated skill projection의 envelope나 provenance record를 넣지 않는다. 반대로 두 rendered adapter skill target에는 approved generator config가 요구하는 envelope, sentinel과 provenance가 각각 정확히 하나 있어야 한다. canonical AGENTS entry의 harness marker는 skill projection sentinel을 대신하지 않고, skill projection sentinel도 canonical contract marker를 대신하지 않는다.

registry, Manifest 또는 generator config가 새 필드나 제약을 도입하는 변경은 그 값을 닫힌 형태로 검사하는 validator와 성공·실패 fixture를 같은 semantic unit에 포함한다. 검증되지 않은 canonical data를 먼저 history에 넣고 validator를 뒤 commit으로 미루지 않는다.

배포 권한이나 공개 환경 설정처럼 현재 작업에 필요하지 않고 독립적으로 확인되지 않은 사실은 필수값으로 만들지 않는다. 실제 절차가 그 사실을 필요로 할 때만 권위 있는 근거로 확인하고, 확인하지 못하면 추측하지 않는다.

## Meaningful unit과 실행 축

meaningful unit은 artifact나 repository state를 만들거나 바꾸는 작업, 외부 side effect를 일으키는 작업, 또는 이후 판단의 근거가 될 분석·권고·평가·결정을 산출하는 작업이다.

Manifest의 현재 unit 기본값은 bootstrap 직후 적용한다. Manifest가 harness와 supervisor를 default-on으로 선언한 경우 그 선언은 write 작업뿐 아니라 pure read-only 답변을 포함한 모든 meaningful unit에 적용된다. pure read-only라는 이유로 면제되는 것은 새 dedicated worktree 생성뿐이며, harness, supervisor, evidence, approval, review 의무는 면제되지 않는다.

각 실행 축의 의미는 다음과 같다.

- **Harness**: 이 계약의 bootstrap, provenance, evidence, approval, gate, review, closure 절차를 unit의 시작부터 끝까지 적용한다.
- **Supervisor**: artifact 실행자와 분리된 감독 주체가 unit의 assignment, 경계, writer ownership, 충돌, 진행 상태, completion과 자원 disposition을 관리한다. supervisor는 감독 중인 artifact의 작성자나 자기 작업의 closure reviewer가 될 수 없다.
- **Dedicated worktree**: repository에 쓰는 unit이 다른 session과 공유하지 않는 branch와 worktree에서 실행된다는 뜻이다.

supervisor가 필요한 unit에서는 bootstrap과 unit 분류에 필요한 최소 read-only 확인을 마친 직후, 첫 task-specific repository 조사, tool call, delegation, candidate 작성 또는 외부 action보다 먼저 supervisor를 시작하고 그 ownership을 확인한다. 이미 시작된 supervisor가 현재 unit과 실행자를 명시적으로 소유하지 않으면 재사용하지 않는다. 요구된 supervision capability를 현재 tool binding이 제공하지 않거나 검증할 수 없으면, Manifest가 허용한 capable binding으로 실행을 옮기거나 fail-closed로 중단한다. capability 부재를 supervisor opt-out으로 바꾸지 않는다.

repository write가 예상되는 unit은 task-specific 작업을 시작하기 전에 dedicated worktree와 branch를 확보하고 writer ownership을 확인한다. 처음부터 끝까지 파일 생성·수정·삭제, identifier 발급, stage, commit, stash, branch 변경을 전혀 하지 않는 pure read-only 답변만 현재 worktree를 공유할 수 있다. read-only unit에 write 필요가 생기면 즉시 멈추고 dedicated worktree로 옮긴 뒤에만 첫 write를 수행한다.

## 명시적 current-unit opt-out

실행 기본값을 끄는 권한과 허용 축은 Manifest가 선언한다. 허용된 경우에도 opt-out은 사용자가 현재 unit과 끌 축을 명시적으로 지정한 때만 성립한다. 침묵, 비용이나 시간 압박, tool 부재, agent의 편의, 이전 unit의 opt-out, 또는 “간단히 하라”와 같은 모호한 표현은 opt-out이 아니다.

opt-out은 지정된 축과 현재 unit에만 적용된다. supervisor opt-out은 harness나 worktree를 끄지 않고, harness opt-out도 다른 축을 끄지 않는다. 사용자가 여러 축을 명시하지 않았다면 cascade하지 않는다. 다음 unit은 Manifest 기본값으로 자동 복귀하며, 대화·branch·worktree·하위 작업으로 상속되지 않는다. 축이나 unit 경계가 불명확하면 질문으로 확정할 때까지 기본값을 유지한다.

사용자의 정확한 opt-out 문구는 feedback record의 protected region에 byte-for-byte로 보존한다. observation은 그 feedback을 pointer로 참조하고 적용한 축, current-unit 경계, 실제 효과만 기록한다. observation에 사용자 문구를 다시 적거나 정규화하여 feedback을 대신하지 않는다.

어떤 opt-out도 system·developer 안전 규칙, destructive action 제한, 비밀 보호, 외부 접근 승인, push 권한처럼 더 높은 권한 경계를 해제하지 않는다.

## Provenance 계층과 exposure state

프로젝트는 실제로 사용하는 계층만 layout registry에 선언하고 charter를 둔다. 채택하지 않은 계층의 placeholder directory를 만들지 않는다. 범용 계층의 의미는 다음과 같다.

- **Immutable inputs**: 외부나 원본에서 들어온 보존 대상이다. 직접 고치지 않으며, correction은 재수입한 원본이나 추적 가능한 derived material에서 수행한다.
- **Derived material**: 하나 이상의 input에서 추적 가능하게 파생한 자료다. source pointer와 derivation 방향을 유지한다.
- **Generated outputs**: input의 기계적 파생이 아니라 inference로 생성한 결과다. 별도 근거 없이 source truth로 취급하지 않는다.
- **Operating contract**: 계약, Manifest, registry, schema, blank form, validator와 evidence 연결 규칙이다. 콘텐츠 계층을 지배하지만 domain knowledge를 대신하지 않는다.

공개·비공개 여부와 배포 상태는 provenance layer가 아니라 artifact의 exposure state다. exposure가 바뀌어도 artifact의 source layer는 바뀌지 않으며, exposure transition은 source pointer, 승인, 대상과 검증 결과에 연결한다. 공개되었다는 사실만으로 artifact가 source truth가 되지 않는다.

어떤 artifact도 registry가 허용한 provenance 계층 중 정확히 하나로 분류되거나, registry가 명시한 합법적 cross-layer projection이어야 한다. 새로운 계층 값을 사용하려면 이 계약의 의미 정의와 validator를 먼저 승인받아 같은 semantic unit에 반영한다.

계층을 채택할 때는 directory, registry 선언과 charter를 같은 commit에 넣는다. charter에는 무엇이 들어오는지, 누가 편집할 수 있는지, derivation이 어느 방향으로 흐르는지를 적고 처음 쓰기 전에 읽는다. 여러 계층이 같은 사실을 담으면 registry와 charter가 정한 reading precedence를 따르며, 원본 검증 요청은 immutable input까지 추적한다.

registry는 추적 대상 경로에 fail-closed로 적용한다. 선언되지 않은 tracked path는 warning이 아니라 실패다. directory 추가·이동·삭제는 구조 변경으로 취급하고, registry·charter·실제 tree의 관련 변경을 같은 commit에 둔다.

## Evidence와 승인된 적용 순서

판단을 생산하는 unit은 registry가 가리키는 schema의 blank form으로 evidence를 남긴다. record를 만들기 전에 해당 form을 읽는다. category의 책임은 섞지 않는다.

- **Observation**: unit이 실제로 한 일, 측정값, 검증 가능한 사실과 source pointer를 기록한다. 생성 후 불변이고 status field를 두지 않는다. 사용자 원문은 담지 않고 feedback을 가리킨다.
- **Feedback**: 사용자가 쓴 bytes를 protected region에 그대로 보존한다. 맞춤법, 공백, 줄바꿈, 언어, encoding 표현을 정리하지 않으며 source digest와 byte count로 무결성을 검증한다.
- **Proposal**: feedback과 observation에 대한 해석, 제안 변경, 범위, 작업 전에 동결한 success criteria를 담는다.
- **Evaluation**: 정확히 하나의 proposal이 동결한 criteria에 대해서만 candidate를 평가하고 concluded verdict를 남긴다. criteria를 사후 변경하지 않는다.
- **Decision**: 정확히 하나의 concluded evaluation을 근거로 outcome만 기록한다. 근거를 다시 서술해 evaluation을 대신하지 않는다.
- **Deferred**: 실재하지만 지금 적용하지 않는 일을 이유와 재검토 조건과 함께 queue에 보존한다. 삭제로 대체하지 않는다.

feedback의 원문 record는 한 발화를 임의로 쪼개지 않는다. scope, recurrence, remediation status, proposal candidacy는 서로 다른 축과 link로 기록한다. `candidate-rule` 같은 승격 상태를 scope 값으로 사용하지 않는다. 반복 observation이 없으면 recurring으로 분류하지 않으며 “재발할 수 있다”는 추정만으로 반복성을 만들지 않는다. 하나의 feedback이 여러 요구를 담으면 protected record 하나를 유지한 채 필요한 proposal이나 remediation link를 여러 개 연결한다.

`main에 반영됨`, `runtime 조치 완료` 같은 상태 주장은 각각 해당 commit이나 runtime observation pointer로 입증한다. pointer가 없거나, exactly-one 관계의 cardinality가 0 또는 2 이상이거나, protected bytes·digest·byte count가 맞지 않거나, frozen criteria와 evaluation 기준이 다르면 evidence chain은 실패다.

구조, operating contract, schema와 그에 준하는 canonical 변경은 다음 순서를 바꿀 수 없다.

1. 관찰한 사실을 tool call이나 변경과 분리된 사용자 turn에서 prose로 보고한다.
2. 질문을 통해 방향과 범위를 합의한다.
3. proposal과 success criteria를 작성하고 criteria를 동결한다.
4. canonical clause의 정확한 wording과 실행 범위를 보여 주고, wording 승인과 실행 승인을 명시적으로 받는다.
5. 승인된 wording과 범위만 dedicated worktree에 non-canonical candidate로 구현한다.
6. gate와 독립 adversarial review로 candidate를 frozen criteria에 대해 evaluation한다.
7. concluded evaluation에 근거한 decision을 기록한다.
8. 승인된 decision 뒤에만 candidate를 canonical 위치와 mainline에 적용하고 application pointer를 observation에 남긴다.

candidate 구현은 canonical 적용이 아니다. evaluation 전의 candidate commit, branch, worktree 또는 generated preview를 정본으로 취급하거나 배포하지 않는다. evaluation이 없거나 미결이거나 실패하면 적용 decision을 만들 수 없고 canonical application도 할 수 없다. candidate가 바뀌면 새 digest 또는 고정 commit range로 gate와 review를 다시 수행한다.

review round에서는 candidate를 canonical에 적용하지 않는다. 사용자의 실행 승인은 정확한 wording 승인과 별개이며, 한쪽만 확인되면 다른 쪽을 추측하지 않는다. 승인 없이 canonical에 적용했다면 그 적용을 안전하게 원복하고 proposal 단계로 돌아간다.

feedback 하나는 자동으로 규칙이 되지 않는다. 승격은 feedback과 observation에서 proposal·approval·candidate·evaluation·decision·canonical application으로 이어져야 한다. 실무 technique은 합의된 contract가 된 뒤에만 automated check로 강제한다.

## 검증 gate와 adapter 동기화

layout registry가 선언한 producer gate는 artifact를 commit하기 전에 실행한다. gate는 최소한 Manifest 무결성, registry와 tracked path의 일치, contract marker와 protected bytes, generated adapter drift, 해당 artifact의 schema·content 검사를 포함한다. 실패가 0개여야 하며 warning은 해결, 명시적 수용, deferred 중 하나로 각각 분류한다.

다음 행위는 서로 분리한다.

1. 검증 명령을 실행한다.
2. 전체 출력과 종료 상태를 읽고 판정한다.
3. 판정이 끝난 뒤 별도 행위로 commit한다.

shell chain, script의 자동 후속 commit, 읽지 않은 성공 표시로 이 경계를 합치지 않는다. 출력이 잘렸거나 결과를 읽을 수 없으면 통과로 간주하지 않는다. artifact를 만드는 절차가 commit 직전에 gate를 호출하지 않으면 그 절차 자체를 결함으로 보고한다.

두 canonical skill 또는 두 projection의 approved generator config를 변경한 뒤 generated adapter skill을 갱신할 때는 source·schema preflight, deterministic sync, adapter drift를 포함한 full lint, no-op sync check 순서로 수행한다. 계약이나 Manifest 변경도 preflight와 full lint 대상이지만 adapter target으로 render하지 않는다. drift는 sync 전의 예상 상태일 수 있으므로 source preflight와 projection drift 검사를 같은 선행 조건으로 묶어 sync를 막지 않는다. 최초 generated skill target 채택은 사용자가 승인한 일회성 bootstrap 절차와 semantic unit 안에서만 허용하고, 일반 sync의 무제한 overwrite option으로 대체하지 않는다.

두 generated skill target은 사람이 직접 편집하지 않는다. sync는 timestamp, absolute machine path, runtime identifier, 현재 branch 같은 비결정적 값을 출력하지 않는다. 같은 입력에 대한 두 번째 check는 byte 변경이 없어야 한다.

## Git과 identifier

repository를 바꾸는 meaningful unit은 하나의 semantic commit으로 끝낸다. 하나의 commit에는 하나의 판단 가능한 단위만 넣고, 다른 작업이나 사용자의 기존 변경을 섞지 않는다. 시작 전에 working tree를 확인하며, 다른 작업의 변경이 있으면 소유권과 처리 방향을 확정하기 전까지 쓰지 않는다.

stage는 explicit path로 한다. 승격·소비·이동되는 하나의 항목에 필요한 source 제거, 새 canonical artifact, provenance pointer, registry·wiring 변경은 같은 commit에 둔다. 자신의 unpushed commit을 바로잡는 correction은 다른 session이 쓰지 않는 dedicated worktree에서 원래 semantic unit에 fold한다.

사용자가 요청하지 않으면 push하지 않는다. commit 권한은 remote 반영 권한이 아니다. mainline에는 merge commit을 만들지 않으며 사용자의 변경을 요청 없이 되돌리지 않는다.

identifier 발급자는 전체 저장소에서 어느 순간에도 정확히 한 명이어야 한다. delegated worker와 isolated execution은 unnumbered draft만 반환한다. 발급자는 최신 기준선 반영, 모든 활성 worktree·branch의 최댓값과 collision 재계산, identifier와 record의 same-commit 반영, 즉시 landing을 하나의 중단 없는 critical section으로 수행한다. landing이 실패하면 최신 상태에서 전체 절차를 다시 시작한다.

path group마다 writer도 정확히 한 명이어야 한다. 둘 이상의 unit이 같은 경로를 쓰려 하면 먼저 ownership을 이전하거나 하나를 중단한다. 서로 다른 기준에서 내린 판단을 뒤 merge로 봉합하지 않는다.

## Delegation, launch 검증과 독립 review

task class의 tier 의미와 tool별 exact model·effort binding은 Manifest에서만 읽는다. 사용자의 현재 unit에 대한 명시적 override가 허용되면 그 값이 해당 unit에서 우선하지만 다른 unit이나 tool로 이어지지 않는다.

delegated launch에는 requested tool·tier·model·effort를 label에 기록한다. 실행 도구가 저장한 authoritative launch record에서 effective 값을 읽어 requested·expected와 exact match인지 검증하며 log, window title, prompt text, worker의 자기 진술로 대체하지 않는다. Manifest가 정의한 record field binding으로 현재 unit, dispatch와 artifact digest가 같은 실행에 속하는지도 확인한다. record가 없거나 identity 또는 binding이 다르면 그 결과를 tier 요건 충족으로 인정하지 않는다.

비기계적 작업은 agent 한 명에게 artifact 하나만 맡긴다. 넓은 blank-page rewrite나 full rebuild는 Manifest가 지정한 rewrite tier의 독립 writer에게 frozen requirements만 주고, orchestrator가 omissions와 assembly를 확인한다. delegated worker는 identifier를 발급하거나 기본적으로 다시 delegate하지 않는다. 추가 독립 관점은 supervisor가 별도 sibling unit으로 발급한다.

Manifest가 특정 tool binding의 delegation이나 supervision capability를 disabled로 선언하면 그 binding으로 해당 capability가 필수인 unit을 시작하지 않는다. 다른 binding의 기본값을 복사하거나 검증되지 않은 실행 경로를 만들어내지 않는다.

Manifest가 harness와 supervisor를 default-on으로 선언한 모든 meaningful unit은 완료 선언 전에 독립 adversarial review를 거친다. reviewer는 unit의 writer나 supervisor와 달라야 하고, Manifest가 지정한 review tier와 launch 검증을 충족해야 한다. 대상은 움직이는 branch 이름이 아니라 고정 commit range 또는 immutable artifact digest로 지정한다.

parent meaningful unit의 이 review 의무만을 수행하도록 위임된 독립 reviewer의 evaluation artifact는 그 parent unit의 bounded component다. 이 bounded evaluation artifact에는 독립 review를 다시 재귀 적용하지 않는다. 대신 parent supervisor가 reviewer identity와 독립성, fixed commit range 또는 immutable artifact digest, parent proposal의 frozen criteria, concluded verdict와 evaluation artifact pointer가 모두 같은 review assignment에 결속되었음을 직접 검증해야 하며, 이 검증이 통과해야 parent unit과 reviewer component를 종료할 수 있다.

이 base case는 parent unit의 독립 review를 위해 명시적으로 위임되고 그 범위를 넘지 않은 evaluation artifact에만 적용한다. 독립적인 분석·권고·평가, 다른 unit에서 재사용되는 report, parent의 scope나 frozen criteria를 변경하는 판단, 또는 별도 proposal·decision의 근거가 되는 산출물은 bounded component가 아니며 일반 meaningful unit의 review 의무를 그대로 따른다. 편의상 작업 이름을 review로 붙이는 것만으로 이 예외를 사용할 수 없다.

reviewer는 요구 누락, provenance 단절, same-commit 위반, gate 우회, 사용자 변경 혼입, approval 순서 위반과 assembled whole 실패를 적극적으로 찾는다. component report가 맞아도 newcomer가 실제로 사용하는 경로로 assembly를 검증한다. 수정이 생기면 gate를 다시 실행하고 바뀐 고정 범위를 독립적으로 재검토한다. task 실행 완료는 closure 승인이 아니다.

## Supervisor의 완료·자원 책임

worker는 완료나 escalation을 supervisor에게 정확히 한 번 보고하고, 자신이 소유하지 않은 terminal·branch·worktree를 닫거나 제거하지 않는다. supervisor는 현재 unit과 dispatch identity를 검증한 뒤 다음 wait나 종료 전에 각 실행 자원에 대해 transfer, release, 명시적으로 승인된 retain 중 정확히 하나를 선택하고 기록한다.

timeout, heartbeat, idle 표시, 질문, escalation은 completion이 아니다. stale하거나 replay된 완료 신호도 현재 identity와 일치하기 전에는 처리하지 않는다. supervisor는 필요한 artifact가 보존되고, commit이 land되었고, worktree가 clean이며, 미완료 상태나 미결 identifier가 없음을 확인한 뒤에만 자원을 release하고 worktree를 제거한다. dirty 또는 미완료 상태는 fail-closed로 보존한다.

## Handoff와 미완료 stopping

완료 handoff는 모든 semantic unit이 commit되고 gate 실패가 0이며, successor에게 필요한 정보가 conversation이나 임시 파일이 아니라 committed canonical artifact에 있고, 소비된 volatile material이 정리되었을 때만 성립한다. handoff snapshot과 entry pointer 갱신은 같은 commit에 둔다. snapshot은 successor가 소비한 뒤 삭제하고 그 사실을 closing observation에 남긴다. 장기 ledger는 layout registry가 선언한 durable repository 영역에 둔다.

끝내지 못한 채 멈출 때는 volatile material을 포함한 현재 상태를 안전한 semantic unit으로 보존하고, 검증한 것과 다시 실행할 것을 구분해 기록한다. completion receipt 생성, done 표시, volatile material 삭제, worktree 제거는 실제로 마무리하는 unit만 수행한다.

## 외부 접근과 사용자 보고

외부 접근은 별도 승인 축이다. 일반적인 작업 승인만으로 web search, page fetch, 외부 자료 import 권한을 추론하지 않는다. 다만 사용자가 승인한 절차가 신뢰 가능한 source 취득을 필수로 요구하면 그 목적과 범위 안에서만 접근한다.

meaningful operation 뒤의 사용자 보고에는 읽은 파일, 만든 파일, 수정한 파일, conflict와 open question, commit hash와 subject, gate와 warning 처리, review 범위와 verdict, delegated execution의 requested/effective binding과 artifact, 하지 않았거나 확인하지 못한 범위를 포함한다. 해당 사항이 없으면 `없음`이라고 명시한다. 사용자 보고와 repository evidence record는 독자가 다르므로 서로를 대신하지 않는다.

## 언어와 보존 경계

모든 durable human-readable prose는 새 문서와 기존 문서를 포함해 Manifest의 language policy를 따른다. 기존 문서의 이주 범위가 크면 adapter나 기능 변경에 섞지 않고 별도 semantic unit으로 제안·승인·평가한다. 계약, projection, 문서가 Manifest의 정확한 언어값을 별도로 재선언하지 않는다.

file·directory name, metadata key, identifier, exact marker, tool·model·skill name과 protected region은 Manifest가 정한 machine-facing policy 또는 원래 bytes를 따른다. feedback protected bytes 보존은 prose language policy보다 강하다. language lint는 layout registry가 선언한 정확한 path 범위까지만 보장하며, 범위 밖까지 검사했다고 주장하지 않는다.

## English brief

This AGENTS entry is both the canonical operating contract and the complete auto-loaded tool entry; its machine marker supplies the registry locator. The registry owns structure and points to the canonical contract and project Manifest, while approved generator configuration owns only the two harness skill projections and their envelopes and provenance. The CLAUDE entry is a static pointer to AGENTS rather than a generated target. Publication is an exposure state rather than a provenance layer, while durable prose follows the Manifest language policy and protected bytes remain unchanged.

<!-- harness:end -->
