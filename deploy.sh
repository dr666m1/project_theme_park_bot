#!/bin/bash
cd $(dirname $0)
gcloud builds submit --tag gcr.io/$gcp_project/qiita-sample
gcloud beta run deploy qiita-sample --image gcr.io/$gcp_project/qiita-sample --platform managed --region us-west1
