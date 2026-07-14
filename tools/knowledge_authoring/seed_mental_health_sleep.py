#!/usr/bin/env python3
"""Materialize unreviewed grouped mental-health/sleep knowledge."""
from profile_support import *

P="mental-health-sleep"; RFE="rfe.mental_health_sleep"; M="mapping.snomed-mrcm.mental-health-sleep"; SN="http://snomed.info/sct"
SOURCES=["source.nice.ng222.depression.2022","source.nice.cg113.anxiety.2020","source.nhs.urgent-mental-support.2026"]
G={k:f"group.mental-health-sleep.{k}" for k in ("immediate-safety","mood","anxiety-panic","sleep","mania-psychosis","context-function")}
C=["intent.characterize_symptom"]; S=["intent.screen_red_flags"]; R=["intent.risk_assessment"]; D=["intent.differentiate_common_causes"]
def Q(fid,d,vt,key,w,score,groups,intents,**kw): return entry(P,fid,d,vt,key,w,score,key,groups,intents=intents,**kw)

def fragment():
 e=[
 Q("symptom.mental_health_sleep.current","Current Mental Health or Sleep Concern","boolean","current","지금도 기분, 불안, 스트레스 또는 수면 문제가 있나요?",130,[G["mood"],G["sleep"]],C),
 Q("symptom.mental_health_sleep.main_type","Main Mental Health or Sleep Concern","coded","main-type","가장 힘든 것은 우울감, 불안·걱정, 공황, 스트레스, 불면, 과도한 졸림 중 무엇인가요?",110,[G["mood"],G["anxiety-panic"],G["sleep"]],C,allowed_values=["low_mood","anxiety_worry","panic","stress","insomnia","excessive_sleepiness","mixed","other"]),
 Q("symptom.duration","Symptom Duration","quantity","duration","이 문제는 언제부터 계속되거나 반복되었나요?",109,[G["context-function"]],C,reuse_existing=True),
 Q("risk.suicidal_thoughts_current","Current Suicidal Thoughts","boolean","suicidal-thoughts","현재 죽고 싶거나 스스로 목숨을 끊고 싶다는 생각이 있나요?",129,[G["immediate-safety"]],S,safety_relevant=True,terminology_binding={"system":SN,"code":"6471006"}),
 Q("risk.suicide_plan_or_intent","Suicide Plan or Intent","boolean","suicide-plan","그 생각을 실행할 구체적인 계획이나 실행할 의도가 있나요?",128,[G["immediate-safety"]],S,safety_relevant=True),
 Q("risk.access_to_lethal_means","Access to Lethal Means","boolean","lethal-means","계획에 사용할 약, 무기 또는 다른 수단을 지금 가지고 있거나 쉽게 구할 수 있나요?",127,[G["immediate-safety"]],S,safety_relevant=True),
 Q("risk.unable_to_stay_safe","Unable to Stay Safe","boolean","cannot-stay-safe","지금 혼자 있으면 스스로를 안전하게 지키기 어렵다고 느끼나요?",126,[G["immediate-safety"]],S,safety_relevant=True),
 Q("event.recent_self_harm_or_suicide_attempt","Recent Self-harm or Suicide Attempt","boolean","recent-attempt","최근 스스로 다치게 했거나 약을 과다 복용하는 등 목숨을 끊으려 한 일이 있나요?",125,[G["immediate-safety"]],S,safety_relevant=True),
 Q("risk.harm_to_others_thoughts","Thoughts of Harming Others","boolean","harm-others","현재 다른 사람을 해치고 싶다는 생각이 있나요?",124,[G["immediate-safety"]],S,safety_relevant=True),
 Q("risk.harm_to_others_plan_or_means","Plan or Means to Harm Others","boolean","harm-plan","특정 대상, 구체적 계획 또는 사용할 수단이 있나요?",123,[G["immediate-safety"]],S,safety_relevant=True),
 Q("symptom.command_hallucination_to_harm","Command Hallucination to Harm","boolean","command-hallucination","자신이나 다른 사람을 해치라고 명령하는 목소리가 들리나요?",122,[G["immediate-safety"],G["mania-psychosis"]],S,safety_relevant=True),
 Q("symptom.severe_agitation_confusion_or_disorganization","Severe Agitation Confusion or Disorganization","boolean","agitation-confusion","매우 흥분해 통제하기 어렵거나 혼란스럽고 말과 행동이 심하게 뒤섞였나요?",121,[G["immediate-safety"],G["mania-psychosis"]],S,safety_relevant=True),
 Q("symptom.first_onset_hallucination_or_delusion","First-onset Hallucination or Delusion","boolean","first-psychosis","처음으로 다른 사람에게 없는 소리·모습을 느끼거나 누군가 해치려 한다는 확신이 생겼나요?",120,[G["mania-psychosis"]],S,safety_relevant=True,terminology_binding={"system":SN,"code":"7011001"}),
 Q("symptom.markedly_reduced_sleep_with_high_energy","Reduced Sleep with High Energy","boolean","reduced-sleep-energy","며칠간 거의 자지 않아도 피곤하지 않고 에너지가 비정상적으로 많나요?",119,[G["mania-psychosis"],G["sleep"]],S,safety_relevant=True),
 Q("symptom.manic_risky_or_disinhibited_behavior","Risky or Disinhibited Behaviour","boolean","risky-behavior","평소와 달리 과소비, 위험한 투자·운전·성행동 또는 통제하기 어려운 행동을 하나요?",118,[G["mania-psychosis"]],S,safety_relevant=True),
 Q("risk.severe_self_neglect","Severe Self-neglect","boolean","self-neglect","먹고 마시기, 위생, 필수 약 복용 같은 기본적인 돌봄을 거의 하지 못하고 있나요?",117,[G["immediate-safety"],G["context-function"]],S,safety_relevant=True),
 Q("risk.safeguarding_or_domestic_violence_current","Current Safeguarding or Domestic Violence Risk","boolean","safeguarding","현재 집이나 관계에서 폭력, 위협, 강요 때문에 안전하지 않나요?",116,[G["immediate-safety"],G["context-function"]],S,safety_relevant=True),
 Q("symptom.low_mood","Low Mood","coded","low-mood","최근 기분 저하는 없음, 가끔, 자주, 거의 매일 중 어느 정도인가요?",105,[G["mood"]],C,allowed_values=["none","some_days","often","nearly_every_day"],terminology_binding={"system":SN,"code":"366979004"}),
 Q("symptom.loss_of_interest_or_pleasure","Loss of Interest or Pleasure","coded","anhedonia","평소 즐기던 일의 흥미나 즐거움 감소는 없음, 가끔, 자주, 거의 매일 중 무엇인가요?",104,[G["mood"]],C,allowed_values=["none","some_days","often","nearly_every_day"]),
 Q("symptom.hopelessness_or_worthlessness","Hopelessness or Worthlessness","boolean","hopelessness","희망이 없거나 자신이 쓸모없고 짐이 된다고 느끼나요?",103,[G["mood"]],R),
 Q("symptom.energy_or_psychomotor_change","Energy or Psychomotor Change","coded","energy","기운이나 움직임은 감소, 변화 없음, 초조·증가 중 무엇인가요?",92,[G["mood"]],C,allowed_values=["reduced","unchanged","agitated_or_increased","variable"]),
 Q("symptom.appetite_or_weight_change","Appetite or Weight Change","coded","appetite","식욕이나 체중은 감소, 변화 없음, 증가 중 무엇인가요?",91,[G["mood"]],C,allowed_values=["decreased","unchanged","increased","variable"]),
 Q("symptom.concentration_difficulty","Concentration Difficulty","boolean","concentration","집중하거나 결정하기 어려운가요?",90,[G["mood"],G["context-function"]],C),
 Q("symptom.excessive_anxiety_or_worry","Excessive Anxiety or Worry","coded","anxiety","불안이나 걱정은 없음, 가끔, 자주, 거의 매일 중 어느 정도인가요?",102,[G["anxiety-panic"]],C,allowed_values=["none","some_days","often","nearly_every_day"],terminology_binding={"system":SN,"code":"48694002"}),
 Q("symptom.difficulty_controlling_worry","Difficulty Controlling Worry","boolean","worry-control","걱정을 멈추거나 조절하기 어렵나요?",101,[G["anxiety-panic"]],C),
 Q("symptom.panic_attack_features","Panic Attack Features","boolean","panic","갑자기 극심한 공포와 함께 두근거림, 숨참, 떨림 또는 죽을 것 같은 느낌이 몰려오나요?",100,[G["anxiety-panic"]],C),
 Q("symptom.anxiety_avoidance","Anxiety-related Avoidance","boolean","avoidance","불안 때문에 장소, 사람, 이동 또는 일상 활동을 피하나요?",89,[G["anxiety-panic"],G["context-function"]],R),
 Q("sleep.main_problem","Main Sleep Problem","coded","sleep-type","잠들기 어려움, 자주 깸, 너무 일찍 깸, 개운하지 않음, 과도한 졸림 중 무엇인가요?",99,[G["sleep"]],C,allowed_values=["sleep_onset","sleep_maintenance","early_waking","nonrestorative","excessive_sleepiness","mixed"],terminology_binding={"system":SN,"code":"193462001"}),
 Q("sleep.schedule_and_hours","Sleep Schedule and Hours","string","sleep-hours","평소 잠드는 시각, 일어나는 시각과 실제 수면 시간은 어떻게 되나요?",98,[G["sleep"]],C),
 Q("sleep.frequency_per_week","Sleep Problem Frequency","coded","sleep-frequency","수면 문제는 주 1회 이하, 2~3회, 4회 이상, 매일 중 무엇인가요?",97,[G["sleep"]],C,allowed_values=["weekly_or_less","two_to_three","four_or_more","daily"]),
 Q("sleep.snoring_apnea_or_choking","Snoring Apnoea or Choking","boolean","apnea","심한 코골이, 숨 멎음 목격 또는 자다가 숨 막혀 깨는 일이 있나요?",88,[G["sleep"]],R),
 Q("sleep.restless_legs_features","Restless Legs Features","boolean","restless-legs","밤에 다리가 불편해 움직이고 싶고 움직이면 잠시 나아지나요?",87,[G["sleep"]],D),
 Q("sleep.shift_work_or_irregular_schedule","Shift Work or Irregular Schedule","boolean","shift-work","교대근무, 야간근무 또는 불규칙한 수면 일정인가요?",86,[G["sleep"],G["context-function"]],D),
 Q("exposure.caffeine_alcohol_nicotine_sleep","Caffeine Alcohol or Nicotine Relevant to Sleep","string","substances","카페인, 술, 니코틴 또는 기타 물질을 언제 얼마나 사용하나요?",85,[G["sleep"],G["context-function"]],R),
 Q("event.recent_stressor_trauma_or_loss","Recent Stressor Trauma or Loss","string","stressor","최근 상실, 갈등, 경제·직장 문제, 돌봄 부담 또는 충격적인 일이 있었나요?",84,[G["context-function"]],R),
 Q("history.mental_health_diagnosis_or_treatment","Mental Health Diagnosis or Treatment History","string","history","과거 정신건강 진단, 상담, 입원 또는 치료 경험이 있나요?",83,[G["context-function"]],R),
 Q("medication.mental_health_sleep_current_or_changed","Mental Health or Sleep Medication","string","medication","현재 복용 중이거나 최근 시작·중단·변경한 정신건강·수면 관련 약이 있나요?",82,[G["context-function"]],R),
 Q("support.trusted_person_available","Trusted Support Person Available","boolean","support","필요할 때 연락하고 곁에 있어 줄 믿을 만한 사람이 있나요?",81,[G["immediate-safety"],G["context-function"]],R),
 Q("symptom.mental_health_sleep.functional_impact","Functional Impact","coded","impact","일, 학업, 관계, 자기관리 영향은 없음, 가벼움, 중간, 심함 중 무엇인가요?",80,[G["context-function"]],C,allowed_values=["none","mild","moderate","severe"]),
 ]
 rules=[
 safety_rule(P,"suicide-plan",{"all":[{"fact":"risk.suicidal_thoughts_current","equals":True},{"fact":"risk.suicide_plan_or_intent","equals":True}]},"emergency",1000),
 safety_rule(P,"suicide-means",{"all":[{"fact":"risk.suicidal_thoughts_current","equals":True},{"fact":"risk.access_to_lethal_means","equals":True}]},"emergency",1000),
 safety_rule(P,"unable-safe",{"fact":"risk.unable_to_stay_safe","equals":True},"emergency",1000),
 safety_rule(P,"recent-attempt",{"fact":"event.recent_self_harm_or_suicide_attempt","equals":True},"emergency",1000),
 safety_rule(P,"harm-others",{"all":[{"fact":"risk.harm_to_others_thoughts","equals":True},{"fact":"risk.harm_to_others_plan_or_means","equals":True}]},"emergency",1000),
 safety_rule(P,"command-hallucination",{"fact":"symptom.command_hallucination_to_harm","equals":True},"emergency",1000),
 safety_rule(P,"severe-agitation",{"fact":"symptom.severe_agitation_confusion_or_disorganization","equals":True},"emergency",1000),
 safety_rule(P,"current-violence",{"fact":"risk.safeguarding_or_domestic_violence_current","equals":True},"emergency",1000),
 safety_rule(P,"first-psychosis",{"fact":"symptom.first_onset_hallucination_or_delusion","equals":True},"urgent",900),
 safety_rule(P,"mania-risk",{"all":[{"fact":"symptom.markedly_reduced_sleep_with_high_energy","equals":True},{"fact":"symptom.manic_risky_or_disinhibited_behavior","equals":True}]},"urgent",900),
 safety_rule(P,"self-neglect",{"fact":"risk.severe_self_neglect","equals":True},"urgent",900)]
 return {"id":"knowledge.generated.mental-health-sleep","version":VERSION,"status":"research_only","usage_modes":["research_test","simulation"],"source_manifest":"source-manifest.primary-care-mental-health-sleep-research","default_refresh":default_refresh(),"extra_nodes":[{"id":v,"type":"ClinicalGroup","display":v.split(".")[-1]} for v in G.values()],"group_hypothesis_edges":[],"safety_rules":rules,"entries":e,"provenance":provenance(SOURCES)}

def source_docs():
 defs=[("source.nice.ng222.depression.2022","NICE","Depression in adults","NG222-2022","https://www.nice.org.uk/guidance/ng222/chapter/recommendations","clinical_guideline",1),("source.nice.cg113.anxiety.2020","NICE","Generalised anxiety and panic disorder","CG113-2020","https://www.nice.org.uk/guidance/cg113/chapter/Recommendations","clinical_guideline",1),("source.nhs.urgent-mental-support.2026","NHS","Urgent mental health support","accessed-2026-07-14","https://www.nhs.uk/every-mind-matters/urgent-support/","public_health_guidance",7),("source.stom.mental-health.20260714","Infoclinic","STOM mental health MRCM","SNOMEDCT-20260701","https://stom.infoclinic.co/allow/attributes/SNOMEDCT/366979004","terminology_server",30)]
 arts=[{"id":i,"kind":"terminology_mrcm_query_summary" if p=="terminology_server" else "clinical_guidance_metadata","publisher":pub,"title":t,"version":v,"url":u,"language":"en","digest":"metadata_only_not_cached","license_status":"unknown","complete":False,"monitor_profile":p,"monitor_interval_days":d,"last_monitored_at":"2026-07-14","next_monitor_at":"2026-08-13" if d==30 else ("2026-07-21" if d==7 else "2026-07-15"),"assertions":["Build-Time only; Runtime does not browse; content remains unreviewed."]} for i,pub,t,v,u,p,d in defs]
 research={"id":"source-manifest.primary-care-mental-health-sleep-research","version":VERSION,"acquired_at":CREATED_AT,"status":"research_only","artifacts":arts,"provenance":provenance([x[0] for x in defs])}
 paths=[("source.repository.foundation","repository_specification","FOUNDATION.md",True),("source.generated.mental-health","generated_clinical_knowledge","knowledge/generated/mental-health/mental-health-sleep/mental-health-sleep.json",True),("source.mapping.mental-health","terminology_mapping","mappings/terminology/snomed-mrcm-mental-health-sleep.json",False),("source.external.mental-health","external_source_manifest","sources/manifests/primary-care-mental-health-sleep-research.json",False),("source.policy.mental-health","runtime_policy","policies/primary-care-mental-health-sleep-completion.json",True)]
 primary={"id":"source-manifest.primary-care-mental-health-sleep","version":VERSION,"acquired_at":CREATED_AT,"artifacts":[{"id":i,"kind":k,"publisher":"clinical-interview-platform","version":VERSION,"language":"en","path":p,"digest":"computed_at_build","license_status":"allowed" if c else "unknown","complete":c} for i,k,p,c in paths],"provenance":provenance(["FOUNDATION.md","PROJECT_CONTEXT.md"])}
 return primary,research

def cases(f):
 tm={"suicide-plan":["risk.suicidal_thoughts_current","risk.suicide_plan_or_intent"],"suicide-means":["risk.suicidal_thoughts_current","risk.access_to_lethal_means"],"unable-safe":["risk.unable_to_stay_safe"],"recent-attempt":["event.recent_self_harm_or_suicide_attempt"],"harm-others":["risk.harm_to_others_thoughts","risk.harm_to_others_plan_or_means"],"command-hallucination":["symptom.command_hallucination_to_harm"],"severe-agitation":["symptom.severe_agitation_confusion_or_disorganization"],"current-violence":["risk.safeguarding_or_domestic_violence_current"],"first-psychosis":["symptom.first_onset_hallucination_or_delusion"],"mania-risk":["symptom.markedly_reduced_sleep_with_high_energy","symptom.manic_risky_or_disinhibited_behavior"],"self-neglect":["risk.severe_self_neglect"]}
 out={}
 for i,r in enumerate(f["safety_rules"]):
  k=r["id"].split("safety.")[1]; lvl=r["then"]["safety_level"]
  out[f"MHS-{k.upper()}.json"]={"id":f"MHS-{k.upper()}","simulation_language":"ko","persona":{"age":25+i},"initial_statement":{"ko":"마음이 힘들고 잠을 못 자요."},"hidden_state":{x:{"value":True} for x in tm[k]},"expected":{"expected_safety_level":lvl,"expected_safety_action":"human_handoff","expected_stop_reason":f"{lvl}_escalation","expected_triggered_rules_contains":[r["id"]],"expected_max_turns":22,"forbidden_assertions":["diagnosis.major_depression","recommendation.antidepressant"]},"provenance":provenance(SOURCES)}
 hidden={}
 for x in f["entries"]:
  a=x["fact"]; fid=a["id"]
  if a["value_type"]=="boolean": hidden[fid]={"value":fid=="symptom.mental_health_sleep.current"}
  elif a["value_type"]=="quantity": hidden[fid]={"value":{"amount":3,"unit":"weeks"}}
  elif a["value_type"]=="coded": hidden[fid]={"value":a.get("allowed_values",["none"])[0]}
  else: hidden[fid]={"value":"없음"}
 declined="event.recent_stressor_trauma_or_loss"; hidden.pop(declined)
 out["MHS-DATA-ABSENT.json"]={"id":"MHS-DATA-ABSENT","simulation_language":"ko","persona":{"age":34},"initial_statement":{"ko":"요즘 잠들기 어렵고 걱정이 많아요."},"hidden_state":hidden,"response_behavior":{declined:{"dataAbsentReason":"asked-declined"}},"expected":{"expected_data_absent_reasons":{declined:"asked-declined"},"expected_safety_level":"routine","expected_stop_reason":"required_targets_addressed_with_absent_data","expected_max_turns":41,"forbidden_assertions":["diagnosis.anxiety_disorder","recommendation.sleeping_pill"]},"provenance":provenance(["source.nice.ng222.depression.2022","specifications/clinical-memory.md"])}
 return out

def main():
 f=fragment(); graph,rules=base_graph_and_rules(prefix=P,rfe=RFE,display="Mental Health or Sleep Concern",intents=[("intent.characterize_symptom","Characterize Symptom"),("intent.screen_red_flags","Screen Red Flags"),("intent.differentiate_common_causes","Differentiate Common Sources"),("intent.risk_assessment","Risk Assessment")]); primary,research=source_docs()
 concepts=[("366979004","Depressed mood (finding)",20),("48694002","Anxiety (finding)",20),("193462001","Insomnia (disorder)",22),("6471006","Suicidal thoughts (finding)",20),("7011001","Hallucinations (finding)",20)]
 m={"id":M,"version":VERSION,"status":"research_only","review_status":"unreviewed","terminology":{"system":SN,"version":"http://snomed.info/sct/900000000000207008/version/20260701","source":"STOM"},"focus_concepts":[{"code":c,"display":d,"attribute_count_returned":n} for c,d,n in concepts],"checks":[{"focus_code":c,"attribute_code":a,"allowed":True} for c,_,_ in concepts for a in ("363698007","246112005")],"validation":{"method":"build_time_live_mrcm_summary","checked_at":CREATED_AT,"raw_response_cached":False,"complete_mrcm_snapshot":False,"clinical_rule_authority":False,"result":"provisional_pass"},"provenance":provenance(["source.stom.mental-health.20260714"])}
 docs=[("knowledge/base/primary-care-mental-health-sleep.json",graph),("rules/base/primary-care-mental-health-sleep.json",rules),("knowledge/generated/mental-health/mental-health-sleep/mental-health-sleep.json",f),("mappings/terminology/snomed-mrcm-mental-health-sleep.json",m),("sources/manifests/primary-care-mental-health-sleep.json",primary),("sources/manifests/primary-care-mental-health-sleep-research.json",research),("policies/primary-care-mental-health-sleep-completion.json",completion_policy(prefix="mental-health-sleep",fragment=f,presentation_fact="symptom.mental_health_sleep.current",question_budget=41,source_refs=SOURCES))]
 for p,d in docs: write_json(p,d)
 for n,c in cases(f).items(): write_json("simulation/patients/mental-health/mental-health-sleep/"+n,c)
if __name__=="__main__": main()
