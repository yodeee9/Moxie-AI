# Moxie

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

## Frontend 

To build and deploy your application for the first time, run the following in your shell:

```bash
npm install
npm run dev
```

## Backend 

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build 
sam deploy --region us-east-1 --parameter-overrides ParameterKey=AgentId,ParameterValue= ParameterKey=AgentAliasId,ParameterValue=
```