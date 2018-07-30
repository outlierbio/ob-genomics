library(DT)
library(tidyverse)
library(plotly)


# Load data
df <- readRDS('data.rds')
genes <- c('GAPDH', 'TP53', 'KRAS', 'MYC')


plot_something <- function(df) {
  ggplot(df, aes(x=some_variable, y=another_var, color=third_var)) + 
    geom_point(aes(text=var_labels)) +
    theme_bw() +
    labs(
      x = '',
      y = 'Y-axis'
    )
}


ui <- fluidPage(
	titlePanel(title = 'Client data viewer', windowTitle = 'Data viewer'),
	tabsetPanel(type='tabs',

	  tabPanel('Tab 1',
       sidebarPanel(
         selectizeInput(inputId = 'in1', label = 'Select a gene',
                        choices = genes, selected = 'GAPDH',
                        multiple = TRUE)
       ),
       mainPanel(
         h3('This by that'),
         plotOutput('fig1', height = 700),
         h1(' ')
       )
    ),

	  tabPanel('Tab 2',
       sidebarPanel(
         selectizeInput(inputId = 'in2', label = 'Select a gene',
                        choices = genes, selected = c('GAPDH'), multiple = FALSE),
         selectizeInput(inputId = 'in3', label = 'Select another variable',
                        choices = c('val1', 'val2'), selected = 'val1', multiple = FALSE)
         uiOutput('generated_list_input'),
         sliderInput("threshold", "A threshold",  
                     min = min(df$var3), max = max(df$var3, value = 1)
       ),
       mainPanel(
         tabsetPanel(type='pills',
            tabPanel('A table',         
              dataTableOutput('table1')
            ),
            tabPanel('Interactive figure',
               plotlyOutput('fig2', height = 700),
               h1(' ')
            )
         )
       )
	   )
  )
)

server <- function(input, output, session) {

  get_data <- reactive({
    df %>%
      filter(gene %in% input$in1) %>%
      filter(var2 == input$in2)
  })

  top_hits <- reactive(get_data() %>% head(input$threshold))
  	
	output$fig1 <- renderPlot({
	  get_data() %>%
      plot_something(df)  # ggplot (flat)
	})

	output$fig2 <- renderPlotly({
		p <- get_data() %>%
		  ggplot(aes(x=var1, y=var2)) +
  		  geom_boxplot(color="gray", outlier.shape=NA, fill=NA) +
  		  geom_jitter(
  		    aes(color=var2, text=var_labels),
  		    alpha=0.3,
  		    position=position_jitter(width=0.2, height=0)) +
		    facet_grid(gene ~ .) +
  		  geom_hline(yintercept = 0, color='gray') +
  		  theme_bw() +
		    theme(axis.text.x = element_text(angle=45, hjust=1), 
		          legend.position = "none") +
  		  xlab('') + ylab('Variable 2')

		ggplotly(p, tooltip='text') %>% layout(margin = list(b=100))  # Convert to plotly with labeled tooltip
	})
	
	output$table1 <- renderDataTable(top_hits())
	
	output$generated_list_input <- renderUI({
	  selectizeInput(inputId = 'in4', label = 'Select from dynamically generated list',
	                 choices = top_hits()$gene, multiple = FALSE)
	})
	
}

shinyApp(ui = ui, server = server)

