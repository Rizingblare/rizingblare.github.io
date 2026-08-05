# 분류 모델 (taxonomy) — 2026-08-05 전면 재설계

codex 적대 검토가 확인한 결함(축 혼재, 경계 중복 22군/49항목, foundations 중복
표현, CS 미분할 집합체)에 대한 사용자 승인 재설계다. **콘텐츠 재작성이 아니라
메타데이터 재분류**이며, 발행 문서 URL은 카탈로그 도메인과 분리되어 있어
영향받지 않는다.

## English brief

Multi-axis classification replacing the mixed 13-domain partition:
`domain` = single-owner canonical topicDomain (15 values; CS split into 4,
foundations dissolved, current-affairs → general-knowledge), plus optional
cross-cutting `collections` (exam subjects, study tracks — scaffolded, exam
mappings pending user-provided data), and `contentType`/`validAsOf` for
time-sensitive items. RF boundary atoms follow an explicit ownership table.

## 축 1 — canonical topicDomain (`domain`/`primaryDomain` 필드, 단일 소유)

한 항목은 정확히 하나의 topicDomain이 소유한다(파일 = 도메인 = 샤드 구조 유지).

| topicDomain | 소유 범위 | 비고 |
|---|---|---|
| signal-processing | 신호의 수학·변환·분석, 변조 **이론** | RF 경계 소유 규칙 참조 |
| radio-antenna | 전파 전파·안테나·급전 **하드웨어**·무선설비·EIRP | |
| mobile-communications | 셀룰러 시스템·세대(1G~5G)·이동망 구조 | |
| broadcast-media | 미디어 제작·전송·영상·방송 표준 | |
| networking | 프로토콜·계층·전송·라우팅 | |
| databases | DB 모델·SQL·트랜잭션·설계 | CS에서 분할 |
| operating-systems | 프로세스·메모리·스케줄링·동기화 | CS에서 분할 |
| algorithms-data-structures | 자료구조·알고리즘·복잡도 | CS에서 분할 |
| computer-architecture | 디지털 논리·회로·컴퓨터 구조·주소지정 | CS에서 분할 |
| software-engineering | 방법론·요구·설계·테스트 | CS의 SW테스트 흡수 |
| programming | 언어 문법·코딩 추적(exercise) | |
| electronics-circuits | 소자·회로 해석·전력 | |
| information-security | 보안 원칙·접근통제·악성코드 | |
| telecom-regulations | 대한민국 법규·인증·설비 기준 | 유지(응집 확인됨) |
| general-knowledge | 일반상식·시사 스터디뱅크 | 구 current-affairs |

**해체**: `foundations` — 해체 시점 41건 = 전공 호스트로 이동 37건 + 기존
canonical과의 중복 통합 4건 (2026-08-06 실행 완료). "여러 도메인의 선수
개념"이라는 성질은 `profile: foundational-definition`이 이미 표현한다.

### RF 경계 소유 규칙 (동일 개념의 canonical 소유자)

- 변조/복조·검파 이론, 대역폭, 잡음, SNR, 헤르츠, 비트레이트 → **signal-processing**
- 급전선·임피던스 정합·EIRP·안테나 파라미터 → **radio-antenna**
- 셀 설계·핸드오버·듀플렉스·다중접속 → **mobile-communications**
- 코덱·영상 신호·방송망 구성(SFN 등) → **broadcast-media**
- 타 도메인이 그 개념을 다룰 때는 자체 사본이 아니라 canonical id를 참조한다
  (`atoms`, concept-ref). 사본 발견 = 중복 통합 대상.

## 축 2 — collections (선택 필드 `collections: [<slug>]`, 교차 소속)

topicDomain과 독립적으로 항목을 재집계하는 컬렉션. 정의부는
`knowledge/collections.json`(슬러그·이름·설명·종류)이 소유한다 —
`catalog/` 밖에 두는 이유: 카탈로그 디렉토리의 모든 JSON은 빌드가 도메인
샤드로 취급하기 때문이다.

- **시험 과목 컬렉션**(examSubject): 정보통신기사·무선설비기사·방송통신기사 등.
  **최신 과목 매핑 근거 데이터가 저장소에 없으므로**(codex 확인) 스캐폴드만
  두고, 사용자가 과목 구성을 제공하면 채운다 — 추정으로 채우지 않는다.
- **스터디 트랙**(studyTrack): 예: computer-general(컴퓨터일반 통합 복습 —
  CS 4분할의 시험 흐름 재결합), general-knowledge-bank.

## 축 3 — contentType / validAsOf (선택 필드)

- `contentType: "time-sensitive"` — 시점 의존 항목(구 current-affairs의 사건·
  제도·기록형). 개념형 항목(오프사이드, DSR 등)은 붙이지 않는다.
- `validAsOf: "YYYY" 또는 "YYYY-MM"` — 시점형 항목의 기준 시점. 제목·요약에
  리터럴로 실재하는 값만 기입한다(추정 금지).
- 구 `kind: current-affairs`는 kind 오용이므로 실제 kind(atomic/taxonomy)로
  교정하고 시점성은 contentType이 표현한다.

## 마이그레이션 규칙

1. id는 절대 불변 — 재분류는 `domain`/`primaryDomain`/`collections`/`contentType`
   필드와 소속 파일 이동만.
2. 이동 후 구 도메인 파일(foundations.json, computer-science.json,
   current-affairs.json)은 빈 배열이 아니라 **삭제**하고, 빌드 산출 샤드도
   함께 정리한다(고아 샤드는 `catalog-sync` 게이트가 잡는다).
3. `wiki/domains/<id>/` 랜딩은 신 도메인 세트로 재생성, 구 랜딩 경로는 신
   경로로 meta-refresh 리다이렉트 스텁을 남긴다.
4. 발행 문서 URL(`wiki/signal-communications/...` 등)은 카탈로그 도메인과
   무관하므로 불변.
