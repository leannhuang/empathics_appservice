# empathics_appservice

# build the docker image and push to docker hub
sudo docker build -t test .
sudo docker tag test user/repo:tag
sudo docker push user/repo:tag

# Deploy to Azure app service
az webapp create --resource-group resourcegroupname --plan planname --name appname --deployment-container-image-name user/repo:tag
