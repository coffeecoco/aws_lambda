# aws_lambda

## Explanation

AWS Lambda functions which allow quick intervention on others function for security and conformity purposes.
This repository has some tools for devOps, which integrates some security within developer test/build/release stage. 

This is a script which allows you to PUT a JSON
composed by all lambda function that you want to change, AWS KMS Keys,
AWS environment variables in order to change update dynamically all your lambda functions.

## Requirements

* Boto3
* AWS Lambda, IA, KMS
* API Gateway available soon

![AWS Lambda Env Vars](https://github.com/fsclyde/aws_lambda/blob/master/resources/aws_lambda_env_vars.png "LLD AWS Lambda Env Vars")


## Usage 

1) Testing mode

```buildoutcfg

    virtualenv2 venv
    pip install boto3
    . venv/bin/activate
    python aws_lambda_env_vars.py -t true

```


2) PUT a JSON file to AWS API Gateway

```buildoutcfg

curl --header "Content-Type: application/json" -X PUT https://[aws_api_gateway_id].execute-api.[aws_region].amazonaws.com/prod/[path] -d @resources/lambda_test.json | jq

```