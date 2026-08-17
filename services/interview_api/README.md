# Clinical Interview API

이 서비스는 기존 `CoreInteractionSession`과 컴파일된 Knowledge Package를 외부 앱이 호출할 수 있게 하는 첫 Backend API입니다. Custom GPT 테스트 환경과 Knowledge 빌드 과정은 변경하지 않습니다.

## 현재 제공 범위

- 상호작용 목적 및 서비스 모드 목록 조회
- 임시 세션 생성, 답변 제출, 다음 질문/종료 상태 반환
- 현재 clinician handoff JSON 조회
- 세션 완료 또는 삭제 시 응답 상태 즉시 폐기
- TTL 만료에 의한 자동 폐기
- Bearer API key, 기본 CORS 차단, 요청 본문 비로깅

임상 콘텐츠는 `draft`, `unreviewed`, `limited use`입니다. 독립적인 진단·치료 결정에 사용하지 않습니다. 안전 신호는 진단을 확정하지 않고 보수적으로 알리며 의료인 확인으로 연결합니다.

FHIR `Questionnaire`, `QuestionnaireResponse`, SDC Extraction은 아직 이 API에 구현되지 않았습니다. 현재 결과 응답에도 이를 `not_implemented`로 명시합니다. 다음 구현 단계에서 기존 질문·Fact 바인딩을 사용해 추가합니다.

현재 API에서 실제 실행되는 모드는 `clinical_adaptive`(자유 문진)입니다. 목록에는 향후 연결할 다른 플랫폼 모드도 보이지만 `api_capabilities.pending_mode_ids`로 구분되며, 해당 adapter는 아직 응답을 수집하지 않습니다.

## 로컬 실행

저장소 루트에서 실행합니다. Python 3.11 이상 외에 별도 패키지는 필요하지 않습니다.

```bash
export CLINICAL_API_KEY='긴-무작위-테스트-키'
python3 -m services.interview_api
```

기본 주소는 `http://127.0.0.1:8000`입니다. API 계약은 [openapi.yaml](openapi.yaml)에 있습니다.

외부 인터페이스에 바인딩하려면 API key가 반드시 필요합니다.

```bash
CLINICAL_API_HOST=0.0.0.0 \
CLINICAL_API_KEY='긴-무작위-운영-키' \
python3 -m services.interview_api
```

운영 배포에서는 TLS를 종료하는 reverse proxy 또는 ingress 뒤에 두고, API key를 secret manager로 주입해야 합니다. 현재 구현은 단일 프로세스 메모리 세션이므로 여러 인스턴스로 확장하기 전에는 sticky routing 또는 별도의 암호화 세션 저장소가 필요합니다.

## 호출 예

목록을 조회합니다.

```bash
curl -s http://127.0.0.1:8000/v1/catalog \
  -H 'Authorization: Bearer 긴-무작위-테스트-키'
```

문진 세션을 바로 시작합니다.

```bash
curl -s http://127.0.0.1:8000/v1/sessions \
  -H 'Authorization: Bearer 긴-무작위-테스트-키' \
  -H 'Content-Type: application/json' \
  -d '{"mode_selection":"문진 시작","initial_message":"기침이 나요"}'
```

응답의 `session_id`를 사용해 다음 답변을 전송합니다.

```bash
curl -s http://127.0.0.1:8000/v1/sessions/SESSION_ID/messages \
  -H 'Authorization: Bearer 긴-무작위-테스트-키' \
  -H 'Content-Type: application/json' \
  -d '{"message":"3일 전부터 시작됐어요"}'
```

결과를 읽은 뒤 완료하며 메모리 상태를 폐기합니다.

```bash
curl -s http://127.0.0.1:8000/v1/sessions/SESSION_ID/complete \
  -X POST \
  -H 'Authorization: Bearer 긴-무작위-테스트-키' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

## 운영 전 남은 필수 항목

이 버전은 Backend 시작점이지 공개 의료서비스 완성본은 아닙니다. 외부 운영 전에는 사용자/기관 인증과 권한, 동의 및 개인정보 처리 고지, 암호화 저장 정책, 감사 로그의 최소화·분리, rate limit/WAF, 장애 복구, 모니터링, 의료인 검토 workflow, FHIR 내보내기 검증, 임상·보안·법률 검토가 필요합니다. MCP는 이 API의 대체물이 아니며, 향후 LLM 도구 연결이 필요할 때 이 API 위에 선택적으로 추가하는 adapter가 적절합니다.
