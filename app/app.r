library(DT)
library(plotly)
library(tidyverse)
library(tools)

source('database.r')
source('plots.r')
genes <- c('GAPDH', 'TP53', 'KRAS', 'MYC')

ui <- fluidPage(
	titlePanel(title = 'Celsius genomics app', windowTitle = 'Celsius genomics'),
	tabsetPanel(type='tabs',

    tabPanel('Tissue',
      sidebarPanel(
        selectizeInput(inputId = 'gene', label = 'Select gene(s)',
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
        selectizeInput(inputId = 'gene', label = 'Select gene(s)',
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
        selectizeInput(inputId = 'gene', label = 'Select gene(s)',
                       choices = genes, selected = c('GAPDH', 'MYC', 'TP53'),
                       multiple = TRUE)
      ),
      mainPanel(
        h2('TCGA expression by immune subtype'),
        plotOutput('expr_immune_subtype', height=400)
      )
    )
    
  )
)

server <- function(input, output, session) {

  tcga_expr <- reactive(tcga_expr_by_gene(input$gene))
  gtex_expr <- reactive(gtex_expr_by_gene(input$gene))
  hpa_expr <- reactive(hpa_expr_by_gene(input$gene))
  hpa_prot <- reactive(hpa_prot_by_gene(input$gene))
  tcga_mut <- reactive(tcga_mut_by_gene(input$gene))
  
	output$tcga_expr <- renderPlot({
	  tcga_expr() %>% plot_tcga_by_cohort
	})
	
	output$gtex_expr <- renderPlot({
	  gtex_expr() %>% plot_gtex_by_tissue
	})

	output$gtex_vs_hpa <- renderPlotly({
	    gtex_vs_hpa_by_gene(input$gene) %>%
	      plot_gtex_vs_hpa %>%
	      ggplotly
	})
	
	output$hpa_prot_vs_expr <- renderPlotly({
	  hpa_prot_vs_expr_by_gene(input$gene) %>%
      plot_hpa_prot_vs_expr %>%
	    ggplotly
	})
	
	output$hpa_prot <- renderPlot({
	  hpa_prot() %>% plot_hpa_by_cell_type
	})
	
	output$expr_immune_subtype <- renderPlot({
	  expr_immune_subtype_by_gene(input$gene) %>%
	    plot_expr_by_immune_subtype
	})
	
	output$tcga_mut <- renderPlot({
	  tcga_mut() %>% plot_tcga_mutations
	})
	
	output$mutation_table <- renderDataTable(mutations())
	
	# output$generated_list_input <- renderUI({
	#   selectizeInput(inputId = 'in4', label = 'Select from dynamically generated list',
	#                  choices = top_hits()$gene, multiple = FALSE)
	# })
	
}

shinyApp(ui = ui, server = server)

