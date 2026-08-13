# 국내 설문 자원 순차 도입 기록

기준일: 2026-08-13
상태: `draft / unreviewed / metadata-only`

이 문서는 국내 공개 설문 자원을 Clinical Interview Platform의 Knowledge·Fact 개선에 활용하기 위한 **출처 도입 기록**이다. 공개 페이지를 볼 수 있거나 파일을 내려받을 수 있다는 사실만으로 문항, 보기, 채점 규칙 또는 전자 시행 권리가 생기지는 않는다.

## 공통 도입 원칙

1. 공식 페이지에서 조사 주체, 최신 버전, 자료 구조와 접근조건을 확인한다.
2. 먼저 조사 영역과 변수 수준의 concept metadata만 기존 Fact와 비교한다.
3. 설문 통계·상관관계는 개인 환자의 임상 Rule이나 진단 근거로 바꾸지 않는다.
4. 새 임상 Fact·Rule은 별도의 공식 임상 근거가 있어야 하며, 설문 자원은 질문 범위·원자성·회상기간·응답영역 설계의 보조자료로만 쓴다.
5. 원문 문항·보기·순서·채점·번역은 해당 자료와 내장된 제3자 척도의 권리를 각각 확인한 후에만 제한적으로 도입한다.
6. source-defined fixed questionnaire는 자동 문구 변경이나 자동 표준용어 exact/equivalent mapping을 하지 않는다.

## 1. 지역사회건강조사(CHS)

- 공식 확인본: 2025년 문항지침서(2026-01-21 게시), 2025 원시자료 이용지침서(2026-02-25 게시)
- 활용 가치: 한국 성인의 건강행태, 예방서비스, 의료접근, 미충족 필요, 손상·안전, 사회·환경 문맥의 누락 여부를 넓게 확인할 수 있다.
- 기존 Coverage 신호: 흡연·니코틴, 음주, 신체활동은 전용 예방 Knowledge와 일부 RFE 문진에 이미 존재한다.
- 우선 gap 후보: 여러 RFE에서 공통으로 재사용할 수 있는 `usual source of care`, 의료접근 장벽·미충족 필요, 지역·환경 문맥의 원자 Fact 모델.
- 현재 허용: 조사영역·변수명 수준 비교, 별도 임상근거를 이용한 프로젝트 자체 질문 설계.
- 현재 차단: 원문 문항·보기 복제, CHS 충실도 주장, 조사 변수명을 근거로 한 자동 LOINC/SNOMED exact mapping, 모집단 결과의 개인 위험규칙 전환.
- 권리 메모: 사이트는 `ALL RIGHT RESERVED`를 표시하고 원시자료 요청에는 신청자 정보와 이용계획이 필요하다.

## 2. 한국의료패널(KHP)

- 공식 확인본: 2025년 발행 `2023년 한국의료패널 기초분석보고서(II)`, 부록 1 `2025년 한국의료패널 조사표`.
- 활용 가치: 응급·입원·외래 이용, 방문 이유, 의료비 부담, 만성·복합질환, 약물·의료용품, 의료경험, 미충족 의료, 건강정보 이해능력 문맥을 함께 볼 수 있다.
- 기존 Coverage 신호: 약물 복용·순응도와 일부 사회경제적 어려움은 특정 패키지/HIRA 연구용 프로그램에 있으나, 의료이용 경험과 건강정보 이해능력은 공통 Fact로 정리되어 있지 않다.
- 우선 gap 후보: `health information comprehension/support need`, `care access barrier and unmet need`, `cost-related care difficulty`, 이전 의료이용·치료경로의 공통 handoff Fact.
- 현재 허용: 개념·문맥 gap 분석, 별도 임상근거를 이용한 프로젝트 자체 질문 설계.
- 현재 차단: 조사표 부록의 원문 탑재, KHP 충실도 주장, 내장 제3자 척도 재사용, 패널 상관관계의 개인 임상규칙 전환.
- 권리 메모: KIHASA 정책상 공공누리 표시가 있는 저작물만 해당 유형 조건으로 이용할 수 있고, 표시가 없는 자료는 사전 협의가 필요하다. 조사표가 포함된 개별 보고서의 공공누리 표시는 별도로 확인해야 한다.

## 3. 고령화연구패널조사(KLoSA)

- 공식 확인본: 2024년 제10차 설문지, 통계청 승인번호 `336002`, 2년 공표주기.
- 활용 가치: 고령자의 기능, 인지·정보출처, 만성질환·의료이용, 고용·퇴직·직업 맥락, 가족·사회적 지원, 돌봄과 생애변화를 함께 검토할 수 있다.
- 기존 Coverage 신호: 고령자 기능·낙상·인지·보호자 지원은 여러 RFE에 증상별 Fact로 흩어져 있고 proxy 정보원 모델도 존재하지만, 재사용 가능한 고령자 공통 domain은 제한적이다.
- 우선 gap 후보: `older adult baseline function/change`, ADL/IADL 지원 필요를 분리한 원자 Fact, proxy 응답의 관찰범위·신뢰도, 비공식 돌봄·사회적 고립, 현재/과거 직업노출의 공통 Context.
- 현재 허용: 고령자 공통 문맥 gap 분석, 별도 임상근거를 이용한 프로젝트 자체 질문 설계.
- 현재 차단: 이용목적 입력 절차를 우회한 자동 첨부 수집, 원문 탑재, KLoSA 충실도 주장, MMSE 등 제3자 척도 문항 탑재, 패널 상관관계의 개인 임상규칙 전환.
- 권리 메모: 설문·자료 다운로드 화면은 개인/기관, 소속과 활용목적을 요구하며 사이트는 `all rights reserved`를 표시한다.

## 순차 구축 queue

| 순서 | 공통 의미축 후보 | 설문 자원의 역할 | 임상 근거 추가 필요 | 현재 상태 |
|---:|---|---|:---:|---|
| 1 | 의료접근 장벽·미충족 필요 | CHS 변수 범위로 누락 점검 | 예 | `queued` |
| 2 | 건강정보 이해·설명 지원 필요 | KHP 조사영역으로 문맥 점검 | 예 | `queued` |
| 3 | 고령자 baseline 기능과 변화 | KLoSA 영역으로 공통 Fact 후보 점검 | 예 | `queued` |
| 4 | proxy 관찰범위·신뢰도 | KLoSA 종단/대리응답 문맥으로 기존 모델 정리 | 예 | `queued` |

이 queue의 항목은 아직 Runtime 질문이나 임상 Knowledge가 아니다. 정규 Knowledge 구축 회차에서 공식 임상근거, 원자성, terminology binding, 환자에게 묻는 필요성과 clinician handoff 가치를 각각 확인한 뒤 도입한다.

## 기계 판독 원본과 검증

- 후보·권리·공식 URL: `sources/inventory/questionnaire-instrument-candidates.json`
- 통합 inventory: `coverage/questionnaire-source-rights-inventory-latest.json`
- 재생성: `python3 tools/inventory/build_questionnaire_source_rights_inventory.py`
- 검증: `python3 -m unittest tests.test_questionnaire_source_rights_inventory`
