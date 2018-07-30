DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

docker build -f Dockerfile.shiny -t outlierbio/shiny .

docker run \
	--rm \
	-p 88:3838 \
	-v $DIR/apps:/srv/shiny-server \
    -v $DIR/logs:/var/log/shiny-server \
	outlierbio/shiny

