- Python
- Docker
- FastAPI
- Artifact registry
- GCR
### 0. Folder structure
source : https://www.youtube.com/watch?v=DQwAX5pS4E8&t=1189s
```
root@da8c8a61a3aa:/code# tree
├── Dockerfile.dev
├── Dockerfile.prod
├── cloudbuild.yaml
├── requirements.txt
├── service.yaml
└── src
    ├── __pycache__
    │   └── main.cpython-312.pyc
    ├── main.py
    └── smokeTest
        ├── __init__.py
        ├── __pycache__
        │   ├── __init__.cpython-312.pyc
        │   └── router.cpython-312.pyc
        └── router.py
```
### 1. Create a Dev Container
1. create folder mkdir .devcontainer
```
mkdir .devcontainer
```
2. create file in .devcontainer folder
```
echo "" > .devcontainer/devcontainer.json
```
   source : Dev container metadata reference (https://containers.dev/implementors/json_reference/)
```
   {
    "name": "Simple API",
    "build": {
        "dockerfile": "../Dockerfile.dev"
    },
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-python.debugpy",
                "ms-azuretools.vscode-docker"
            ],
            "settings": {}
        }
    },
    "forwardPorts": [
        "5678:5678"
    ],
    "workspaceMount": "source=${localWorkspaceFolder},target=/code,type=bind,consistency=delegated",
    "workspaceFolder": "/code",
    "runArgs": []
}
```
3. create Dockerfile.dev
```
echo "" > Dockerfile.dev  
```
paste this
```
FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl git vim net-tools build-essential

WORKDIR /code

ENV PYTHONPATH=/code/src
```
4. create image on docker
```
docker build -f Dockerfile.dev -t simpleapi-dev .
```
5. start docker then exec in it
```
docker run -it --name simpleapi-dev-container -p 8000:8000 -v %cd%:/code simpleapi-dev bash
```
or
```
docker run -it --name simplegemini-dev-container -p 4000:4000 -v %cd%:/code simplegemini-dev bash
```
6. check these things
```
root@f8962855a682:/code# git version
git version 2.47.3

root@f8962855a682:/code# curl --version
curl 8.14.1 (x86_64-pc-linux-gnu) libcurl/8.14.1 OpenSSL/3.5.4 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10
Release-Date: 2025-06-04, security patched: 8.14.1-2+deb13u2
Protocols: dict file ftp ftps gopher gophers http https imap imaps ipfs ipns ldap ldaps mqtt pop3 pop3s rtmp rtsp scp sftp smb smbs smtp smtps telnet tftp ws wss
Features: alt-svc AsynchDNS brotli GSS-API HSTS HTTP2 HTTP3 HTTPS-proxy IDN IPv6 Kerberos Largefile libz NTLM PSL SPNEGO SSL threadsafe TLS-SRP UnixSockets zstd

root@f8962855a682:/code# python --version
Python 3.12.12

root@f8962855a682:/code# cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
VERSION_CODENAME=trixie
DEBIAN_VERSION_FULL=13.2
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
root@f8962855a682:/code# 
```

### 2. Build a simple FastAPI
1. <code>echo "" > requirements.txt</code>
```
fastapi>=0.110.0,<0.111.0
uvicorn>=0.29.0,<1.0.0
debugpy>=1.8.0,<2.0.0
```
2. <code>mkdir src</code>
3. echo "" > src/main.py
```
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import smokeTest
import debugpy
debugpy.listen(("0.0.0.0", 5678))

# debugpy.wait_for_client()
app = FastAPI()
origins = [
    "*"
]
  
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(smokeTest.router, prefix="/smoke-test")
# Define the API endpoints
@app.get('/')
def health():
    return {
        "message": "OK now can update"
    }
```
4. <code>mkdir src/smokeTest</code>
5. <code>echo "" > src/smokeTest/router.py</code>
```
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ResponseBody(BaseModel):
    message: str

@router.get("/hello-world")
def prompt() -> ResponseBody:
    return {"message": "Hello, world!"}
```
4. <code>echo "from .router import *" > src/smokeTest/__init__.py</code>
5. <code>pip install -r requirements.txt</code>
6. uvicorn src.main:app --host 0.0.0.0 --port 4000 --reload
```
   use
   netstat -tulnp | grep 4000
   >>> tcp  0  0 0.0.0.0:4000   0.0.0.0:*   LISTEN   47/python3.12
   then
   kill -9 47 
   until nothing
```
7. check api on uvicorn with
```
root@f8962855a682:/code# curl http://localhost:4000/smoke-test/hello-world
{"message":"Hello, world!"}root@f8962855a682:/code#
```
### 3. Deploy the API to GCR
1. Update Dockerfile.dev
```
FROM python:3.12-slim

RUN apt-get update && apt-get install -y apt-transport-https ca-certificates gnupg curl

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

RUN apt-get update && apt-get install -y git vim net-tools build-essential google-cloud-cli=473.0.0-0

WORKDIR /code

ENV PYTHONPATH=/code/src
```
2. remove docker image
```
docker rm -f simpleapi-dev-container
```
2. Rebuild container again
   <code>docker build -f Dockerfile.dev -t simpleapi-dev .</code>
```
[+] Building 0.2s (10/10) FINISHED                            docker:desktop-linux
 => [internal] load build definition from Dockerfile.dev                      0.1s
 => => transferring dockerfile: 606B                                          0.0s
 => [internal] load metadata for docker.io/library/python:3.12-slim           0.0s
 => [internal] load .dockerignore                                             0.0s
 => => transferring context: 2B                                               0.0s
 => [1/6] FROM docker.io/library/python:3.12-slim                             0.0s
 => CACHED [2/6] RUN apt-get update && apt-get install -y apt-transport-http  0.0s
 => CACHED [3/6] RUN curl https://packages.cloud.google.com/apt/doc/apt-key.  0.0s
 => CACHED [4/6] RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.g  0.0s
 => CACHED [5/6] RUN apt-get update && apt-get install -y git vim net-tools   0.0s
 => CACHED [6/6] WORKDIR /code                                                0.0s
 => exporting to image                                                        0.0s
 => => exporting layers                                                       0.0s
 => => writing image sha256:5bdca6fe4cf0b1c537db495298c6857b80804b1914a02de6  0.0s
 => => naming to docker.io/library/fastapi-dev                                0.0s
```
3. Run it to start docker container then exec it
```
docker run -it --name simpleapi-dev-container -p 8000
:8000 -v %cd%:/code simpleapi-dev bash
```
Now we got gcloud
```
root@da8c8a61a3aa:/code# gcloud --version
Google Cloud SDK 473.0.0
alpha 2024.04.19
beta 2024.04.19
bq 2.1.4
bundled-python3-unix 3.11.8
core 2024.04.19
gcloud-crc32c 1.0.0
gsutil 5.27
```
4. log in gcloud
   
```
root@da8c8a61a3aa:/code# gcloud init
Welcome! This command will take you through the configuration of gcloud.

Your current configuration has been set to: [default]

You can skip diagnostics next time by using the following flag:
  gcloud init --skip-diagnostics

Network diagnostic detects and fixes local network connection issues.
Checking network connection...done.
Reachability Check passed.
Network diagnostic passed (1/1 checks passed).

You must log in to continue. Would you like to log in (Y/n)?  y

Go to the following link in your browser, and complete the sign-in prompts:

    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=32555940559.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fsdk.cloud.google.com%2Fauthcode.html&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fappengine.admin+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcompute+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Faccounts.reauth&state=nvPtaDPMTluH6hsqah8JlDqUELXwEU&prompt=consent&token_usage=remote&access_type=offline&code_challenge=bMkFwWgFBPFQ2vEPsAbKz5xWyFPxZzpLnH6CkDZBbh0&code_challenge_method=S256

Once finished, enter the verification code provided in your browser: 4/0Ab32j92_GUfMQ4U_vacmSo23u4WEppGEb_Sn-lpO9W-q6D7Q27KVYBmOIvF2chw4wHuBuQ
You are logged in as: [tun.k@terradigitalventures.com].

Pick cloud project to use: 
 [1] aip-automation-artifact
 [2] aip-automation-bootstrap
 [3] aip-automation-ci-cd
 [4] aip-dev-ai
 [5] aip-dev-application
 [6] aip-dev-data
 [7] aip-dev-external
 [8] aip-lz-billing
 [9] aip-lz-iam
 [10] aip-lz-networking
 [11] aip-lz-remote-access
 [12] aip-lz-security
 [13] aip-prd-ai
 [14] aip-prd-application
 [15] aip-prd-data
 [16] aip-prd-external
 [17] aip-preprd-ai
 [18] aip-preprd-application
 [19] aip-preprd-data
 [20] aip-preprd-external
 [21] aip-sit-ai
 [22] aip-sit-application
 [23] aip-sit-data
 [24] aip-sit-external
 [25] aip-uat-ai
 [26] aip-uat-application
 [27] aip-uat-data
 [28] aip-uat-external
 [29] cs-host-fb9f74f99c984bb8bbc5f1
 [30] poc-piloturl-nonprod
 [31] cvevaluation-01
 [32] gen-lang-client-0156389874
 [33] google-mpf-532040072629
 [34] green-rookery-455408-d5
 [35] hi-lab-projects
 [36] llrs-prod
 [37] ndlp-poc
 [38] parinya-poc-aip-gcp
 [39] poc-piloturl-nonprod
 [40] poc-plagiarism
 [41] poc-project-471710
 [42] poc-sitetestcheck-nonprod
 [43] poc-skytestdomain-nonprod
 [44] prj-b-cicd-wif-gh-90e9
 [45] prj-b-seed-b0a7
 [46] prj-c-billing-export-x46u
 [47] prj-c-bu1-infra-pipeline-yv37
 [48] prj-c-kms-4mk3
 [49] prj-c-logging-kjb0
 [50] prj-c-scc-byry
Did not print [94] options.
Too many options [144]. Enter "list" at prompt to print choices fully.
Please enter numeric choice or text value (must exactly match list item):  30

Your current project has been set to: [cs-poc-6ybmdro11muhuzqa0ti4uuj].

Do you want to configure a default Compute Region and Zone? (Y/n)?  y

Which Google Compute Engine zone would you like to use as project default?
If you do not specify a zone via a command line flag while working with Compute Engine
resources, the default is assumed.
 [1] us-east1-b
 [2] us-east1-c
 [3] us-east1-d
 [4] us-east4-c
 [5] us-east4-b
 [6] us-east4-a
 [7] us-central1-c
 [8] us-central1-a
 [9] us-central1-f
 [10] us-central1-b
 [11] us-west1-b
 [12] us-west1-c
 [13] us-west1-a
 [14] europe-west4-a
 [15] europe-west4-b
 [16] europe-west4-c
 [17] europe-west1-b
 [18] europe-west1-d
 [19] europe-west1-c
 [20] europe-west3-c
 [21] europe-west3-a
 [22] europe-west3-b
 [23] europe-west2-c
 [24] europe-west2-b
 [25] europe-west2-a
 [26] asia-east1-b
 [27] asia-east1-a
 [28] asia-east1-c
 [29] asia-southeast1-b
 [30] asia-southeast1-a
 [31] asia-southeast1-c
 [32] asia-northeast1-b
 [33] asia-northeast1-c
 [34] asia-northeast1-a
 [35] asia-south1-c
 [36] asia-south1-b
 [37] asia-south1-a
 [38] australia-southeast1-b
 [39] australia-southeast1-c
 [40] australia-southeast1-a
 [41] southamerica-east1-b
 [42] southamerica-east1-c
 [43] southamerica-east1-a
 [44] africa-south1-a
 [45] africa-south1-b
 [46] africa-south1-c
 [47] asia-east2-a
 [48] asia-east2-b
 [49] asia-east2-c
 [50] asia-northeast2-a
Did not print [78] options.
Too many options [128]. Enter "list" at prompt to print choices fully.
Please enter numeric choice or text value (must exactly match list item):  30

Your project default Compute Engine zone has been set to [asia-southeast1-a].
You can change it by running [gcloud config set compute/zone NAME].

Your project default Compute Engine region has been set to [asia-southeast1].
You can change it by running [gcloud config set compute/region NAME].

Created a default .boto configuration file at [/root/.boto]. See this file and
[https://cloud.google.com/storage/docs/gsutil/commands/config] for more
information about configuring Google Cloud Storage.
Your Google Cloud SDK is configured and ready to use!

* Commands that require authentication will use tun.k@terradigitalventures.com by default      
* Commands will reference project `cs-poc-6ybmdro11muhuzqa0ti4uuj` by default
* Compute Engine commands will use region `asia-southeast1` by default
* Compute Engine commands will use zone `asia-southeast1-a` by default

Run `gcloud help config` to learn how to change individual settings

This gcloud configuration is called [default]. You can create additional configurations if you work with multiple accounts and/or projects.
Run `gcloud topic configurations` to learn more.

Some things to try next:

* Run `gcloud --help` to see the Cloud Platform services you can interact with. And run `gcloud help COMMAND` to get help on any gcloud command.
* Run `gcloud topic --help` to learn about advanced features of the SDK like arg files and output formatting
* Run `gcloud cheat-sheet` to see a roster of go-to `gcloud` commands.
```

Log in

![[Pasted image 20251121132247.png]]
Copy this
![[Pasted image 20251121132320.png]]
Then paste in terminal to connect with GCP
5. Enable artifact registry
   ![[Pasted image 20251120105621.png]]
   
6.  push
```
gcloud artifacts repositories create simpleapi \
  --repository-format=docker \
  --project=cs-poc-6ybmdro11muhuzqa0ti4uuj \
  --location=asia-southeast1
```
![[Pasted image 20251121133029.png]]
You gonna got your docker image on Artifact register

7. Create Dockerfile.prod
   <code>echo "" > Dockerfile.prod</code>
```
FROM python:3.12-slim

ENV PYTHONUNBUFFERED True

# set the working directory
WORKDIR /usr/src/app

# install dependencies
COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# copy src code
COPY ./src ./src
  
EXPOSE 4000

# start the server

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "4000", "--proxy-headers"]
```
8. create cloudbuild.yaml file
   <code>echo "" > cloudbuild.yaml</code>
```
   steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-f', 'Dockerfile.prod',
      '-t', 'asia-southeast1-docker.pkg.dev/cs-poc-6ybmdro11muhuzqa0ti4uuj/simpleapi/simpleapi:latest',
      '.'
    ]
  
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'push',
      'asia-southeast1-docker.pkg.dev/cs-poc-6ybmdro11muhuzqa0ti4uuj/simpleapi/simpleapi:latest'
    ]
```
8. command
```
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=cs-poc-6ybmdro11muhuzqa0ti4uuj
```
![[Pasted image 20251121134159.png]]
9. echo "" > service.yaml
```
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: custom-fastapi-service
spec:
  template:
    spec:
      containers:
        - image: asia-southeast1-docker.pkg.dev/cs-poc-6ybmdro11muhuzqa0ti4uuj/custom-fastapi/custom-fastapi:latest
          env:
          ports:
            - containerPort: 4000
```
10. run gcloud service
```
gcloud run services replace service.yaml \
    --region asia-southeast1
```
or this command (This command is better !!! above command can use to deploy but not refresh)
```
gcloud run deploy simpleapi-service \
  --image="asia-southeast1-docker.pkg.dev/cs-poc-6ybmdro11muhuzqa0ti4uuj/simpleapi/simpleapi:latest" \
  --region="asia-southeast1" \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=5 \
  --set-env-vars APP_ENV=prod
```
![[Pasted image 20251121134654.png]]![[Pasted image 20251121134714.png]]
11. Take token
    <code>gcloud auth print-identity-token</code>
```
eyJhbGciOiJSUzI1NiIsImtpZCI6ImE1NzMzYmJiZDgxOGFhNWRiMTk1MTk5Y2Q1NjhlNWQ2ODUxMzJkM2YiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIzMjU1NTk0MDU1OS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsImF1ZCI6IjMyNTU1OTQwNTU5LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwic3ViIjoiMTE3ODE4ODEyODIzMTc4NjQ5NjM3IiwiZW1haWwiOiJ0dW4ua0B0ZXJyYWRpZ2l0YWx2ZW50dXJlcy5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6InNMSUc3YlVpSTVnMWdjMkRPUWF1b0EiLCJpYXQiOjE3NjM3MDc5MzAsImV4cCI6MTc2MzcxMTUzMH0.PgYt0rOP5EvDY80eftqGA-0H7tQiezRUT6CAZ58UiYxJOK7qdDR1RubFPueSYuoaE7it1Qqv0HKEXZ0H3da6aC3Sk52xgDgdwOYIoIthpBR6D9wrV0blfu5jNEx_tVPNvTv0lyPN7QQ_nNuKaPFOUnzpmbVHlE8vAvIIM_LckgGisY8vKxzfEiwCx9z52ZLyczftf0PHloXtQqWqRR8NGmjHcVoCN_k8Is-VHT_6dJxqMN2RqGZHF9B26PIsqpjDWWkbQYKjLimnzLiqPwEsTXU7ExHSYQ9vq1001i4SQOL1GpBaW7TEmpH11GTszkE5yU6flFAZH6UGEQ-stpLkrQ
```
12. Postman
    ![[Pasted image 20251121135509.png]]

### 4. Update API
1. Update code
![[Pasted image 20251121135542.png]]
2. command
```
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=cs-poc-6ybmdro11muhuzqa0ti4uuj

```
3. run
```
gcloud run deploy simpleapi-service \
  --image="asia-southeast1-docker.pkg.dev/cs-poc-6ybmdro11muhuzqa0ti4uuj/simpleapi/simpleapi:latest" \
  --region="asia-southeast1" \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=5 \
  --set-env-vars APP_ENV=prod

```
4. Test it on Postman
![[Pasted image 20251121141216.png]]


##### 5. Update
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=cs-poc-6ybmdro11muhuzqa0ti4uuj

OR 

gcloud builds submit --config=cloudbuild.yaml


gcloud run deploy simplegemini-service \
  --image="asia-southeast1-docker.pkg.dev/cs.../simplegemini:latest" \
  --region="asia-southeast1" \
  --port=4000 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=5 \
  --set-env-vars APP_ENV=prod,GOOGLE_API_KEY="AIzaS...CNDYaKbHg8"
  






