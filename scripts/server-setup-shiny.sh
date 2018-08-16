sudo yum update -y
sudo yum install docker git

# Start docker
sudo usermod -aG docker ec2-user
# log out and back in
sudo service docker start

# Clone and install the code
git clone https://github.com/outlierbio/ob-genomics
cd ob-genomics

# Add database credentials
nano apps/genomics/creds.r