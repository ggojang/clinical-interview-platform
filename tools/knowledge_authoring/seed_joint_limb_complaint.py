#!/usr/bin/env python3
"""Materialize unreviewed grouped joint/limb complaint knowledge."""
from profile_support import *

P="joint-limb"; RFE="rfe.joint_limb_complaint"; M="mapping.snomed-mrcm.joint-limb"; SN="http://snomed.info/sct"
SOURCES=["source.nhs.joint-pain.2026","source.nhs.septic-arthritis.2023","source.nice.ng38.fracture.2025","source.nice.ng226.osteoarthritis.2022"]
G={k:f"group.joint-limb.{k}" for k in ("trauma-safety","infection-safety","neurovascular-safety","pain-function","inflammatory","context")}
C=["intent.characterize_symptom"]; S=["intent.screen_red_flags"]; R=["intent.risk_assessment"]; D=["intent.differentiate_common_causes"]
def Q(fid,d,vt,key,w,score,groups,intents,**kw): return entry(P,fid,d,vt,key,w,score,key,groups,intents=intents,**kw)

def fragment():
 e=[
 Q("symptom.joint_limb.current","Current Joint or Limb Complaint","boolean","current","지금도 관절·팔다리·목·어깨 통증, 붓기 또는 손상 증상이 있나요?",130,[G["pain-function"]],C),
 Q("symptom.joint_limb.main_type","Main Joint or Limb Complaint","coded","main-type","주된 문제는 통증, 붓기, 뻣뻣함, 외상, 움직임 제한, 불안정함 중 무엇인가요?",110,[G["pain-function"]],C,allowed_values=["pain","swelling","stiffness","injury","restricted_motion","instability","mixed","other"]),
 Q("symptom.duration","Symptom Duration","quantity","duration","증상은 언제부터 시작했나요?",109,[G["pain-function"]],C,reuse_existing=True),
 Q("symptom.joint_limb.location","Joint or Limb Location","coded","location","목, 어깨, 팔꿈치, 손목·손, 엉덩이, 무릎, 발목·발 중 어디인가요?",108,[G["pain-function"]],C,allowed_values=["neck","shoulder","elbow","wrist_hand","hip","knee","ankle_foot","other","multiple"],terminology_binding={"system":SN,"focus_code":"57676002"},mrcm_ref=M),
 Q("symptom.joint_limb.side","Affected Side","coded","side","왼쪽, 오른쪽, 양쪽 중 어디인가요?",107,[G["pain-function"]],C,allowed_values=["left","right","bilateral","midline","multiple","unclear"]),
 Q("event.joint_limb.recent_injury","Recent Joint or Limb Injury","boolean","recent-injury","넘어짐, 충돌, 비틀림 또는 직접 충격 뒤 시작했나요?",106,[G["trauma-safety"],G["context"]],C,safety_relevant=True),
 Q("symptom.joint_limb.visible_deformity","Visible Deformity","boolean","deformity","다친 부위가 휘거나 관절이 제자리에서 벗어난 것처럼 보이나요?",129,[G["trauma-safety"]],S,safety_relevant=True),
 Q("symptom.joint_limb.open_wound_or_exposed_bone","Open Wound or Exposed Bone","boolean","open-wound","다친 부위에 깊은 상처가 있거나 뼈가 보이나요?",128,[G["trauma-safety"]],S,safety_relevant=True),
 Q("symptom.joint_limb.unable_weight_bear_or_use","Unable to Bear Weight or Use Limb","boolean","cannot-use","다친 뒤 걷거나 체중을 싣지 못하거나 팔을 전혀 사용할 수 없나요?",127,[G["trauma-safety"]],S,safety_relevant=True),
 Q("symptom.joint_limb.postinjury_numbness","Post-injury Numbness","boolean","postinjury-numbness","다친 부위 아래쪽이 저리거나 감각이 없나요?",126,[G["neurovascular-safety"]],S,safety_relevant=True),
 Q("symptom.joint_limb.cold_pale_blue_distal","Cold Pale or Blue Distal Limb","boolean","cold-blue","손가락이나 발가락이 반대쪽보다 차갑고 창백하거나 파랗게 변했나요?",125,[G["neurovascular-safety"]],S,safety_relevant=True),
 Q("symptom.joint_limb.severe_escalating_pain_tight_swelling","Escalating Pain with Tight Swelling","boolean","compartment","진통에도 통증이 빠르게 심해지고 팔다리가 단단하게 붓나요?",124,[G["neurovascular-safety"]],S,safety_relevant=True),
 Q("symptom.hot_swollen_joint","Hot Swollen Joint","boolean","hot-swollen","관절이 붓고 뜨겁거나 붉게 보이나요?",123,[G["infection-safety"],G["inflammatory"]],S,safety_relevant=True,terminology_binding={"system":SN,"code":"271771009"}),
 Q("symptom.fever","Fever","boolean","fever","열이 나거나 춥고 떨리나요?",122,[G["infection-safety"]],S,safety_relevant=True,reuse_existing=True),
 Q("symptom.systemically_unwell","Systemically Unwell","boolean","unwell","전신 상태가 몹시 나쁘거나 기운이 없나요?",121,[G["infection-safety"]],S,safety_relevant=True),
 Q("symptom.sudden_severe_single_joint","Sudden Severe Single-joint Pain","boolean","severe-mono","한 관절에 갑자기 매우 심한 통증과 붓기가 생겼나요?",120,[G["infection-safety"],G["inflammatory"]],S,safety_relevant=True),
 Q("symptom.neck_pain_with_bilateral_weakness_or_clumsiness","Neck Pain with Bilateral Weakness or Clumsiness","boolean","neck-neuro","목 통증과 함께 양쪽 팔다리 힘이 빠지거나 손이 서툴고 걷기가 달라졌나요?",119,[G["neurovascular-safety"]],S,safety_relevant=True),
 Q("symptom.new_bladder_bowel_dysfunction_with_neck_back_pain","Bladder or Bowel Dysfunction with Spinal Pain","boolean","spinal-bladder","목·허리 통증과 함께 새로 배뇨·배변 조절이 달라졌나요?",118,[G["neurovascular-safety"]],S,safety_relevant=True),
 Q("symptom.chest_pain","Chest Pain","boolean","chest-pain","어깨·팔 통증과 함께 가슴 통증이나 압박감이 있나요?",117,[G["neurovascular-safety"]],S,safety_relevant=True,reuse_existing=True),
 Q("symptom.severe_dyspnea","Severe Shortness of Breath","boolean","dyspnea","어깨·팔 통증과 함께 심한 호흡곤란이나 식은땀이 있나요?",116,[G["neurovascular-safety"]],S,safety_relevant=True,reuse_existing=True),
 Q("symptom.joint_limb.onset","Joint or Limb Symptom Onset","coded","onset","갑자기 시작했나요, 서서히 시작했나요?",105,[G["pain-function"]],C,allowed_values=["sudden","gradual","unclear"]),
 Q("symptom.joint_limb.pain_severity","Pain Severity","coded","severity","통증은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?",104,[G["pain-function"]],C,allowed_values=["none","mild","moderate","severe"]),
 Q("symptom.joint_limb.number_of_joints","Number of Joints","coded","joint-count","한 관절, 2~4개, 5개 이상 중 어디에 해당하나요?",103,[G["inflammatory"]],C,allowed_values=["one","two_to_four","five_or_more","not_joint","unclear"]),
 Q("symptom.joint_limb.range_of_motion","Range of Motion","coded","motion","움직임은 정상, 일부 제한, 거의 불가능 중 무엇인가요?",102,[G["pain-function"]],C,allowed_values=["normal","partly_limited","nearly_impossible","unclear"]),
 Q("symptom.joint_limb.morning_stiffness","Morning Stiffness Duration","coded","morning-stiffness","아침에 뻣뻣함이 없다, 30분 이하, 30분 초과 중 무엇인가요?",101,[G["inflammatory"]],D,allowed_values=["none","up_to_30_minutes","over_30_minutes","unclear"]),
 Q("symptom.joint_limb.activity_relation","Activity Relation","coded","activity-relation","움직일 때 악화, 쉬면 악화, 둘 다, 관련 없음 중 무엇인가요?",100,[G["pain-function"]],D,allowed_values=["worse_with_activity","worse_after_rest","both","no_relation","unclear"]),
 Q("symptom.joint_limb.night_or_rest_pain","Night or Rest Pain","boolean","night-pain","밤에 깨거나 쉬고 있어도 계속 아픈가요?",99,[G["pain-function"]],R),
 Q("symptom.joint_limb.locking_or_giving_way","Locking or Giving Way","boolean","locking","관절이 잠기거나 갑자기 힘이 풀리나요?",98,[G["pain-function"]],C),
 Q("symptom.joint_limb.rapid_worsening_or_deformity","Rapid Worsening or Progressive Deformity","boolean","rapid-worsening","최근 빠르게 악화하거나 관절 모양이 변하고 있나요?",97,[G["inflammatory"]],R),
 Q("event.joint_limb.injury_mechanism","Injury Mechanism","string","mechanism","다쳤다면 어떻게 다쳤고 어느 방향으로 힘이 가해졌나요?",96,[G["trauma-safety"],G["context"]],C),
 Q("history.inflammatory_arthritis_gout_or_psoriasis","Inflammatory Arthritis Gout or Psoriasis History","boolean","arthritis-history","류마티스관절염, 통풍, 건선 또는 다른 염증성 관절질환 병력이 있나요?",90,[G["inflammatory"],G["context"]],R),
 Q("risk.joint_infection_recent_procedure_or_infection","Recent Joint Procedure or Infection","boolean","infection-risk","최근 관절 주사·수술, 피부 상처 또는 다른 감염이 있었나요?",89,[G["infection-safety"],G["context"]],R),
 Q("patient.immunocompromised","Immunocompromised","boolean","immunocompromised","면역을 낮추는 약이나 치료를 받고 있나요?",88,[G["infection-safety"]],R,reuse_existing=True),
 Q("medication.anticoagulant_or_steroid","Anticoagulant or Steroid Use","string","medication","항응고제, 스테로이드 또는 관련 약을 복용하나요?",87,[G["context"]],R),
 Q("exposure.repetitive_work_sport_or_new_load","Repetitive Work Sport or New Load","string","load","반복 작업, 운동 또는 갑작스러운 활동량 증가와 관련 있나요?",86,[G["context"]],D),
 Q("treatment.joint_limb_response","Self-care or Treatment Response","coded","response","휴식·냉찜질·진통제 등을 했다면 호전, 변화 없음, 악화 중 무엇인가요?",85,[G["context"]],R,allowed_values=["not_tried","improved","unchanged","worsened"]),
 Q("symptom.joint_limb.functional_impact","Functional Impact","coded","impact","걷기, 옷 입기, 일·수면 영향은 없음, 가벼움, 중간, 심함 중 무엇인가요?",84,[G["pain-function"]],C,allowed_values=["none","mild","moderate","severe"]),
 ]
 rules=[
 safety_rule(P,"deformity",{"fact":"symptom.joint_limb.visible_deformity","equals":True},"emergency",1000),
 safety_rule(P,"open-wound",{"fact":"symptom.joint_limb.open_wound_or_exposed_bone","equals":True},"emergency",1000),
 safety_rule(P,"cannot-use",{"all":[{"fact":"event.joint_limb.recent_injury","equals":True},{"fact":"symptom.joint_limb.unable_weight_bear_or_use","equals":True}]},"emergency",1000),
 safety_rule(P,"postinjury-numbness",{"all":[{"fact":"event.joint_limb.recent_injury","equals":True},{"fact":"symptom.joint_limb.postinjury_numbness","equals":True}]},"emergency",1000),
 safety_rule(P,"vascular",{"fact":"symptom.joint_limb.cold_pale_blue_distal","equals":True},"emergency",1000),
 safety_rule(P,"compartment",{"fact":"symptom.joint_limb.severe_escalating_pain_tight_swelling","equals":True},"emergency",1000),
 safety_rule(P,"spinal-neurology",{"fact":"symptom.neck_pain_with_bilateral_weakness_or_clumsiness","equals":True},"emergency",1000),
 safety_rule(P,"spinal-bladder",{"fact":"symptom.new_bladder_bowel_dysfunction_with_neck_back_pain","equals":True},"emergency",1000),
 safety_rule(P,"cardiopulmonary",{"all":[{"fact":"symptom.chest_pain","equals":True},{"fact":"symptom.severe_dyspnea","equals":True}]},"emergency",1000),
 safety_rule(P,"hot-joint-fever",{"all":[{"fact":"symptom.hot_swollen_joint","equals":True},{"fact":"symptom.fever","equals":True}]},"urgent",900),
 safety_rule(P,"hot-joint-unwell",{"all":[{"fact":"symptom.hot_swollen_joint","equals":True},{"fact":"symptom.systemically_unwell","equals":True}]},"urgent",900),
 safety_rule(P,"sudden-monoarthritis",{"fact":"symptom.sudden_severe_single_joint","equals":True},"urgent",850)]
 return {"id":"knowledge.generated.joint-limb","version":VERSION,"status":"research_only","usage_modes":["research_test","simulation"],"source_manifest":"source-manifest.primary-care-joint-limb-research","default_refresh":default_refresh(),"extra_nodes":[{"id":v,"type":"ClinicalGroup","display":v.split(".")[-1]} for v in G.values()],"group_hypothesis_edges":[],"safety_rules":rules,"entries":e,"provenance":provenance(SOURCES)}

def source_docs():
 defs=[("source.nhs.joint-pain.2026","NHS","Joint pain","2026-02-26","https://www.nhs.uk/symptoms/joint-pain/","public_health_guidance",7),("source.nhs.septic-arthritis.2023","NHS","Septic arthritis","2023-04-12","https://www.nhs.uk/conditions/septic-arthritis/","public_health_guidance",7),("source.nice.ng38.fracture.2025","NICE","Fractures non-complex","NG38-2025","https://www.nice.org.uk/guidance/ng38/chapter/recommendations","clinical_guideline",1),("source.nice.ng226.osteoarthritis.2022","NICE","Osteoarthritis","NG226-2022","https://www.nice.org.uk/guidance/ng226/chapter/recommendations","clinical_guideline",1),("source.stom.joint-limb.20260714","Infoclinic","STOM joint limb MRCM","SNOMEDCT-20260701","https://stom.infoclinic.co/allow/attributes/SNOMEDCT/57676002","terminology_server",30)]
 arts=[{"id":i,"kind":"terminology_mrcm_query_summary" if p=="terminology_server" else "clinical_guidance_metadata","publisher":pub,"title":t,"version":v,"url":u,"language":"en","digest":"metadata_only_not_cached","license_status":"unknown","complete":False,"monitor_profile":p,"monitor_interval_days":d,"last_monitored_at":"2026-07-14","next_monitor_at":"2026-08-13" if d==30 else ("2026-07-21" if d==7 else "2026-07-15"),"assertions":["Build-Time only; Runtime does not browse; content remains unreviewed."]} for i,pub,t,v,u,p,d in defs]
 research={"id":"source-manifest.primary-care-joint-limb-research","version":VERSION,"acquired_at":CREATED_AT,"status":"research_only","artifacts":arts,"provenance":provenance([x[0] for x in defs])}
 paths=[("source.repository.foundation","repository_specification","FOUNDATION.md",True),("source.generated.joint-limb","generated_clinical_knowledge","knowledge/generated/musculoskeletal/joint-limb/joint-limb.json",True),("source.mapping.joint-limb","terminology_mapping","mappings/terminology/snomed-mrcm-joint-limb.json",False),("source.external.joint-limb","external_source_manifest","sources/manifests/primary-care-joint-limb-research.json",False),("source.policy.joint-limb","runtime_policy","policies/primary-care-joint-limb-completion.json",True)]
 primary={"id":"source-manifest.primary-care-joint-limb","version":VERSION,"acquired_at":CREATED_AT,"artifacts":[{"id":i,"kind":k,"publisher":"clinical-interview-platform","version":VERSION,"language":"en","path":p,"digest":"computed_at_build","license_status":"allowed" if c else "unknown","complete":c} for i,k,p,c in paths],"provenance":provenance(["FOUNDATION.md","PROJECT_CONTEXT.md"])}
 return primary,research

def cases(f):
 tm={"deformity":["symptom.joint_limb.visible_deformity"],"open-wound":["symptom.joint_limb.open_wound_or_exposed_bone"],"cannot-use":["event.joint_limb.recent_injury","symptom.joint_limb.unable_weight_bear_or_use"],"postinjury-numbness":["event.joint_limb.recent_injury","symptom.joint_limb.postinjury_numbness"],"vascular":["symptom.joint_limb.cold_pale_blue_distal"],"compartment":["symptom.joint_limb.severe_escalating_pain_tight_swelling"],"spinal-neurology":["symptom.neck_pain_with_bilateral_weakness_or_clumsiness"],"spinal-bladder":["symptom.new_bladder_bowel_dysfunction_with_neck_back_pain"],"cardiopulmonary":["symptom.chest_pain","symptom.severe_dyspnea"],"hot-joint-fever":["symptom.hot_swollen_joint","symptom.fever"],"hot-joint-unwell":["symptom.hot_swollen_joint","symptom.systemically_unwell"],"sudden-monoarthritis":["symptom.sudden_severe_single_joint"]}
 out={}
 for i,r in enumerate(f["safety_rules"]):
  k=r["id"].split("safety.")[1]; lvl=r["then"]["safety_level"]
  out[f"JOINT-{k.upper()}.json"]={"id":f"JOINT-{k.upper()}","simulation_language":"ko","persona":{"age":35+i},"initial_statement":{"ko":"관절과 팔다리가 아파요."},"hidden_state":{x:{"value":True} for x in tm[k]},"expected":{"expected_safety_level":lvl,"expected_safety_action":"human_handoff","expected_stop_reason":f"{lvl}_escalation","expected_triggered_rules_contains":[r["id"]],"expected_max_turns":25,"forbidden_assertions":["diagnosis.fracture","diagnosis.septic_arthritis"]},"provenance":provenance(SOURCES)}
 hidden={}
 for x in f["entries"]:
  a=x["fact"]; fid=a["id"]
  if a["value_type"]=="boolean": hidden[fid]={"value":fid=="symptom.joint_limb.current"}
  elif a["value_type"]=="quantity": hidden[fid]={"value":{"amount":10,"unit":"days"}}
  elif a["value_type"]=="coded": hidden[fid]={"value":a.get("allowed_values",["unclear"])[-1]}
  else: hidden[fid]={"value":"없음"}
 declined="medication.anticoagulant_or_steroid"; hidden.pop(declined)
 out["JOINT-DATA-ABSENT.json"]={"id":"JOINT-DATA-ABSENT","simulation_language":"ko","persona":{"age":52},"initial_statement":{"ko":"무릎이 서서히 아파요."},"hidden_state":hidden,"response_behavior":{declined:{"dataAbsentReason":"asked-declined"}},"expected":{"expected_data_absent_reasons":{declined:"asked-declined"},"expected_safety_level":"routine","expected_stop_reason":"required_targets_addressed_with_absent_data","expected_max_turns":40,"forbidden_assertions":["diagnosis.osteoarthritis"]},"provenance":provenance(["source.nice.ng226.osteoarthritis.2022","specifications/clinical-memory.md"])}
 return out

def main():
 f=fragment(); graph,rules=base_graph_and_rules(prefix=P,rfe=RFE,display="Joint or Limb Complaint",intents=[("intent.characterize_symptom","Characterize Symptom"),("intent.screen_red_flags","Screen Red Flags"),("intent.differentiate_common_causes","Differentiate Common Sources"),("intent.risk_assessment","Risk Assessment")]); primary,research=source_docs()
 concepts=[("57676002","Pain of joint (finding)",20),("271771009","Joint swelling (finding)",20),("127278005","Injury of upper extremity (disorder)",22),("81680005","Neck pain (finding)",20),("45326000","Pain of shoulder region (finding)",20)]
 m={"id":M,"version":VERSION,"status":"research_only","review_status":"unreviewed","terminology":{"system":SN,"version":"http://snomed.info/sct/900000000000207008/version/20260701","source":"STOM"},"focus_concepts":[{"code":c,"display":d,"attribute_count_returned":n} for c,d,n in concepts],"checks":[{"focus_code":c,"attribute_code":a,"allowed":True} for c,_,_ in concepts for a in ("363698007","246112005")],"validation":{"method":"build_time_live_mrcm_summary","checked_at":CREATED_AT,"raw_response_cached":False,"complete_mrcm_snapshot":False,"clinical_rule_authority":False,"result":"provisional_pass"},"provenance":provenance(["source.stom.joint-limb.20260714"])}
 docs=[("knowledge/base/primary-care-joint-limb.json",graph),("rules/base/primary-care-joint-limb.json",rules),("knowledge/generated/musculoskeletal/joint-limb/joint-limb.json",f),("mappings/terminology/snomed-mrcm-joint-limb.json",m),("sources/manifests/primary-care-joint-limb.json",primary),("sources/manifests/primary-care-joint-limb-research.json",research),("policies/primary-care-joint-limb-completion.json",completion_policy(prefix="joint-limb",fragment=f,presentation_fact="symptom.joint_limb.current",question_budget=39,source_refs=SOURCES))]
 for p,d in docs: write_json(p,d)
 for n,c in cases(f).items(): write_json("simulation/patients/musculoskeletal/joint-limb/"+n,c)
if __name__=="__main__": main()
