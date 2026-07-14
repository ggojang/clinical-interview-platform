#!/usr/bin/env python3
"""Materialize unreviewed edema knowledge."""
from profile_support import *
P="edema"; RFE="rfe.edema"; M="mapping.snomed-mrcm.edema"; SN="http://snomed.info/sct"
SOURCES=["source.nhs.edema.2026","source.nice.ng158.vte.2023","source.nice.ng106.heart-failure.2025"]
G={k:f"group.edema.{k}" for k in ("cardiopulmonary-safety","unilateral-vte","infection","distribution","systemic-fluid","context")}
C=["intent.characterize_symptom"]; S=["intent.screen_red_flags"]; R=["intent.risk_assessment"]; D=["intent.differentiate_common_causes"]
def Q(fid,d,vt,key,w,score,groups,intents,**kw): return entry(P,fid,d,vt,key,w,score,key,groups,intents=intents,**kw)

def fragment():
 e=[
 Q("symptom.edema.current","Current Edema","boolean","current","지금도 발·다리·손·얼굴 또는 몸이 붓나요?",130,[G["distribution"]],C,safety_relevant=True,terminology_binding={"system":SN,"code":"267038008"}),
 Q("symptom.duration","Symptom Duration","quantity","duration","붓기는 언제부터 시작했나요?",110,[G["distribution"]],C,reuse_existing=True),
 Q("symptom.edema.sudden_onset","Sudden Edema Onset","boolean","sudden","붓기가 갑자기 시작했나요?",109,[G["distribution"],G["unilateral-vte"]],C,safety_relevant=True),
 Q("symptom.edema.location","Edema Location","coded","location","발·발목, 종아리·다리 전체, 손·팔, 얼굴, 배, 전신 중 어디가 붓나요?",108,[G["distribution"]],C,allowed_values=["feet_ankles","calf_leg","hands_arms","face","abdomen","generalized","multiple"],terminology_binding={"system":SN,"focus_code":"271809000"},mrcm_ref=M),
 Q("symptom.edema.laterality","Edema Laterality","coded","laterality","왼쪽만, 오른쪽만, 양쪽 중 무엇인가요?",107,[G["distribution"],G["unilateral-vte"]],C,allowed_values=["left","right","bilateral","not_applicable","unclear"]),
 Q("symptom.severe_dyspnea","Severe Shortness of Breath","boolean","severe-dyspnea","가만히 있어도 숨이 차거나 숨쉬기 매우 어렵나요?",129,[G["cardiopulmonary-safety"]],S,safety_relevant=True,reuse_existing=True),
 Q("symptom.chest_pain","Chest Pain","boolean","chest-pain","가슴이 조이거나 무겁고 아픈가요?",128,[G["cardiopulmonary-safety"]],S,safety_relevant=True,reuse_existing=True),
 Q("symptom.hemoptysis","Coughing Blood","boolean","hemoptysis","기침할 때 피가 나오나요?",127,[G["cardiopulmonary-safety"]],S,safety_relevant=True,reuse_existing=True),
 Q("symptom.faint_confused_clammy","Faint Confused or Clammy","boolean","faint-clammy","심하게 어지럽거나 실신, 혼란, 식은땀이 있나요?",126,[G["cardiopulmonary-safety"]],S,safety_relevant=True),
 Q("symptom.sudden_face_tongue_throat_swelling","Sudden Face Tongue or Throat Swelling","boolean","allergic-swelling","얼굴·입술·혀·목이 갑자기 붓고 있나요?",125,[G["cardiopulmonary-safety"]],S,safety_relevant=True),
 Q("symptom.unilateral_leg_pain_swelling","Unilateral Leg Pain and Swelling","boolean","unilateral-pain","한쪽 다리만 붓고 종아리나 깊은 곳이 아픈가요?",124,[G["unilateral-vte"]],S,safety_relevant=True,terminology_binding={"system":SN,"code":"449615005"}),
 Q("symptom.edema.red_or_hot","Red or Hot Swollen Area","boolean","red-hot","부은 부위가 붉거나 뜨겁나요?",123,[G["infection"],G["unilateral-vte"]],S,safety_relevant=True),
 Q("symptom.fever","Fever","boolean","fever","열이 나거나 춥고 떨리나요?",122,[G["infection"]],S,safety_relevant=True,reuse_existing=True),
 Q("symptom.edema.rapid_generalized_worsening","Rapid Generalized Worsening","boolean","rapid-generalized","얼굴·배를 포함해 여러 부위가 빠르게 심하게 붓고 있나요?",121,[G["systemic-fluid"]],S,safety_relevant=True),
 Q("symptom.markedly_reduced_urine","Markedly Reduced Urine","boolean","low-urine","소변량이 평소보다 크게 줄었거나 거의 나오지 않나요?",120,[G["systemic-fluid"]],S,safety_relevant=True),
 Q("patient.pregnant_or_postpartum","Pregnant or Postpartum","coded","pregnancy","현재 임신 중이거나 출산 후 6주 이내인가요?",119,[G["systemic-fluid"]],S,safety_relevant=True,allowed_values=["pregnant","postpartum_6_weeks","not_applicable","unclear"]),
 Q("symptom.preeclampsia_warning_features","Pregnancy Hypertension Warning Features","boolean","pregnancy-warning","임신·산후 상태에서 심한 두통, 시야 변화 또는 명치·오른쪽 윗배 통증이 있나요?",118,[G["systemic-fluid"]],S,safety_relevant=True),
 Q("symptom.edema.severity","Edema Severity","coded","severity","붓기는 가벼움, 중간, 심함 중 어느 정도인가요?",106,[G["distribution"]],C,allowed_values=["mild","moderate","severe"]),
 Q("symptom.edema.pitting","Pitting Edema","coded","pitting","손가락으로 5초 눌렀을 때 자국이 남음, 안 남음, 확인 못함 중 무엇인가요?",105,[G["distribution"]],C,allowed_values=["pitting","non_pitting","not_checked","unclear"],terminology_binding={"system":SN,"code":"284521000"}),
 Q("symptom.edema.time_pattern","Edema Time Pattern","coded","time-pattern","아침, 저녁, 하루 종일 중 언제 가장 심한가요?",104,[G["distribution"]],C,allowed_values=["morning","evening","all_day","variable"]),
 Q("symptom.edema.pain","Edema Pain","coded","pain","부은 부위 통증은 없음, 가벼움, 중간, 심함 중 무엇인가요?",103,[G["distribution"],G["unilateral-vte"]],C,allowed_values=["none","mild","moderate","severe"]),
 Q("symptom.edema.skin_change_or_wound","Skin Change or Wound","boolean","skin-change","피부가 팽팽·번들거리거나 색이 변하고 상처·진물이 있나요?",94,[G["infection"],G["context"]],R),
 Q("symptom.dyspnea_on_exertion","Exertional Dyspnea","boolean","exertional-dyspnea","평소 활동이나 계단에서 전보다 숨이 차나요?",102,[G["systemic-fluid"]],R,reuse_existing=True),
 Q("symptom.orthopnea","Orthopnea","boolean","orthopnea","누우면 숨이 차서 베개를 여러 개 쓰거나 앉아 자나요?",101,[G["systemic-fluid"]],R,reuse_existing=True),
 Q("symptom.paroxysmal_nocturnal_dyspnea","Paroxysmal Nocturnal Dyspnea","boolean","pnd","자다가 숨이 차서 깨거나 앉아야 나아지나요?",100,[G["systemic-fluid"]],R,reuse_existing=True),
 Q("symptom.rapid_weight_gain","Rapid Weight Gain","boolean","weight-gain","며칠 사이 체중이 빠르게 늘었나요?",99,[G["systemic-fluid"]],R),
 Q("symptom.abdominal_swelling_or_ascites","Abdominal Swelling","boolean","abdominal-swelling","배가 붓거나 둘레가 빠르게 늘었나요?",98,[G["systemic-fluid"]],R),
 Q("risk.recent_immobility_or_surgery","Recent Immobility or Surgery","boolean","immobility","최근 12주 안에 수술, 입원, 깁스, 장거리 이동 또는 며칠간 거의 움직이지 못한 일이 있나요?",97,[G["unilateral-vte"],G["context"]],R,reuse_existing=True),
 Q("history.venous_thromboembolism","History of DVT or PE","boolean","vte-history","심부정맥혈전이나 폐색전을 진단받은 적이 있나요?",96,[G["unilateral-vte"]],R,reuse_existing=True),
 Q("risk.active_cancer_or_hormonal_therapy","Cancer or Hormonal Therapy","boolean","cancer-hormone","활동성 암 치료 중이거나 피임약·호르몬 치료를 사용하나요?",95,[G["unilateral-vte"]],R),
 Q("history.heart_kidney_liver_or_venous_disease","Heart Kidney Liver or Venous Disease","string","systemic-history","심부전, 신장·간 질환, 정맥부전 또는 림프부종 병력이 있나요?",93,[G["systemic-fluid"],G["context"]],R),
 Q("medication.edema_relevant","Edema-relevant Medication","string","medication","암로디핀 같은 혈압약, 호르몬, 소염진통제, 스테로이드 등 최근 시작·변경한 약이 있나요?",92,[G["context"]],R),
 Q("event.edema.injury_bite_or_local_trigger","Injury Bite or Local Trigger","boolean","local-trigger","부은 부위에 최근 외상, 벌레 물림, 주사 또는 상처가 있었나요?",91,[G["infection"],G["context"]],D),
 Q("lifestyle.prolonged_standing_sitting_or_salt","Standing Sitting or Salt","string","lifestyle","오래 서거나 앉기, 짠 음식 또는 최근 활동 변화와 관련 있나요?",90,[G["context"]],D),
 Q("symptom.edema.functional_impact","Functional Impact","coded","impact","걷기, 신발 착용, 일상 또는 수면 영향은 없음, 가벼움, 중간, 심함 중 무엇인가요?",89,[G["distribution"]],C,allowed_values=["none","mild","moderate","severe"]),
 ]
 rules=[
 safety_rule(P,"severe-dyspnea",{"all":[{"fact":"symptom.edema.current","equals":True},{"fact":"symptom.severe_dyspnea","equals":True}]},"emergency",1000),
 safety_rule(P,"chest-pain",{"all":[{"fact":"symptom.edema.current","equals":True},{"fact":"symptom.chest_pain","equals":True}]},"emergency",1000),
 safety_rule(P,"hemoptysis",{"all":[{"fact":"symptom.edema.current","equals":True},{"fact":"symptom.hemoptysis","equals":True}]},"emergency",1000),
 safety_rule(P,"faint-clammy",{"all":[{"fact":"symptom.edema.current","equals":True},{"fact":"symptom.faint_confused_clammy","equals":True}]},"emergency",1000),
 safety_rule(P,"allergic-swelling",{"fact":"symptom.sudden_face_tongue_throat_swelling","equals":True},"emergency",1000),
 safety_rule(P,"pregnancy-warning",{"all":[{"fact":"patient.pregnant_or_postpartum","in":["pregnant","postpartum_6_weeks"]},{"fact":"symptom.preeclampsia_warning_features","equals":True}]},"emergency",1000),
 safety_rule(P,"unilateral-pain",{"fact":"symptom.unilateral_leg_pain_swelling","equals":True},"urgent",900),
 safety_rule(P,"red-hot-fever",{"all":[{"fact":"symptom.edema.red_or_hot","equals":True},{"fact":"symptom.fever","equals":True}]},"urgent",900),
 safety_rule(P,"rapid-low-urine",{"all":[{"fact":"symptom.edema.rapid_generalized_worsening","equals":True},{"fact":"symptom.markedly_reduced_urine","equals":True}]},"urgent",900),
 safety_rule(P,"sudden-severe",{"all":[{"fact":"symptom.edema.sudden_onset","equals":True},{"fact":"symptom.edema.severity","equals":"severe"}]},"urgent",850)]
 return {"id":"knowledge.generated.edema","version":VERSION,"status":"research_only","usage_modes":["research_test","simulation"],"source_manifest":"source-manifest.primary-care-edema-research","default_refresh":default_refresh(),"extra_nodes":[{"id":v,"type":"ClinicalGroup","display":v.split(".")[-1]} for v in G.values()],"group_hypothesis_edges":[],"safety_rules":rules,"entries":e,"provenance":provenance(SOURCES)}

def source_docs():
 defs=[("source.nhs.edema.2026","NHS","Swollen ankles feet and legs","2026","https://www.nhs.uk/conditions/oedema/","public_health_guidance",7),("source.nice.ng158.vte.2023","NICE","Venous thromboembolic diseases","NG158-2023","https://www.nice.org.uk/guidance/ng158/chapter/Recommendations","clinical_guideline",1),("source.nice.ng106.heart-failure.2025","NICE","Chronic heart failure","NG106-2025","https://www.nice.org.uk/guidance/ng106/chapter/recommendations","clinical_guideline",1),("source.stom.edema.20260714","Infoclinic","STOM edema MRCM","SNOMEDCT-20260701","https://stom.infoclinic.co/allow/attributes/SNOMEDCT/267038008","terminology_server",30)]
 arts=[{"id":i,"kind":"terminology_mrcm_query_summary" if p=="terminology_server" else "clinical_guidance_metadata","publisher":pub,"title":t,"version":v,"url":u,"language":"en","digest":"metadata_only_not_cached","license_status":"unknown","complete":False,"monitor_profile":p,"monitor_interval_days":d,"last_monitored_at":"2026-07-14","next_monitor_at":"2026-08-13" if d==30 else ("2026-07-21" if d==7 else "2026-07-15"),"assertions":["Build-Time only; Runtime does not browse; content remains unreviewed."]} for i,pub,t,v,u,p,d in defs]
 research={"id":"source-manifest.primary-care-edema-research","version":VERSION,"acquired_at":CREATED_AT,"status":"research_only","artifacts":arts,"provenance":provenance([x[0] for x in defs])}
 paths=[("source.repository.foundation","repository_specification","FOUNDATION.md",True),("source.generated.edema","generated_clinical_knowledge","knowledge/generated/cardiovascular/edema/edema.json",True),("source.mapping.edema","terminology_mapping","mappings/terminology/snomed-mrcm-edema.json",False),("source.external.edema","external_source_manifest","sources/manifests/primary-care-edema-research.json",False),("source.policy.edema","runtime_policy","policies/primary-care-edema-completion.json",True)]
 primary={"id":"source-manifest.primary-care-edema","version":VERSION,"acquired_at":CREATED_AT,"artifacts":[{"id":i,"kind":k,"publisher":"clinical-interview-platform","version":VERSION,"language":"en","path":p,"digest":"computed_at_build","license_status":"allowed" if c else "unknown","complete":c} for i,k,p,c in paths],"provenance":provenance(["FOUNDATION.md","PROJECT_CONTEXT.md"])}
 return primary,research

def cases(f):
 tm={"severe-dyspnea":["symptom.edema.current","symptom.severe_dyspnea"],"chest-pain":["symptom.edema.current","symptom.chest_pain"],"hemoptysis":["symptom.edema.current","symptom.hemoptysis"],"faint-clammy":["symptom.edema.current","symptom.faint_confused_clammy"],"allergic-swelling":["symptom.sudden_face_tongue_throat_swelling"],"pregnancy-warning":["patient.pregnant_or_postpartum","symptom.preeclampsia_warning_features"],"unilateral-pain":["symptom.unilateral_leg_pain_swelling"],"red-hot-fever":["symptom.edema.red_or_hot","symptom.fever"],"rapid-low-urine":["symptom.edema.rapid_generalized_worsening","symptom.markedly_reduced_urine"],"sudden-severe":["symptom.edema.sudden_onset","symptom.edema.severity"]}
 out={}
 for i,r in enumerate(f["safety_rules"]):
  k=r["id"].split("safety.")[1]; lvl=r["then"]["safety_level"]; hs={x:{"value":True} for x in tm[k]}
  if k=="pregnancy-warning": hs["patient.pregnant_or_postpartum"]={"value":"pregnant"}
  if k=="sudden-severe": hs["symptom.edema.severity"]={"value":"severe"}
  out[f"EDEMA-{k.upper()}.json"]={"id":f"EDEMA-{k.upper()}","simulation_language":"ko","persona":{"age":42+i},"initial_statement":{"ko":"다리가 부었어요."},"hidden_state":hs,"expected":{"expected_safety_level":lvl,"expected_safety_action":"human_handoff","expected_stop_reason":f"{lvl}_escalation","expected_triggered_rules_contains":[r["id"]],"expected_max_turns":26,"forbidden_assertions":["diagnosis.dvt","diagnosis.heart_failure"]},"provenance":provenance(SOURCES)}
 hidden={}
 for x in f["entries"]:
  a=x["fact"]; fid=a["id"]
  if a["value_type"]=="boolean": hidden[fid]={"value":fid=="symptom.edema.current"}
  elif a["value_type"]=="quantity": hidden[fid]={"value":{"amount":5,"unit":"days"}}
  elif a["value_type"]=="coded": hidden[fid]={"value":a.get("allowed_values",["unclear"])[-1]}
  else: hidden[fid]={"value":"없음"}
 declined="medication.edema_relevant"; hidden.pop(declined)
 out["EDEMA-DATA-ABSENT.json"]={"id":"EDEMA-DATA-ABSENT","simulation_language":"ko","persona":{"age":56},"initial_statement":{"ko":"양쪽 발목이 조금 부어요."},"hidden_state":hidden,"response_behavior":{declined:{"dataAbsentReason":"asked-declined"}},"expected":{"expected_data_absent_reasons":{declined:"asked-declined"},"expected_safety_level":"routine","expected_stop_reason":"required_targets_addressed_with_absent_data","expected_max_turns":37,"forbidden_assertions":["diagnosis.venous_insufficiency"]},"provenance":provenance(["source.nhs.edema.2026","specifications/clinical-memory.md"])}
 return out

def main():
 f=fragment(); graph,rules=base_graph_and_rules(prefix=P,rfe=RFE,display="Swelling or Edema",intents=[("intent.characterize_symptom","Characterize Symptom"),("intent.screen_red_flags","Screen Red Flags"),("intent.differentiate_common_causes","Differentiate Common Sources"),("intent.risk_assessment","Risk Assessment")]); primary,research=source_docs()
 concepts=[("267038008","Edema (finding)",20),("271809000","Peripheral edema (disorder)",22),("449615005","Swelling of lower leg (finding)",20),("284521000","Pitting edema (finding)",20),("445088006","Edema of face (finding)",20)]
 m={"id":M,"version":VERSION,"status":"research_only","review_status":"unreviewed","terminology":{"system":SN,"version":"http://snomed.info/sct/900000000000207008/version/20260701","source":"STOM"},"focus_concepts":[{"code":c,"display":d,"attribute_count_returned":n} for c,d,n in concepts],"checks":[{"focus_code":c,"attribute_code":a,"allowed":True} for c,_,_ in concepts for a in ("363698007","246112005")],"validation":{"method":"build_time_live_mrcm_summary","checked_at":CREATED_AT,"raw_response_cached":False,"complete_mrcm_snapshot":False,"clinical_rule_authority":False,"result":"provisional_pass"},"provenance":provenance(["source.stom.edema.20260714"])}
 docs=[("knowledge/base/primary-care-edema.json",graph),("rules/base/primary-care-edema.json",rules),("knowledge/generated/cardiovascular/edema/edema.json",f),("mappings/terminology/snomed-mrcm-edema.json",m),("sources/manifests/primary-care-edema.json",primary),("sources/manifests/primary-care-edema-research.json",research),("policies/primary-care-edema-completion.json",completion_policy(prefix="edema",fragment=f,presentation_fact="symptom.edema.current",question_budget=37,source_refs=SOURCES))]
 for p,d in docs: write_json(p,d)
 for n,c in cases(f).items(): write_json("simulation/patients/cardiovascular/edema/"+n,c)
if __name__=="__main__": main()
