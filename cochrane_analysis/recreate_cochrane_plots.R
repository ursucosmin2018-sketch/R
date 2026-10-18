#!/usr/bin/env Rscript
# Recalculate the readable new source figures and render a RevMan-style layout.
if (!requireNamespace("meta", quietly = TRUE)) {
  install.packages("meta", repos = "https://cloud.r-project.org")
}
if (!requireNamespace("meta", quietly = TRUE)) stop("Install the R package meta")

specifications <- data.frame(
  outcome = c("walk_distance", "nyha", "quality_of_life", "composite", "hhf", "mortality"),
  title = c("6-minute walk distance", "NYHA functional class", "Quality of life",
            "Composite of HHF or all-cause mortality", "Hospitalization for heart failure", "All-cause mortality"),
  measure = c("MD", "SMD", "SMD", "OR", "OR", "OR"),
  filename = c("01_walk_distance.png", "02_nyha.png", "03_quality_of_life.png",
               "04_composite_hhf_or_mortality.png", "05_hhf.png", "06_all_cause_mortality.png"),
  stringsAsFactors = FALSE
)

fit_outcome <- function(d, measure) {
  d$subgroup <- factor(d$subgroup, levels = c("HBP", "LBBAP"))
  if (anyNA(d$subgroup)) stop("Unknown pacing subgroup")
  if (any(d$n_csp <= 0 | d$n_biv <= 0)) stop("Invalid sample size")
  args <- list(data = d, studlab = d$study, subgroup = d$subgroup,
               label.e = "CSP", label.c = "BiVP", sm = measure,
               common = FALSE, random = TRUE, method.tau = "REML",
               method.random.ci = "classic", method.I2 = "Q", tau.common = FALSE,
               level = 0.95, level.ma = 0.95)
  if (measure == "OR") {
    if (any(d$event_csp < 0 | d$event_csp > d$n_csp |
            d$event_biv < 0 | d$event_biv > d$n_biv)) stop("Invalid event count")
    args <- c(args, list(event.e = d$event_csp, n.e = d$n_csp,
                        event.c = d$event_biv, n.c = d$n_biv,
                        method = "Inverse", incr = 0.5, method.incr = "only0",
                        allstudies = FALSE))
    do.call(meta::metabin, args)
  } else {
    if (any(d$n_csp < 2 | d$n_biv < 2 | d$sd_csp <= 0 | d$sd_biv <= 0)) stop("Invalid continuous arm data")
    args <- c(args, list(n.e = d$n_csp, mean.e = d$mean_csp, sd.e = d$sd_csp,
                        n.c = d$n_biv, mean.c = d$mean_biv, sd.c = d$sd_biv,
                        pooledvar = FALSE, method.smd = "Hedges", exact.smd = TRUE,
                        method.ci.cont = "z"))
    do.call(meta::metacont, args)
  }
}

render_plot <- function(m, spec, file) {
  # The meta package implements Cochrane/RevMan's column arrangement directly.
  height <- 4.6 + 0.24 * length(m$studlab) + 0.8 * length(m$subgroup.levels)
  grDevices::png(file, width = 16, height = height, units = "in", res = 300,
                type = "cairo", bg = "white")
  on.exit(grDevices::dev.off(), add = TRUE)
  lower_favours_csp <- spec$outcome %in% c("nyha", "composite", "hhf", "mortality")
  meta::forest(
    m, layout = "RevMan5", common = FALSE, random = TRUE,
    label.e = "CSP", label.c = "BiVP", print.subgroup.name = FALSE,
    smlab = paste0(spec$title, "\n", spec$measure, ", IV, Random, 95% CI"),
    label.left = if (lower_favours_csp) "Favours CSP" else "Favours BiVP",
    label.right = if (lower_favours_csp) "Favours BiVP" else "Favours CSP",
    text.random = "Total (95% CI)", text.random.w = "Subtotal (95% CI)",
    test.overall = TRUE, test.effect.subgroup = TRUE, test.subgroup = TRUE,
    overall.hetstat = TRUE, hetstat = TRUE, print.tau2 = TRUE,
    print.I2 = TRUE, print.Q = TRUE, print.pval.Q = TRUE,
    digits = 2, digits.mean = 2, digits.sd = 2, digits.weight = 1,
    digits.tau2 = 4, digits.I2 = 1, digits.pval.Q = 4,
    lab.NA.effect = "Not estimable", lab.NA.weight = "0.0%",
    col.square = "#008000", col.square.lines = "#008000",
    col.diamond = "black", col.diamond.lines = "black",
    col.subgroup = "black", col.inside = "white",
    fontsize = 10, fs.hetstat = 9, fs.test.overall = 9,
    fs.test.subgroup = 9, fs.test.effect.subgroup = 9,
    fontfamily = "sans", plotwidth = "8cm", spacing = 1.05,
    colgap.forest.left = "5mm", colgap.forest.right = "5mm",
    addrows.below.overall = 3
  )
  # meta 8.5 concatenates both missing effect and missing CI placeholders in
  # the combined RevMan column. Collapse that duplicated display text only.
  for (name in grid::grid.ls(print = FALSE)$name) {
    grob <- grid::grid.get(name)
    if (inherits(grob, "text") && is.character(grob$label) &&
        any(grepl("Not estimableNot estimable", grob$label, fixed = TRUE))) {
      grid::grid.edit(name, label = gsub("Not estimableNot estimable", "Not estimable", grob$label, fixed = TRUE))
    }
  }
}

run_analysis <- function(data_dir, output_dir) {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  refs <- read.csv(file.path(data_dir, "reference_summary.csv"))
  readability <- read.csv(file.path(data_dir, "source_readability.csv"))
  audit <- studies <- pooled <- models <- list()
  add_check <- function(outcome, group, study, field, source, calculated, digits) {
    flag <- readability[readability$outcome == outcome & readability$group == group &
                          readability$field == field & study == "Pooled", ]
    if (nrow(flag) && flag$status == "uncertain") {
      status <- "source_unreadable_at_required_precision"
      note <- flag$note
    } else if (nrow(flag) && flag$status == "less_than") {
      status <- if (calculated < source) "match" else "mismatch"
      note <- flag$note
    } else if (is.na(source) && is.na(calculated)) {
      status <- "not_estimable_or_not_applicable"
      note <- ""
    } else {
      status <- if (!is.na(source) && !is.na(calculated) &&
                    abs(round(calculated, digits) - source) < 1e-7) "match" else "mismatch"
      note <- ""
    }
    audit[[length(audit) + 1L]] <<- data.frame(outcome, group, study, field, source,
      recalculated = calculated, digits, status, note, stringsAsFactors = FALSE)
  }
  for (i in seq_len(nrow(specifications))) {
    spec <- specifications[i, ]
    d <- read.csv(file.path(data_dir, paste0(spec$outcome, ".csv")))
    m <- fit_outcome(d, spec$measure)
    tf <- if (spec$measure == "OR") exp else identity
    w <- 100 * m$w.random / sum(m$w.random, na.rm = TRUE)
    sr <- data.frame(outcome = spec$outcome, subgroup = d$subgroup, study = d$study,
                     effect = tf(m$TE), lower = tf(m$lower), upper = tf(m$upper), weight = w)
    for (j in seq_len(nrow(d))) for (field in c("effect", "lower", "upper", "weight")) {
      add_check(spec$outcome, d$subgroup[j], d$study[j], field,
                d[[paste0("shown_", field)]][j], sr[[field]][j], if (field == "weight") 1 else 2)
    }
    groups <- c(m$subgroup.levels, "Overall")
    pr <- data.frame(outcome = spec$outcome, group = groups, measure = spec$measure,
      effect = tf(c(m$TE.random.w, m$TE.random)),
      lower = tf(c(m$lower.random.w, m$lower.random)),
      upper = tf(c(m$upper.random.w, m$upper.random)),
      I2 = 100 * c(m$I2.w, m$I2), tau2 = c(m$tau2.w, m$tau2),
      Q = c(m$Q.w, m$Q),
      Q_df = c(vapply(m$subgroup.levels, function(g) sum(d$subgroup == g & is.finite(m$TE)) - 1L, integer(1)), m$df.Q),
      Q_p = c(m$pval.Q.w, m$pval.Q),
      weight = c(vapply(m$subgroup.levels, function(g) sum(w[d$subgroup == g], na.rm = TRUE), numeric(1)), 100),
      group_Q = c(rep(NA_real_, length(m$subgroup.levels)), m$Q.b.random),
      group_p = c(rep(NA_real_, length(m$subgroup.levels)), m$pval.Q.b.random))
    for (j in seq_len(nrow(pr))) {
      ref <- refs[refs$outcome == spec$outcome & refs$group == pr$group[j], ]
      if (nrow(ref) != 1) stop("Missing reference row")
      for (field in c("effect", "lower", "upper", "I2", "tau2", "Q_p", "weight", "group_Q", "group_p")) {
        digits <- if (field %in% c("I2", "weight")) 1 else
          if (field %in% c("tau2", "Q_p", "group_p")) 4 else 2
        add_check(spec$outcome, pr$group[j], "Pooled", field, ref[[field]], pr[[field]][j], digits)
      }
    }
    render_plot(m, spec, file.path(output_dir, spec$filename))
    studies[[spec$outcome]] <- sr
    pooled[[spec$outcome]] <- pr
    models[[spec$outcome]] <- m
    message(spec$filename, " generated: ", length(m$studlab), " rows; pooled ",
            spec$measure, " ", sprintf("%.2f [%.2f, %.2f]", tf(m$TE.random), tf(m$lower.random), tf(m$upper.random)))
  }
  audit <- do.call(rbind, audit)
  write.csv(audit, file.path(output_dir, "verification.csv"), row.names = FALSE)
  write.csv(do.call(rbind, studies), file.path(output_dir, "study_results.csv"), row.names = FALSE)
  write.csv(do.call(rbind, pooled), file.path(output_dir, "pooled_results.csv"), row.names = FALSE)
  saveRDS(models, file.path(output_dir, "models.rds"))
  writeLines(capture.output(sessionInfo()), file.path(output_dir, "sessionInfo.txt"))
  message("Verification counts:")
  print(table(audit$status))
  if (any(audit$status == "mismatch")) warning("Source mismatches: see verification.csv")
  invisible(list(models = models, verification = audit))
}

if (sys.nframe() == 0L) {
  arg <- commandArgs()[grepl("^--file=", commandArgs())]
  script_dir <- if (length(arg)) dirname(normalizePath(sub("^--file=", "", arg[1]))) else getwd()
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) > 1L) stop("Usage: Rscript recreate_cochrane_plots.R [output_directory]")
  output_dir <- if (length(args)) args[1] else file.path(script_dir, "output")
  run_analysis(file.path(script_dir, "data"), output_dir)
}
