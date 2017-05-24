# aws_lambda

AWS Lambda functions which allow quick intervention on others function for security and conformity purposes.
This repository has some tools for devOps, which integrates some security within developer test/build/release stage.

### aws_policy_env_vars 

This is a script which allows you to PUT a JSON
composed by all lambda function, AWS KMS Keys,
AWS environment variables that you want to change,
 n order dynamically update environment variables for these.

### Requirements

* Boto3
* AWS Lambda, IAM, KMS, API Gateway
* AWS Cloud Formation in progress

![AWS Lambda Env Vars](https://github.com/fsclyde/aws_lambda/blob/master/resources/aws_lambda_env_vars.png "LLD AWS Lambda Env Vars")


### Usage 

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