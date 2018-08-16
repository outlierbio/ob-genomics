library(shiny)
library(DT)
library(dplyr)
library(plotly)
library(tidyverse)

source("database.r")
source("plots.r")

genes <- gene %>%
  filter(ensembl_id != "") %>%
  select(symbol) %>%
  arrange(symbol) %>%
  collect() %>%
  .$symbol

cohorts <- cohort %>%
  select(cohort_id) %>%
  arrange(cohort_id) %>%
  collect() %>%
  .$cohort_id

clinical_attributes <- all_clinical_attributes()

ui <- fluidPage(
  titlePanel(title = "Outlier bio genomics app", windowTitle = "OB genomics"),
  sidebarLayout(
    sidebarPanel(
      selectizeInput(
        inputId = "gene", label = "Select gene(s)",
        choices = genes, selected = "KRAS",
        multiple = FALSE
      ),
      width = 2
    ),
    mainPanel(
      tabsetPanel(
        type = "tabs",

        tabPanel(
          "Tissue",
          h2("GTEx expression by tissue"),
          plotOutput("gtex_expr", height = 400),
          h2("HPA expression by cell type"),
          plotOutput("hpa_prot", height = 400),
          h2("GTEx vs HPA mRNA expression"),
          plotlyOutput("gtex_vs_hpa", height = 400),
          h2("HPA protein vs mRNA expression"),
          plotlyOutput("hpa_prot_vs_expr", height = 400)
        ),

        tabPanel(
          "Cancer",
          sidebarPanel(
            selectizeInput(
              inputId = "cohorts_cancer", label = "Select tumor type(s)",
              choices = cohorts, multiple = TRUE,
              selected = c("BRCA", "LUAD", "SKCM")
            )
          ),
          mainPanel(
            h2("TCGA expression by cohort"),
            plotOutput("tcga_expr", height = 400),
            h2("TCGA mutations by cohort"),
            plotOutput("tcga_mut", height = 400)
          )
        ),

        tabPanel(
          "Immuno-oncology",
          sidebarPanel(
            selectizeInput(
              inputId = "cohort_immune", label = "Select tumor type(s)",
              choices = cohorts, selected = c("BRCA", "LUAD", "SKCM"),
              multiple = TRUE
            ),
            selectizeInput(
              inputId = "component", label = "Select fractional component(s)",
              choices = all_components(),
              selected = c(
                "Leukocyte Fraction",
                "Stromal Fraction",
                "TIL Regional Fraction"
              ),
              multiple = TRUE
            ),
            selectizeInput(
              inputId = "signature",
              label = "Select signature(s)",
              choices = all_signatures(),
              selected = c(
                "Macrophages",
                "T Cells CD8",
                "T cells Regulatory Tregs"
              ),
              multiple = TRUE
            )
          ),
          mainPanel(
            h2("TCGA expression by immune subtype"),
            plotOutput("tcga_expr_immune_subtype", height = 400),
            h2("TCGA expression by tumor composition"),
            plotOutput("tcga_expr_immune_composition", height = 400),
            h2("TCGA expression by immune signature"),
            plotOutput("tcga_expr_signature_score", height = 400)
          )
        ),

        tabPanel(
          "Correlations",
          sidebarPanel(
            selectInput(
              inputId = "gene_y",
              label = "Select gene (y-axis)",
              choices = genes,
              selected = "MYC",
              multiple = FALSE,
              selectize = FALSE
            ),
            selectInput(
              inputId = "clinical_attr",
              label = "Select clinical attribute (x-axis)",
              choices = clinical_attributes,
              selected = "days_to_death",
              multiple = FALSE,
              selectize = FALSE
            )
          ),
          mainPanel(
            h2("TCGA expression vs clinical attribute"),
            plotlyOutput("tcga_expr_clinical", height = 400),
            h2("TCGA expression correlations"),
            plotlyOutput("tcga_expr_pair", height = 400),
            h2("GTEx expression correlations"),
            plotlyOutput("gtex_expr_pair", height = 400),
            h2("HPA expression correlations"),
            plotlyOutput("hpa_expr_pair", height = 400)
          )
        )
      )
    )
  )
)
