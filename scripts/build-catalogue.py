"""Build auditable source routing; never infer a clinical regimen from a title match."""
import json,pathlib,re,unicodedata,collections,argparse
root=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--pdf-cache',type=pathlib.Path,default=root/'.source-cache');args=parser.parse_args()
legacy=json.loads((root/'data/legacy.json').read_text())
sources=json.loads((root/'data/sources.json').read_text());byid={s['id']:s for s in sources}
chapters={27:'Common Conditions',63:'Emergency Conditions',96:'Cardiovascular Diseases',107:'Central Nervous System Diseases',123:'Genitourinary Diseases',128:'Endocrine Diseases',141:'Gastrointestinal Diseases',154:'Infections',172:'ENT Diseases',185:'Eye Diseases',212:'Skin Diseases',237:'Obstetrics and Gynecology',292:'Psychiatry Disorders',316:'Orthopedic Conditions',325:'Surgery',356:'Respiratory Diseases',373:'Pediatric Conditions',424:'Dental Conditions'}
mo={'Common Conditions':['8721','86111'],'Emergency Conditions':['5821','9451'],'Cardiovascular Diseases':['3811'],'Central Nervous System Diseases':['1621'],'Genitourinary Diseases':['5821','3601'],'Endocrine Diseases':['3601'],'Gastrointestinal Diseases':['9721','2101'],'Infections':['8721','86111'],'ENT Diseases':['4251','290'],'Eye Diseases':['6251'],'Skin Diseases':['8721'],'Obstetrics and Gynecology':['4571'],'Psychiatry Disorders':['606'],'Orthopedic Conditions':['8611'],'Surgery':['6191','2101','9471'],'Respiratory Diseases':['3261'],'Pediatric Conditions':['891'],'Dental Conditions':['475','9711']}
volume3={'Skin Diseases','Endocrine Diseases','Eye Diseases','Orthopedic Conditions','Gastrointestinal Diseases','Surgery'}
# Explicit disease-to-workflow routes reviewed against the ICMR catalogue.
ic={
 'Hypertension':['hypertensioninadults_final'], 'Atrial Fibrillation':['cardiology_1-1'], 'Bradyarrhythmias':['bradyarrthymia13_2_2'], 'Angina Pectoris':['cardiology_1-6'], 'Myocaridal Infraction':['cardiology_1-5','cardiology_1-4'],
 'Epilepsy':['neurology_epilepsy'],'Status Epilepticus':['neurology_epilepsy'],'Migraine':['neurology_headache'],'Tension-Type Headache (Tth)':['neurology_headache'],'Cluster Headache (Ch)':['neurology_headache'],'Stroke':['neurology_stroke'],'Dementia':['neurology_dementia'],'Acute Bacterial Meningitis':['neurology_neuroinfections'],'Viral Encephalitis':['neurology_neuroinfections'],'Paraplegia And Quadriplegia':['neurology_acute_paralysis'],
 'Urinary Tract Infection':['uti'],'Urinary Tract Infection (Uti)':['uti'],'Chronic Kidney Disease':['chronickidneydisease-updated'],'Acute Renal Failure (Arf)':['acutekidneyinjury-updated'],'Nephrotic Syndrome':['glomerulardiseases-updated'],
 'Hypothyroidism':['hypothyroidism'],'Diabetes Mellitus':['diabetes_mellitus_type_1','diabetes_mellitus_type_2'],'Diabetic Ketoacidosis':['diabetic_ketoacidosis'],
 'Acute Sinusitis':['ent_acute_rhinosinusitis'],'Epistaxis':['ent_epistaxis'],'Acute Suppurative Otitis Media':['ent_otorrhoea'],'Acute Tonsillitis':['ent_pharyngitis_and_sore_throat'],'Chronic Tonsillitis':['ent_pharyngitis_and_sore_throat'],
 'Normal Pregnancy':['ante-natalmanagementofnormalpregnancy-7'],'Postpartum Haemorrhage (Pph)':['updatedpostpartumhaemorrhage'],'Atonic Pph':['updatedpostpartumhaemorrhage'],
 'Major Depressive Disorder':['psychiatry_depression'],'Other Psychotic Disorders':['psychiatry_psychosis'],'Alcohol Use Disorder':['psychiatry_alcohol_use_disorders'],'Panic Disorder':['psychiatry_anxiety_disorder'],'Phobic Disorders':['psychiatry_anxiety_disorder'],'Conversion Disorder':['psychiatry_somatoform_disorder'],'Autistic Disorder':['psychiatry_developmental_problems'],'Mental Retardation':['psychiatry_developmental_problems'],
 'Bronchial Asthma':['pulmonology_asthma'],'Pneumonia':['paediatrics_severe_pneumonia'],'Acute Diarrhoea':['paediatrics_diarrhea'],'Protein Energy Malnutrition':['paediatrics_severe_acute_malnutrition'],'Tubercular Meningitis (Tbm)':['5_paediatric_tubercular_meningitis'],'Urinary Retention':['acuteurinaryretentioninmen3'],
 'Scabies':['stw_vol_3_20222'],'Bacterial Skin Infections':['stw_vol_3_20222'],'Tinea Cruris And Corporis':['stw_vol_3_20222'],'Tinea Capitis':['stw_vol_3_20222'],'Eczema':['stw_vol_3_20222'],'Contact Dermatitis':['stw_vol_3_20222'],'Psoriasis':['stw_vol_3_20222'],'Urticaria':['stw_vol_3_20222'],'Vitiligo':['stw_vol_3_20222'],'Alopecia Areata':['stw_vol_3_20222'],'Pemphigus Vulgaris':['stw_vol_3_20222'],'Chicken Pox':['stw_vol_3_20222'],'Herpes Zoster':['stw_vol_3_20222'],'I. Maculopapular Rash':['cutaneous_part_a'],'Iii.Fixed Drug Eruption':['cutaneous_part_a'],
 'Senile Cataract':['cataract'],'Diabetic Retinopathy':['diabetic_retinopathy'],'Glaucoma':['glaucoma'],'Primary Open Angle Glaucoma':['glaucoma'],'Primary Angle-Closure Glaucoma':['glaucoma'],
}
# These related workflows do not provide direct guidance for every presentation.
related={'Status Epilepticus','Angina Pectoris','Myocaridal Infraction','Acute Bacterial Meningitis','Viral Encephalitis','Paraplegia And Quadriplegia','Nephrotic Syndrome','Acute Tonsillitis','Chronic Tonsillitis','Acute Suppurative Otitis Media','Pneumonia','Protein Energy Malnutrition','Urinary Retention','Primary Open Angle Glaucoma','Primary Angle-Closure Glaucoma'}
specificmo={'Hypertension':['5191','6591'],'Snake Bite':['3941','5341'],'Dog Bite (Rabies)':['238'],'Diabetic Foot':['5381','9761'],'Alcohol Use Disorder':['7661','8291'],'Neonatal Jaundice':['8591','5461'],'Low Birth Weight Babies':['8361','8521'],'Osteoarthritis':['31911'],'Acute Sinusitis':['4221'],'Dental Fluorosis':['9711'],'Leprosy':['50','516'],'Chikungunya':['155'],'Malaria':['892'],'Leptospirosis':['919'],'Tuberculosis':['93'],'Dengue':['8721'],'Herpes Genitalis':['448'],'Syphillis':['448'],'Chancroid':['448'],'Lymphogranuloma Venerum':['448'],'Urethral Discharge':['448'],'Vaginal Discharge':['448']}
fix={'Myocaridal Infraction':'Myocardial infarction','Pyogenic Liver Abcess':'Pyogenic liver abscess','Ityrosporum Infections':'Pityrosporum infections','Syphillis':'Syphilis','Viral Keratits':'Viral keratitis','Mental Retardation':'Intellectual disability','Scorpions Bite':'Scorpion sting'}
normalize=lambda s:re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).lower()).strip()
# Optional locally retrieved PDFs are used only to locate disease headings, not to synthesize doses.
pdfs={}
try:
 import fitz
 for s in sources:
  path=args.pdf_cache/s['url'].split('/')[-1]
  if s['id'].startswith('mohfw-') and path.exists():
   d=fitz.open(path);heads=[]
   for i,p in enumerate(d):
    for b in p.get_text('dict')['blocks']:
     for l in b.get('lines',[]):
      text=' '.join(x['text'] for x in l['spans']).strip()
      if len(text)>4 and len(text)<110 and (text.isupper() or any(x['flags']&16 for x in l['spans'])):
       heads.append((i+1,normalize(text)))
   pdfs[s['id']]=heads
except ImportError:pass
conditions=[]
for x in legacy:
 original=x['t'];cat=chapters[max(k for k in chapters if k<=x['p'])];title=fix.get(original,original)
 refs=[]
 for key in ic.get(original,[]):
  sid='icmr-'+key.lower()
  if sid not in byid:raise ValueError('Missing source '+sid)
  relation='related-workflow' if original in related else 'topic-in-volume' if key=='stw_vol_3_20222' else 'condition-workflow'
  if cat=='Pediatric Conditions' and original in ['Hypothyroidism','Diabetes Mellitus','Urinary Tract Infection (Uti)','Nephrotic Syndrome','Status Epilepticus']:relation='related-workflow'
  refs.append({'sourceId':sid,'relation':relation,'note':'Check the workflow population and severity; it may cover only part of this condition.' if relation=='related-workflow' else 'Find the named topic inside Volume 3.' if relation=='topic-in-volume' else 'Condition-specific official workflow.'})
 for key in dict.fromkeys(specificmo.get(original,[])+mo.get(cat,[])):
  sid='mohfw-'+key
  if sid not in byid:continue
  tokens=normalize(re.sub(r'\([^)]*\)','',title));candidates=[]
  for p,h in pdfs.get(sid,[]):
   if p<3:continue
   if tokens==h or (len(tokens)>9 and tokens in h and len(h)<len(tokens)+35):candidates.append((p,h))
  match=candidates[0] if candidates else None
  refs.append({'sourceId':sid,'relation':'disease-heading' if match else 'condition-document' if key in specificmo.get(original,[]) and key not in ['8721'] else 'specialty-reference','page':match[0] if match else None,'matchedHeading':match[1] if match else None,'note':'Disease heading located in the PDF; the document edition may be unspecified.' if match else 'Relevant official document. Scope and edition must be checked.'})
 primary=any(r['relation'] in ['condition-workflow','topic-in-volume','condition-document','disease-heading'] for r in refs)
 conditions.append({'id':x['id'],'title':title,'originalTitle':original,'category':cat,'population':'children' if cat=='Pediatric Conditions' else 'pregnancy / gynecology' if cat=='Obstetrics and Gynecology' else 'see source population','legacyPage':x['p'],'legacyId':x['id'],'references':refs,'sourceStatus':'condition-source' if primary else 'related-source' if any(r['relation']=='related-workflow' for r in refs) else 'specialty-only','regimenStatus':'not-revalidated','checkedOn':'2026-10-06','summary':None})
# Fill clinically important omissions in the original automated index.
new=[('Heart failure','Cardiovascular Diseases','cardiology_1-3'),('NSTEMI','Cardiovascular Diseases','cardiology_1-4'),('STEMI','Cardiovascular Diseases','cardiology_1-5'),('COPD','Respiratory Diseases','pulmonology_chronic_obstructive_pulmonary_disease'),('Respiratory failure','Respiratory Diseases','pulmonology_respiratory_failure'),('Community acquired pneumonia','Respiratory Diseases','pulmonology_acute_respiratory_infections'),('Hospital acquired pneumonia','Respiratory Diseases',None),('Generalized anxiety disorder','Psychiatry Disorders','psychiatry_anxiety_disorder'),('Obsessive compulsive disorder','Psychiatry Disorders','psychiatry_anxiety_disorder'),('Gastrointestinal bleeding','Gastrointestinal Diseases','gastrointestinal_bleed_part_a')]
for title,cat,key in new:
 refs=[{'sourceId':'icmr-'+key,'relation':'related-workflow' if 'pneumonia' in title.lower() else 'condition-workflow','note':'Read the official workflow for treatment, doses and duration.'}] if key else []
 for mid in mo[cat]:
  if 'mohfw-'+mid in byid:refs.append({'sourceId':'mohfw-'+mid,'relation':'specialty-reference','note':'Relevant specialty guideline; confirm the condition section.'})
 conditions.append({'id':len(conditions),'title':title,'originalTitle':title,'category':cat,'population':'see source population','legacyId':None,'legacyPage':None,'references':refs,'sourceStatus':'condition-source' if key and 'pneumonia' not in title.lower() else 'related-source' if key else 'specialty-only','regimenStatus':'not-revalidated','checkedOn':'2026-10-06','summary':None})
# A small number of summaries were read from the named source, rather than inferred from catalogue titles.
for c in conditions:
 if c['title']=='Hypertension':
  c['summary']={'sourceId':'mohfw-5191','edition':'2016','scope':'Adult primary hypertension; source-specific summary, not a claim of latest practice','assessment':['Confirm blood pressure with repeat measurements and assess cardiovascular risk, kidney function and comorbidities.'],'treatment':['Lifestyle measures accompany individualized antihypertensive therapy. A calcium-channel blocker may be used alone or in combination with an ACE inhibitor/ARB or low-dose diuretic.'],'regimens':[{'drug':'Amlodipine','population':'Adults','dose':'5 mg orally once daily initially; 2.5 mg initially in elderly, small patients or hepatic impairment','titration':'Increase at 7–14 day intervals when indicated; maximum 10 mg once daily','duration':'Ongoing treatment individualized to BP response; no fixed short course','cautions':'Monitor hypotension and adverse effects. Check interacting medicines; the source limits concomitant simvastatin to 20 mg/day.','sourcePage':132}],'followUp':['The source describes monthly review until BP control, then six-monthly review; shorten follow-up according to clinical need.']};c['regimenStatus']='source-summary'
 if c['title']=='Diabetes Mellitus' and c['category']=='Endocrine Diseases':
  c['summary']={'sourceId':'icmr-diabetes_mellitus_type_2','edition':'2022','scope':'Type 2 diabetes only; the original mixed diabetes entry also links a separate type 1 workflow.','assessment':['Confirm diabetes using plasma glucose or HbA1c criteria. Assess cardiovascular and kidney disease, neuropathy, feet and retina. Obtain HbA1c, creatinine, potassium, lipids, urine albumin/creatinine and liver tests as appropriate.'],'treatment':['The 2022 workflow uses metformin monotherapy below HbA1c 8.5%, combination therapy at 8.5–10%, and consideration of insulin-based or triple therapy above 10%, alongside diet and activity. These are source-era pathways requiring patient-specific review.'],'regimens':[],'doseNote':'This workflow extract does not establish individual drug doses or durations; consult the full source and drug-specific guidance.','followUp':[]};c['regimenStatus']='source-summary'
 if c['title']=='Scabies':
  c['summary']={'sourceId':'icmr-stw_vol_3_20222','edition':'2022','scope':'Uncomplicated scabies; crusted scabies requires a separate regimen.','assessment':['Diagnosis is usually clinical; skin scraping or dermoscopy can support uncertain cases.'],'treatment':['Treat household and close contacts at the same time. Wash recently used clothes and bedding, or seal nonwashable items for at least three days.'],'regimens':[{'drug':'Permethrin 5% cream','population':'Adults; check age-specific guidance for children','dose':'Apply to clean dry skin from the neck down; infants also need face and scalp treatment per source','titration':'Wash off after 8–12 hours; repeat after 7–14 days','duration':'Two applications separated by 7–14 days','cautions':'Cover finger webs, nails and genital areas carefully; reapply to hands after washing during contact time.','sourcePage':None}],'followUp':['Review response and possible reinfestation. Crusted scabies or poor response needs specialist-directed treatment.']};c['regimenStatus']='source-summary'
report={'checkedOn':'2026-10-06','totalConditions':len(conditions),'originalConditions':len(legacy),'addedConditions':len(new),'statusCounts':dict(collections.Counter(c['sourceStatus'] for c in conditions)),'summaryCount':sum(c['summary'] is not None for c in conditions),'importantLimitation':'Source routing is not a complete clinical revalidation. Only explicitly labelled summaries replace old treatment passages. Other doses/durations remain unreviewed in the 2013 archive. ICMR document years are not inferred from upload timestamps; undated MoHFW documents are not described as new editions.'}
(root/'data/conditions.json').write_text(json.dumps(conditions,ensure_ascii=False,indent=2))
(root/'data/coverage.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
