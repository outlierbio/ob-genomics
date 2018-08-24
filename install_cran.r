# CRAN official packages
install.packages(c(
  'devtools',
  'magrittr',
  'rsconnect',
  'tidyverse'
), repos='http://cran.r-project.org')

# Dev versions
library(devtools)
devtools::install_github('tidyverse/ggplot2')