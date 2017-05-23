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
import json
import base64

kms = boto3.client('kms', region_name='us-west-2')
lambd = boto3.client('lambda', region_name='us-west-2')

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


    # Encryption function for KMS
    def encrypt_env_variables(self, kms_key, env_value):

        status = "encryption unsuccessful"
        encrypted = ""

        try:
            encrypt = kms.encrypt(KeyId=kms_key, Plaintext=env_value)
            # Base64 + utf-8 for KMS encryption
            encrypted = base64.b64encode(encrypt['CiphertextBlob']).decode("utf-8")

            status = "encryption_successful"
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                status = "AWS Resource not found: check AWS region"

        return status, encrypted # return the status of the encryption and an encrypted value

    # Update lambda function with new environment variables
    def update_lambda_with_env(self, func_lambda, env_name, env_value):

        status = "update_unsuccessful"

        try:
            response = lambd.update_function_configuration(
                FunctionName=func_lambda,
                Environment={
                    'Variables':{
                        env_name:env_value
                    }
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
#         "env_var_name":{
#             "is_encrypt": "[true / false]",
#             "env_name": "[name]",
#             "env_value": "[value]",
#             "kms_key": "[kms_key_name]" only if is_encryt == true
#         },
#         ...
#     },
#     ...
# }


def main(event, context):

    MyManageLambdaFunction = ManageLambdaFunction()
    response = results_process = env_variables_per_func = {}
    globale_vars_func = []
    status_encryption = "encryption_none"

    # check http response
    response, func_lambda_variables = MyManageLambdaFunction.check_http_response(event)

    f = open("lambda_test.json","r")
    func_lambda_variables = json.loads(f.read())

    if func_lambda_variables:
        # Read all lmabda function
        for row_function in func_lambda_variables:
            func_lambda = row_function

            # Read all attr of lambda function
            for attribue_name in func_lambda_variables[func_lambda]:

                # Populate the environment valariables
                is_encrypt = func_lambda_variables[func_lambda][attribue_name]["is_encrypt"]
                kms_key = func_lambda_variables[func_lambda][attribue_name]["kms_key"]
                env_name = func_lambda_variables[func_lambda][attribue_name]["env_name"]
                env_value = func_lambda_variables[func_lambda][attribue_name]["env_value"]

                # Check if encryption is needed
                #
                # Call encryption function: encrypt_env_variables(kms key, environment value)
                if is_encrypt == True :
                    status_encryption, env_value = MyManageLambdaFunction.encrypt_env_variables(kms_key,env_value)

                # Call function which will add env variable to lambda function: update_lambda_with_env(env_name, env_value)
                status_update = MyManageLambdaFunction.update_lambda_with_env(func_lambda, env_name, env_value)

                # Append to a Json table the variable information
                env_variables_per_func = {
                    "status_update":status_update,
                    "env_name":env_name,
                    "status_encryption": status_encryption
                }

                # All attributs for a function
                globale_vars_func.append(env_variables_per_func)
                env_variables_per_func = []

            # All functions with attributs
            results_process[func_lambda] = globale_vars_func
            globale_vars_func = []

        # Get the threats JSON
        response = {"body":results_process}

    print(json.dumps(response))

    #print(response)

    return response

if __name__ == '__main__':
    context = event = {}
    main(event, context)