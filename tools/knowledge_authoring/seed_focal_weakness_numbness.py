#!/usr/bin/env python3
"""Materialize unreviewed focal weakness/numbness knowledge."""
from profile_support import *

P="focal-neurology"; RFE="rfe.focal_weakness_numbness"; M="mapping.snomed-mrcm.focal-weakness-numbness"; SN="http://snomed.info/sct"
SOURCES=["source.nhs.stroke.2024","source.nice.ng127.2023"]
G={k:f"group.focal-neurology.{k}" for k in ("stroke-safety","spinal-safety","distribution","motor","sensory","context")}
C=["intent.characterize_symptom"]; S=["intent.screen_red_flags"]; R=["intent.risk_assessment"]; D=["intent.differentiate_common_causes"]

def Q(fid,d,vt,key,w,score,groups,intents,**kw): return entry(P,fid,d,vt,key,w,score,key,groups,intents=intents,**kw)

def fragment():
 e=[
 Q("symptom.focal_neurology.current","Current Weakness or Sensory Change","boolean","current","지금도 힘 빠짐, 감각 둔함 또는 저림이 있나요?",130,[G["stroke-safety"],G["distribution"]],C,safety_relevant=True),
 Q("symptom.focal_neurology.main_type","Main Focal Neurologic Symptom","coded","main-type","주된 증상은 실제 힘 빠짐, 감각 둔함, 찌릿한 저림, 통증 때문에 못 움직임 중 무엇인가요?",110,[G["motor"],G["sensory"]],C,allowed_values=["weakness","numbness","tingling","pain_limited","mixed","unclear"]),
 Q("symptom.duration","Symptom Duration","quantity","duration","처음 증상이 시작된 시각이나 날짜는 언제인가요?",109,[G["stroke-safety"]],C,reuse_existing=True),
 Q("symptom.focal_neurology.sudden_onset","Sudden Onset","boolean","sudden","증상이 수초에서 수분 사이 갑자기 시작했나요?",129,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.focal_neurology.one_sided","One-sided Symptom","boolean","one-sided","얼굴이나 몸의 한쪽에만 증상이 있나요?",128,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.face_droop","Face Droop","boolean","face-droop","웃을 때 한쪽 얼굴이나 입꼬리가 처지나요?",127,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.arm_drift_or_cannot_raise","Arm Drift","boolean","arm-drift","두 팔을 들 때 한쪽 팔이 내려가거나 들 수 없나요?",126,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.speech_or_language_disturbance","Speech Disturbance","boolean","speech","말이 어눌하거나 단어가 나오지 않거나 말을 이해하기 어렵나요?",125,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.sudden_visual_loss_or_field_defect","Sudden Visual Loss","boolean","vision","시야가 갑자기 흐려지거나 보이지 않는 부분이 생겼나요?",124,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.sudden_gait_unsteadiness","Sudden Gait Unsteadiness","boolean","gait","갑자기 걷기 어렵거나 한쪽으로 넘어지나요?",123,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.focal_neurology.resolved_within_24h","Resolved Within 24 Hours","boolean","resolved","지난 24시간 안에 갑자기 생겼다가 사라진 증상인가요?",122,[G["stroke-safety"]],S,safety_relevant=True),
 Q("symptom.symmetric_progressive_weakness","Symmetric Progressive Weakness","boolean","symmetric-progressive","양쪽 팔다리 힘이 며칠에서 4주 사이 빠르게 약해지나요?",121,[G["spinal-safety"]],S,safety_relevant=True),
 Q("symptom.dyspnea_at_rest_or_supine","Breathlessness at Rest or Supine","boolean","breathing","가만히 있거나 누우면 숨이 차나요?",120,[G["spinal-safety"]],S,safety_relevant=True),
 Q("symptom.new_swallowing_impairment","New Swallowing Impairment","boolean","swallowing","새로 삼키기 어렵거나 자주 사레가 드나요?",119,[G["spinal-safety"]],S,safety_relevant=True),
 Q("symptom.severe_back_pain_radiating_leg","Severe Back Pain Radiating to Leg","boolean","back-leg-pain","심한 허리 통증이 다리로 뻗치나요?",118,[G["spinal-safety"]],S,safety_relevant=True),
 Q("symptom.new_bladder_bowel_or_sexual_dysfunction","New Bladder Bowel or Sexual Dysfunction","boolean","bladder-bowel","새로 배뇨·배변 조절 또는 성기능이 달라졌나요?",117,[G["spinal-safety"]],S,safety_relevant=True),
 Q("symptom.perineal_or_saddle_numbness","Saddle Numbness","boolean","saddle","회음부나 항문 주위 감각이 새로 둔해졌나요?",116,[G["spinal-safety"]],S,safety_relevant=True),
 Q("symptom.single_limb_rapid_progression","Rapid Single-limb Progression","boolean","single-progressive","한쪽 팔다리 힘이 몇 시간에서 며칠 사이 빠르게 약해지나요?",115,[G["motor"]],S,safety_relevant=True),
 Q("symptom.focal_neurology.side","Affected Side","coded","side","왼쪽, 오른쪽, 양쪽 중 어디인가요?",106,[G["distribution"]],C,allowed_values=["left","right","bilateral","variable","unclear"]),
 Q("symptom.focal_neurology.region","Affected Region","coded","region","얼굴, 팔·손, 다리·발, 몸통, 회음부 중 어디인가요?",105,[G["distribution"]],C,allowed_values=["face","arm_hand","leg_foot","trunk","perineum","multiple","unclear"],terminology_binding={"system":SN,"focus_code":"44077006"},mrcm_ref=M),
 Q("symptom.focal_neurology.progression","Progression","coded","progression","호전, 그대로, 서서히 악화, 빠르게 악화, 반복 중 무엇인가요?",104,[G["distribution"]],C,allowed_values=["improving","stable","slow_worsening","rapid_worsening","recurrent","unclear"]),
 Q("symptom.objective_motor_task_loss","Motor Task Loss","string","motor-task","물건 잡기, 계단 오르기 등 실제로 못 하게 된 동작이 있나요?",103,[G["motor"]],C,terminology_binding={"system":SN,"code":"26544005"}),
 Q("symptom.sensory_quality","Sensory Quality","coded","sensory-quality","무감각, 바늘로 찌름, 화끈거림, 전기 느낌 중 무엇인가요?",102,[G["sensory"]],C,allowed_values=["numb","pins_needles","burning","electric","mixed","unclear"],terminology_binding={"system":SN,"code":"91019004"}),
 Q("symptom.neck_or_back_pain","Neck or Back Pain","boolean","neck-back","목이나 허리 통증이 함께 있나요?",94,[G["context"]],D),
 Q("symptom.radicular_pain","Radiating Limb Pain","boolean","radicular","목이나 허리에서 팔다리로 뻗치는 통증이 있나요?",93,[G["context"]],D),
 Q("symptom.position_or_repetition_trigger","Position Trigger","boolean","position","특정 자세나 반복 동작에서 생기고 자세를 바꾸면 나아지나요?",92,[G["context"]],D),
 Q("event.recent_injury_or_procedure","Recent Injury or Procedure","boolean","injury","최근 머리·척추·팔다리 외상이나 시술이 있었나요?",91,[G["context"]],R),
 Q("event.recent_infection_or_vaccination","Recent Infection or Vaccination","boolean","infection","증상 전 수주 안에 감염이나 예방접종이 있었나요?",90,[G["context"]],R),
 Q("history.diabetes_or_neuropathy","Diabetes or Neuropathy","boolean","diabetes","당뇨병이나 말초신경병증 병력이 있나요?",89,[G["context"]],R),
 Q("history.stroke_tia_or_neurologic_disease","Neurologic History","boolean","history","뇌졸중·TIA 또는 다른 신경질환 병력이 있나요?",88,[G["context"]],R),
 Q("medication.neurologic_relevant","Relevant Medication or Substance","string","medication","최근 바뀐 약, 항암제, 진정제 또는 과음·약물 사용이 있나요?",87,[G["context"]],R),
 Q("symptom.focal_neurology.functional_impact","Functional Impact","coded","impact","일상 영향은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?",86,[G["motor"]],C,allowed_values=["none","mild","moderate","severe"]),
 ]
 rules=[
 safety_rule(P,"sudden-unilateral",{"all":[{"fact":"symptom.focal_neurology.sudden_onset","equals":True},{"fact":"symptom.focal_neurology.one_sided","equals":True}]},"emergency",1000),
 *[safety_rule(P,k,{"fact":f,"equals":True},"emergency",1000) for k,f in [("fast-face","symptom.face_droop"),("fast-arm","symptom.arm_drift_or_cannot_raise"),("fast-speech","symptom.speech_or_language_disturbance"),("resolved-24h","symptom.focal_neurology.resolved_within_24h")]],
 safety_rule(P,"sudden-vision",{"all":[{"fact":"symptom.focal_neurology.sudden_onset","equals":True},{"fact":"symptom.sudden_visual_loss_or_field_defect","equals":True}]},"emergency",1000),
 safety_rule(P,"progressive-breathing",{"all":[{"fact":"symptom.symmetric_progressive_weakness","equals":True},{"fact":"symptom.dyspnea_at_rest_or_supine","equals":True}]},"emergency",1000),
 safety_rule(P,"progressive-swallowing",{"all":[{"fact":"symptom.symmetric_progressive_weakness","equals":True},{"fact":"symptom.new_swallowing_impairment","equals":True}]},"emergency",1000),
 safety_rule(P,"cauda-bladder",{"all":[{"fact":"symptom.severe_back_pain_radiating_leg","equals":True},{"fact":"symptom.new_bladder_bowel_or_sexual_dysfunction","equals":True}]},"emergency",1000),
 safety_rule(P,"cauda-saddle",{"all":[{"fact":"symptom.severe_back_pain_radiating_leg","equals":True},{"fact":"symptom.perineal_or_saddle_numbness","equals":True}]},"emergency",1000),
 safety_rule(P,"single-progression",{"fact":"symptom.single_limb_rapid_progression","equals":True},"urgent",900)]
 extra=[{"id":v,"type":"ClinicalGroup","display":v.split(".")[-1]} for v in G.values()]
 return {"id":"knowledge.generated.focal-neurology","version":VERSION,"status":"research_only","usage_modes":["research_test","simulation"],"source_manifest":"source-manifest.primary-care-focal-weakness-numbness-research","default_refresh":default_refresh(),"extra_nodes":extra,"group_hypothesis_edges":[],"safety_rules":rules,"entries":e,"provenance":provenance(SOURCES)}

def sources():
 defs=[("source.nhs.stroke.2024","NHS","Stroke symptoms","2024-09-12","https://www.nhs.uk/conditions/stroke/symptoms/","public_health_guidance",7),("source.nice.ng127.2023","NICE","Suspected neurological conditions","NG127-2023","https://www.nice.org.uk/guidance/ng127/chapter/Recommendations-for-adults-aged-over-16","clinical_guideline",1),("source.stom.focal.20260714","Infoclinic","STOM focal neurology MRCM","SNOMEDCT-20260701","https://stom.infoclinic.co/allow/attributes/SNOMEDCT/26544005","terminology_server",30)]
 arts=[{"id":i,"kind":"clinical_guidance_metadata" if p!="terminology_server" else "terminology_mrcm_query_summary","publisher":pub,"title":t,"version":v,"url":u,"language":"en","digest":"metadata_only_not_cached","license_status":"unknown","complete":False,"monitor_profile":p,"monitor_interval_days":d,"last_monitored_at":"2026-07-14","next_monitor_at":"2026-08-13" if d==30 else ("2026-07-21" if d==7 else "2026-07-15"),"assertions":["Build-Time only; Runtime does not browse; content remains unreviewed."]} for i,pub,t,v,u,p,d in defs]
 research={"id":"source-manifest.primary-care-focal-weakness-numbness-research","version":VERSION,"acquired_at":CREATED_AT,"status":"research_only","artifacts":arts,"provenance":provenance([x[0] for x in defs])}
 paths=[("source.repository.foundation","repository_specification","FOUNDATION.md",True),("source.generated.focal","generated_clinical_knowledge","knowledge/generated/neurological/focal-weakness-numbness/focal-weakness-numbness.json",True),("source.mapping.focal","terminology_mapping","mappings/terminology/snomed-mrcm-focal-weakness-numbness.json",False),("source.external.focal","external_source_manifest","sources/manifests/primary-care-focal-weakness-numbness-research.json",False),("source.policy.focal","runtime_policy","policies/primary-care-focal-weakness-numbness-completion.json",True)]
 primary={"id":"source-manifest.primary-care-focal-weakness-numbness","version":VERSION,"acquired_at":CREATED_AT,"artifacts":[{"id":i,"kind":k,"publisher":"clinical-interview-platform","version":VERSION,"language":"en","path":p,"digest":"computed_at_build","license_status":"allowed" if c else "unknown","complete":c} for i,k,p,c in paths],"provenance":provenance(["FOUNDATION.md","PROJECT_CONTEXT.md"])}
 return primary,research

def cases(frag):
 tm={"sudden-unilateral":["symptom.focal_neurology.sudden_onset","symptom.focal_neurology.one_sided"],"fast-face":["symptom.face_droop"],"fast-arm":["symptom.arm_drift_or_cannot_raise"],"fast-speech":["symptom.speech_or_language_disturbance"],"resolved-24h":["symptom.focal_neurology.resolved_within_24h"],"sudden-vision":["symptom.focal_neurology.sudden_onset","symptom.sudden_visual_loss_or_field_defect"],"progressive-breathing":["symptom.symmetric_progressive_weakness","symptom.dyspnea_at_rest_or_supine"],"progressive-swallowing":["symptom.symmetric_progressive_weakness","symptom.new_swallowing_impairment"],"cauda-bladder":["symptom.severe_back_pain_radiating_leg","symptom.new_bladder_bowel_or_sexual_dysfunction"],"cauda-saddle":["symptom.severe_back_pain_radiating_leg","symptom.perineal_or_saddle_numbness"],"single-progression":["symptom.single_limb_rapid_progression"]}
 out={}
 for i,r in enumerate(frag["safety_rules"]):
  k=r["id"].split("safety.")[1]; lvl=r["then"]["safety_level"]
 out[f"FOCAL-{k.upper()}.json"]={"id":f"FOCAL-{k.upper()}","simulation_language":"ko","persona":{"age":40+i},"initial_statement":{"ko":"한쪽 팔다리가 이상해요."},"hidden_state":{x:{"value":True} for x in tm[k]},"expected":{"expected_safety_level":lvl,"expected_safety_action":"human_handoff","expected_stop_reason":f"{lvl}_escalation","expected_triggered_rules_contains":[r["id"]],"expected_max_turns":24,"forbidden_assertions":["diagnosis.stroke"]},"provenance":provenance(SOURCES)}
 hidden={}
 for item in frag["entries"]:
  f=item["fact"]; fid=f["id"]
  if f["value_type"]=="boolean": hidden[fid]={"value":fid=="symptom.focal_neurology.current"}
  elif f["value_type"]=="quantity": hidden[fid]={"value":{"amount":7,"unit":"days"}}
  elif f["value_type"]=="coded": hidden[fid]={"value":f.get("allowed_values",["unclear"])[-1]}
  else: hidden[fid]={"value":"없음"}
 declined="medication.neurologic_relevant"; hidden.pop(declined)
 out["FOCAL-DATA-ABSENT.json"]={"id":"FOCAL-DATA-ABSENT","simulation_language":"ko","persona":{"age":46},"initial_statement":{"ko":"손끝이 가끔 저려요."},"hidden_state":hidden,"response_behavior":{declined:{"dataAbsentReason":"asked-declined"}},"expected":{"expected_data_absent_reasons":{declined:"asked-declined"},"expected_safety_level":"routine","expected_stop_reason":"required_targets_addressed_with_absent_data","expected_max_turns":34,"forbidden_assertions":["diagnosis.carpal_tunnel"]},"provenance":provenance(["source.nice.ng127.2023","specifications/clinical-memory.md"])}
 return out

def main():
 f=fragment(); graph,rules=base_graph_and_rules(prefix=P,rfe=RFE,display="Focal Weakness or Numbness",intents=[("intent.characterize_symptom","Characterize Symptom"),("intent.screen_red_flags","Screen Red Flags"),("intent.differentiate_common_causes","Differentiate Common Sources"),("intent.risk_assessment","Risk Assessment")]); primary,research=sources()
 m={"id":M,"version":VERSION,"status":"research_only","review_status":"unreviewed","terminology":{"system":SN,"version":"http://snomed.info/sct/900000000000207008/version/20260701","source":"STOM"},"focus_concepts":[{"code":c,"display":d,"attribute_count_returned":20} for c,d in [("26544005","Muscle weakness (finding)"),("44077006","Numbness (finding)"),("91019004","Paresthesia (finding)")]],"checks":[{"focus_code":c,"attribute_code":a,"allowed":True} for c in ("26544005","44077006","91019004") for a in ("363698007","246112005")],"validation":{"method":"build_time_live_mrcm_summary","checked_at":CREATED_AT,"raw_response_cached":False,"complete_mrcm_snapshot":False,"clinical_rule_authority":False,"result":"provisional_pass"},"provenance":provenance(["source.stom.focal.20260714"])}
 docs=[("knowledge/base/primary-care-focal-weakness-numbness.json",graph),("rules/base/primary-care-focal-weakness-numbness.json",rules),("knowledge/generated/neurological/focal-weakness-numbness/focal-weakness-numbness.json",f),("mappings/terminology/snomed-mrcm-focal-weakness-numbness.json",m),("sources/manifests/primary-care-focal-weakness-numbness.json",primary),("sources/manifests/primary-care-focal-weakness-numbness-research.json",research),("policies/primary-care-focal-weakness-numbness-completion.json",completion_policy(prefix="focal-weakness-numbness",fragment=f,presentation_fact="symptom.focal_neurology.current",question_budget=34,source_refs=SOURCES))]
 for p,d in docs: write_json(p,d)
 for n,c in cases(f).items(): write_json("simulation/patients/neurological/focal-weakness-numbness/"+n,c)
if __name__=="__main__": main()
