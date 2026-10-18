#!/usr/bin/env Rscript
# RStudio: open this directory as a project, then source this script.
# Command line: Rscript make_blue_forest_plots.R [input_directory] [output_directory]
# The selection plan is explicit below. Missing values are never replaced by zero.
for (pkg in c('meta','metafor','readxl')) {
  if (!requireNamespace(pkg,quietly=TRUE)) install.packages(pkg,repos='https://cloud.r-project.org')
}
suppressPackageStartupMessages(library(meta))
suppressPackageStartupMessages(library(readxl))
args <- commandArgs(trailingOnly=TRUE)
sa <- grep('^--file=',commandArgs(FALSE),value=TRUE)
sp <- if(length(sa)) sub('^--file=','',sa[1]) else ''
base <- if(nzchar(sp) && file.exists(sp)) dirname(normalizePath(sp)) else getwd()
input_dir <- if(length(args)>=1) args[1] else file.path(base,'inputs')
output_dir <- if(length(args)>=2) args[2] else file.path(base,'output')
dir.create(output_dir,recursive=TRUE,showWarnings=FALSE)
files <- c(walk='01_six_minute_walk_distance.xlsx',nyha='02_nyha_class.xlsx',
 qol='03_quality_of_life.xlsx',qrs='04_qrs_duration.xlsx',lvef='05_lvef.xlsx',
 threshold='09_pacing_threshold.xlsx',composite='10_composite_outcome.xlsx',
 hhf='11_heart_failure_hospitalization.xlsx',mortality='12_all_cause_mortality.xlsx')
stopifnot(all(file.exists(file.path(input_dir,files))))
cache <- lapply(files,function(f){
 p<-file.path(input_dir,f);setNames(lapply(excel_sheets(p),function(s)as.data.frame(read_excel(p,sheet=s))),excel_sheets(p))
})
row <- function(o,s,sheet='data',variant=NULL){
 d<-cache[[o]][[sheet]];if(is.null(d))stop('Missing worksheet: ',o,'/',sheet)
 d<-d[d$study==s,,drop=FALSE]
 if(!is.null(variant))d<-d[d$variant==variant,,drop=FALSE]
 if(nrow(d)!=1L)stop('Selection must identify exactly one row: ',o,' ',s,' ',sheet)
 d
}
cohort <- function(s)if(s %in% c('LEVEL-AT 2022','CONSYST-CRT 2025'))'Barcelona_LEVEL_CONSYST' else s
getval <- function(d,k,default=NA){if(k %in% names(d))d[[k]][1] else default}
record <- function(o,s,te,se,follow,basis,sheet,r,reason){
 data.frame(study=s,TE=te,seTE=se,follow_up=follow,basis=basis,cohort=cohort(s),
 input_file=files[o],input_sheet=sheet,input_row_id=getval(r,'row_id',''),
 selection_reason=reason,stringsAsFactors=FALSE,row.names=NULL)
}
# A raw independent-arm MD is only computed from complete source mean/SD/N.
arm <- function(o,s,follow,sheet='data',variant=NULL,reason='Independent-arm source mean/SD/N'){
 d<-row(o,s,sheet,variant);v<-as.numeric(d[1,c('n_csp','mean_csp','sd_csp','n_biv','mean_biv','sd_biv')])
 stopifnot(all(is.finite(v)),v[1]>1,v[4]>1,v[3]>=0,v[6]>=0)
 record(o,s,v[2]-v[5],sqrt(v[3]^2/v[1]+v[6]^2/v[4]),follow,'Mean / SD',sheet,d,reason)
}
# Preserve reported model/adjusted estimates rather than reconstruct raw SDs.
published <- function(o,s,follow,reason='Reported study contrast; normal approximation from rounded 95% CI'){
 d<-row(o,s,'reported_contrasts');se<-(d$upper_95-d$lower_95)/(2*qnorm(.975))
 stopifnot(is.finite(se),se>0)
 record(o,s,d$estimate,se,follow,'Reported CI','reported_contrasts',d,reason)
}
# For LEFT-BUNDLE-CRT only: unadjusted arm mean CIs, not model CIs.
# SE reconstructed using t(.975,n-1); independent arm variances are summed.
# This is an explicit approximation because source CIs are rounded.
arm_ci <- function(o,s,follow){
 d<-row(o,s);z<-row(o,s,'other_statistics')
 nc<-as.numeric(d$n_csp);nb<-as.numeric(d$n_biv)
 sec<-(z$ci_high_csp-z$ci_low_csp)/(2*qt(.975,nc-1))
 seb<-(z$ci_high_biv-z$ci_low_biv)/(2*qt(.975,nb-1))
 stopifnot(is.finite(sec),is.finite(seb),sec>0,seb>0)
 record(o,s,d$mean_csp-d$mean_biv,sqrt(sec^2+seb^2),follow,'Arm CIs*','other_statistics + data',d,
 'Approximate SE from rounded arm mean 95% CIs, using t quantiles and independent arms; no SD imputation')
}
bin <- function(o,s,follow,sheet='data',reason='Verified randomized-allocation event counts'){
 d<-row(o,s,sheet);v<-as.numeric(d[1,c('n_csp','event_csp','n_biv','event_biv')])
 stopifnot(all(is.finite(v)),v[1]>0,v[3]>0,v[2]>=0,v[4]>=0,v[2]<=v[1],v[4]<=v[3])
 data.frame(study=s,n_csp=v[1],event_csp=v[2],n_biv=v[3],event_biv=v[4],follow_up=follow,
 cohort=cohort(s),input_file=files[o],input_sheet=sheet,input_row_id=getval(d,'row_id',''),selection_reason=reason,stringsAsFactors=FALSE,row.names=NULL)
}
bind <- function(...)do.call(rbind,list(...))
# Primary selections: one contribution per independent cohort and outcome.
# Continuous MDs (not SMDs) can combine final values and changes on the same scale.
# LVEF uses changes throughout; thresholds use 6-month values throughout.
D <- list()
D$walk <- bind(arm('walk','His-Alternative 2021','6 months'),
 published('walk','LBBP-RESYNC 2022','6 months'),published('walk','PhysioSync-HF 2026','12 months'),
 arm_ci('walk','LEFT-BUNDLE-CRT 2026','12 months'))
D$nyha <- bind(arm('nyha','His-Alternative 2021','6 months','alternatives','six_month_ITT'),
 published('nyha','LBBP-RESYNC 2022','6 months'),
 arm('nyha','CONSYST-CRT 2025','12 months',reason='Larger shared Barcelona cohort selected; excludes overlapping LEVEL-AT'))
D$qol <- bind(published('qol','PhysioSync-HF 2026','12 months'),arm_ci('qol','LEFT-BUNDLE-CRT 2026','12 months'))
D$qrs <- bind(arm('qrs','His-Alternative 2021','6 months','alternatives','six_month_ITT'),
 arm('qrs','LBBP-RESYNC 2022','Implant'),
 arm('qrs','CONSYST-CRT 2025','12 months',reason='Larger Barcelona cohort; QRS change measured from pacing spike; overlapping LEVEL-AT excluded'),
 published('qrs','CSP-SYNC 2025','6 months'),published('qrs','PhysioSync-HF 2026','12 months'))
D$lvef <- bind(arm('lvef','His-Alternative 2021','6 months','alternatives','six_month_ITT_change'),
 published('lvef','LBBP-RESYNC 2022','6 months'),
 arm('lvef','HOT-CRT 2023','6 months','alternatives','six_month_change',reason='Complete-case echo change: 44/44; not randomized group headings 50/50'),
 arm('lvef','CONSYST-CRT 2025','12 months',reason='Larger Barcelona cohort; overlapping LEVEL-AT excluded'),
 published('lvef','CSP-SYNC 2025','6 months'),published('lvef','PhysioSync-HF 2026','12 months'),
 arm_ci('lvef','LEFT-BUNDLE-CRT 2026','12 months'))
D$threshold <- bind(arm('threshold','His-Alternative 2021','6 months','alternatives','six_month_ITT',reason='HBP versus BiVP at 1 ms; six-month ITT'),
 arm('threshold','LEVEL-AT 2022','6 months','alternatives','six_month',reason='Six-month Barcelona cohort selected to align follow-up; overlapping CONSYST excluded; pulse widths vary'),
 arm('threshold','LBBP-RESYNC 2022','6 months',reason='Six-month randomized comparison; exploratory voltage synthesis, not energy'))
# For ORs double-zero studies are displayed but contribute no pooled weight.
zeros <- function(o)bind(bin(o,'His-Alternative 2021','6 months','alternatives',reason='Verified six-month alternative: double-zero; excluded from OR weights'),
 bin(o,'LBBP-RESYNC 2022','6 months','alternatives',reason='Verified six-month alternative: double-zero; excluded from OR weights'))
D$composite <- rbind(zeros('composite'),bind(
 bin('composite','LEVEL-AT 2022','6 months',reason='Strict death or hospitalization composite; exclude overlapping transplant-inclusive CONSYST'),
 bin('composite','LEFT-BUNDLE-CRT 2026','12 months')))
D$hhf <- rbind(zeros('hhf'),bind(bin('hhf','LEVEL-AT 2022','6 months',reason='Usable HHF counts; overlapping CONSYST lacks verified component counts'),
 bin('hhf','HOT-CRT 2023','6 months'),bin('hhf','CSP-SYNC 2025','Mean 22.1 mo'),
 bin('hhf','PhysioSync-HF 2026','12 months'),bin('hhf','LEFT-BUNDLE-CRT 2026','12 months')))
D$mortality <- rbind(zeros('mortality'),bind(bin('mortality','LEVEL-AT 2022','6 months',reason='Usable mortality counts; overlapping CONSYST lacks verified component counts'),
 bin('mortality','HOT-CRT 2023','6 months'),
 bin('mortality','CSP-SYNC 2025','Mean 22.1 mo',reason='Uses two CSP deaths from original flowchart; source narrative omission remains documented'),
 bin('mortality','HeartSync-LBBP 2026','Median 36 mo'),bin('mortality','PhysioSync-HF 2026','12 months'),bin('mortality','LEFT-BUNDLE-CRT 2026','12 months')))
# Additional separately labelled sensitivities. They do not alter primary plots.
D$composite_broad <- bind(bin('composite','HeartSync-LBBP 2026','Median 36 mo',reason='All-cause death or HF events including urgent IV-diuretic visits'),
 bin('composite','PhysioSync-HF 2026','12 months',reason='All-cause death or HF hospitalization or urgent HF visits'))
D$hhf_broad <- rbind(D$hhf,bin('hhf','HeartSync-LBBP 2026','Median 36 mo',reason='Sensitivity includes urgent IV-diuretic visits within HFH definition'))
D$mortality_as_treated <- rbind(D$mortality,bin('mortality','His-SYNC 2019','Mean 12.2 mo',reason='Sensitivity only: treatment-received counts, not randomized allocation'))
D$qrs_as_treated <- rbind(D$qrs,arm('qrs','His-SYNC 2019','Implant',reason='Sensitivity only: treatment-received 16/24; SD corrected to22'))
# Specifications: nine primary PNGs plus four explicit sensitivity PNGs.
spec <- data.frame(key=names(D),title=c('6-minute walk distance','NYHA functional class','Quality of life: EQ-5D utility',
 'QRS duration','Left ventricular ejection fraction','Pacing threshold: exploratory voltage comparison',
 'All-cause death or HF hospitalization','Heart-failure hospitalization','All-cause mortality',
 'Death or HF events, including urgent visits','HF hospitalization / urgent visits: sensitivity',
 'All-cause mortality: as-treated sensitivity','QRS duration: as-treated sensitivity'),
 unit=c('m','NYHA classes','EQ-5D utility','ms','percentage points','V',rep('OR',6),'ms'),
 binary=c(rep(FALSE,6),rep(TRUE,6),FALSE),
 lower_better=c(FALSE,TRUE,FALSE,TRUE,FALSE,TRUE,rep(TRUE,7)),stringsAsFactors=FALSE)
# Named model settings apply consistently across all outputs.
settings <- list(common=FALSE,random=TRUE,method.tau='REML',method.random.ci='HK',
 adhoc.hakn.ci='se',method.I2='Q',level=.95,level.ma=.95)
models<-list();pool<-list();study_results<-list();selection<-list();validations<-list()
footer <- c(
 walk='Same-scale endpoint and change MDs combined. *SE approximated from rounded arm CIs.',
 nyha='Exploratory numeric NYHA-class MD; endpoint/change estimates combined. One Barcelona cohort only.',
 qol='EQ-5D utility only; two studies. *SE approximated from rounded arm CIs; other scales excluded.',
 qrs='Endpoint/change MDs combined; QRS timing and measurement conventions vary. One Barcelona cohort only.',
 lvef='Changes in LVEF only. Model contrasts retained. *SE approximated from rounded arm CIs.',
 threshold='Six-month values only. Pulse widths and pacing modalities differ: voltage MD is exploratory, not capture energy.',
 composite='Strict all-cause death / HF hospitalization definition. Different composites excluded. Double-zero rows unweighted.',
 hhf='Urgent-visit-inclusive HeartSync endpoint excluded here. Double-zero rows unweighted. Follow-up varies.',
 mortality='Randomized-allocation counts; CSP-SYNC uses two deaths from source flowchart. Double-zero rows unweighted.',
 composite_broad='Separate broader endpoint analysis; not the strict hospitalization/death composite. Only two studies.',
 hhf_broad='Sensitivity adds HeartSync HFH definition, which includes urgent IV-diuretic visits.',
 mortality_as_treated='Sensitivity adds His-SYNC treatment-received counts; this mixes randomized and as-treated estimates.',
 qrs_as_treated='Sensitivity adds His-SYNC treatment-received estimates; this mixes randomized and as-treated estimates.')
render <- function(m,d,s,path){
 h<-4.5+.25*nrow(d)
 png(path,width=14,height=h,units='in',res=300,type='cairo',bg='white')
 on.exit(dev.off(),add=TRUE)
 a<-list(x=m,layout='meta',common=FALSE,random=TRUE,
 smlab=paste0(s$title,'\n',if(s$binary)'Odds ratio' else paste0('Mean difference (',s$unit,')'),', 95% CI'),
 text.random='Pooled (95% CI)',label.e='CSP',label.c='BiVP',
 label.left=if(s$lower_better)'Favours CSP' else 'Favours BiVP',
 label.right=if(s$lower_better)'Favours BiVP' else 'Favours CSP',
 col.square='#247AB5',col.square.lines='#174A72',col.diamond='#123B64',col.diamond.lines='#123B64',
 col.study='#174A72',col.inside='white',col.label.left='#174A72',col.label.right='#174A72',
 fontsize=10,fontfamily='sans',plotwidth='8cm',spacing=1.12,
 colgap.forest.left='5mm',colgap.forest.right='5mm',colgap.right='7mm',
 digits=if(s$key=='qol')3 else 2,digits.weight=1,print.tau2=TRUE,print.I2=TRUE,print.pval.Q=TRUE,
 digits.tau2=4,digits.I2=1,overall.hetstat=TRUE,test.overall=TRUE,addrows.below.overall=4,
 lab.NA.effect='Not estimable',lab.NA.weight='0.0%')
 if(s$binary){
  a$leftcols<-c('studlab','follow_up','event.e','n.e','event.c','n.c')
  a$leftlabs<-c('Study','Follow-up','Events','Total','Events','Total')
 }else{
  a$leftcols<-c('studlab','follow_up','basis');a$leftlabs<-c('Study','Follow-up','Input')
 }
 a$rightcols<-c('effect','ci','w.random');a$rightlabs<-c(if(s$binary)'OR' else 'MD','95% CI','Weight')
 do.call(meta::forest,a)
 # Fix meta8.5 RevMan rendering of a duplicated non-estimable label.
 for(nm in grid::grid.ls(print=FALSE)$name){
  g<-grid::grid.get(nm)
  if(inherits(g,'text') && is.character(g$label) && any(grepl('Not estimableNot estimable',g$label,fixed=TRUE)))
   grid::grid.edit(nm,label=gsub('Not estimableNot estimable','Not estimable',g$label,fixed=TRUE))
 }
 if(s$binary && exp(m$lower.random)<.005){
  upper_label<-formatC(exp(m$upper.random),format='f',digits=2)
  sci_ci<-sprintf('[%.1g; %.1g]',exp(m$lower.random),exp(m$upper.random))
  for(nm in grid::grid.ls(print=FALSE)$name){
   g<-grid::grid.get(nm)
   if(inherits(g,'text') && is.character(g$label)){
    hit<-grepl(upper_label,g$label,fixed=TRUE) & grepl('[',g$label,fixed=TRUE)
    if(any(hit)){g$label[hit]<-sci_ci;grid::grid.edit(nm,label=g$label)}
   }
  }
 }
 grid::grid.text('Random effects: REML; Hartung-Knapp 95% CI with variance floor',x=.5,y=.055,
 gp=grid::gpar(fontsize=10,col='#174A72',fontfamily='sans'))
 grid::grid.text(footer[[s$key]],x=.5,y=.027,
 gp=grid::gpar(fontsize=8.5,col='#475569',fontfamily='sans'))
}
for(i in seq_len(nrow(spec))){
 s<-spec[i,];d<-D[[s$key]];stopifnot(!anyDuplicated(d$cohort))
 if(s$binary){
  m<-do.call(meta::metabin,c(list(event.e=d$event_csp,n.e=d$n_csp,event.c=d$event_biv,n.c=d$n_biv,
   studlab=d$study,data=d,sm='OR',method='Inverse',incr=.5,method.incr='only0',allstudies=FALSE),settings))
 }else{
  stopifnot(all(is.finite(d$TE)),all(is.finite(d$seTE)),all(d$seTE>0))
  m<-do.call(meta::metagen,c(list(TE=d$TE,seTE=d$seTE,studlab=d$study,data=d,sm='MD'),settings))
 }
 stopifnot(m$k>=2,is.finite(m$TE.random),is.finite(m$lower.random),is.finite(m$upper.random))
 # Independent numerical verification with metafor, including the HK variance floor.
 keep<-is.finite(m$TE)&is.finite(m$seTE)&m$seTE>0
 fit<-metafor::rma.uni(yi=m$TE[keep],vi=m$seTE[keep]^2,method='REML',test='knha')
 w<-1/(m$seTE[keep]^2+fit$tau2);mu<-sum(w*m$TE[keep])/sum(w)
 q<-sum(w*(m$TE[keep]-mu)^2)/(sum(keep)-1)
 sehk<-sqrt(max(1,q)/sum(w));lo<-mu-qt(.975,sum(keep)-1)*sehk;hi<-mu+qt(.975,sum(keep)-1)*sehk
 tol<-1e-4
 stopifnot(abs(mu-m$TE.random)<tol,abs(lo-m$lower.random)<tol,abs(hi-m$upper.random)<tol)
 transform<-if(s$binary)exp else identity
 file<-sprintf('%02d_%s.png',i,s$key)
 render(m,d,s,file.path(output_dir,file))
 models[[s$key]]<-m
 pool[[s$key]]<-data.frame(analysis=s$key,title=s$title,file=file,measure=if(s$binary)'OR' else 'MD',unit=s$unit,
  k_estimable=m$k,rows_displayed=nrow(d),estimate=transform(m$TE.random),lower_95=transform(m$lower.random),upper_95=transform(m$upper.random),
  I2_percent=100*m$I2,tau2=m$tau2,p_value=m$pval.random,model='REML / Hartung-Knapp with SE floor')
 weights<-100*m$w.random/sum(m$w.random,na.rm=TRUE)
 study_results[[s$key]]<-data.frame(analysis=s$key,study=d$study,effect=transform(m$TE),lower_95=transform(m$lower),upper_95=transform(m$upper),weight_percent=weights)
 sel<-d[,c('study','follow_up','cohort','input_file','input_sheet','input_row_id','selection_reason')]
 sel$analysis<-s$key;selection[[s$key]]<-sel
 write.csv(d,file.path(output_dir,paste0('analysis_inputs_',s$key,'.csv')),row.names=FALSE,na='')
 validations[[s$key]]<-data.frame(analysis=s$key,metafor_difference=abs(mu-m$TE.random),lower_ci_difference=abs(lo-m$lower.random),upper_ci_difference=abs(hi-m$upper.random),unique_cohorts=TRUE)
 message(file,'  ',m$k,' estimable studies; ',sprintf('%.3f [%.3f, %.3f]',transform(m$TE.random),transform(m$lower.random),transform(m$upper.random)))
}
write.csv(do.call(rbind,pool),file.path(output_dir,'pooled_results.csv'),row.names=FALSE)
write.csv(do.call(rbind,study_results),file.path(output_dir,'study_results.csv'),row.names=FALSE,na='')
write.csv(do.call(rbind,selection),file.path(output_dir,'selection_log.csv'),row.names=FALSE)
write.csv(do.call(rbind,validations),file.path(output_dir,'independent_validation.csv'),row.names=FALSE)
saveRDS(models,file.path(output_dir,'models.rds'))
writeLines(capture.output(sessionInfo()),file.path(output_dir,'sessionInfo.txt'))
# Every original main-sheet row receives a decision for the primary outcome.
ledger<-list()
for(o in names(files)){
 d<-cache[[o]]$data;sel<-D[[o]];notes<-cache[[o]]$review_notes
 for(j in seq_len(nrow(d))){
  s<-d$study[j];used<-s %in% sel$study;nr<-notes[notes$study==s,,drop=FALSE]
  why<-if(used)sel$selection_reason[match(s,sel$study)] else paste(getval(nr,'comparison',''),getval(nr,'required_action',''))
  if(!used && s=='LEVEL-AT 2022' && o %in% c('nyha','qrs','lvef'))why<-'Overlapping cohort: larger CONSYST-CRT selected; LEVEL-AT not counted again.'
  if(!used && s=='CONSYST-CRT 2025')why<-if(o=='threshold')'Overlapping cohort: LEVEL-AT six-month alternative selected to harmonize follow-up.' else 'Overlapping LEVEL-AT selected; CONSYST components unavailable or composite includes transplant.'
  if(!used && s=='ALTERNATIVE-AF 2022')why<-'Paired crossover uncertainty/period denominators unavailable; first-period endpoint LVEF omitted from change-only LVEF analysis.'
  if(!used && s=='His-SYNC 2019' && o %in% c('qrs','mortality'))why<-'Treatment-received population; included only in separately labelled sensitivity plot.'
  if(!used && o=='composite')why<-paste('Not included in strict death-or-HFH composite.',why)
  ledger[[length(ledger)+1]]<-data.frame(outcome=o,study=s,primary_decision=if(used)'included' else 'excluded',
   selected_sheet=if(used)sel$input_sheet[match(s,sel$study)] else '',reason=why,stringsAsFactors=FALSE)
 }
}
stopifnot(length(ledger)==87)
write.csv(do.call(rbind,ledger),file.path(output_dir,'all_87_primary_row_decisions.csv'),row.names=FALSE)
cat('Finished:',nrow(spec),'PNG files; nine primary outcomes and four sensitivity analyses.\n')
