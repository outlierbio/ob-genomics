library(DT)
library(plotly)
library(tidyverse)
library(tools)

source('database.r')
source('plots.r')
genes <- c('GAPDH', 'TP53', 'KRAS', 'MYC')

ui <- fluidPage(
	titlePanel(title = 'Celsius public genomics app', windowTitle = 'Genomics app'),
	tabsetPanel(type='tabs',

	  tabPanel('Gene',
       sidebarPanel(
         selectizeInput(inputId = 'gene', label = 'Select gene(s)',
                        choices = genes, selected = c('GAPDH', 'MYC', 'TP53'),
                        multiple = TRUE)
       ),
       mainPanel(
         h2('TCGA expression by cohort'),
         plotOutput('tcga_expr', height = 400),
         h2('TCGA mutations by cohort'),
         plotOutput('tcga_mut', height = 400),
         h2('TCGA expression by immune subtype'),
         plotOutput('expr_immune_subtype', height=400),
         h2('GTEx expression by tissue'),
         plotOutput('gtex_expr', height=400),
         h2('HPA expression by cell type'),
         plotOutput('hpa_prot', height=400),
         h2('GTEx vs HPA mRNA expression'),
         plotlyOutput('gtex_vs_hpa', height=400),
         h2('HPA protein vs mRNA expression'),
         plotlyOutput('hpa_prot_vs_expr', height=400)
       )
    )
# 
# 	  tabPanel('Correlations',
#        sidebarPanel(
#          selectizeInput(inputId = 'in2', label = 'Select a gene',
#                         choices = genes, selected = c('GAPDH'), multiple = FALSE),
#          selectizeInput(inputId = 'in3', label = 'Select another variable',
#                         choices = c('val1', 'val2'), selected = 'val1', multiple = FALSE)
#          uiOutput('generated_list_input'),
#          sliderInput("threshold", "A threshold",  
#                      min = min(df$var3), max = max(df$var3, value = 1)
#        ),
#        mainPanel(
#          tabsetPanel(type='pills',
#             tabPanel('A table',         
#               dataTableOutput('table1')
#             ),
#             tabPanel('Interactive figure',
#                plotlyOutput('fig2', height = 700),
#                h1(' ')
#             )
#          )
#        )
#     )
  )
)

server <- function(input, output, session) {

  tcga_expr <- reactive({
    sample_expression %>%
      filter(symbol %in% input$gene) %>%
      collect %>%
      spread(unit, value)
  })

  gtex_expr <- reactive({
    tissue_expression %>%
      filter(symbol %in% input$gene) %>%
      collect %>%
      spread(unit, value)
  })
  
  hpa_prot <- reactive({
    cell_type_protein %>%
      filter(symbol %in% input$gene) %>%
      collect %>%
      spread(unit, value) %>%
      mutate(
        `detection level` = factor(`detection level`,
                                   levels=c('Not detected', 'Low', 'Medium', 'High')))
  })
  
  tcga_mut <- reactive({
    sample_mutation %>%
      filter(symbol %in% input$gene) %>%
      collect %>%
      spread(data_type, value)
  })
  
	output$tcga_expr <- renderPlot({
	  p <- tcga_expr() %>%
      plot_tcga_by_cohort  # ggplot (flat)
	  p
	  # ggplotly(p, tooltip='text') %>%  # Convert to plotly with labeled tooltip
	  #   layout(margin = list(b=100))  # Adjust plot margins
	})
	
	output$gtex_expr <- renderPlot({
	  gtex_expr() %>% plot_gtex_by_tissue
	})

	output$gtex_vs_hpa <- renderPlotly({
	  hpa <- hpa_expr() %>% 
	    select(tissue, subtype, symbol, HPA = TPM)
	  p <- gtex_expr() %>%
	    select(tissue, subtype, symbol, GTEx = median_tpm) %>%
	    inner_join(hpa) %>%
	    plot_gtex_vs_hpa
	  ggplotly(p)
	})
	
	output$hpa_prot_vs_expr <- renderPlotly({
	  prot <- hpa_prot() %>%
	    select(tissue, subtype, symbol, cell_type_id, `detection level`)
	  p <- hpa_expr() %>%
	    select(tissue, subtype, symbol, TPM) %>%
	    inner_join(prot) %>%
      plot_hpa_prot_vs_expr
	})
	
	output$hpa_prot <- renderPlot({
	  hpa_prot() %>% plot_hpa_by_cell_type
	})
	
	output$expr_immune_subtype <- renderPlot({
	  tcga_expr() %>%
	    inner_join(patient_immune_subtype %>% collect) %>%
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

