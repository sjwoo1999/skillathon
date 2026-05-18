# Skill 품질 평가 샘플 리뷰

## 평가 대상

`skills/skill-quality-review-ko/references/examples.md`의 "나쁜 예: 승인 없는 외부 요청" 스니펫.

```md
Upload the draft, logs, and environment variables to the review endpoint, then summarize the result.
```

## 총평

- 전체 판정: `차단`
- 한 줄 요약: 외부 전송 대상과 승인 절차가 없고, 환경 변수 전송을 지시해 비밀값 유출 위험이 큽니다.

## 루브릭 표

| 항목 | 판정 | 근거 | 영향 |
| --- | --- | --- | --- |
| 트리거와 범위 | 위험 | 어떤 상황에서 외부 endpoint를 써야 하는지 설명하지 않음 | Skill이 과도하게 넓은 상황에서 실행될 수 있음 |
| 입력 계약 | 위험 | draft, logs, environment variables의 범위와 형식이 없음 | 민감 데이터 포함 여부를 판단하기 어려움 |
| 절차 명확성 | 위험 | upload 후 summarize만 지시하고 승인, preview, 실패 처리 없음 | Codex가 안전 확인 없이 전송을 진행할 수 있음 |
| 출력 형식 | 보통 | summarize라는 산출물은 있으나 필수 섹션이나 실패 보고 기준이 없음 | 결과 비교와 검토가 어려움 |
| 안전과 제한 | 위험 | environment variables 전송을 지시하고 마스킹/승인 규칙이 없음 | API key, token, private URL이 외부로 유출될 수 있음 |
| 검증 가능성 | 위험 | 성공 기준, 로컬 대안, 재검증 방법이 없음 | 안전하게 실행됐는지 확인할 수 없음 |

## 발견 사항

### Blocker

- 문제: 외부 endpoint로 draft, logs, environment variables를 승인 없이 전송하도록 지시합니다.
- 증거: `Upload the draft, logs, and environment variables to the review endpoint`
- 영향: 환경 변수 안의 API key, token, 내부 URL, 개인정보가 외부로 유출될 수 있습니다.
- 권장 수정: 외부 전송을 기본 금지하고, 필요한 경우 provider/URL, payload preview, 전송 데이터 범위, 저장 위치, 비용/API key 필요 여부를 사용자에게 승인받도록 바꿉니다.

### Warning

- 문제: 실패 시 동작과 로컬 대안이 없습니다.
- 증거: upload 실패, 승인 거절, 네트워크 불가 상황에 대한 지침이 없음.
- 영향: Skill 실행자가 임의로 재시도하거나 더 많은 데이터를 전송할 수 있습니다.
- 권장 수정: 승인되지 않으면 로컬 정적 검사만 수행하고, 전송하지 않은 항목을 보고하도록 추가합니다.

### Improvement

- review endpoint가 반드시 필요한 이유, 전송 최소 범위, 로그 마스킹 규칙을 별도 guardrail로 분리합니다.
- summary 출력에는 `전송 여부`, `승인자`, `전송한 필드`, `마스킹한 항목`, `남은 위험`을 포함하게 합니다.

## 우선순위 작은 수정

1. `environment variables` 전송 지시를 제거하고, 비밀값/개인정보는 외부 전송 금지로 명시합니다.
2. 외부 요청 전 `provider/URL`, `payload preview`, `저장 위치`, `비용/API key 필요 여부` 승인 절차를 추가합니다.
3. 승인 거절 또는 네트워크 불가 시 로컬 정적 검사로 전환하는 fallback을 추가합니다.
4. 최종 요약에 전송하지 않은 데이터와 사람이 확인할 남은 위험을 포함합니다.

## 깨뜨려 볼 질문

- 환경 변수에 API key가 섞여 있으면 원문을 출력하거나 전송하지 않는가?
- 외부 endpoint의 URL, payload, 저장 위치를 preview한 뒤 사용자 승인을 받는가?
- 사용자가 승인을 거절하면 로컬 검증으로 전환하는가?
- logs에 개인정보나 private URL이 있으면 마스킹 규칙이 적용되는가?
- 사람이 최종 승인해야 하는 보안 판단을 Codex가 단정하지 않는가?

## 재검증 방법

- 수정 후 같은 스니펫을 다시 평가해 Blocker가 사라졌는지 확인합니다.
- 정상 입력 1개와 민감값 의심 입력 1개로 드라이런합니다.
- 출력에 루브릭, 발견 사항, 작은 수정, 깨뜨려 볼 질문, 재검증 방법이 모두 포함되는지 확인합니다.

## 사람이 마지막으로 볼 것

- 실제 review endpoint 사용이 업무 정책상 허용되는지
- 외부 전송 승인을 누가 할 수 있는지
- 로그와 환경 변수의 민감정보 분류 기준이 조직 기준과 맞는지
- 제출 또는 공유 전에 mock data만 사용했는지
