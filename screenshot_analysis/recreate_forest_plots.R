#!/usr/bin/env Rscript
# Reconstruct the supplied screenshots from their printed arm-level values.
# No previous Excel-workbook data are used. See README.md for source limitations.

if (!requireNamespace("metafor", quietly = TRUE)) {
  install.packages("metafor", repos = "https://cloud.r-project.org")
}
if (!requireNamespace("metafor", quietly = TRUE)) stop("metafor installation failed")

plot_specifications <- data.frame(
  outcome = c("hf_all", "nyha", "hf_subset", "lvesv", "procedural", "qrs", "threshold"),
  title = c("Heart failure - all studies", "NYHA functional class",
            "Heart failure - subset shown", "Left ventricular end-systolic volume (LVESV)",
            "Procedural complications", "QRS duration", "Pacing threshold at implant"),
  type = c("binary", "continuous", "binary", "continuous", "binary", "continuous", "continuous"),
  filename = c("01_heart_failure_all.png", "02_nyha.png", "03_heart_failure_subset.png",
               "06_lvesv.png", "07_procedural_complications.png", "08_qrs_duration.png",
               "09_threshold_implant.png"),
  stringsAsFactors = FALSE
)

estimate_effects <- function(d, type) {
  numeric_names <- if (type == "binary") {
    c("event_csp", "nonevent_csp", "event_biv", "nonevent_biv")
  } else c("n_csp", "mean_csp", "sd_csp", "n_biv", "mean_biv", "sd_biv")
  if (!all(c("study", numeric_names) %in% names(d))) stop("Input columns are missing")
  if (any(!is.finite(as.matrix(d[numeric_names])))) stop("Missing/non-finite arm data")
  if (type == "binary") {
    counts <- as.matrix(d[numeric_names])
    if (any(counts < 0 | counts != floor(counts))) stop("Invalid event/non-event count")
    if (any(d$event_csp + d$nonevent_csp == 0 | d$event_biv + d$nonevent_biv == 0)) {
      stop("A study arm has no participants")
    }
    # bi and di are NON-EVENT counts, not group totals. This is required to
    # reproduce the printed RRs. Retain double-zero studies as in the source.
    es <- metafor::escalc(
      measure = "RR", ai = d$event_csp, bi = d$nonevent_csp,
      ci = d$event_biv, di = d$nonevent_biv,
      add = 0.5, to = "only0", drop00 = FALSE
    )
  } else {
    if (any(d$n_csp < 2 | d$n_biv < 2 | d$n_csp != floor(d$n_csp) |
            d$n_biv != floor(d$n_biv) | d$sd_csp < 0 | d$sd_biv < 0)) {
      stop("Invalid continuous sample size or standard deviation")
    }
    # HO pools the two within-study variances, matching the supplied figures.
    es <- metafor::escalc(
      measure = "MD", m1i = d$mean_csp, sd1i = d$sd_csp, n1i = d$n_csp,
      m2i = d$mean_biv, sd2i = d$sd_biv, n2i = d$n_biv, vtype = "HO"
    )
  }
  if (any(!is.finite(es$yi) | !is.finite(es$vi) | es$vi <= 0)) stop("Non-estimable study")
  model <- metafor::rma(yi = es$yi, vi = es$vi, method = "REML", test = "z")
  z <- qnorm(0.975)
  d$yi <- es$yi
  d$vi <- es$vi
  d$lower_analysis <- es$yi - z * sqrt(es$vi)
  d$upper_analysis <- es$yi + z * sqrt(es$vi)
  d$weight <- as.numeric(stats::weights(model))
  backtransform <- if (type == "binary") exp else identity
  d$effect <- backtransform(d$yi)
  d$lower <- backtransform(d$lower_analysis)
  d$upper <- backtransform(d$upper_analysis)
  for (item in c("effect", "lower", "upper")) {
    if (any(abs(round(d[[item]], 2) - d[[paste0("shown_", item)]]) > 1e-7)) {
      stop("A study's ", item, " does not reproduce the screenshot; check transcription")
    }
  }
  list(data = d, model = model)
}

number <- function(x) format(x, trim = TRUE, scientific = FALSE, digits = 6)
p_text <- function(p) if (p < 0.001) "< 0.001" else paste0("= ", sprintf("%.3f", p))
effect_text <- function(x, lo, hi) sprintf("%.2f [%.2f, %.2f]", x, lo, hi)

draw_plot <- function(result, spec, path) {
  d <- result$data
  m <- result$model
  binary <- spec$type == "binary"
  k <- nrow(d)
  width <- 16
  height <- max(5.1, 3.8 + 0.255 * k)
  grDevices::png(path, width = width, height = height, units = "in", res = 220,
                type = if (capabilities("cairo")) "cairo" else getOption("bitmapType"),
                bg = "white")
  on.exit(grDevices::dev.off(), add = TRUE)
  grid::grid.newpage()
  text <- function(label, x, y, size = 10.5, bold = FALSE, just = "centre", colour = "#151515") {
    grid::grid.text(label, x = x / width, y = y / height, just = just,
                   gp = grid::gpar(fontfamily = "sans", fontsize = size,
                                   fontface = if (bold) "bold" else "plain", col = colour))
  }
  line <- function(x0, y0, x1, y1, colour = "#252525", lwd = 0.8, lty = 1) {
    grid::grid.lines(x = c(x0, x1) / width, y = c(y0, y1) / height,
                    gp = grid::gpar(col = colour, lwd = lwd, lty = lty))
  }
  text(spec$title, width / 2, height - 0.28, size = 17, bold = TRUE)
  text("Conduction system pacing (CSP) versus biventricular pacing (BiV)",
       width / 2, height - 0.59, size = 11)
  header_group <- height - 0.99
  header_row <- height - 1.23
  text("Study", 0.25, header_row, bold = TRUE, just = "left")
  if (binary) {
    x_columns <- c(4.15, 5.0, 6.0, 6.85)
    header_columns <- c("Events", "No events", "Events", "No events")
    value_columns <- c("event_csp", "nonevent_csp", "event_biv", "nonevent_biv")
    group_centres <- c(mean(x_columns[1:2]), mean(x_columns[3:4]))
  } else {
    x_columns <- c(3.45, 4.15, 4.85, 5.5, 6.15, 6.85)
    header_columns <- rep(c("N", "Mean", "SD"), 2)
    value_columns <- c("n_csp", "mean_csp", "sd_csp", "n_biv", "mean_biv", "sd_biv")
    group_centres <- c(mean(x_columns[1:3]), mean(x_columns[4:6]))
  }
  for (j in seq_along(x_columns)) text(header_columns[j], x_columns[j], header_row, bold = TRUE)
  text("CSP", group_centres[1], header_group, bold = TRUE, size = 11)
  text("BiV", group_centres[2], header_group, bold = TRUE, size = 11)
  chart_left <- 7.5
  chart_right <- 11.65
  text(if (binary) "Risk ratio" else "Mean difference", mean(c(chart_left, chart_right)), header_row, bold = TRUE)
  text(paste0(if (binary) "RR" else "MD", " with 95% CI"), 13.45, header_row, bold = TRUE)
  text("Weight (%)", 15.45, header_row, bold = TRUE)
  line(0.2, height - 1.43, 15.8, height - 1.43, colour = "#888888")

  y <- height - 1.66 - (seq_len(k) - 1) * 0.255
  y_overall <- tail(y, 1) - 0.45
  y_axis <- y_overall - 0.35
  # Full confidence intervals are shown; no clipping or arrow truncation.
  bounds <- range(c(d$lower_analysis, d$upper_analysis, 0, m$ci.lb, m$ci.ub))
  if (binary) {
    candidate_ticks <- 10^seq(-6, 6)
    ticks <- candidate_ticks[log(candidate_ticks) >= bounds[1] & log(candidate_ticks) <= bounds[2]]
    if (length(ticks) < 3) ticks <- c(0.1, 0.5, 1, 2, 5, 10)
    tick_positions <- log(ticks)
    bounds <- range(c(bounds, tick_positions))
  } else {
    ticks <- pretty(bounds, n = 5)
    tick_positions <- ticks
    bounds <- range(c(bounds, ticks))
  }
  padding <- diff(bounds) * 0.035
  bounds <- bounds + c(-padding, padding)
  chart_x <- function(value) chart_left + (value - bounds[1]) / diff(bounds) * (chart_right - chart_left)
  line(chart_x(0), y_overall - 0.12, chart_x(0), y[1] + 0.16, colour = "#B6B6B6", lwd = 0.8)
  for (i in seq_len(k)) {
    text(d$study[i], 0.25, y[i], just = "left")
    for (j in seq_along(value_columns)) text(number(d[[value_columns[j]]][i]), x_columns[j], y[i])
    line(chart_x(d$lower_analysis[i]), y[i], chart_x(d$upper_analysis[i]), y[i], colour = "#438A94", lwd = 1)
    side <- 0.20 * sqrt(d$weight[i] / max(d$weight))
    grid::grid.rect(x = chart_x(d$yi[i]) / width, y = y[i] / height,
                    width = grid::unit(side, "in"), height = grid::unit(side, "in"),
                    gp = grid::gpar(fill = "#087F8C", col = NA))
    text(effect_text(d$effect[i], d$lower[i], d$upper[i]), 13.45, y[i])
    text(sprintf("%.2f", d$weight[i]), 15.45, y[i])
  }
  transform <- if (binary) exp else identity
  text("Overall (random effects)", 0.25, y_overall, bold = TRUE, just = "left", size = 11)
  grid::grid.polygon(x = chart_x(c(m$ci.lb, as.numeric(m$b), m$ci.ub, as.numeric(m$b))) / width,
                     y = c(y_overall, y_overall + 0.075, y_overall, y_overall - 0.075) / height,
                     gp = grid::gpar(fill = "#111111", col = "#111111"))
  text(effect_text(transform(as.numeric(m$b)), transform(m$ci.lb), transform(m$ci.ub)),
       13.45, y_overall, bold = TRUE)
  text("100.00", 15.45, y_overall, bold = TRUE)
  line(chart_left, y_axis, chart_right, y_axis)
  for (i in seq_along(ticks)) {
    x <- chart_x(tick_positions[i])
    line(x, y_axis, x, y_axis - 0.055)
    text(number(ticks[i]), x, y_axis - 0.17, size = 9)
  }
  text(if (binary) "Risk ratio (CSP / BiV), logarithmic axis" else "Mean difference (CSP - BiV)",
       mean(c(chart_left, chart_right)), y_axis - 0.37, size = 9)
  text(sprintf("Heterogeneity: tau² = %.2f; I² = %.2f%%; H² = %.2f", m$tau2, m$I2, m$H2),
       0.25, y_axis - 0.10, just = "left", size = 9.5)
  text(sprintf("Q(%d) = %.2f; p %s", m$k - 1, m$QE, p_text(m$QEp)),
       0.25, y_axis - 0.35, just = "left", size = 9.5)
  text(sprintf("Overall effect: z = %.2f; p %s", m$zval, p_text(m$pval)),
       0.25, y_axis - 0.60, just = "left", size = 9.5)
  method_note <- if (binary) {
    "REML; normal 95% CIs. Source reproduction: non-event counts; 0.5 correction in zero-cell studies, including double-zero studies."
  } else "REML; normal 95% CIs. Source reproduction uses the pooled within-study SD and the printed means, SDs, and sample sizes."
  text(method_note, width / 2, 0.40, size = 8.5, colour = "#444444")
}

run_all <- function(data_dir, output_dir) {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  reference <- read.csv(file.path(data_dir, "reference_summary.csv"))
  summaries <- effects <- audits <- models <- list()
  for (i in seq_len(nrow(plot_specifications))) {
    spec <- plot_specifications[i, ]
    d <- read.csv(file.path(data_dir, paste0(spec$outcome, ".csv")), stringsAsFactors = FALSE)
    result <- estimate_effects(d, spec$type)
    m <- result$model
    transform <- if (spec$type == "binary") exp else identity
    current <- data.frame(
      outcome = spec$outcome, studies = m$k, measure = if (spec$type == "binary") "RR" else "MD",
      effect = transform(as.numeric(m$b)), lower = transform(m$ci.lb), upper = transform(m$ci.ub),
      tau2 = m$tau2, I2 = m$I2, H2 = m$H2, Q = m$QE, Q_df = m$k - 1,
      Q_p = m$QEp, z = m$zval, effect_p = m$pval
    )
    ref <- reference[reference$outcome == spec$outcome, ]
    if (nrow(ref) != 1 || ref$studies != m$k) stop("Reference study count mismatch")
    for (field in c("effect", "lower", "upper", "tau2", "I2", "H2", "Q", "z")) {
      audits[[length(audits) + 1L]] <- data.frame(
        outcome = spec$outcome, study = "Overall", field = field,
        source = ref[[field]], recalculated = current[[field]],
        difference = current[[field]] - ref[[field]],
        matches_printed_precision = abs(round(current[[field]], 2) - ref[[field]]) < 1e-7
      )
    }
    if (any(abs(round(unlist(current[c("effect", "lower", "upper")]), 2) -
                unlist(ref[c("effect", "lower", "upper")])) > 1e-7)) stop("Pooled result mismatch")
    for (field in c("effect", "lower", "upper", "weight")) {
      audits[[length(audits) + 1L]] <- data.frame(
        outcome = spec$outcome, study = result$data$study, field = field,
        source = result$data[[paste0("shown_", field)]], recalculated = result$data[[field]],
        difference = result$data[[field]] - result$data[[paste0("shown_", field)]],
        matches_printed_precision = abs(round(result$data[[field]], 2) - result$data[[paste0("shown_", field)]]) < 1e-7
      )
    }
    draw_plot(result, spec, file.path(output_dir, spec$filename))
    result$data$outcome <- spec$outcome
    effects[[spec$outcome]] <- result$data[c("outcome", "study", "yi", "vi", "effect", "lower", "upper", "weight")]
    summaries[[spec$outcome]] <- current
    models[[spec$outcome]] <- m
    message(spec$filename, ": ", m$k, " studies; ", effect_text(current$effect, current$lower, current$upper))
  }
  # The user supplied nine images; images 4 and 5 repeat images 1 and 2.
  for (pair in list(c("01_heart_failure_all.png", "04_heart_failure_all_repeat.png"),
                    c("02_nyha.png", "05_nyha_repeat.png"))) {
    if (!file.copy(file.path(output_dir, pair[1]), file.path(output_dir, pair[2]), overwrite = TRUE)) stop("Duplicate-image copy failed")
  }
  write.csv(do.call(rbind, summaries), file.path(output_dir, "pooled_results.csv"), row.names = FALSE)
  write.csv(do.call(rbind, effects), file.path(output_dir, "study_results.csv"), row.names = FALSE)
  write.csv(do.call(rbind, audits), file.path(output_dir, "reproduction_audit.csv"), row.names = FALSE)
  saveRDS(models, file.path(output_dir, "models.rds"))
  writeLines(capture.output(sessionInfo()), file.path(output_dir, "sessionInfo.txt"))
  message("Created nine separate PNG files (seven distinct plots) in ", normalizePath(output_dir))
  invisible(do.call(rbind, summaries))
}

if (sys.nframe() == 0L) {
  script_arg <- commandArgs()[grepl("^--file=", commandArgs())]
  script_dir <- if (length(script_arg)) dirname(normalizePath(sub("^--file=", "", script_arg[1]))) else getwd()
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) > 1L) stop("Usage: Rscript recreate_forest_plots.R [output_directory]")
  output_dir <- if (length(args)) args[1] else file.path(script_dir, "output")
  run_all(file.path(script_dir, "data"), output_dir)
}
