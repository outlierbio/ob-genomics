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
         selectizeInput(inputId = 'gene', label = 'Select a gene',
                        choices = genes, selected = 'GAPDH',
                        multiple = TRUE)
       ),
       mainPanel(
         h1('TCGA expression by cohort'),
         plotOutput('tcga_expr', height = 400),
         h1('GTEx expression by tissue'),
         plotOutput('gtex_expr', height=400)
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
      filter(symbol %in% input$gene, unit == 'median_tpm') %>%
      collect %>%
      spread(unit, value)
  })
  
	output$tcga_expr <- renderPlot({
	  p <- tcga_expr() %>%
      plot_tcga_by_cohort()  # ggplot (flat)
	  p
	  # ggplotly(p, tooltip='text') %>%  # Convert to plotly with labeled tooltip
	  #   layout(margin = list(b=100))  # Adjust plot margins
	})
	
	output$gtex_expr <- renderPlot({
	  p <- gtex_expr() %>%
	    plot_gtex_by_tissue()  # ggplot (flat)
	  p
	  # ggplotly(p, tooltip='text') %>%  # Convert to plotly with labeled tooltip
	  #   layout(margin = list(b=100))  # Adjust plot margins
	})

	# output$table1 <- renderDataTable(top_hits())
	
	# output$generated_list_input <- renderUI({
	#   selectizeInput(inputId = 'in4', label = 'Select from dynamically generated list',
	#                  choices = top_hits()$gene, multiple = FALSE)
	# })
	
}

shinyApp(ui = ui, server = server)

