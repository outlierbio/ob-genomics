BUCKET=s3://outlierbio/reference

sudo yum update -y
sudo yum install -y \
  docker \
  git

sudo mkfs -t ext4 /dev/sdb
sudo mkdir /mnt
sudo mount /dev/sdb /mnt
sudo mkdir /mnt/reference   
mkdir /mnt/scratch
sudo mkdir /mnt/scratch
sudo chmod 777 /mnt/scratch/

# Sync data to local
aws s3 sync $BUCKET/tcga/ /mnt/reference/tcga/
aws s3 sync $BUCKET/gtex /mnt/reference/gtex/
aws s3 sync $BUCKET/hpa/ /mnt/reference/hpa/
aws s3 sync $BUCKET/tissue/ /mnt/reference/tissue/
aws s3 sync $BUCKET/ncbi/ /mnt/reference/ncbi/
aws s3 sync $BUCKET/tcga/ /mnt/reference/tcga/

# Install Python packages
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
conda install nomkl
conda install pandas psycopg2
pip install boto3 luigi

# Clone and install the code
git clone https://github.com/outlierbio/ob-genomics
cd ob-genomics
pip install -e .

# Configure
nano config.yml
nano .env
source .env

# Run the pipeline
ob-genomics init
ob-genomics meta
ob-genomics build