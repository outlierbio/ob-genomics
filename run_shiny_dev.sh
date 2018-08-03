DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

docker build -f Dockerfile.rstudio -t outlierbio/shiny-dev .

docker run \
	--rm \
	-d \
	-p 80:8787 \
	-v $DIR:/home/rstudio \
	outlierbio/shiny-dev

