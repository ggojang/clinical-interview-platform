# Clinical Interview API

이 서비스는 기존 `CoreInteractionSession`과 컴파일된 Knowledge Package를 외부 앱이 호출할 수 있게 하는 첫 Backend API입니다. Custom GPT 테스트 환경과 Knowledge 빌드 과정은 변경하지 않습니다.

## 현재 제공 범위

- 상호작용 목적 및 서비스 모드 목록 조회
- 임시 세션 생성, 답변 제출, 다음 질문/종료 상태 반환
- 현재 clinician handoff JSON 조회
- 세션 완료 또는 삭제 시 응답 상태 즉시 폐기
- TTL 만료에 의한 자동 폐기
- Bearer API key, 기본 CORS 차단, 요청 본문 비로깅
- 서버 허용목록 기반 LLM provider 조회·선택
- 기본 `local_vllm`, 요청자 허용범위와 참여자 선택권 분리
- 외부 상용 LLM 선택 시 명시적 외부처리 동의 강제
- 컴파일된 질문의 환자 친화적 표현만 LLM에 위임하고 임상 판단은 Runtime에 유지
- `/demo`에서 세 입력 유형과 draft 산출물을 비교하는 테스트 UI 제공
- FHIR R4/R5 Questionnaire JSON 업로드·붙여넣기와 브라우저 미리보기
- 환자경험평가, 국가검진 후보 질문군, 텍스트 설문의 브라우저 정형 대화 데모

임상 콘텐츠는 `draft`, `unreviewed`, `limited use`입니다. 독립적인 진단·치료 결정에 사용하지 않습니다. 안전 신호는 진단을 확정하지 않고 보수적으로 알리며 의료인 확인으로 연결합니다.

FHIR `Questionnaire`, `QuestionnaireResponse`, SDC Extraction은 아직 이 API에 구현되지 않았습니다. 현재 결과 응답에도 이를 `not_implemented`로 명시합니다. 다음 구현 단계에서 기존 질문·Fact 바인딩을 사용해 추가합니다.

데모 UI가 만드는 Questionnaire/QuestionnaireResponse 및 R4/R5 다운로드는 공통 요소를 이용한 **브라우저 draft**입니다. 서버 변환이나 공식 FHIR validator 검증 결과가 아니며, SDC Extraction은 가짜 결과를 만들지 않고 `not_implemented`로 표시합니다. 이미지 설문은 브라우저 미리보기만 지원하고 OCR·문항 구조화는 아직 지원하지 않습니다. 업로드 파일과 API key는 브라우저 영구 저장소에 기록하지 않습니다.

현재 API에서 실제 실행되는 모드는 `clinical_adaptive`(자유 문진)입니다. 목록에는 향후 연결할 다른 플랫폼 모드도 보이지만 `api_capabilities.pending_mode_ids`로 구분되며, 해당 adapter는 아직 응답을 수집하지 않습니다.

## LLM provider 경계

원격 `banttas-ai` 배포의 기본 provider는 같은 서버의 `qwen3-27b`입니다. 선택된 LLM은 현재 **이미 컴파일된 한 개의 질문을 환자에게 자연스럽게 표현하는 용도**로만 호출됩니다. 환자 답변, Fact, trace, 파일, clinician handoff는 LLM 호출에 전달하지 않습니다. 질문 선택, red flag, 질문 순서와 완료 판정은 계속 컴파일된 Knowledge·Rule Runtime이 담당합니다. Provider 장애 시 원문 질문으로 즉시 fallback합니다.

`GET /v1/llm/providers`에서 선택 가능한 provider를 확인할 수 있습니다. 세션 생성 시 요청자는 `llm_policy.allowed_provider_ids`, `default_provider_id`, `participant_may_choose`를 선언하고, 참여자는 허용범위 안에서 `llm_selection`을 지정할 수 있습니다. 아무 선택도 없으면 `local_vllm`입니다.

```json
{
  "mode_selection": "문진 시작",
  "initial_message": "기침이 나요",
  "llm_policy": {
    "allowed_provider_ids": ["local_vllm", "commercial_approved"],
    "default_provider_id": "local_vllm",
    "participant_may_choose": true
  },
  "llm_selection": {
    "provider_id": "commercial_approved",
    "selected_by": "participant",
    "external_processing_consent": true
  }
}
```

Provider URL, model과 API key는 클라이언트가 임의 지정할 수 없습니다. 상용 provider는 운영자가 `CLINICAL_LLM_PROVIDERS_JSON`으로 allowlist에 등록하고, 실제 키는 `api_key_env`가 가리키는 Podman secret으로 별도 주입합니다. 외부 provider에 대한 명시적 동의가 없으면 세션 생성이 거부됩니다. 현재 공용 API key 하나를 쓰는 staging 단계이므로 요청자/참여자 권한의 암호학적 분리는 후속 execution-order API에서 추가해야 합니다.

## 로컬 실행

저장소 루트에서 실행합니다. Python 3.11 이상 외에 별도 패키지는 필요하지 않습니다.

```bash
export CLINICAL_API_KEY='긴-무작위-테스트-키'
python3 -m services.interview_api
```

기본 주소는 `http://127.0.0.1:8000`입니다. API 계약은 [openapi.yaml](openapi.yaml)에 있습니다.
데모 화면은 `http://127.0.0.1:8000/demo`에서 열 수 있습니다. 화면 자체는 인증 없이 열리지만 리소스 조회와 세션 실행에는 API key가 필요합니다.

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
