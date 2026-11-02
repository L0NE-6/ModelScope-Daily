<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ModelScope Daily

**ModelScope 중국판과 국제판 일일 체크인을 위한 단일 파일 스크립트입니다. 토큰을 분리하고 마클릭(Magicube) 크레딧 원장 확인, 잔액, 사용량을 조회합니다.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 전체 중국어 문서는 [../README.md](../README.md)에서 확인하세요.

## ✨ 핵심 기능

- 중국판과 국제판 자격 증명을 분리합니다.
- `GET /api/v1/users/login/info` 호출로 일일 체크인을 발생시킵니다.
- 중국판은 `/openapi/v1/magicubes/transactions`로 크레딧 지급을 확인합니다.
- 같은 날짜의 `daily_active`와 `aliyun_bindlogin` 수익을 합산합니다.
- 총 크레딧, 사용 가능, 동결, 오늘의 추론 사용 횟수를 조회합니다.
- 대소문자 두 가지 응답 형식을 지원합니다.
- HTTP `401` 인증 실패와 HTTP `403` 위험 관리 차단을 구분합니다.

## 🧭 동작 방식

ModelScope에는 별도 체크인 버튼이 없습니다. 로그인 정보 API 호출이 일일 체크인을 발생시키며 반복 호출은 멱등입니다.

```text
ms- token
  → Cookie: m_session_id=<token>
  → GET /api/v1/users/login/info
  → 중국판은 당일 크레딧 원장 확인
  → 잔액과 사용량 조회
  → 성공 / 이미 수령 / 미확인 / 실패 보고
```

`--query`도 로그인 정보 API를 호출하므로 체크인을 발생시킵니다. 완전한 읽기 전용 모드는 없습니다.

## 🚀 최단 설정

```bash
python -m pip install -r requirements.txt
```

해당 ModelScope 콘솔에서 `ms-` 액세스 토큰을 만듭니다.

단일 계정:

```text
MODELSCOPE_CN_TOKEN=ms-CN_TOKEN
MODELSCOPE_INTL_TOKEN=ms-INTL_TOKEN
```

다중 계정:

```text
MODELSCOPE_CN_TOKENS=
중국판 메인|ms-CN_TOKEN
중국판 서브|ms-CN_TOKEN

MODELSCOPE_INTL_TOKENS=
국제판 메인|ms-INTL_TOKEN
```

실행:

```bash
python modelscope_daily.py
python modelscope_daily.py --only 1
python modelscope_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

`MODELSCOPE_CN_TOKENS`와 `MODELSCOPE_INTL_TOKENS`를 설정하고 작업을 만듭니다.

```text
30 8 * * * python3 modelscope_daily.py
```

처음 검증할 때 `--only`로 계정을 하나씩 확인할 수 있습니다.

## ☁️ GitHub Actions

워크플로는 [../.github/workflows/daily.yml](../.github/workflows/daily.yml)입니다. 수동 실행이 활성화되어 있고 일정 부분은 주석 처리되어 있습니다.

| Secret | 필수 | 용도 |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | 둘 중 하나 | 중국판 다중 계정 |
| `MODELSCOPE_INTL_TOKENS` | 둘 중 하나 | 국제판 다중 계정 |
| `MODELSCOPE_CN_TOKEN` | 둘 중 하나 | 중국판 단일 계정 |
| `MODELSCOPE_INTL_TOKEN` | 둘 중 하나 | 국제판 단일 계정 |
| `MODELSCOPE_PROXY` | 선택 | 프록시 |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 선택 | 알림 |

정기 실행을 사용하려면 주석을 해제하세요. `30 0 * * *`는 UTC이며 베이징 시간 08:30입니다.

## 🔧 주요 환경 변수

| 변수 | 설명 |
| :--- | :--- |
| `MODELSCOPE_CN_TOKENS` | 중국판 다중 계정: `이름\|ms-token` |
| `MODELSCOPE_INTL_TOKENS` | 국제판 다중 계정: `이름\|ms-token` |
| `MODELSCOPE_CN_TOKEN` | 중국판 단일 계정 |
| `MODELSCOPE_INTL_TOKEN` | 국제판 단일 계정 |
| `MODELSCOPE_PROXY` | HTTP(S) / SOCKS 프록시 |
| `MODELSCOPE_VERIFY_DELAY` | 중국판 원장 재조회 대기 시간, 기본 `2`초 |
| `MODELSCOPE_NO_NOTIFY` | `1`이면 알림 비활성화 |

## 📊 성공 기준

| 상황 | 판정 |
| :--- | :--- |
| HTTP `401` | 토큰 무효 또는 사이트 불일치 |
| HTTP `403` | 위험 관리 차단, 로그인 만료로 단정하지 않음 |
| 잔액 데이터 누락 | 조회 실패, 0으로 표시하지 않음 |
| 중국판 | 당일 `type=EARN`과 `daily_active / aliyun_bindlogin` 기록 필요 |
| 원장이 처음 비어 있음 | `MODELSCOPE_VERIFY_DELAY` 후 한 번 더 조회 |
| 국제판 | 별도 버튼 API 없이 로그인 발생 기준으로 보고 |

중국판에서 유효한 원장 기록이 없으면 “미확인”으로 표시하며 로그인 성공을 체크인 성공으로 가장하지 않습니다.

## 📦 릴리스 정보

현재 릴리스는 `v1.0.2`입니다. `401`과 `403`을 분리하고 잔액 데이터가 부족할 때 0으로 표시하지 않도록 수정했습니다. CHANGELOG에는 새 오프라인 테스트 7개, 총 11개 통과가 기록되어 있으며, 해당 회차에는 실제 계정으로 실사용 체크인 요청을 보내지 않았다고 명시되어 있습니다.

## 🔒 개인정보

- 계정 데이터를 수집하거나 업로드하지 않습니다.
- 로그에 전체 `ms-` 토큰을 출력하지 않습니다.
- `.env`와 로그 파일을 Git에 커밋하지 마세요.
- 토큰은 로컬 환경 변수, GitHub Secrets, Qinglong 변수에만 보관하세요.
- Issue를 작성하기 전에 토큰, 닉네임, 계정 ID, 원장 상세를 제거하세요.

## 🔗 링크

- [Releases](https://github.com/L0NE-6/ModelScope-Daily/releases)
- [Issues](https://github.com/L0NE-6/ModelScope-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
