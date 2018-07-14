library(DT)
library(plotly)
library(tidyverse)
library(tools)

source('database.r')
source('plots.r')
genes <- c('GAPDH', 'TP53', 'KRAS', 'MYC')
clinical_attributes <- c('gender', 'days_to_death', 'years_to_birth', 'vital status')
# clinical_attributes <- all_clinical_attributes()

ui <- fluidPage(
	titlePanel(title = 'Outlier bio genomics app', windowTitle = 'OB genomics'),
	tabsetPanel(type='tabs',

    tabPanel('Tissue',
      sidebarPanel(
        selectizeInput(inputId = 'gene_tissue', label = 'Select gene(s)',
                       choices = genes, selected = c('GAPDH', 'MYC', 'TP53'),
                       multiple = TRUE)
      ),
      mainPanel(
        h2('GTEx expression by tissue'),
        plotOutput('gtex_expr', height=400),
        h2('HPA expression by cell type'),
        plotOutput('hpa_prot', height=400),
        h2('GTEx vs HPA mRNA expression'),
        plotlyOutput('gtex_vs_hpa', height=400),
        h2('HPA protein vs mRNA expression'),
        plotlyOutput('hpa_prot_vs_expr', height=400)
      )
    ),

    tabPanel('Cancer',
      sidebarPanel(
        selectizeInput(inputId = 'gene_cancer', label = 'Select gene(s)',
                       choices = genes, selected = c('GAPDH', 'MYC', 'TP53'),
                       multiple = TRUE)
      ),
      mainPanel(
        h2('TCGA expression by cohort'),
        plotOutput('tcga_expr', height = 400),
        h2('TCGA mutations by cohort'),
        plotOutput('tcga_mut', height = 400)
      )
    ),
    
    tabPanel('Immuno-oncology',
      sidebarPanel(
        selectizeInput(inputId = 'gene_immune', label = 'Select gene(s)',
                       choices = genes, selected = c('GAPDH', 'MYC', 'TP53'),
                       multiple = TRUE),
        selectizeInput(inputId = 'component', label = 'Select fractional component(s)',
                       choices = all_components(), selected = c('Leukocyte Fraction', 'Stromal Fraction', 'TIL Regional Fraction'),
                       multiple = TRUE),
        selectizeInput(inputId = 'signature', label = 'Select signature(s)',
                       choices = all_signatures(), selected = c('Macrophages', 'T Cells CD8', 'T cells Regulatory Tregs'),
                       multiple = TRUE)
        
      ),
      mainPanel(
        h2('TCGA expression by immune subtype'),
        plotOutput('tcga_expr_immune_subtype', height=400),
        h2('TCGA expression by tumor composition'),
        plotOutput('tcga_expr_immune_composition', height=400),
        h2('TCGA expression by immune signature'),
        plotOutput('tcga_expr_signature_score', height=400)
      )
    ),

    tabPanel('Correlations',
             sidebarPanel(
               selectizeInput(inputId = 'gene_x', label = 'Select gene (x-axis)',
                              choices = genes, selected = 'GAPDH',
                              multiple = FALSE),
               selectizeInput(inputId = 'gene_y', label = 'Select gene (y-axis)',
                              choices = genes, selected = 'MYC',
                              multiple = FALSE),
               selectizeInput(inputId = 'clinical_attr',
                              label = 'Select clinical attribute (x-axis)',
                              choices = clinical_attributes, selected = 'gender',
                              multiple = FALSE)
               
             ),
             mainPanel(
               h2('TCGA expression vs clinical attribute'),
               plotlyOutput('tcga_expr_clinical', height=400),
               h2('TCGA expression correlations'),
               plotlyOutput('tcga_expr_pair', height=400),
               h2('GTEx expression correlations'),
               plotlyOutput('gtex_expr_pair', height=400),
               h2('HPA expression correlations'),
               plotlyOutput('hpa_expr_pair', height=400)
             )
    )
    
    
  )
)

server <- function(input, output, session) {

  tcga_expr <- reactive(tcga_expr_by_gene(input$gene_cancer))
  tcga_mut <- reactive(tcga_mut_by_gene(input$gene_cancer))
  tcga_expr_immune_subtype <- reactive(tcga_expr_immune_subtype_by_gene(input$gene_immune))
  tcga_expr_immune_composition <- reactive(tcga_expr_immune_composition_by_gene(input$gene_immune, input$component))
  tcga_expr_signature_score <- reactive(tcga_expr_signature_score_by_gene(input$gene_immune, input$signature))
  tcga_clinical <- reactive(tcga_clinical_by_attr(input$clinical_attr))
  tcga_expr_clinical <- reactive(tcga_expr_by_clinical_attr(input$gene_y, input$clinical_attr))
  tcga_expr_pair <- reactive(tcga_expr_pair_by_gene(input$gene_x, input$gene_y))
  gtex_expr <- reactive(gtex_expr_by_gene(input$gene_tissue))
  gtex_expr_pair <- reactive(gtex_expr_pair_by_gene(input$gene_x, input$gene_y))
  hpa_expr <- reactive(hpa_expr_by_gene(input$gene_tissue))
  hpa_expr_pair <- reactive(hpa_expr_pair_by_gene(input$gene_x, input$gene_y))
  hpa_prot <- reactive(hpa_prot_by_gene(input$gene_tissue))
  gtex_vs_hpa <- reactive(gtex_vs_hpa_by_gene(input$gene_tissue))
  hpa_prot_vs_expr <- reactive(hpa_prot_vs_expr_by_gene(input$gene_tissue))
  
	output$tcga_expr <- renderPlot({
	  tcga_expr() %>% plot_tcga_by_cohort
	})
	
	output$gtex_expr <- renderPlot({
	  gtex_expr() %>% plot_gtex_by_tissue
	})

	output$gtex_vs_hpa <- renderPlotly({
	    gtex_vs_hpa() %>%
	      plot_gtex_vs_hpa %>%
	      ggplotly
	})
	
	output$hpa_prot_vs_expr <- renderPlotly({
	  hpa_prot_vs_expr() %>%
      plot_hpa_prot_vs_expr %>%
	    ggplotly
	})
	
	output$hpa_prot <- renderPlot({
	  hpa_prot() %>% plot_hpa_by_cell_type
	})
	
	output$tcga_expr_immune_subtype <- renderPlot({
	  tcga_expr_immune_subtype() %>%
	    plot_tcga_expr_immune_subtype
	})
	
	output$tcga_expr_immune_composition <- renderPlot({
	  tcga_expr_immune_composition() %>%
	    plot_tcga_expr_immune_composition
	})
	
	output$tcga_expr_signature_score <- renderPlot({
	  tcga_expr_signature_score() %>%
	    plot_tcga_expr_signature_score
	})
	
	output$tcga_mut <- renderPlot({
	  tcga_mut() %>% plot_tcga_mutations
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
	    ggplotly
	})
	
	output$hpa_expr_pair <- renderPlotly({
	  hpa_expr_pair() %>%
	    plot_hpa_expr_pair(input$gene_x, input$gene_y) %>%
	    ggplotly()
	})
	
	# output$generated_list_input <- renderUI({
	#   selectizeInput(inputId = 'in4', label = 'Select from dynamically generated list',
	#                  choices = top_hits()$gene, multiple = FALSE)
	# })
	
}

shinyApp(ui = ui, server = server)

