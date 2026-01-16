
docker build -f Dockerfile.dev -t cvresume .

C:\Users\TunKedsaro\Desktop\CVResume>docker run -it --name simpleapi-dev-container -p 4000:4000 -v %cd%:/code -e GOOGLE_API_KEY=AIzaSyDSTj....DbFOhM11Nisis cvresume


```text
gcloud artifacts repositories create simplegemini \
  --repository-format=docker \
  --project=poc-piloturl-nonprod \
  --location=asia-southeast1
```

```text
gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=poc-piloturl-nonprod

gcloud run deploy cvresume-service \
  --image="asia-southeast1-docker.pkg.dev/poc-piloturl-nonprod/cvresume/cvresume:latest" \
  --region="asia-southeast1" \
  --port=4000 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=5 \
  --set-env-vars="APP_ENV=prod,GOOGLE_API_KEY=AIzaSyDSTj....DbFOhM11Nisis" \
  --allow-unauthenticated
  
```
