"""Build the two outcome workbooks and source audit from source_extraction.json.
Requires openpyxl. Does not infer missing values or convert source statistics.
"""
import json,csv,math,hashlib,re,zipfile
from pathlib import Path
from collections import Counter
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.worksheet.table import Table,TableStyleInfo
from openpyxl.utils import get_column_letter
BASE=Path(__file__).resolve().parent
D=json.loads((BASE/'source_extraction.json').read_text());ROWS=D['forest_rows'];EXTRA=D['additional_source_rows'];CONTRASTS=D['reported_contrasts']
CONT=[r for r in ROWS if r['data_type']=='continuous'];BINARY=[r for r in ROWS if r['data_type']=='binary']
OUT=BASE/'output';OUT.mkdir(exist_ok=True)
# Persistent inventory can be reused without access to private PDFs.
invpath=BASE/'study_inventory.json'
if not invpath.exists():
 manifest=json.load(open('/workspace/research_sources/originals/manifest.json'))
 citations=list(csv.DictReader((BASE.parent/'cochrane_analysis/data/primary_source_verification.csv').open()))
 inv=[]
 for m in manifest:
  rs=[r for r in ROWS if r['source_pdf'].removesuffix('.pdf').replace(' et al.','')==m['study']]
  if not rs:raise ValueError(m['study'])
  study=rs[0]['study'];cite=next(x for x in citations if x['study']==study)
  text=Path(m['text']).read_text(); first=text.split('\f')[0]
  dois=re.findall(r'10\.\d{4,9}/[A-Za-z0-9./_-]+',first)
  doi=dois[0].rstrip('.') if dois else ''
  inv.append(dict(study=study,source_file=Path(m['pdf']).name,pdf_pages=m['pages'],sha256=hashlib.sha256(Path(m['pdf']).read_bytes()).hexdigest(),citation=cite['citation'],doi=doi,doi_url=('https://doi.org/'+doi) if doi else cite.get('original_publication_url',''),report_type='press release' if study=='LECART 2026' else 'original trial report / secondary trial analysis',design=rs[0]['design'],analysis_population=rs[0]['analysis_population'],timepoints=rs[0]['follow_up'],forest_rows_checked=len(rs),continuous_rows=sum(r['data_type']=='continuous' for r in rs),binary_rows=sum(r['data_type']=='binary' for r in rs),shared_cohort=rs[0]['overlap_group'],review_status='All forest rows checked against supplied PDF; unresolved fields explicitly identified',source_scope='Uploaded main document only; external supplements/follow-up reports were not supplied',checked_date='2026-10-18'))
 invpath.write_text(json.dumps(inv,indent=2,ensure_ascii=False)+'\n')
INVENTORY=json.loads(invpath.read_text())
MODALITY={
 'Lustgarten 2015':'HBP; forest QRS uses His-to-LV vector',
 'His-SYNC 2019':'HBP, treatment-received analysis',
 'His-Alternative 2021':'HBP strategy with crossovers',
 'LEVEL-AT 2022':'CSP strategy, includes HBP and LBBP; four HBP recipients',
 'LBBP-RESYNC 2022':'LBBP strategy with crossovers',
 'ALTERNATIVE-AF 2022':'HBP after AV nodal ablation, crossover',
 'HOT-CRT 2023':'HBP/LBBAP and LBBAP plus coronary-sinus pacing strategy',
 'CONSYST-CRT 2025':'CSP strategy, includes HBP and LBBP; four HBP recipients',
 'CSP-SYNC 2025':'LBBAP strategy',
 'HeartSync-LBBP 2026':'LBBP strategy',
 'PhysioSync-HF 2026':'CSP strategy, includes LBB area, deep septal, optimized and His pacing',
 'LEFT-BUNDLE-CRT 2026':'LBBAP strategy, includes LBB capture, LV septal capture and deep septal pacing',
 'LECART 2026':'LBBAP strategy; press release only'}
for r in ROWS:
 r['source_csp_modality']=MODALITY[r['study']]
 r['figure_subgroup']=r.pop('subgroup')
MISSING=[
 dict(study='His-Alternative 2021',needed='Frandsen et al2026 long-term follow-up; DOI10.1016/j.jacep.2026.02.016',affects='NYHA,QRS,LVEF,LVESV,threshold,composite,HFH,mortality',reason='Uploaded2021 paper ends at6 months. Long-term forest entries cannot be verified from it.'),
 dict(study='LBBP-RESYNC 2022',needed='Zou et al2026 four-year follow-up abstract/presentation; HeartRhythm23:S62-S63',affects='composite,HFH,mortality',reason='Uploaded2022 paper reports no6-month events and randomized20/20. Forest uses22/18 and later events.'),
 dict(study='LECART 2026',needed='EHRA2026 LECART presentation or full arm-level outcome tables',affects='composite,HFH,mortality',reason='Press release lacks arm denominators and exact component counts. Rounded primary-composite percentages cannot recover these.'),
 dict(study='LEFT-BUNDLE-CRT 2026',needed='Online supplementary TablesS3 andS4; unindexed LVESV if needed',affects='threshold; absolute LVESV',reason='Threshold numbers absent. Available LVESV change is indexed in mL/m2, not mL.'),
 dict(study='PhysioSync-HF 2026',needed='Supplement2 SAP and Supplement3 eTable1/outcome sample sizes',affects='threshold; continuous outcome Ns',reason='Main paper supplies continuous mean/SD but not individual outcome Ns; threshold forest values not in main paper.'),
 dict(study='CONSYST-CRT 2025',needed='Supplemental Table1 and separate clinical components/overlap',affects='HFH,mortality,strict death-or-HFH composite',reason='Main report composite includes transplantation; individual component counts unavailable in supplied PDF.'),
 dict(study='ALTERNATIVE-AF 2022',needed='Supplemental Tables1-3 and crossover-period denominators/covariance',affects='threshold; event risks; paired outcomes',reason='Need period-specific thresholds, at-risk denominators, and paired uncertainty;25/25 sequence counts are not exposure-period denominators.'),
 dict(study='Lustgarten 2015',needed='Numerical data behind Figures2-4, paired covariance and vector-specific QRS Ns',affects='all seven continuous rows',reason='Unlabelled graphs do not certify decimal SDs; QoL prose/bar and walking units disagree.'),
 dict(study='HOT-CRT 2023',needed='Outcome-specific Ns for6-month QRS,walking andQoL',affects='QRS,walking,QoL',reason='Group heading50/50 is not measured N;44/44 completed follow-up including echo.'),
 dict(study='HeartSync-LBBP 2026',needed='Observed Ns for last-follow-up continuous outcomes',affects='NYHA,QRS,LVEF,threshold',reason='Table2 heading100/100 denotes randomization; measured last-follow-up N not separately reported.'),
 dict(study='LEVEL-AT 2022',needed='Six-month measured echo Ns / missing-data handling',affects='LVEF,LVESV',reason='Table2 header35/35, but two BiVP deaths and forest LVEF N35/33. Shared cohort with CONSYST must also be handled.'),
 dict(study='CSP-SYNC 2025',needed='Clarification of mortality timing and raw continuous SDs if arm-based analysis is intended',affects='mortality timing; continuous SDs',reason='Figure1 shows two LBBAP deaths; narrative only describes its cardiovascular death. Mixed-model CIs do not provide raw patient SDs.'),
 dict(study='His-SYNC 2019',needed='Raw mean/SDs or explicit median-conversion plan; randomized allocation data for ITT synthesis',affects='LVEF,QoL,threshold; population choice',reason='Published source uses medians/IQRs and treatment-received groups16/24.')]
ISSUES=[
 ('Shared participants','CONSYST-CRT Methods explicitly says first70 participants came from LEVEL-AT. Do not count these as independent trials for the same pooled outcome.','CONSYST-CRT.pdf p2, Study population'),
 ('Incompatible LVESV units','His-SYNC and CONSYST report relative percent change; LEFT-BUNDLE reports indexed mL/m2; other trials report mL. Separate outcome sheets preserve this distinction.','His-SYNC p7; CONSYST p6 Table2; LEFT-BUNDLE pp8-9 Table2'),
 ('Different composite endpoints','PhysioSync adds urgent HF visits; CONSYST adds transplantation; CSP-SYNC uses cardiovascular death and worsening HF; HeartSync HFH includes urgent IV-diuretic visits. Do not label all as inpatient HFH or all-cause death.','Study definitions and source summaries in row audit'),
 ('Crossover observations','Lustgarten and ALTERNATIVE-AF repeated treatment measurements are paired. Randomized sequence Ns are not denominators for treatment-period event ORs.','Lustgarten pp2-4; ALTERNATIVE-AF pp3-5'),
 ('Outcome N versus group N','Randomization/table-header N is stored separately from outcome N. Missing observed N is blank, not silently copied from enrollment.','HOT-CRT p5; PhysioSync p6; HeartSync p5'),
 ('Model uncertainty is not raw SD','LBBP-RESYNC LS mean SEs and CSP-SYNC longitudinal-model CIs are preserved. Multiplying model SE bysqrt(N) need not recover patient SD. Study contrasts are provided separately.','LBBP-RESYNC p8 Table3; CSP-SYNC pp4-6'),
 ('Medians are not observed means','Median/IQR values remain median/IQR. No unlabelled median-to-mean conversion has been applied.','His-SYNC, CSP-SYNC, LEFT-BUNDLE source tables'),
 ('Change and endpoint SMD','NYHA and QoL figures mix endpoint and change values. SMDs based on endpoint SDs and change SDs cannot automatically be combined as if equivalent. Harmonize type and direction first.','Source measurement_type/scale columns'),
 ('Different pacing thresholds','Pulse widths, lead-capture versus QRS-correction thresholds, and implant/follow-up times differ. Voltage alone is not fully comparable without these details.','His-SYNC Table2; HOT-CRT Table2; other threshold source notes'),
 ('Follow-up extension unavailable','Older uploaded trial papers do not verify later follow-up outcomes. Six-month alternatives are separate records, not silent corrections to longer-term data.','His-Alternative2021; LBBP-RESYNC2022'),
 ('CSP is not uniformly LBBAP','The forest subgroup called LBBAP contains CSP strategies with HBP, deep septal pacing, crossovers and hybrid pacing. Original subgroup label is retained as figure_subgroup only.','LEVEL-AT, CONSYST, HOT-CRT, PhysioSync and LEFT-BUNDLE methods'),
 ('Exact versus rounded','Reported means/CIs are rounded and adjusted study contrasts may differ from the simple difference of rounded arm means. These are not automatically extraction errors.','Study_contrasts sheet')]
READ_ME=[
 ('Purpose','Source-checked data for all10 outcomes in the supplied latest forest figures:64 continuous and32 binary study/outcome rows from13 uploaded studies.'),
 ('What has been checked','Every one of the96 forest rows was compared with the supplied primary document. This is a complete audit, not a claim that all96 rows have complete or verified numerical inputs.'),
 ('Important limitation','Some necessary supplements, long-term reports and numerical graph data were not supplied. Empty source cells mean not recoverable with adequate certainty from these PDFs. They NEVER mean zero.'),
 ('Where to find values','Outcome sheets place source fields first. Original forest values are retained in figure_* columns. Source_mean,source_sd andsource_event are distinct from medians,IQR,SE andCI.'),
 ('Mean/SD availability','An empty source_sd beside an LS mean or model CI is intentional. Do not fill it with the forest SD. Median-to-mean conversions were not performed.'),
 ('Sample sizes','source_n is the outcome N when ascertainable; group_n is enrollment or reported arm size. Read sample_size_basis. Numeric N may describe a model cohort or paired cohort, not independent raw observations.'),
 ('LVESV','mL, relative percent change and indexed mL/m2 are in separate sheets. They cannot be pooled as one mean difference.'),
 ('Do not double-count','LEVEL-AT and CONSYST-CRT share70 participants. Select one report per cohort in any single analysis; cohort label is included.'),
 ('Interpretation of status','VERIFIED means that indicated source numbers match. It does not by itself establish design compatibility, independence, completeness or eligibility for a particular pooling protocol.'),
 ('Interpretation of pooling_eligibility','A planning flag, not an automatic inclusion rule. HOLD means a method/data decision remains. ELIGIBLE_NUMERIC still requires compatible timepoint,definition,design and units. SENSITIVITY flags non-ITT populations.'),
 ('Alternative rows','Additional_source_data contains six-month alternatives and other clearly labelled source values. These must not be combined with the main row from the same trial as independent evidence.'),
 ('Reported contrasts','Study_contrasts preserves original study estimates/CIs, especially for model-based continuous outcomes. These are not recomputed crude differences.'),
 ('Scope','All outcomes shown in the latest Figures1-3 were audited. This is not extraction of every additional endpoint ever measured by each trial.'),
 ('Source citations','PDF page numbers are1-based pages in each uploaded file. Study_inventory records file SHA256 hashes and citations. No original copyrighted PDF is redistributed.'),
 ('Delivery','Three Excel workbooks, CSV/JSON data, extraction/build code and an R validation script are included. The older forest plots remain a separate reproduction of meta-analysis inputs; they are not a validated corrected analysis.'),
 ('Next information needed','See Missing_data for the precise supplement/follow-up/report or denominator required to fill remaining blanks.'),
 ('Checked on','2026-10-18')]
# Field-by-field audit: 512 numerical arm cells, not effect/weight cells.
FIELDS=[]
for r in ROWS:
 ks=['n_csp','event_csp','n_biv','event_biv'] if r['data_type']=='binary' else ['n_csp','mean_csp','sd_csp','n_biv','mean_biv','sd_biv']
 for k in ks:
  fig=r.get('figure_'+k);src=r.get('source_'+k)
  if src is None: verdict='UNVERIFIABLE_AS_THIS_STATISTIC'
  elif not r['same_estimand_as_figure']:verdict='DIFFERENT_ESTIMAND'
  elif math.isclose(fig,src,abs_tol=1e-9):verdict='NUMERIC_MATCH_READ_ROW_FLAGS'
  else:verdict='NUMERIC_DIFFERENCE_READ_ROW_FLAGS'
  FIELDS.append(dict(study=r['study'],outcome=r['outcome'],field=k,forest_value=fig,source_value=src,comparison=verdict,row_status=r['status'],source_statistic=r['statistic'],source_unit=r['unit'],source_pdf=r['source_pdf'],pdf_pages=r['pdf_pages'],source_location=r['source_location'],context=r['comparison'],required_action=r['required_action']))
assert len(FIELDS)==512
# Audit summary and self-contained narrative.
counts=Counter(r['status'] for r in ROWS);fc=Counter(r['comparison'] for r in FIELDS)
SUMMARY=[dict(category='Rows checked',item='Continuous',count=len(CONT)),dict(category='Rows checked',item='Binary',count=len(BINARY)),dict(category='Rows checked',item='All rows',count=len(ROWS)),dict(category='Arm data cells',item='All cells',count=len(FIELDS))]+[dict(category='Row status',item=k,count=v) for k,v in sorted(counts.items())]+[dict(category='Numeric comparison',item=k,count=v) for k,v in sorted(fc.items())]
def columns(records,preferred=None):
 keys=list(preferred or [])
 for r in records:
  for k in r:
   if k not in keys:keys.append(k)
 return keys
CORE=['study','outcome','status','pooling_eligibility','statistic','measurement_type','follow_up','unit','scale','source_n_csp','source_mean_csp','source_sd_csp','source_event_csp','source_n_biv','source_mean_biv','source_sd_biv','source_event_biv','source_median_csp','source_q1_csp','source_q3_csp','source_median_biv','source_q1_biv','source_q3_biv','source_se_csp','source_se_biv','source_ci_low_csp','source_ci_high_csp','source_ci_low_biv','source_ci_high_biv','group_n_csp','group_n_biv','sample_size_basis','analysis_population','design','overlap_group','source_csp_modality','source_pdf','pdf_pages','source_location','source_summary','comparison','required_action']
# Fewer irrelevant columns in each workbook.
CC=[k for k in CORE if k not in ['source_event_csp','source_event_biv']]
BC=[k for k in CORE if not any(x in k for x in ['mean_','sd_','median_','q1_','q3_','se_','ci_low_','ci_high_']) and k not in ['statistic','measurement_type']]
CC += ['figure_n_csp','figure_mean_csp','figure_sd_csp','figure_n_biv','figure_mean_biv','figure_sd_biv']
BC += ['figure_n_csp','figure_event_csp','figure_n_biv','figure_event_biv']
# Keep selected sheet columns explicit, avoiding duplicate figure effects etc.
for cols in [CC,BC]:cols += ['figure_subgroup','same_estimand_as_figure','higher_is_better','record_id']
NUM_START=('source_n_','source_mean_','source_sd_','source_event_','source_median_','source_q1_','source_q3_','source_se_','source_ci_','figure_','group_n_')
def sheet(wb,name,records,cols=None):
 ws=wb.create_sheet(name);records=list(records)
 cols=cols or columns(records)
 if not cols:cols=['note'];records=[{'note':'No records'}]
 ws.append(cols)
 for r in records:
  values=[r.get(k) for k in cols]
  ws.append([json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for v in values])
 ws.freeze_panes='C2';ws.sheet_view.zoomScale=80
 ws.row_dimensions[1].height=44
 for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='174A63');c.alignment=Alignment(wrap_text=True,vertical='center')
 for i,k in enumerate(cols,1):
  width=16
  if k in ['study','outcome','status','pooling_eligibility','statistic','measurement_type']:width=27
  if k in ['source_pdf','source_location','follow_up','unit','analysis_population','design','overlap_group','source_csp_modality']:width=34
  if k in ['source_summary','comparison','required_action','context','reason','needed','description','text','value','citation','sample_size_basis']:width=72
  if k in ['sha256','doi_url']:width=65
  ws.column_dimensions[get_column_letter(i)].width=width
 for row in ws.iter_rows(min_row=2):
  for c in row:
   c.alignment=Alignment(vertical='top',wrap_text=True)
   if isinstance(c.value,(int,float)) and not isinstance(c.value,bool):c.number_format='0.########'
  ws.row_dimensions[row[0].row].height=95 if len(cols)>10 else 65
 if len(records):
  t=Table(displayName='T_'+str(len(wb.worksheets))+'_'+re.sub('[^A-Za-z0-9]','',name)[:20],ref=f'A1:{get_column_letter(len(cols))}{len(records)+1}')
  t.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True,showColumnStripes=False);ws.add_table(t)
  if 'status' in cols:
   idx=cols.index('status')+1
   for rr in range(2,len(records)+2):
    val=ws.cell(rr,idx).value or '';color='FFF2CC'
    if val=='VERIFIED':color='D9EAD3'
    elif any(k in val for k in ['CORRECTED','WRONG_','MISMATCH']):color='F4CCCC'
    ws.cell(rr,idx).fill=PatternFill('solid',fgColor=color)
 ws.auto_filter.ref=ws.dimensions
 ws.print_options.horizontalCentered=False;ws.sheet_properties.pageSetUpPr.fitToPage=True
 ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3;ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=0
 ws.print_title_rows='1:1'
 return ws
def workbook():
 wb=Workbook();wb.remove(wb.active);wb.properties.creator='Source-data audit';wb.properties.title='CSP versus BiVP: primary-source data audit';wb.properties.description='Source values, forest comparisons and explicit missing-data flags.'
 sheet(wb,'READ_ME',[dict(topic=a,text=b) for a,b in READ_ME]);return wb
def writecsv(name,rows,preferred=None):
 cols=columns(rows,preferred)
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
wb=workbook()
for outcome,title in [('walk_distance','6MWD'),('nyha','NYHA'),('quality_of_life','Quality_of_life'),('qrs','QRS'),('lvef','LVEF'),('threshold','Pacing_threshold')]:
 sheet(wb,title,[r for r in CONT if r['outcome']==outcome],CC)
for unit,title in [('mL','LVESV_mL'),('percent relative change','LVESV_percent'),('mL/m2','LVESVi_mL_m2')]:
 sheet(wb,title,[r for r in CONT if r['outcome']=='lvesv' and r['unit']==unit],CC)
sheet(wb,'Additional_source_data',[r for r in EXTRA if r['outcome'] not in ['composite','hhf','mortality']])
sheet(wb,'Study_contrasts',CONTRASTS)
sheet(wb,'Missing_data',MISSING)
wb.save(OUT/'CSP_vs_BiVP_continuous_source_checked.xlsx')
wb=workbook()
for outcome,title in [('composite','Composite'),('hhf','HF_hospitalization'),('mortality','All_cause_mortality')]:sheet(wb,title,[r for r in BINARY if r['outcome']==outcome],BC)
sheet(wb,'Additional_source_data',[r for r in EXTRA if r['outcome'] in ['composite','hhf','mortality']])
sheet(wb,'Definitions_and_design',[dict(issue=a,description=b,source=c) for a,b,c in ISSUES])
sheet(wb,'Missing_data',MISSING)
wb.save(OUT/'CSP_vs_BiVP_binary_source_checked.xlsx')
wb=workbook();sheet(wb,'Summary',SUMMARY);sheet(wb,'Study_inventory',INVENTORY)
sheet(wb,'Row_audit',ROWS,['study','outcome','status','comparison','required_action','source_pdf','pdf_pages','source_location','pooling_eligibility'])
sheet(wb,'Cell_audit_512',FIELDS);sheet(wb,'Design_and_definition_issues',[dict(issue=a,description=b,source=c) for a,b,c in ISSUES]);sheet(wb,'Missing_data',MISSING)
wb.save(OUT/'CSP_vs_BiVP_audit_and_sources.xlsx')
writecsv('continuous_source_checked.csv',CONT,CC);writecsv('binary_source_checked.csv',BINARY,BC);writecsv('all_96_rows.csv',ROWS,CORE)
writecsv('cell_audit_512.csv',FIELDS);writecsv('additional_source_data.csv',EXTRA);writecsv('reported_study_contrasts.csv',CONTRASTS);writecsv('missing_source_information.csv',MISSING);writecsv('study_inventory.csv',INVENTORY)
# Concrete numeric correction log is deliberately narrower than every numeric difference.
CORRECTIONS=[
 ('His-SYNC2019','QRS CSP SD','20','22','p6 on-treatment results','Primary paper explicitly reports22.'),
 ('PhysioSync-HF2026','LVEF CSP mean change','9','8','p6 Table2','Primary paper explicitly reports8; SD11 unchanged. Outcome N unresolved.'),
 ('HOT-CRT2023','EQ5D BiVP mean change','0.08','0.07','p8 Table4','Primary paper explicitly reports0.07.'),
 ('His-Alternative2021','6MWD CSP N','46','25','p6 Table3 ITT','Means444(133)/451(105) are six-month ITT n25/25.'),
 ('ALTERNATIVE-AF2022','QRS CSP mean','107.7','107.6','p4 Table1 andp5','Paired observations in same50 patients.'),
 ('LBBP-RESYNC2022','LVEF endpoint SDs','8.54 /8.69','13.2 /9.4','p7 Figure3A','Forest combines final means with dispersion reconstructed from model change SEs. Observed final N20/19 derived from p6.'),
 ('HOT-CRT2023','Echo endpoint N','50 /50','44 /44','p5 follow-up completion; p8 Table4','88 patients completed six-month visit including echo; table50/50 headings denote trial groups.'),
 ('HOT-CRT2023','Threshold N','50 /50','57 /43','p5 Table2 pacing-parameter subheading','Lead-type comparison, not randomized arm comparison.'),
 ('His-SYNC2019','LVESV sign and units','+22 /+19; treated as volume','-22% /-19%; relative change','p7 on-treatment results','SD24/14 retained in percent; do not pool as mL.'),
 ('CONSYST-CRT2025','LVESV unit and N','volume;67 /67','relative percent;66 /62','p6 Table2 andfootnote','Arm changes-27.9(27)/-27.9(28.1) are percentages; unavailable echo in1/5.'),
 ('LEFT-BUNDLE-CRT2026','LVESV unit','mL','mL/m2','pp8-9 Table2','Indexed volume change; cannot convert to mL without additional data.'),
 ('CSP-SYNC2025','All-cause deaths CSP','1','2','p4 Figure1','Flowchart lists1CV plus1non-CV death in LBBAP. Narrative mentions onlyCV death; retain source note.')]
with (OUT/'confirmed_corrections.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['study','field','forest','source','source_location','note']);w.writerows(CORRECTIONS)
report=['# CSP versus BiVP: primary-source audit','',f'Checked all **{len(ROWS)} study/outcome rows** across **13 uploaded documents**, covering **64 continuous and32 binary rows** in the10 plotted outcomes. Compared512 arm-data cells.','',
'All13 supplied documents were reviewed. This does **not** mean all data are complete: missing supplements, follow-up reports, measured sample sizes and numerical graph data prevent some values from being certified. Blank cells are intentional.','',
'## Workbooks','', '- `CSP_vs_BiVP_continuous_source_checked.xlsx`: seven continuous outcomes; LVESV separated into mL, percent change andmL/m2; additional source rows and published contrasts.', '- `CSP_vs_BiVP_binary_source_checked.xlsx`: composite, HF hospitalization andall-cause mortality, with exact endpoint definitions.', '- `CSP_vs_BiVP_audit_and_sources.xlsx`: all96 row reviews,512-cell audit, study citations/hashes andmissing-information list.','',
'## Confirmed corrections and source discrepancies','', '|Study|Field|Forest|Source|Reference|','|---|---|---|---|---|']
for s,k,a,b,p,n in CORRECTIONS:report.append(f'|{s}|{k}|{a}|{b}|{p}|')
report+=['','See `confirmed_corrections.csv` and workbook notes for population, source uncertainty andtimepoint qualifications.','', '## Changes needed before pooling','']
for a,b,c in ISSUES:report.extend([f'**{a}.** {b} Source: {c}.',''])
report+=['## Missing information','']
for x in MISSING:report.extend([f"- **{x['study']}:** {x['needed']}. {x['reason']}"])
report+=['','## Reproducibility','', 'The original forest-input CSVs remain unchanged in `../cochrane_analysis/data`. `extract_sources.py` contains the manually verified,page-referenced extraction; `source_extraction.json` is the resulting record. `build_workbooks.py` writes the Excel/CSV files. `validate_workbooks.R` reads every outcome sheet with`readxl`,checks key source corrections, validates numerical fields and confirms source references.','',
'No corrected pooled forest plot is presented here: the source audit identifies overlapping cohorts andincompatible definitions/statistics that first require an explicit synthesis plan. The earlier plots reproduce the meta-analysis inputs andshould not be treated as source-validated results.','',
'PDFs were used only as source documents andwere not uploaded to GitHub. DOI links/citations andfile hashes identify the sources.']
(BASE/'README.md').write_text('\n'.join(report)+'\n')
# Validate generated workbooks and record count; no formulas or invalid ranges.
for file in OUT.glob('*.xlsx'):
 w=load_workbook(file,data_only=False)
 assert w['READ_ME'].max_row>10
 for ws in w:
  for row in ws:
   for c in row:
    assert c.data_type!='f', (file.name,ws.title,c.coordinate)
 print(file.name, len(w.sheetnames),'sheets',file.stat().st_size,'bytes')
assert len(CONT)==64 and len(BINARY)==32 and len(INVENTORY)==13
print('512-cell comparison counts:',dict(fc))
