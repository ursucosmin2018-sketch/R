#!/usr/bin/env Rscript
# Read back the delivered workbooks and validate provenance, data types and key corrections.
suppressPackageStartupMessages(library(readxl))
args <- commandArgs(trailingOnly=FALSE)
script <- sub('^--file=', '', args[grepl('^--file=', args)])
base <- if (length(script)) dirname(normalizePath(script)) else getwd()
out <- file.path(base, 'output')
contfile <- file.path(out, 'CSP_vs_BiVP_continuous_source_checked.xlsx')
binfile <- file.path(out, 'CSP_vs_BiVP_binary_source_checked.xlsx')
auditfile <- file.path(out, 'CSP_vs_BiVP_audit_and_sources.xlsx')
contsheets <- c('6MWD','NYHA','Quality_of_life','QRS','LVEF','Pacing_threshold','LVESV_mL','LVESV_percent','LVESVi_mL_m2')
binsheets <- c('Composite','HF_hospitalization','All_cause_mortality')
read_sheets <- function(file, sheets) {
  tabs <- lapply(sheets, function(s) as.data.frame(read_excel(file, sheet=s)))
  do.call(rbind,tabs)
}
cdata <- read_sheets(contfile,contsheets)
bdata <- read_sheets(binfile,binsheets)
stopifnot(nrow(cdata)==64L,nrow(bdata)==32L,!anyDuplicated(c(cdata$record_id,bdata$record_id)))
stopifnot(all(!is.na(cdata$source_location)),all(!is.na(bdata$source_location)))
stopifnot(all(!is.na(cdata$status)),all(!is.na(bdata$status)))
# Do not allow missing data to become zero in Excel.
stopifnot(all(is.na(bdata$source_event_csp[bdata$study=='LECART 2026'])))
for (d in list(cdata,bdata)) {
  for (arm in c('csp','biv')) {
    n <- as.numeric(d[[paste0('source_n_',arm)]])
    stopifnot(all(n[!is.na(n)]>0),all(n[!is.na(n)]==floor(n[!is.na(n)])))
  }
}
for (arm in c('csp','biv')) {
  e <- as.numeric(bdata[[paste0('source_event_',arm)]])
  n <- as.numeric(bdata[[paste0('source_n_',arm)]])
  stopifnot(all(e[!is.na(e)]>=0),all(e[!is.na(e)]==floor(e[!is.na(e)])))
  stopifnot(all(e[!is.na(e)&!is.na(n)]<=n[!is.na(e)&!is.na(n)]))
  sd <- as.numeric(cdata[[paste0('source_sd_',arm)]])
  stopifnot(all(sd[!is.na(sd)]>=0))
}
get <- function(d,study,outcome,field) d[d$study==study & d$outcome==outcome,field][[1]]
stopifnot(get(cdata,'His-SYNC 2019','qrs','source_sd_csp')==22)
stopifnot(get(cdata,'PhysioSync-HF 2026','lvef','source_mean_csp')==8)
stopifnot(get(cdata,'HOT-CRT 2023','quality_of_life','source_mean_biv')==0.07)
stopifnot(get(cdata,'His-Alternative 2021','walk_distance','source_n_csp')==25)
stopifnot(get(cdata,'HOT-CRT 2023','threshold','source_n_csp')==57)
stopifnot(get(cdata,'HOT-CRT 2023','threshold','source_n_biv')==43)
stopifnot(get(cdata,'LBBP-RESYNC 2022','lvef','source_sd_csp')==13.2)
stopifnot(get(cdata,'LBBP-RESYNC 2022','lvef','source_sd_biv')==9.4)
stopifnot(get(cdata,'CONSYST-CRT 2025','lvesv','source_n_csp')==66)
stopifnot(get(cdata,'CONSYST-CRT 2025','lvesv','source_n_biv')==62)
stopifnot(get(cdata,'LEFT-BUNDLE-CRT 2026','lvesv','unit')=='mL/m2')
stopifnot(get(cdata,'His-SYNC 2019','lvesv','source_mean_csp')== -22)
stopifnot(get(bdata,'CSP-SYNC 2025','mortality','source_event_csp')==2)
# Medians and model SEs are not silently converted to raw SDs.
stopifnot(is.na(get(cdata,'CSP-SYNC 2025','walk_distance','source_mean_csp')))
stopifnot(get(cdata,'CSP-SYNC 2025','walk_distance','source_median_csp')==450)
stopifnot(is.na(get(cdata,'LBBP-RESYNC 2022','walk_distance','source_sd_csp')))
stopifnot(get(cdata,'LBBP-RESYNC 2022','walk_distance','source_se_csp')==14.14)
stopifnot(get(cdata,'LEVEL-AT 2022','nyha','overlap_group')==get(cdata,'CONSYST-CRT 2025','nyha','overlap_group'))
ca <- read_excel(auditfile,sheet='Cell_audit_512')
inv <- read_excel(auditfile,sheet='Study_inventory')
stopifnot(nrow(ca)==512L,nrow(inv)==13L)
# Compare underlying extracted JSON values via the CSV export for workbook fidelity.
for (pair in list(list(cdata,'continuous_source_checked.csv'),list(bdata,'binary_source_checked.csv'))) {
  d <- pair[[1]]; csv <- read.csv(file.path(out,pair[[2]]),check.names=FALSE,na.strings='')
  csv <- csv[match(d$record_id,csv$record_id),]
  for (k in intersect(names(d),names(csv))) {
    lhs <- as.character(d[[k]]);rhs <- as.character(csv[[k]])
    # Python CSV encodes boolean strings as True/False, while readxl returns logical.
    rhs[rhs=='True' & !is.na(rhs)] <- 'TRUE';rhs[rhs=='False' & !is.na(rhs)] <- 'FALSE'
    ok <- (is.na(lhs)&is.na(rhs)) | (!is.na(lhs)&!is.na(rhs)&lhs==rhs)
    stopifnot(all(ok))
  }
}
msg <- c('PASS: all three workbooks read successfully with R/readxl.',
         'PASS:64 continuous rows,32 binary rows,13 source documents,512 arm-data comparisons.',
         'PASS: key source corrections, missing values, event denominators and separated units checked.',
         'PASS: outcome worksheets match exported CSV values.',
         'LIMIT: checks validate extraction packaging and explicit source values; they do not resolve missing primary-source data.',
         paste('R:',R.version.string),paste('readxl:',as.character(packageVersion('readxl'))))
writeLines(msg,file.path(out,'validation_report.txt'))
writeLines(capture.output(sessionInfo()),file.path(out,'R_sessionInfo.txt'))
cat(paste(msg,collapse='\n'),'\n')
