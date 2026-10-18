# RStudio: open this folder as your project, then run this script.
# Install once if needed: install.packages("readxl")
library(readxl)

# Rscript also works from another folder.
script_arg <- grep("^--file=", commandArgs(FALSE), value = TRUE)
data_dir <- if (length(script_arg)) {
  dirname(normalizePath(sub("^--file=", "", script_arg[1])))
} else {
  getwd()
}

files <- list.files(data_dir, pattern = "^[0-9]{2}_.*\\.xlsx$", full.names = TRUE)
if (length(files) != 12L) stop("Set your working directory to the folder containing the 12 Excel files.")

# Each object is the compact data sheet from one outcome file.
outcomes <- setNames(
  lapply(files, function(f) {
    d <- read_excel(f, sheet = "data")
    # Keep entirely blank numeric columns numeric too.
    numeric_cols <- intersect(c("n_csp", "mean_csp", "sd_csp", "n_biv",
                                "mean_biv", "sd_biv", "event_csp", "event_biv"), names(d))
    d[numeric_cols] <- lapply(d[numeric_cols], as.numeric)
    d
  }),
  sub("^[0-9]{2}_", "", tools::file_path_sans_ext(basename(files)))
)

# Examples:
qrs <- outcomes$qrs_duration
mortality <- outcomes$all_cause_mortality
# View(qrs)
# View(mortality)

# Optional: read source notes or non-mean statistics from the same file.
qrs_notes <- read_excel(file.path(data_dir, "04_qrs_duration.xlsx"), sheet = "review_notes")

# Data with complete numeric inputs can be inspected this way:
qrs_complete <- qrs[qrs$has_inputs, ]
# This is NOT an automatic analysis selection. Review analysis_use, cohort_id,
# measurement, timepoint, units and review_notes before pooling.
# In particular, LEVEL-AT and CONSYST-CRT share participants.

cat("Loaded", length(outcomes), "separate outcome files containing",
    sum(vapply(outcomes, nrow, integer(1))), "primary rows.\n")
