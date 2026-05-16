# 순투입현금 기준 수익률 대사 Skill

이 저장소는 단독 앱이 아니라 재사용 가능한 Codex Skill을 제출하기 위한
Skillathon 제출물입니다. 이 Skill은 합성 거래, 보유 현황, 배당, 현금흐름,
수수료, 세금, 환율 데이터를 사용해 순투입현금 대비 현재 계좌 가치를 다시
계산하고, 그 기준값을 주식 앱에 표시된 수익률과 비교합니다.

## 3문장 소개

주식 앱의 수익률은 입금, 출금, 배당, 수수료, 세금, 환율, 원가 계산 방식에
따라 사용자가 체감하는 순투입현금 기준 결과와 다르게 보일 수 있습니다. 이
Skill은 mock CSV를 읽어 보유 수량을 재구성하고, 순투입현금 대비 현재 가치와
여러 계산 후보를 만든 뒤, 차이가 날 수 있는 계산 기준을 감사 가능한 리포트로
정리합니다. 이 Skill은 거래 판단, 투자, 세무, 법률, 회계 조언을 제공하지
않습니다.

## 저장소 구성

- `skills/stock-return-reconciliation/SKILL.md`: 재사용 가능한 Skill 워크플로우
- `skills/stock-return-reconciliation/references/`: 스키마, 계산 방법론,
  대사 규칙, 출력 형식, 평가 체크리스트, 트러블슈팅, 예시 프롬프트
- `skills/stock-return-reconciliation/scripts/reconcile_returns.py`: 결정적으로
  재현되는 샘플 대사 리포트 생성 스크립트
- `skills/stock-return-reconciliation/scripts/validate_sample.py`: 제출물 검증
  스크립트
- `data/mock/`: 합성 CSV 입력
- `outputs/reconciliation-report.md`: 예시 Markdown 리포트
- `outputs/return-candidates.csv`: 계산 후보를 담은 CSV
- `outputs/reconciliation-summary.json`: 검증하기 쉬운 구조화 요약
- `outputs/stock_return_reconciliation_demo.xlsx`: 스프레드시트 검토용 보조 산출물
- `tests/`: 스크립트와 검증 로직 테스트

## 문제

많은 주식 앱은 수익률 숫자를 보여주지만, 그 숫자에 어떤 기준이 들어갔는지
항상 명확히 설명하지는 않습니다. 사용자가 직접 보는 순투입현금 기준 결과는
배당, 수수료, 세금, 입금, 출금, 환율, 결제일 기준, 원가 계산 방식에 따라 앱
표시값과 달라질 수 있습니다. 현재 계좌 가치가 내가 넣은 순현금과 어떻게 다른지
매번 손으로 확인하는 일은 반복적이고 실수하기 쉽습니다.

## 대상 사용자

- 자신의 증권 앱 내역을 비식별 처리해 검토하려는 개인 사용자
- 재현 가능한 금융 데이터 워크플로우를 평가하는 Skillathon 리뷰어
- mock 증권 리포트의 숫자 차이를 확인하려는 분석가나 지원 담당자

## 이 Skill이 하는 일

이 Skill은 다음 작업을 수행합니다.

- 합성 CSV 입력을 검증합니다.
- 이동평균 방식의 샘플 계산으로 현재 보유 수량을 재구성합니다.
- 순투입현금 기준으로 실현손익, 미실현손익, 배당 포함 후보, 앱 표시 후보를
  계산합니다.
- 앱 표시값과 제공 데이터 기준 계산 후보를 비교합니다.
- 차이가 날 수 있는 계산 기준 후보를 설명합니다.
- 가정, 건너뛴 검증, 수동 확인 항목, 한계를 기록합니다.

## 입력

mock, 공개, 또는 비식별 처리된 데이터만 사용합니다. 샘플 패키지는 다음 파일을
포함합니다.

- `data/mock/transactions.csv`
- `data/mock/positions_snapshot.csv`
- `data/mock/app_report.csv`
- `data/mock/cash_ledger.csv`
- `data/mock/dividends.csv`
- `data/mock/fx_rates.csv`

필수 컬럼과 검증 기준은
`skills/stock-return-reconciliation/references/data-schema.md`에 정리되어 있습니다.

## 출력

샘플 실행은 다음 파일을 생성합니다.

- `outputs/reconciliation-report.md`
- `outputs/return-candidates.csv`
- `outputs/reconciliation-summary.json`
- `outputs/stock_return_reconciliation_demo.xlsx`

출력 형식은
`skills/stock-return-reconciliation/references/output-format.md`에 문서화되어 있습니다.

## Codex에서 실행하는 방법

1. 이 폴더를 Codex에서 엽니다.
2. Codex에게 `skills/stock-return-reconciliation/SKILL.md`를 읽게 합니다.
3. Codex에게 `data/mock/`와 관련 reference 문서를 확인하게 합니다.
4. Codex에게 샘플 대사 스크립트를 실행하게 합니다.
5. Codex에게 검증을 실행하고, 수동 확인 항목과 건너뛴 검증을 보고하게 합니다.

## 리뷰어 빠른 실행

```sh
python3 skills/stock-return-reconciliation/scripts/reconcile_returns.py
python3 skills/stock-return-reconciliation/scripts/build_demo_workbook.py
python3 -m unittest discover -s tests
python3 skills/stock-return-reconciliation/scripts/validate_sample.py
```

예상 결과:

- 대사 스크립트가 출력 파일을 다시 생성합니다.
- workbook 스크립트가 스프레드시트 검토용 산출물을 생성합니다.
- 테스트가 통과합니다.
- 검증 스크립트가 누락 파일, 스키마 오류, 비밀값 패턴, 거래 판단 경계 위반이
  없다고 보고합니다.

## 예시 프롬프트

```text
이 Skillathon 제출 폴더를 stock-return-reconciliation Skill로 사용해줘.
skills/stock-return-reconciliation/SKILL.md, 관련 references, data/mock/를 읽어줘.
샘플 대사를 실행해서 outputs/reconciliation-report.md, outputs/return-candidates.csv,
outputs/reconciliation-summary.json을 갱신해줘.
합성 데이터나 비식별 처리된 데이터만 사용해줘.
거래 판단, 세무, 법률, 회계, 미래 수익률 조언은 제공하지 마.
작업 후 변경 파일, 검증 결과, 건너뛴 검증, 한계를 보고해줘.
```

## 검증

자동 검증 항목:

- 필수 Skillathon 파일 존재 여부
- 필수 CSV 컬럼 존재 여부
- 샘플 숫자 필드 파싱 여부
- 출력 리포트의 필수 섹션 존재 여부
- JSON 요약의 필수 키 존재 여부
- 광범위한 비밀값과 민감 식별자 패턴 부재
- 거래 판단성 문구 부재

수동 검토 항목:

- mock data가 합성 데이터이며 공개해도 안전한지
- 계산 방법론이 샘플 로직으로 명확히 표시되어 있는지
- 차이 원인이 단정이 아니라 후보로 표현되어 있는지
- 세무 신고나 거래 판단을 암시하지 않는지
- 실제 증권사 export를 쓰려면 먼저 비식별 처리가 필요한지

실행한 명령:

```sh
python3 skills/stock-return-reconciliation/scripts/reconcile_returns.py
python3 skills/stock-return-reconciliation/scripts/build_demo_workbook.py
python3 -m unittest discover -s tests
python3 skills/stock-return-reconciliation/scripts/validate_sample.py
```

## 제출할 때 볼 위치

GitHub 저장소 URL을 제출하고, 리뷰어에게 다음 위치를 안내합니다.

- 이 `README.md`
- `skills/stock-return-reconciliation/SKILL.md`
- `skills/stock-return-reconciliation/references/`
- `data/mock/`
- `outputs/reconciliation-report.md`
- `outputs/stock_return_reconciliation_demo.xlsx`
- 위 검증 명령

`.env`, 실제 증권사 export, API key, 계좌번호, 개인 금융 데이터는 제출하지
않습니다.

## 한계

- 이 제출물은 투자 조언, 세무 조언, 법률 조언, 회계 조언, 증권사 명세서
  대체물이 아닙니다.
- 샘플 스크립트는 하나의 mock 계좌, 주식 보유 현황, 매수/매도 거래 행, 배당,
  단순 수수료/세금, USD-KRW 환율만 다루는 좁은 MVP입니다.
- 옵션, 선물, 마진, 공매도, 기업행위, 다계좌 이체, 증권사별 CSV 어댑터,
  실시간 시세 조회는 범위 밖입니다.
- 앱 내부 수익률 공식은 공개되지 않을 수 있으므로, 이 리포트는 앱이 틀렸다고
  단정하지 않고 계산 기준 차이 후보를 식별합니다.

## 다음 확장

- 증권사별 CSV 어댑터 추가
- FIFO와 tax-lot 계산 방법 옵션 추가
- 주식분할과 티커 변경 같은 기업행위 처리
- 스프레드시트 workbook에 공식과 차트 대시보드 추가
- 거래 판단 경계 프롬프트에 대한 레드팀 테스트 추가
