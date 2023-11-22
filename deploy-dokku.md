# Deploying on Dokku

## Installing Docker & Dokku

```shell
# Installing Docker
sudo apt update
sudo apt install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# To test Docker installation, run:
docker run --rm hello-world

# Installing Dokku
wget -qO- https://packagecloud.io/dokku/dokku/gpgkey | sudo tee /etc/apt/trusted.gpg.d/dokku.asc
# programmatically determine distro and codename
DISTRO="$(awk -F= '$1=="ID" { print tolower($2) ;}' /etc/os-release)"
OS_ID="$(awk -F= '$1=="VERSION_CODENAME" { print tolower($2) ;}' /etc/os-release)"
echo "deb https://packagecloud.io/dokku/dokku/${DISTRO}/ ${OS_ID} main" | sudo tee /etc/apt/sources.list.d/dokku.list
sudo apt-get update -qq >/dev/null
sudo apt-get -qq -y install dokku
sudo dokku plugin:install-dependencies --core

# don't keep `run` containers around
dokku config:set --global DOKKU_RM_CONTAINER=1

# Installing Dokku plugins
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
```

## Configuring Dokku

You must add your SSH public key to Dokku so you can deploy applications to it
using git. Put your public key inside a file and run:

```shell
dokku ssh-keys:add admin path/to/pub_key
```

## Creating the Application

On Dokku server, set the correct values for the variables:

```shell
export ADMIN_EMAIL="admin@api.noepicentro.news"
export APP_NAME="noepicentro-backend"
export DOMAIN="api.noepicentro.news"
```

Now, run the commands to create and configure the app:

```shell
# Create app
dokku apps:create $APP_NAME
dokku checks:disable $APP_NAME
dokku letsencrypt:set $APP_NAME email $ADMIN_EMAIL
dokku domains:add $APP_NAME $DOMAIN
```

## First Deployment

Since you've created and configured the app on the server, you can switch to
your local machine and execute the first app deploy! After cloning the
repository (and inside its directory), execute:

```shell
git remote add dokku dokku@<server-ip>:<app-name>
git push dokku master:main
```

## Finishing Installation

To finish the installtion you need to configure the SSL certificate

Finally, on server again:

```shell
# Create/configure SSL certificate:
dokku letsencrypt:enable $APP_NAME
```

