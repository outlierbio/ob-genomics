DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

docker build -f Dockerfile.pipeline -t genomics-pipeline .

docker run --rm	genomics-pipeline build