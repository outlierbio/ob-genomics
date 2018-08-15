library(shiny)
library(tidyverse)

source("database.r")

server <- function(input, output, session) {
  tcga_expr <- reactive(
    tcga_expr_by_gene(input$gene_cancer, input$cohorts_cancer)
  )
  tcga_mut <- reactive(
    tcga_mut_by_gene(input$gene_cancer, input$cohorts_cancer)
  )
  tcga_expr_immune_subtype <- reactive(
    tcga_expr_immune_subtype_by_gene(input$gene_immune)
  )
  tcga_expr_immune_composition <- reactive(
    tcga_expr_immune_composition_by_gene(input$gene_immune, input$component)
  )
  tcga_expr_signature_score <- reactive(
    tcga_expr_signature_score_by_gene(input$gene_immune, input$signature)
  )
  tcga_clinical <- reactive(tcga_clinical_by_attr(input$clinical_attr))
  tcga_expr_clinical <- reactive(
    tcga_expr_by_clinical_attr(input$gene_y, input$clinical_attr)
  )
  tcga_expr_pair <- reactive(tcga_expr_pair_by_gene(input$gene_x, input$gene_y))
  gtex_expr <- reactive(gtex_expr_by_gene(input$gene_tissue))
  gtex_expr_pair <- reactive(gtex_expr_pair_by_gene(input$gene_x, input$gene_y))
  hpa_expr <- reactive(hpa_expr_by_gene(input$gene_tissue))
  hpa_expr_pair <- reactive(hpa_expr_pair_by_gene(input$gene_x, input$gene_y))
  hpa_prot <- reactive(hpa_prot_by_gene(input$gene_tissue))
  gtex_vs_hpa <- reactive(gtex_vs_hpa_by_gene(input$gene_tissue))
  hpa_prot_vs_expr <- reactive(hpa_prot_vs_expr_by_gene(input$gene_tissue))

  output$tcga_expr <- renderPlot({
    tcga_expr() %>% plot_tcga_by_cohort()
  })

  output$gtex_expr <- renderPlot({
    gtex_expr() %>% plot_gtex_by_tissue()
  })

  output$gtex_vs_hpa <- renderPlotly({
    gtex_vs_hpa() %>%
      plot_gtex_vs_hpa() %>%
      ggplotly()
  })

  output$hpa_prot_vs_expr <- renderPlotly({
    hpa_prot_vs_expr() %>%
      plot_hpa_prot_vs_expr() %>%
      ggplotly()
  })

  output$hpa_prot <- renderPlot({
    hpa_prot() %>% plot_hpa_by_cell_type()
  })

  output$tcga_expr_immune_subtype <- renderPlot({
    tcga_expr_immune_subtype() %>%
      plot_tcga_expr_immune_subtype()
  })

  output$tcga_expr_immune_composition <- renderPlot({
    tcga_expr_immune_composition() %>%
      plot_tcga_expr_immune_composition()
  })

  output$tcga_expr_signature_score <- renderPlot({
    tcga_expr_signature_score() %>%
      plot_tcga_expr_signature_score()
  })

  output$tcga_mut <- renderPlot({
    tcga_mut() %>% plot_tcga_mutations()
  })

  output$mutation_table <- renderDataTable(mutations())

  output$tcga_expr_pair <- renderPlotly({
    tcga_expr_pair() %>%
      plot_tcga_expr_pair(input$gene_x, input$gene_y) %>%
      ggplotly()
  })

  output$tcga_expr_clinical <- renderPlotly({
    tcga_expr_clinical() %>%
      plot_tcga_expr_by_clinical(input$gene_y, input$clinical_attr) %>%
      ggplotly()
  })

  output$gtex_expr_pair <- renderPlotly({
    gtex_expr_pair() %>%
      plot_gtex_expr_pair(input$gene_x, input$gene_y) %>%
      ggplotly()
  })

  output$hpa_expr_pair <- renderPlotly({
    hpa_expr_pair() %>%
      plot_hpa_expr_pair(input$gene_x, input$gene_y) %>%
      ggplotly()
  })
}
