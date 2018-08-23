library(shiny)
library(tidyverse)

source("database.r")

server <- function(input, output, session) {
  # Pack up reactive functions to keep namespace clean
  data_fns <- list()
  data_fns$tcga_expr <- reactive(
    tcga_expr_by_gene(input$gene, input$cohort)
  )
  data_fns$tcga_mut <- reactive(
    tcga_mut_by_gene(input$gene, input$cohort)
  )
  data_fns$tcga_expr_immune_subtype <- reactive(
    tcga_expr_immune_subtype_by_gene(input$gene, input$cohort)
  )
  data_fns$tcga_expr_immune_composition <- reactive(
    tcga_expr_immune_composition_by_gene(
      input$gene,
      input$component,
      input$cohort
    )
  )
  data_fns$tcga_expr_signature_score <- reactive(
    tcga_expr_signature_score_by_gene(
      input$gene,
      input$signature,
      input$cohort
    )
  )
  data_fns$tcga_isoform <- reactive(tcga_isoform_by_gene(input$gene, input$cohort))
  data_fns$tcga_clinical <- reactive(tcga_clinical_by_attr(input$clinical_attr))
  data_fns$tcga_expr_clinical <- reactive(
    tcga_expr_by_clinical_attr(
      input$gene_y,
      input$clinical_attr,
      input$cohort
    )
  )
  data_fns$tcga_expr_pair <- reactive(
    tcga_expr_pair_by_gene(input$gene, input$gene_y, input$cohort)
  )
  data_fns$gtex_expr <- reactive(gtex_expr_by_gene(input$gene))
  data_fns$gtex_isoform <- reactive(gtex_isoform_by_gene(input$gene))
  data_fns$gtex_expr_pair <- reactive(gtex_expr_pair_by_gene(input$gene, input$gene_y))
  data_fns$hpa_expr <- reactive(hpa_expr_by_gene(input$gene))
  data_fns$hpa_expr_pair <- reactive(hpa_expr_pair_by_gene(input$gene, input$gene_y))
  data_fns$hpa_prot <- reactive(hpa_prot_by_gene(input$gene))
  data_fns$gtex_vs_hpa <- reactive(gtex_vs_hpa_by_gene(input$gene))
  data_fns$hpa_prot_vs_expr <- reactive(hpa_prot_vs_expr_by_gene(input$gene))

  output$tcga_expr <- renderPlot({
    data_fns$tcga_expr() %>% plot_tcga_by_cohort()
  })
  
  output$tcga_isoform <- renderPlot({
    data_fns$tcga_isoform() %>% plot_tcga_isoform_by_cohort()
  })
  
  output$gtex_expr <- renderPlot({
    data_fns$gtex_expr() %>% plot_gtex_by_tissue()
  })
  
  output$gtex_isoform <- renderPlot({
    data_fns$gtex_isoform() %>% plot_gtex_isoform_by_tissue()
  })
  output$gtex_vs_hpa <- renderPlotly({
    data_fns$gtex_vs_hpa() %>%
      plot_gtex_vs_hpa() %>%
      ggplotly() %>%
      layout(margin = list(b=100, l=100))
  })

  output$hpa_prot_vs_expr <- renderPlotly({
    data_fns$hpa_prot_vs_expr() %>%
      plot_hpa_prot_vs_expr() %>%
      ggplotly() %>%
      layout(margin = list(b=100, l=100))
  })

  output$hpa_prot <- renderPlot({
    data_fns$hpa_prot() %>% plot_hpa_by_cell_type()
  })

  output$tcga_expr_immune_subtype <- renderPlot({
    data_fns$tcga_expr_immune_subtype() %>%
      plot_tcga_expr_immune_subtype()
  })

  output$tcga_expr_immune_composition <- renderPlot({
    data_fns$tcga_expr_immune_composition() %>%
      plot_tcga_expr_immune_composition()
  })

  output$tcga_expr_signature_score <- renderPlot({
    data_fns$tcga_expr_signature_score() %>%
      plot_tcga_expr_signature_score()
  })

  output$tcga_mut <- renderPlot({
    data_fns$tcga_mut() %>% plot_tcga_mutations()
  })

  output$mutation_table <- renderDataTable({
    data_fns$tcga_mut() %>%
      select(patient_id, symbol, cohort_id, cohort=name, `variant type`,
             `variant classification`, `protein change`=HGVSp_Short)
    })

  output$tcga_expr_pair <- renderPlotly({
    data_fns$tcga_expr_pair() %>%
      plot_tcga_expr_pair(input$gene, input$gene_y) %>%
      ggplotly()
  })

  output$tcga_expr_clinical <- renderPlotly({
    data_fns$tcga_expr_clinical() %>%
      plot_tcga_expr_by_clinical(input$gene_y, input$clinical_attr) %>%
      ggplotly()
  })

  output$gtex_expr_pair <- renderPlotly({
    data_fns$gtex_expr_pair() %>%
      plot_gtex_expr_pair(input$gene, input$gene_y) %>%
      ggplotly()
  })

  output$hpa_expr_pair <- renderPlotly({
    data_fns$hpa_expr_pair() %>%
      plot_hpa_expr_pair(input$gene, input$gene_y) %>%
      ggplotly()
  })
}
