# Frozen Knowledge Research Release

현재까지 컴파일된 Knowledge를 더 이상 갱신하지 않고 외부 환경에서
사용하려면 전체 Knowledge Factory 저장소를 배포하지 않는다. 대신 다음만
포함한 hash-locked 스냅샷을 배포한다.

- immutable compiled Knowledge Packages
- 답변이 없는 read-only GPT Knowledge API projection
- snapshot identity, repository revision, package semantic digest
- 모든 포함 파일의 SHA-256
- 무결성 검증기와 정적 GET 서버
- OpenAI-compatible LLM 비교용 비영속 연구 harness

Builder, Compiler, source acquisition, terminology publication, feedback
ingestion 및 실제 환자응답은 제외한다. Runtime에서 STOM이나 외부 임상 source를
조회하지 않으며 Knowledge 파일을 수정하지 않는다.

## Build

```bash
python3 tools/release/build_frozen_knowledge_bundle.py \
  --output-dir /tmp/clinical-interview-frozen \
  --zip /tmp/clinical-interview-frozen.zip \
  --created-at 2026-07-31T00:00:00Z
python3 /tmp/clinical-interview-frozen/app/verify.py
```

동일 저장소 revision, 동일 입력 파일, 동일 `created-at`으로 만든 bundle은
출력 디렉터리 이름과 관계없이 동일한 내용과 ZIP byte sequence를 가져야 한다.
Manifest 자신은 self-digest
순환을 피하기 위해 파일 목록에서 제외한다.

## Runtime boundary

동결은 현재 연구 Knowledge의 임상 승인 상태를 바꾸지 않는다. 모든 패키지는
기존 `research_only/unreviewed` 제한을 유지한다. 결함이나 새로운 근거가
발견되어도 활성 스냅샷을 수정하지 않고 별도 revision과 snapshot identifier를
가진 새 배포본을 만들어야 한다.

외부 LLM은 언어 이해와 표현을 지원할 수 있지만, 새로운 Fact, Question, Rule,
urgency 또는 completion policy를 만들 권한이 없다. 배포된 `chat.py`는 Custom
GPT 연구 지침과 선택한 한 RFE의 compact resources를 메모리에 pre-load하여
OpenAI-compatible endpoint 간 비교를 돕는다. 대화는 저장하지 않는다.
