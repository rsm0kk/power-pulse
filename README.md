# Power Equipment Pulse — 전력기기 대시보드

## 폴더 구성
```
power_pulse.py    수집기 + HTML 생성기  ← API 키가 들어있음. 절대 공유 금지
template.py       HTML 템플릿 (하우스 스타일)
run.bat           더블클릭 실행 (Windows)
store.json        누적 데이터 (자동 생성, 지우지 말 것)
cache/            DART 기업코드 캐시 (자동 생성)
out/              완성된 HTML  ← 이것만 공유
```

## 최초 1회
1. Python 3.9+ 설치 (python.org, 설치 시 **Add Python to PATH** 체크)
2. `power_pulse.py` 상단 `CUSTOMS_KEY` 에 관세청 인증키(Decoding) 붙여넣기
   - DART / FRED 키는 이미 들어있음
3. 외부 라이브러리 설치 불필요 (표준 라이브러리만 사용)

## 실행
- `run.bat` 더블클릭, 또는 `python power_pulse.py`
- 2~4분 소요. 콘솔에 소스별 성공/실패가 찍힘
- `out/전력기기_대시보드_YYYYMMDD.html` 생성 → 이 파일만 텔레그램 공유

## 매일 자동 실행 (선택)
Windows 작업 스케줄러 → 작업 만들기 → 트리거: 매일 07:30
→ 동작: 프로그램 시작 → 프로그램 `run.bat`, 시작 위치는 이 폴더 경로

## 미리보기
`python power_pulse.py --demo` → 합성 데이터로 화면만 확인 (실제 수치 아님)

## 데이터 소스
| 패널 | 소스 | 갱신 |
|---|---|---|
| 수출 P/Q, 품목별 실적 | 관세청 품목별 국가별 수출입실적 | 월 (확정 2개월 지연) |
| 분기 실적, 공시 | DART Open API | 분기 / 수시 |
| 미국 수요지표, 구리 | FRED | 월 |
| 리드타임·GOES·수주잔고 | 화면 내 수기 입력 | 수시 |

## 주의
- 관세청 확정치는 약 2개월 지연. 기준월이 최근월이 아닌 게 정상.
- HTML 안 수기 입력값은 브라우저에 저장됨. 캐시 삭제 대비해 **[JSON 내보내기]** 로 백업 권장.
- 실패한 항목은 화면 하단 **수집 상태** 패널에 표시됨. store.json 덕분에 실패해도 직전 데이터는 유지됨.
