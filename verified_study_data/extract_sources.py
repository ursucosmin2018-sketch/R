"""Manual, page-referenced extraction from the 13 supplied primary-source PDFs.
Run with Python 3. No PDF is redistributed. Blank values mean unavailable, never zero.
This file records source statistics; it does not convert medians or model SEs to raw SDs.
"""
import csv, json, hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
OLD=BASE.parent/'cochrane_analysis'/'data'
OUTCOMES=['walk_distance','nyha','quality_of_life','qrs','lvef','lvesv','threshold','composite','hhf','mortality']
BIN={'composite','hhf','mortality'}
MAPPING={'Lustgarten 2015':'Lustgarten','His-SYNC 2019':'His-SYNC','His-Alternative 2021':'His-Alternative','LEVEL-AT 2022':'LEVEL-AT','LBBP-RESYNC 2022':'LBBB-RESYNC','ALTERNATIVE-AF 2022':'ALTERNATIVE-AF','HOT-CRT 2023':'HOT-CRT','CONSYST-CRT 2025':'CONSYST-CRT','CSP-SYNC 2025':'CSP-SYNC','HeartSync-LBBP 2026':'HeartSync-LBBP','PhysioSync-HF 2026':'PhysioSync-HF','LEFT-BUNDLE-CRT 2026':'LEFT-BUNDLE-CRT','LECART 2026':'LECART'}
# group sizes are kept separate from outcome-specific observed sample sizes.
CFG={
'Lustgarten 2015':('randomized crossover','12 paired completers','6 months per pacing period',12,12),
'His-SYNC 2019':('parallel randomized trial; secondary as-treated report','treatment received, not randomized allocation','6 months echo; latest 6/12 months KCCQ; mean clinical follow-up 12.2 months',16,24),
'His-Alternative 2021':('parallel randomized trial','ITT; additional as-treated/per-protocol results available','6 months in supplied 2021 paper',25,25),
'LEVEL-AT 2022':('parallel randomized trial','ITT','6 months clinical; early paced QRS/implant threshold',35,35),
'LBBP-RESYNC 2022':('parallel randomized trial','ITT','6 months',20,20),
'ALTERNATIVE-AF 2022':('randomized two-period crossover','38 paired completers; 50 originally randomized to two sequences','9 months per period; total 18 months',25,25),
'HOT-CRT 2023':('parallel randomized trial','ITT unless explicitly lead-based','6 months',50,50),
'CONSYST-CRT 2025':('parallel randomized trial; includes LEVEL-AT cohort','ITT','12 months',67,67),
'CSP-SYNC 2025':('parallel randomized trial','ITT; longitudinal mixed-model continuous estimates','6 months functional; mean 22.1 months clinical',31,31),
'HeartSync-LBBP 2026':('parallel randomized trial','ITT','last follow-up; median 36 months (range 33-39)',100,100),
'PhysioSync-HF 2026':('parallel randomized trial','modified ITT: randomized and underwent procedure','12 months; 6-month value carried forward when unavailable',87,86),
'LEFT-BUNDLE-CRT 2026':('parallel randomized trial','available-case ITT; clinical-events cohort 92/82','12 months; continuous table cohort 87/74',92,82),
'LECART 2026':('parallel randomized trial; press release only','not adequately specified in supplied release','1 year',None,None)}
UNITS={'walk_distance':'m','nyha':'NYHA class','quality_of_life':'scale-specific','qrs':'ms','lvef':'percentage points','lvesv':'mL','threshold':'V','composite':'participants with event','hhf':'participants with event','mortality':'participants with event'}
ROWS=[]; EXTRA=[]; CONTRASTS=[]
for outcome in OUTCOMES:
 for x in csv.DictReader((OLD/(outcome+'.csv')).open()):
  s=x['study']; d,p,t,gnc,gnb=CFG[s]
  r=dict(record_id=outcome+'__'+s.replace(' ','_'),outcome=outcome,study=s,subgroup=x['subgroup'],data_type='binary' if outcome in BIN else 'continuous',status='not_reviewed',statistic='',measurement_type='',unit=UNITS[outcome],scale='',higher_is_better=outcome in ['walk_distance','quality_of_life','lvef'],source_n_csp=None,source_n_biv=None,group_n_csp=gnc,group_n_biv=gnb,sample_size_basis='',source_mean_csp=None,source_sd_csp=None,source_mean_biv=None,source_sd_biv=None,source_event_csp=None,source_event_biv=None,source_median_csp=None,source_q1_csp=None,source_q3_csp=None,source_median_biv=None,source_q1_biv=None,source_q3_biv=None,source_ci_low_csp=None,source_ci_high_csp=None,source_ci_low_biv=None,source_ci_high_biv=None,source_se_csp=None,source_se_biv=None,design=d,analysis_population=p,follow_up=t,overlap_group='Barcelona_LEVEL_CONSYST' if s in ['LEVEL-AT 2022','CONSYST-CRT 2025'] else s,source_pdf=MAPPING[s]+('.pdf' if s!='Lustgarten 2015' else ' et al..pdf'),pdf_pages='',source_location='',source_summary='',comparison='',required_action='',pooling_eligibility='HOLD',same_estimand_as_figure=True)
  for k,v in x.items():
   if k not in ['study','subgroup']:
    r['figure_'+k]=None if v in ['NA',''] else float(v)
  ROWS.append(r)
def get(s,o): return next(r for r in ROWS if r['study']==s and r['outcome']==o)
def setr(s,o,status,pages,loc,summary,comparison='',action='',**kw):
 r=get(s,o);r.update(status=status,pdf_pages=str(pages),source_location=loc,source_summary=summary,comparison=comparison,required_action=action,**kw);return r
def ms(r,n1,m1,s1,n0,m0,s0,**kw):
 r.update(statistic='mean and SD',source_n_csp=n1,source_mean_csp=m1,source_sd_csp=s1,source_n_biv=n0,source_mean_biv=m0,source_sd_biv=s0,measurement_type='follow-up value');r.update(kw);return r
def ev(r,n1,e1,n0,e0,**kw):
 r.update(statistic='participant event counts',source_n_csp=n1,source_event_csp=e1,source_n_biv=n0,source_event_biv=e0,measurement_type='cumulative events');r.update(kw);return r
def med(r,n1,a,b,c,n0,d,e,f,**kw):
 r.update(statistic='median and IQR',source_n_csp=n1,source_median_csp=a,source_q1_csp=b,source_q3_csp=c,source_n_biv=n0,source_median_biv=d,source_q1_biv=e,source_q3_biv=f,measurement_type='follow-up value');r.update(kw);return r
def ci(r,n1,a,b,c,n0,d,e,f,model=False,**kw):
 r.update(statistic='model mean and 95% CI' if model else 'mean and 95% CI',source_n_csp=n1,source_mean_csp=a,source_ci_low_csp=b,source_ci_high_csp=c,source_n_biv=n0,source_mean_biv=d,source_ci_low_biv=e,source_ci_high_biv=f,measurement_type='change from baseline');r.update(kw);return r
def extra(s,o,variant,pages,loc,summary,**kw):
 d,p,t,nc,nb=CFG[s]
 r=dict(record_id='extra__'+o+'__'+s.replace(' ','_')+'__'+variant,study=s,outcome=o,variant=variant,source_pdf=MAPPING[s]+'.pdf',pdf_pages=str(pages),source_location=loc,source_summary=summary,analysis_population=p,design=d,follow_up=t,unit=UNITS.get(o,''),pooling_eligibility='HOLD',**kw);EXTRA.append(r);return r
def contrast(s,o,estimate,low,high,pages,loc,model,unit=None,follow=None):
 CONTRASTS.append(dict(study=s,outcome=o,estimate=estimate,lower_95=low,upper_95=high,measure='MD',unit=unit or UNITS[o],follow_up=follow or CFG[s][2],source_pdf=MAPPING[s]+'.pdf',pdf_pages=str(pages),source_location=loc,analysis=model,orientation='CSP minus BiVP',note='Reported study contrast. CI may be rounded/model-based; differs from a simple difference of rounded arm values.'))
# Lustgarten: all clinical results are paired, and most SDs only appear as unlabelled bars.
s='Lustgarten 2015'
for o,page,loc in [('walk_distance',4,'Figure 2D; Results p3'),('nyha',4,'Figure 2B; Results p3'),('lvef',4,'Figure 2A; Results p3'),('quality_of_life',4,'Figure 2C; Results p3'),('lvesv',5,'Figure 3A'),('threshold',6,'Figure 4A')]:
 r=setr(s,o,'PARTIAL_GRAPH_ONLY',f'3,{page}',loc,'Twelve patients completed both crossover periods. Error bars denote SD, but exact bar values are not printed.','Forest decimal SDs cannot be independently certified from unlabelled bars; walking/QoL forest N=21 is not the clinical completer N=12.','Obtain numerical source data or document formal graph digitization; use paired crossover variance.',source_n_csp=12,source_n_biv=12,sample_size_basis='same 12 participants under each pacing mode; not independent groups',statistic='graph-only mean/SD; some means in prose',measurement_type='follow-up value')
 if o=='nyha':r.update(source_mean_csp=1.9,source_mean_biv=1.9)
 if o=='lvef':r.update(source_mean_csp=32,source_mean_biv=31)
 if o=='walk_distance':r.update(source_mean_csp=383,source_mean_biv=361,comparison=r['comparison']+' Prose reports 383/361 and calls distance feet; Figure 2D axis explicitly says meters. Forest 384.20/361.67 appear digitized, not printed means.',required_action='Resolve prose/figure unit discrepancy and obtain exact SDs; paired analysis required.')
 if o=='quality_of_life':r.update(scale='Minnesota Living with Heart Failure Questionnaire (MLHFQ)',higher_is_better=False,comparison='Figure 2C shows positive follow-up scores around 27/31, not negative change scores. Prose says 38/31, conflicting with the HBP bar. Forest -26.92/-30.92 may be direction-reversed follow-up estimates; this transformation is not explained in the forest.',required_action='Resolve HBP prose/figure conflict; obtain exact paired values. Preserve original lower-is-better scale.')
 if o=='threshold':r.update(follow_up='12 months',comparison='Forest values roughly resemble 12-month capture-threshold bars. They are not the separate higher programmed output needed for maximal QRS normalization.',required_action='Obtain numeric threshold SDs and paired covariance; pulse widths differ and are plotted separately.')
r=setr(s,'qrs','DEFINITION_AND_N_UNRESOLVED',3,'Table 1','Table 1: nonselective HBP 160 (25); selective HBP 131 (35); His-to-LV 145 (24); BiVP 165 (17).','Forest 145 (24) is the His-to-LV vector, not selective HBP. N for each vector is not tabulated; 21/29 patients showed HBP narrowing.','Select intended pacing vector and verify vector-specific paired N; do not treat repeated pacing measurements as independent.',sample_size_basis='vector-specific N not reported',measurement_type='paced QRS at implant')
ms(r,None,145,24,None,165,17,measurement_type='paced QRS at implant',scale='His-to-LV vector versus BiVP')
extra(s,'qrs','other_vectors',3,'Table 1','Selective HBP 131 (35) ms; nonselective HBP 160 (25) ms; BiVP 165 (17) ms. Vector-specific N not provided.')
# His-SYNC: on-treatment, medians and relative LVESV change.
s='His-SYNC 2019'
r=setr(s,'qrs','CORRECTED',6,'Primary endpoints by on-treatment analysis','QRS 125 +/-22 versus 164 +/-25 ms; treatment-received groups 16/24.','Forest CSP SD=20 is wrong; primary report says 22.','Use on-treatment only as sensitivity analysis when targeting randomized effects.',sample_size_basis='treatment-received groups 16/24',pooling_eligibility='SENSITIVITY_AS_TREATED')
ms(r,16,125,22,24,164,25,measurement_type='paced QRS at implant')
r=setr(s,'lvef','MEDIAN_NOT_MEAN','6','On-treatment primary endpoints','Follow-up LVEF medians 34.6 (30.8-45.0) versus 32.0 (30.9-40.1), median follow-up 6.2 months.','Forest 36.9/34.5 and SDs11.5/7.2 are not reported raw means/SDs; likely median conversions.','Keep median/IQR; any conversion needs an explicit estimation method and sensitivity analysis.',sample_size_basis='on-treatment group sizes; observed echo N not separately tabulated')
med(r,16,34.6,30.8,45,24,32,30.9,40.1,follow_up='median 6.2 months')
r=setr(s,'lvesv','WRONG_UNIT_AND_SIGN',7,'On-treatment primary endpoints','Mean relative LVESV changes -22% (24%) and -19% (14%).','Forest +22/+19 reverses signs and places percentage changes in a volume (mL) analysis.','Keep as relative percentage change; cannot pool with mL or mL/m2.',unit='percent relative change',sample_size_basis='treatment-received group sizes')
ms(r,16,-22,24,24,-19,14,measurement_type='relative percent change from baseline')
r=setr(s,'quality_of_life','MEDIAN_NOT_MEAN',7,'Secondary endpoints','KCCQ increase: median +16 (IQR +8 to +25) versus +10 (+2 to +16).','Forest16.36(13.82)/9.28(11.03) are not directly reported means/SDs.','Keep medians and IQR; verify scale scoring and paired follow-up before conversion.',scale='KCCQ score as reported',sample_size_basis='on-treatment groups; outcome-specific responder N not tabulated')
med(r,16,16,8,25,24,10,2,16,measurement_type='change from baseline',follow_up='latest available 6- or 12-month measurement')
r=setr(s,'threshold','MEDIAN_NOT_MEAN',9,'Table 2, 6-month follow-up','His/LV capture threshold medians 2.00 (1.00-3.25) versus0.94 (0.75-1.25) V. Pulse widths1.00 versus0.40 ms.','Forest2.09(1.82)/0.98(0.39) are not directly reported means/SDs.','Do not label converted medians as measured means; preserve pulse-width difference.',sample_size_basis='Table2 on-treatment groups16/24',follow_up='6 months')
med(r,16,2,1,3.25,24,.94,.75,1.25,scale='His QRS-correction threshold at 1ms vs LV threshold at0.4ms')
r=setr(s,'mortality','VERIFIED_AS_TREATED',7,'Primary endpoints; deaths narrative','Two deaths occurred among patients receiving His-CRT, including a patient randomized to BiVP who crossed to His. No BiVP-received deaths.','2/16 vs0/24 matches as-treated grouping, not randomized allocation.','Use in as-treated sensitivity analysis, not an unqualified ITT meta-analysis.',pooling_eligibility='SENSITIVITY_AS_TREATED',sample_size_basis='treatment received')
ev(r,16,2,24,0)
# His-Alternative: uploaded original report is 6 months, not the 2026 extension.
s='His-Alternative 2021'
for o in ['nyha','qrs','lvef','lvesv','threshold','composite','hhf','mortality']:
 setr(s,o,'FOLLOWUP_REPORT_MISSING','6-7','Table3 and adverse-events results','Supplied 2021 report has six-month ITT and per-protocol data. Meta-analysis also cites Frandsen et al2026 long-term follow-up (10.1016/j.jacep.2026.02.016), not supplied.','Forest values/populations do not match this six-month report. This does not establish that the long-term forest values are wrong.','Obtain 2026 extension to verify forest target. Six-month alternatives are recorded separately; never substitute timepoints silently.',same_estimand_as_figure=False)
r=setr(s,'walk_distance','CORRECTED_N',6,'Table3, intention-to-treat 6-month columns','CSP444 (133), BiVP451 (105), with25 randomized patients per group.','Forest CSP N=46 is unsupported and exceeds randomized CSP N=25. Arm means/SDs match six-month ITT.','Use25/25 for this six-month ITT row.',follow_up='6 months',sample_size_basis='Table3 ITT n25/25; no losses',pooling_eligibility='ELIGIBLE_NUMERIC')
ms(r,25,444,133,25,451,105)
for o,vals in {'nyha':(1.8,.4,1.9,.6),'qrs':(131,20,134,15),'lvef':(46,9,43,7),'lvesv':(74,30,79,29),'threshold':(2.3,1.4,1.4,.5)}.items():
 r=extra(s,o,'six_month_ITT',6,'Table3, 6-month ITT columns','Six-month alternative; not confirmation/replacement of long-term forest row.',pooling_note='Choose this only in a prespecified six-month analysis.')
 ms(r,25,vals[0],vals[1],25,vals[2],vals[3]);r['follow_up']='6 months';r['sample_size_basis']='explicit ITT table sizes; no losses';r['pooling_eligibility']='ELIGIBLE_NUMERIC';r['scale']='V at1ms' if o=='threshold' else ''
r=extra(s,'lvef','six_month_ITT_change',6,'Table3','LVEF absolute change16(7) vs13(6) percentage points.');ms(r,25,16,7,25,13,6,measurement_type='change from baseline')
for o in BIN:
 r=extra(s,o,'six_month_ITT', '6-7','Results and adverse events','No patients died or were hospitalized for worsening HF during six months. Therefore death-or-HFH composite also zero in both arms.');ev(r,25,0,25,0);r['pooling_eligibility']='DOUBLE_ZERO';r['follow_up']='6 months'
# LEVEL-AT: exact data, but overlapping participants with CONSYST.
s='LEVEL-AT 2022'
for o,vals in {'qrs':(125,18,129,13),'lvef':(12.2,9,13.1,9),'lvesv':(-37,59,-30,41),'nyha':(-.8,.8,-.4,.8),'threshold':(1,.4,1.2,.5)}.items():
 r=setr(s,o,'VERIFIED_WITH_COHORT_OVERLAP','8-9','Table2; procedural outcomes','Table2 or procedural paragraph reports the arm means/SDs. Table2 secondary-outcome header gives35/35.','Numerical means/SDs match. Do not include alongside CONSYST-CRT: same first70 patients.','Choose one report per shared cohort per analysis; verify observed echo denominators (two BiVP deaths).',sample_size_basis='Table2 secondary-outcome header35/35; echo complete-case N not explicit',pooling_eligibility='HOLD_COHORT_OVERLAP')
 ms(r,35,vals[0],vals[1],35,vals[2],vals[3],measurement_type='change from baseline' if o in ['nyha','lvef','lvesv'] else 'follow-up value')
 if o=='lvef':r.update(status='N_NOT_IN_SOURCE_TABLE',comparison='Forest uses35/33. Table2 gives secondary header35/35, but two BiVP deaths make observed echo N uncertain. Do not resolve by assuming the header or death count alone.',source_n_csp=None,source_n_biv=None)
 if o=='threshold':r.update(follow_up='implant',scale='pulse width not uniform; see Table4',comparison='Forest1.0/1.2 are acute thresholds; six-month values are0.8/1.0. Also shares cohort with CONSYST.')
for o,e in {'composite':(1,4),'hhf':(1,3),'mortality':(0,2)}.items():
 r=setr(s,o,'VERIFIED_WITH_COHORT_OVERLAP',8,'Table2','CSP/BiVP: HFH or death1/4, HFH1/3, deaths0/2; one BiVP hospitalized patient later died.','All forest counts and denominators match. Participants overlap CONSYST.','Do not pool both reports independently.',pooling_eligibility='HOLD_COHORT_OVERLAP',sample_size_basis='ITT35/35')
 ev(r,35,e[0],35,e[1])
r=extra(s,'threshold','six_month',9,'Procedural outcomes','Six-month threshold0.8(0.4) vs1.0(0.3) V; differs from forest acute threshold.');ms(r,35,.8,.4,35,1,.3);r['follow_up']='6 months'
# LBBP-RESYNC: adjusted LS means/SE must not be used as raw patient SDs.
s='LBBP-RESYNC 2022'
for o,vals,effect,lim,unit in [
 ('walk_distance',(100.69,14.14,80.56,15.92),43.99,(-13.08,101.07),'m'),
 ('nyha',(-1.22,.11,-1.10,.11),-.09,(-.47,.30),'NYHA class'),
 ('lvesv',(-77.74,7.80,-55.58,8.80),-24.97,(-49.58,-.36),'mL')]:
 r=setr(s,o,'MODEL_SE_NOT_RAW_SD',8,'Table3','Table explicitly reports least-squares means +/-SE from mixed-effects models adjusted for baseline.','Forest SD approximately equals published SE*sqrt(20). A model-based SE is not necessarily raw sample SD; use reported adjusted contrast.','Preserve LS mean/SE and study contrast; do not treat converted values as measured SD.',statistic='adjusted least-squares mean and SE',measurement_type='change from baseline',source_n_csp=20,source_n_biv=20,source_mean_csp=vals[0],source_se_csp=vals[1],source_mean_biv=vals[2],source_se_biv=vals[3],sample_size_basis='model ITT group sizes; not necessarily complete-case raw N')
 if o=='lvesv':r['comparison']+=' Printed forest MD -22.18 also does not equal -77.74 -(-55.58)=-22.16.'
 contrast(s,o,effect,*lim,8,'Table3','baseline-adjusted repeated-measures model',unit)
r=setr(s,'lvef','CORRECTED_SD',7,'Figure3A numeric table','Six-month ITT LVEF49.4(SD13.2) vs46.5(SD9.4).','Forest SD8.54/8.69 equals LS-change SE1.91/1.94 multiplied bysqrt20. It mixes final means with dispersion from a different, modelled change outcome.','Use final SD13.2/9.4 for final values; confirm outcome N. Alternatively use adjusted change contrast5.62[.29,10.95].',sample_size_basis='ITT groups20/20; one BiVP-assigned crossover lacked 6-month echo (p6); raw observed N not explicitly attached to Figure3A',source_n_csp=None,source_n_biv=None)
ms(r,20,49.4,13.2,19,46.5,9.4)
r.update(sample_size_basis='Observed six-month echo N derived from documented follow-up:20 CSP and19 BiVP; p6 says one BiVP-assigned crossover had no six-month echo. Figure3A labels ITT, and Figure4 response denominator19 corroborates.',required_action='Use20/19 for observed endpoint summaries; do not confuse with20/20 repeated-measures model cohort. Adjusted change contrast available separately.',pooling_eligibility='ELIGIBLE_WITH_DERIVED_N')
contrast(s,'lvef',5.62,.29,10.95,8,'Table3','baseline-adjusted repeated-measures model; absolute LVEF change')
for o,v in {'qrs':(131.5,12.5,136.6,12.9),'threshold':(.82,.20,1.12,.67)}.items():
 r=setr(s,o,'VERIFIED',6,'Table2','ITT Table2 reports these means/SDs under n20/20.','Forest values match.','For threshold record time and units; table says mV but narrative p7 confirms V.',sample_size_basis='Table2 n20/20',pooling_eligibility='ELIGIBLE_NUMERIC')
 ms(r,20,v[0],v[1],20,v[2],v[3]);r['follow_up']='implant' if o=='qrs' else '6 months'
for o in BIN:
 r=setr(s,o,'FOLLOWUP_REPORT_MISSING','6-7','Results; secondary endpoints','Six-month report: no HF rehospitalizations, ventricular arrhythmias, or deaths. Meta-analysis cites a separate four-year follow-up abstract, not supplied.','Forest clinical grouping22/18 is not randomized20/20; long-term counts cannot be verified from this report.','Obtain Zou et al2026 four-year abstract/data; keep six-month alternatives separate.',same_estimand_as_figure=False)
 r=extra(s,o,'six_month_ITT',7,'Secondary endpoints','Explicitly no HF rehospitalizations or all-cause deaths during six-month follow-up.');ev(r,20,0,20,0);r['pooling_eligibility']='DOUBLE_ZERO'
# ALTERNATIVE-AF crossover: first period LVEF is an independent sequence comparison; others paired.
s='ALTERNATIVE-AF 2022'
r=setr(s,'nyha','VERIFIED_PAIRED',7,'Table2','HBP1.50(0.60), BVP1.58(0.64), same38 patients completing both periods.','Numbers match but observations are paired, not two independent groups of38.','Use crossover treatment estimate/SE or within-person covariance.',sample_size_basis='same38 participants',analysis_population='paired completers')
ms(r,38,1.5,.60,38,1.58,.64)
r=setr(s,'qrs','CORRECTED_PAIRED',4,'Table1; pacing parameters p5','All50 implanted patients: paced HBP QRS107.6(12.5), BVP135.7(16.6).','Forest107.7 should be107.6. Both modes measured in same50 people.','Paired analysis required; do not count as100 independent participants.',sample_size_basis='50 paired implant measurements')
ms(r,50,107.6,12.5,50,135.7,16.6,follow_up='implant',measurement_type='paced QRS at implant')
r=setr(s,'lvef','VERIFIED_FIRST_PERIOD',5,'Figure2A labels and participant counts','At9 months sequence1 HBP n18:53.9(11.9); sequence2 BVP n20:51.3(7.4).','Forest values match first-period completers. This is not the paired18-month comparison or full randomized25/25.','Use as first-period completer analysis; keep distinct from paired pooled periods.',follow_up='9 months, first period',analysis_population='first-period completers by assigned sequence',sample_size_basis='Figure2 n18/20',pooling_eligibility='SENSITIVITY_COMPLETERS')
ms(r,18,53.9,11.9,20,51.3,7.4)
r=setr(s,'threshold','SUPPLEMENT_REQUIRED',5,'Pacing parameters; Supplemental Table3 referenced','Main text reports18-month HBP0.9(0.6) and LV1.0(0.5) V at0.5ms; forest uses1.0(0.6) in both with18/20.','Forest timepoint/sequence-specific thresholds cannot be confirmed without supplementary table.','Obtain Supplemental Table3. Do not replace first-period values with18-month paired values silently.',same_estimand_as_figure=False)
r=extra(s,'threshold','eighteen_month_paired',5,'Pacing parameters','HBP0.9(0.6), LV1.0(0.5) V/0.5ms. Outcome-specific N not printed.');ms(r,None,.9,.6,None,1,.5);r['follow_up']='18 months';r['analysis_population']='paired leads; outcome N not stated'
for o,e,page in [('hhf',(1,2),5),('mortality',(3,4),3)]:
 r=setr(s,o,'WRONG_DENOMINATOR_FOR_CROSSOVER',page,'Clinical events' if o=='hhf' else 'Patient flow','Events assigned by active pacing period: '+('1 HBP and2 BVP HF hospitalizations' if o=='hhf' else '3 deaths during HBP and4 during BVP')+'.','Forest denominators25/25 are randomized sequence sizes; they are not denominators of independent exposure groups across both crossover periods.','Retain period event counts but do not calculate a parallel-group OR from25/25; obtain period-specific risks/person-time.',statistic='events by active crossover period',source_event_csp=e[0],source_event_biv=e[1],source_n_csp=None,source_n_biv=None,sample_size_basis='25/25 sequences; exposure-period denominator unavailable',measurement_type='events during pacing periods')
# HOT-CRT
s='HOT-CRT 2023'
for o,v in {'walk_distance':(278,152,280,148),'qrs':(137,20,141,19),'lvef':(42.9,10.1,39.1,9.7),'lvesv':(102,52,107,51),'quality_of_life':(.02,.29,.07,.20)}.items():
 r=setr(s,o,'VERIFIED_VALUES_N_REVIEW',8,'Table4; follow-up completion p5','Table4 labels groups50/50; p5 states88 patients (44 per group) completed six-month visit including echo.','Means/SDs match except BiVP EQ5D change, which is0.07 (forest0.08). Outcome-specific N must not be assumed50.', 'Use44/44 for complete-case echo; for walking/QoL/QRS confirm outcome-specific measured N.',sample_size_basis='Table header50/50; observed echo44/44, other outcome Ns not individually specified')
 ms(r,44 if o in ['lvef','lvesv'] else None,v[0],v[1],44 if o in ['lvef','lvesv'] else None,v[2],v[3])
 if o in ['lvef','lvesv']:r.update(status='CORRECTED_N',pooling_eligibility='SENSITIVITY_COMPLETERS',analysis_population='six-month completers, by randomized assignment',comparison='Forest uses50/50. Paper reports44/44 completed six-month visit including echocardiography.')
 if o=='quality_of_life':r.update(status='CORRECTED_MEAN_N_UNRESOLVED',scale='EQ-5D utility',measurement_type='change from baseline')
r=setr(s,'threshold','CORRECTED_N_AND_POPULATION',5,'Table2, pacing parameters subheading','HBP/LBBAP leads n57 versus CS leads n43:0.7(0.4) vs1.2(0.7) V at0.5ms, implant and follow-up.','Forest erroneously uses50/50 randomized groups for this57/43 lead-type comparison.','Use lead-based sensitivity analysis; do not represent it as a randomized ITT arm comparison.',analysis_population='lead type received: HBP/LBBAP versus CS',sample_size_basis='explicit pacing-parameter subheading57/43',pooling_eligibility='SENSITIVITY_AS_TREATED')
ms(r,57,.7,.4,43,1.2,.7,scale='V at0.5ms',follow_up='implant and six-month values identical')
for o,e in {'hhf':(7,2),'mortality':(2,2)}.items():
 r=setr(s,o,'VERIFIED',6,'Secondary endpoints','HFH7/50 vs2/50; deaths2/50 vs2/50.','Forest counts and denominators match.','',pooling_eligibility='ELIGIBLE_NUMERIC',sample_size_basis='ITT50/50')
 ev(r,50,e[0],50,e[1])
r=extra(s,'lvef','six_month_change',6,'Table3','LVEF change12.4(7.3) vs8.0(10.1) percentage points;88 echo completers.');ms(r,44,12.4,7.3,44,8,10.1,measurement_type='change from baseline')
# CONSYST-CRT: same first70 participants as LEVEL-AT.
s='CONSYST-CRT 2025'
for o,v in {'nyha':(-.6,.7,-.5,.7),'qrs':(-20,26,-19,24),'lvef':(14.1,10.5,14.4,9.9),'lvesv':(-27.9,27,-27.9,28.1),'threshold':(.8,.4,1,.5)}.items():
 r=setr(s,o,'VERIFIED_WITH_COHORT_OVERLAP','2,5-6','Table2; procedural results','Means/SDs match Table2 or12-month threshold results. Study population paragraph: first70 patients recruited from LEVEL-AT.','Shares participants with LEVEL-AT. Forest LVESV also has wrong unit and denominator.','Use one report per cohort. LVESV is relative percent change, not mL.',sample_size_basis='ITT67/67; LVESV complete-case66/62',pooling_eligibility='HOLD_COHORT_OVERLAP')
 ms(r,66 if o=='lvesv' else 67,v[0],v[1],62 if o=='lvesv' else 67,v[2],v[3],measurement_type='change from baseline' if o!='threshold' else 'follow-up value')
 if o=='lvesv':r.update(status='WRONG_UNIT_AND_N',unit='percent relative change',measurement_type='relative percent change from baseline',comparison='Table2 explicitly labels deltaLVESV %. Footnote gives66/62 evaluable volumes, not67/67. Forest incorrectly pools with absolute mL changes.')
 if o=='qrs':r['scale']='QRS measured from pacing spike; alternative fast-deflection change -49(24)/-45(23)'
r=setr(s,'composite','DEFINITION_MISMATCH','2,6','Table2','8/67 versus12/67 is all-cause mortality OR cardiac transplantation OR HF hospitalization.','Forest labels endpoint as HFH or all-cause mortality; cardiac transplant is an additional component.','Obtain component overlap/strict two-component count; also avoid LEVEL-AT double-counting.',scale='death OR cardiac transplant OR HF hospitalization',pooling_eligibility='HOLD_DEFINITION_AND_OVERLAP')
ev(r,67,8,67,12)
for o in ['hhf','mortality']:
 setr(s,o,'SUPPLEMENT_REQUIRED','5-6','Table2; Supplemental Table1 referenced','Main paper reports combined clinical outcome, but not the separate arm counts used in the forest.','Forest '+('HFH8/10' if o=='hhf' else 'mortality1/3')+' cannot be verified from the supplied main paper.','Obtain Supplemental Table1; do not infer components by subtraction or addition. Shared LEVEL-AT cohort also applies.')
# CSP-SYNC: preserve mixed-model CI, medians; verify all-cause deaths from flow chart.
s='CSP-SYNC 2025'
for o,v in {'qrs':(-33,-40,-26,-32,-39,-25),'lvef':(14,11.2,16.8,8.5,5.6,11.2),'lvesv':(-64,-78,-50,-40,-54,-25)}.items():
 r=setr(s,o,'MODEL_CI_NOT_RAW_SD','4-6','Statistical analysis; Table2','Longitudinal random-intercept mixed model; arm changes reported with95%CIs, not raw SDs.','Forest SDs were apparently reconstructed from CIs and n31. That does not establish raw change SDs.','Use source model contrast/CI or obtain raw change SDs; do not substitute reconstructed SD without justification.',sample_size_basis='31/31 randomized model groups; mixed model handles longitudinal observations')
 ci(r,31,v[0],v[1],v[2],31,v[3],v[4],v[5],model=True)
 if o=='qrs':r['comparison']+=' Forest upper study CI5.51 is arithmetically inconsistent; source between-group CI is[-11,9].'
contrast(s,'qrs',-1,-11,9,6,'Table2','longitudinal mixed model',follow='6 months')
contrast(s,'lvef',5.6,1.6,9.5,6,'Table2','longitudinal mixed model',follow='6 months')
contrast(s,'lvesv',-24,-44,-4,6,'Table2','longitudinal mixed model',follow='6 months')
r=setr(s,'walk_distance','MEDIAN_NOT_MEAN',5,'Secondary endpoints','Six-month walk medians450(374-510) and420(295-480) m.','Forest444.29(105.69)/396.84(143.77) are not source raw means/SDs.','Preserve median/IQR; conversion requires a documented method.',sample_size_basis='31/31 randomized; outcome-specific measured N not separately printed')
med(r,31,450,374,510,31,420,295,480,follow_up='6 months')
r=setr(s,'quality_of_life','MEDIAN_NOT_MEAN',5,'Secondary endpoints','EQ VAS at6 months80(IQR60-90) in both groups.','Forest76.44(23.32) in both arms appears converted; not observed mean/SD.','Keep median/IQR and scale; no silent conversion.',scale='EuroQol VAS 0-100',sample_size_basis='31/31 randomized; outcome-specific measured N not separately printed')
med(r,31,80,60,90,31,80,60,90,follow_up='6 months')
r=setr(s,'hhf','VERIFIED',5,'Echocardiographic response and clinical events','Two(6.5%) vs seven(22.6%) HF hospitalizations among31 per arm.','Counts and denominators match.','',sample_size_basis='ITT31/31',pooling_eligibility='ELIGIBLE_NUMERIC')
ev(r,31,2,31,7)
r=setr(s,'composite','DEFINITION_MISMATCH','3,5','Study endpoints; clinical events','Two versus seven is cardiovascular death OR worsening HF, defined as HF hospitalization OR unplanned ED visit needing IV diuretic.','Different from all-cause death or HF hospitalization; cannot recover strict composite without patient overlap.','Keep original definition; do not use in strict two-component composite.',scale='CV death OR worsening HF (including urgent IV-diuretic visits)')
ev(r,31,2,31,7)
r=setr(s,'mortality','CORRECTED_FROM_FLOWCHART','4-5','Figure1; clinical-events narrative','Figure1 explicitly lists1 cardiovascular death AND1 non-cardiovascular death in LBBAP, versus1 non-cardiovascular death in BiV.','Forest1/31 vs1/31 omits the extra non-CV death shown for LBBAP. Narrative mentions only its CV death; Figure1 supplies the all-cause total.','Use2/31 vs1/31 from flowchart, with narrative/figure difference documented; author clarification useful for exact death timing.',sample_size_basis='31 randomized per arm',pooling_eligibility='ELIGIBLE_WITH_SOURCE_NOTE')
ev(r,31,2,31,1)
# HeartSync: source means/SD match, but do not use original group N as measured survivor N.
s='HeartSync-LBBP 2026'
for o,v in {'nyha':(1.9,.7,2.3,.8),'qrs':(119.4,14.9,136.6,11.6),'lvef':(47.3,10.6,41.5,8.6),'threshold':(.8,.3,1.5,.4)}.items():
 r=setr(s,o,'VERIFIED_VALUES_N_UNRESOLVED',5,'Table2','Last-follow-up arm means/SDs match Table2, which labels randomized groups100/100.','Seven deaths occurred; observed last-follow-up measurement Ns are not separately given in this main table. Do not assert that100 measurements exist per arm.','Obtain outcome-specific measurement N or reported model contrast.',sample_size_basis='group labels100/100; measured last-follow-up N not separately reported')
 ms(r,None,v[0],v[1],None,v[2],v[3])
 if o=='threshold':r['scale']='V at0.5ms'
for o,e in {'composite':(8,28),'hhf':(7,28),'mortality':(2,5)}.items():
 r=setr(s,o,'VERIFIED_WITH_DEFINITION_NOTE' if o!='mortality' else 'VERIFIED','3,6','Trial endpoints; Table3','Table3 participant counts match. Study defines HFH as urgent visit OR hospitalization for HF requiring IV diuretics.','Counts match; HHF definition is broader than inpatient-only hospitalization.' if o!='mortality' else 'Counts and denominators match.','Keep study HFH definition in eligibility decisions.' if o!='mortality' else '',sample_size_basis='ITT100/100',pooling_eligibility='HOLD_STRICT_HFH_DEFINITION' if o!='mortality' else 'ELIGIBLE_NUMERIC',scale='all-cause death OR study-defined HFH' if o=='composite' else ('HFH includes urgent IV-diuretic visits' if o=='hhf' else 'all-cause mortality'))
 ev(r,100,e[0],100,e[1])
# PhysioSync: published MDs account for precision/analysis; the true mean change is8, not9.
s='PhysioSync-HF 2026'
for o,v in {'walk_distance':(390,103,358,100),'qrs':(122,25,126,21),'lvef':(8,11,12,11),'quality_of_life':(.70,.32,.73,.23)}.items():
 r=setr(s,o,'CORRECTED_MEAN_N_UNRESOLVED' if o=='lvef' else 'VERIFIED_VALUES_N_UNRESOLVED',6,'Table2 including footnote a','Table2 gives these means/SDs;12-month missing continuous values use6-month measurements per SAP. Table headings87/86 describe the primary cohort.','CSP LVEF mean change is8, not forest9.' if o=='lvef' else 'Arm mean/SD values match. Outcome-specific measured N not given;87/86 are not verified continuous-outcome Ns.', 'Obtain Supplement2/3 outcome Ns or use published between-group contrast; do not include deceased participants as measured observations.',sample_size_basis='modified-ITT cohort87/86; outcome-specific continuous N not specified')
 ms(r,None,v[0],v[1],None,v[2],v[3],measurement_type='change from baseline' if o=='lvef' else 'follow-up value')
 if o=='quality_of_life':r['scale']='EQ-5D utility'
for o,val,l,h in [('walk_distance',33.1,3,63.2),('qrs',-4.5,-11.7,2.6),('lvef',-3.8,-7.3,-.3),('quality_of_life',-.03,-.12,.05)]:
 contrast(s,o,val,l,h,6,'Table2','reported between-group difference; source values rounded')
r=setr(s,'threshold','SUPPLEMENT_REQUIRED','5-6','Procedural results; eTable1 in Supplement3 referenced','Main text gives acute medians0.8(IQR0.5-1.0) and0.8(0.6-1.4).','Forest0.76(0.38)/0.94(0.61) and71/71 not tabulated in uploaded main PDF.','Obtain Supplement3 eTable1 and verify timepoint, N, and distribution.',same_estimand_as_figure=False)
r=extra(s,'threshold','acute_medians',5,'Procedure','Acute median(IQR) thresholds0.8(0.5-1.0) vs0.8(0.6-1.4).');med(r,None,.8,.5,1,None,.8,.6,1.4);r['follow_up']='implant'
for o,e in {'hhf':(6,4),'mortality':(11,4),'composite':(15,8)}.items():
 r=setr(s,o,'DEFINITION_MISMATCH' if o=='composite' else 'VERIFIED',6,'Table2','Counts explicitly reported out of87/86.','Composite includes urgent HF visits as well as all-cause death and HF hospitalization.' if o=='composite' else 'Counts and denominators match.','Cannot derive strict death-or-HFH count from margins; obtain component overlap.' if o=='composite' else '',sample_size_basis='modifiedITT87/86',pooling_eligibility='HOLD_DEFINITION' if o=='composite' else 'ELIGIBLE_NUMERIC',scale='death OR HF hospitalization OR urgent HF visit' if o=='composite' else o)
 ev(r,87,e[0],86,e[1])
# LEFT-BUNDLE-CRT: mean CI versus median IQR; LVESV indexed, not mL.
s='LEFT-BUNDLE-CRT 2026'
for o,v in {'walk_distance':(23,-7,51,5,-24,46),'lvef':(16,14,18,19,16,21),'lvesv':(-34,-40,-27,-32,-38,-25),'quality_of_life':(.14,.09,.18,.17,.11,.23)}.items():
 r=setr(s,o,'MEAN_CI_NOT_REPORTED_SD','8-9','Table2 ITT12-month columns; table footnote','Delta rows are mean(95%CI); table footnote distinguishes these from median[IQR] endpoint rows.','Forest SDs are derived from rounded CIs, not reported raw SDs.','Keep source mean/CI. Optional CI-derived SD may be estimated with explicit n and t assumptions; never call it source SD.',sample_size_basis='Table2 ITT header87/74 at6 and12 months',group_n_csp=92,group_n_biv=82)
 ci(r,87,v[0],v[1],v[2],74,v[3],v[4],v[5])
 if o=='quality_of_life':r['scale']='EQ-5D utility change'
 if o=='lvesv':r.update(status='WRONG_UNIT_INDEXED_VOLUME',unit='mL/m2',measurement_type='change in indexed LVESV',comparison='Table2 labels deltaLVESVi (mL/m2). Forest pools these indexed volumes with mL; this cannot be corrected without body surface area or unindexed volumes.',required_action='Keep indexed outcome separate; obtain absolute mL data for inclusion in absolute-volume analysis.')
r=setr(s,'qrs','MEDIAN_NOT_MEAN',4,'Procedural characteristics','Final paced QRS130(IQR122-138) CSP and130(124-140) BiVP ms.','Forest130(12.05)/131.4(12.07) appears median-to-mean/SD conversion, not directly observed means/SDs.','Keep median/IQR; do not label conversions as measured values.',sample_size_basis='postimplant analysis groups92/82; measured QRS N not separately stated')
med(r,92,130,122,138,82,130,124,140,follow_up='postimplant')
r=setr(s,'threshold','SUPPLEMENT_REQUIRED',4,'Procedural characteristics; TablesS3/S4 referenced','Main text says CS threshold is higher than LBBAP at implant,6 and12 months; exact numbers are in absent supplements.','Forest0.78 vs0.68 implies opposite direction; mean difference0.12 also disagrees with printed means (0.10). No source-supported numerical correction is possible yet.','Obtain TablesS3/S4; do not replace0.68 with hypothetical0.66.')
for o,e in {'composite':(5,6),'hhf':(5,3),'mortality':(0,3)}.items():
 r=setr(s,o,'VERIFIED',10,'Table3','Table3 explicitly gives number of patients with events, LBBAPn92/BiVPn82.','Counts and denominators match. Clinical-event population differs from161 continuous-outcome completers.','',sample_size_basis='clinical cohort92/82, perTable3',pooling_eligibility='ELIGIBLE_NUMERIC')
 ev(r,92,e[0],82,e[1])
# LECART press release cannot verify arm denominators or exact component counts.
s='LECART 2026'
for o in BIN:
 setr(s,o,'NOT_REPORTED_IN_PRESS_RELEASE','2-3','ESC press release,14April2026','Release says168 patients randomized1:1; four-component endpoint13%LBBAP vs25%BiVP. It does not give arm counts or death/HFH counts.','Forest arm denominators80/88 and component events cannot be certified from this release.13%/25% refer to a different composite including reintervention and failed therapy.','Obtain EHRA2026 LECART presentation/full outcome table. Do not infer counts from rounded percentages.',sample_size_basis='only total168 reported; no arm-specific N',statistic='not reported',same_estimand_as_figure=False)
# Ensure all requested forest rows reviewed, store exact source extraction.
assert len(ROWS)==96 and all(r['status']!='not_reviewed' for r in ROWS)
BASE.mkdir(exist_ok=True)
(BASE/'source_extraction.json').write_text(json.dumps({'forest_rows':ROWS,'additional_source_rows':EXTRA,'reported_contrasts':CONTRASTS},indent=2,ensure_ascii=False)+'\n')
print('Extracted',len(ROWS),'forest rows;',len(EXTRA),'additional rows;',len(CONTRASTS),'reported study contrasts')
