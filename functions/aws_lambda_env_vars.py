__author__ = "Clyde Fondop"
# -*- coding: utf-8 -*-
# !/usr/bin/env python
# title           : Lambda env vars
# description     : Change environment variable KMS for all lambda function
#                   AWS Lambda Role Name: devsecopsLambdaEnvVars
#                   AWS Lambda Arn: arn:aws:iam::824366033707:role/devsecopsLambdaEnvVars
#                   AWS KMS Arn: arn:aws:kms:us-east-1:824366033707:key/79711a62-b836-466f-a3b5-cd482c119dbf
#                   AWS Key ID: 79711a62-b836-466f-a3b5-cd482c119dbf
#
# author          : clyde
# date            :
# version         : 0.1
# usage           : python2 aws_lambda_env_vars.py
# notes           :
# python_version  : 2.7
# ==============================================================================
#
#
#
# Import the modules needed to run the script.

import boto3, os
from botocore.exceptions import ClientError
import json, argparse
import base64


#################################################
#
# Functions
#
#################################################

class ManageLambdaFunction:
    def __init__(self):
        self.message = {}

        # Response Object
        self.response = {}
        self.response['headers'] = {'Access-Control-Allow-Origin': '*'}
        self.response['statusCode'] = 200
        self.bad_http_requests = "Error requests wrong format"
        self.description_text = "Change environment variable KMS for all lambda function."

    # Argument for testing mode
    def createParser(self):
        parser = argparse.ArgumentParser(description=self.description_text)
        parser.add_argument("-t", "--test", dest="test", required=False, help='Example usage: python aws_lambda_env_vars.py -t true')

        return parser

    # check http response code
    def check_http_response(self, event):

        get_json = {}

        try:
            get_json = event['body']
            checkJson = True
        except KeyError:
            self.response["body"] = self.bad_http_requests
            self.response['statusCode'] = 404
        except TypeError:
            self.response["body"] = self.bad_http_requests
            self.response['statusCode'] = 404

        return self.response, get_json

    # initialize lambda AWS artefacts
    def aws_initialization(self, module, aws_region):

        aws_init = boto3.client(module, region_name=aws_region)

        return aws_init


    # Encryption function for KMS
    def encrypt_env_variables(self, aws_kms_key, aws_env_value, aws_region):

        status = "encryption unsuccessful"
        encrypted = ""
        kms = self.aws_initialization("kms", aws_region)

        try:
            # Base64 + utf-8 for KMS encryption
            encrypt = kms.encrypt(KeyId=aws_kms_key, Plaintext=aws_env_value)
            encrypted = base64.b64encode(encrypt['CiphertextBlob']).decode("utf-8")
            status = "encryption_successful"

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                status = "AWS Resource not found: check AWS region"

        return status, encrypted # return the status of the encryption and an encrypted value

    # Update  nction with new environment variables
    def update_lambda_with_env(self, aws_region, func_lambda, aws_dict):

        status = "update_unsuccessful"
        lambd = self.aws_initialization("lambda", aws_region)

        try:
            # Update Lambda function
            response = lambd.update_function_configuration(
                FunctionName=func_lambda,
                Environment={
                    'Variables': aws_dict
                }

            )
            status = "update_successful"
        except ClientError as e:
              if e.response['Error']['Code'] == 'ResourceNotFoundException':
                  status = "AWS Resource not found"

        return status

#################################################
#
# start point
#
#################################################
# json syntax
# {
#     "function_name":{
#         "aws_region": "[value]",
#         "aws_kms_key": "[aws_kms_key_name]" only if is_encryt == true
#         "env_var_name":{
#             "is_encrypt": "[true / false]",
#             "aws_env_name": "[name]",
#             "aws_env_value": "[value]"
#         },
#         ...
#     },
#     ...
# }


def main(event, context):

    MyManageLambdaFunction = ManageLambdaFunction()

    response = env_variables_per_func = env_variables_only = {}
    results_process = []
    status_encryption = "encryption_none"

    # check http response
    response, func_lambda_variables = MyManageLambdaFunction.check_http_response(event)

    # test mode
    parser = MyManageLambdaFunction.createParser()
    args = parser.parse_args()

    if args.test:
        f = open("../resources/lambda_test.json","r")
        func_lambda_variables = json.loads(f.read())

    ##########

    if func_lambda_variables:
        # Read all lmabda function
        for row_function in func_lambda_variables:
            func_lambda = row_function
            aws_kms_key = func_lambda_variables[func_lambda]["aws_kms_key"]
            aws_region = func_lambda_variables[func_lambda]["aws_region"]

            # Read all attr of lambda function
            for attribue_name in func_lambda_variables[func_lambda]["data"]:

                # Populate the environment valariables
                is_encrypt = attribue_name["is_encrypt"]
                aws_env_name = attribue_name["aws_env_name"]
                aws_env_value = attribue_name["aws_env_value"]

                # Check if encryption is needed
                #
                # Call encryption function: encrypt_env_variables(kms key, environment value)
                if is_encrypt == True :
                    status_encryption, aws_env_value = MyManageLambdaFunction.encrypt_env_variables(aws_kms_key,aws_env_value,aws_region)

                # only: aws_env_name, aws_env_value
                env_variables_only.update({aws_env_name:aws_env_value})

            # Call function which will add env variable to lambda function: update_lambda_with_env(aws_env_name, aws_env_value, aws_region)
            status_update = MyManageLambdaFunction.update_lambda_with_env(aws_region, func_lambda, env_variables_only)

            # Append to a Json table the variable information
            env_variables_per_func = {
                func_lambda: {
                    "status_update": status_update,
                    "status_encryption": status_encryption,
                    "updated_data":
                        env_variables_only
                }
            }

            # All functions with attributs
            results_process.append(env_variables_per_func)
            env_variables_only = {}
            env_variables_per_func = []

        # Get the threats JSON
        response = {"body":results_process}

    if args.test:
       print(json.dumps(response))

    return response

if __name__ == '__main__':
    context = event = {}
    main(event, context)