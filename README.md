# Serverless Secrets Manager

## Overiew

Serverless Secerts Manager is a serverless solution for securely storing passwords and other
secrets in the cloud.  The design assumes that you cannot trust your cloud provider.

## Security

### Password is never sent to the server

Many systems store a hashed version of your password.  We store an RSA public key.  The client
signs the random token with your private key and transmits that to the server.  The server
uses the stored public key to verify the signature.

### Each secret is encrypted with it's own AES256 key

Each secret has it's own AES256 key.  The key is encrypted with the user's public key before
being stored on the server.  Secrets can be shared with other users by encrypting the secret
with the other user's public key as well

### Secrets are never unencrypted on the server

All secrets are encrypted and decrypted client side.  The encrypted value is sent and retrieved
from the server.

## Technology

The system is implemented as a Lambda function that stores data in DynamoDB.  An API Gateway
is used to expose the REST interface to the client.  KMS is NOT used because data is sent
to the REST service already encrypted.  There is no need to reencrypt the data.


## Storing the private key in DynamoDB

You have the option of storing a user's encrypted private key in DynamoDB.  The key is
encrypted with an scrypt-generated AES256 key.  This allows for easier distribution of
the private key.  Users would authenticate the first time with their password and would
download the private key to their client.  This is less secure because both the password
and private key would be available to your cloud provider in the request/response of the
REST call.  This mode of operation is optional.  It makes it easier to distribute private
keys but you can use a secure side channel to transfer your private keys.


### CloudFormation

#### Create the stack

aws --region=us-east-1 cloudformation create-stack --stack-name SecretManagerAPI --template-body "$(cat cfn.yaml)" --capabilities CAPABILITY_IAM && aws --region=us-east-1 cloudformation wait stack-create-complete --stack-name SecretManagerAPI


#### Update the stack

aws --region=us-east-1 cloudformation update-stack --stack-name SecretManagerAPI --template-body "$(cat cfn.yaml)" --capabilities CAPABILITY_IAM && aws --region=us-east-1 cloudformation wait stack-update-complete --stack-name SecretManagerAPI


#### Delete the stack

aws --region=us-east-1 cloudformation delete-stack --stack-name SecretManagerAPI && aws --region=us-east-1 cloudformation wait stack-delete-complete --stack-name SecretManagerAPI

### Generate the Android Retrofit2 client based on the swagger file

sudo docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli generate -i /local/swagger.yaml -l java --library retrofit2 --api-package com.intirix.secretsmanager.clientv1.api --model-package com.intirix.secretsmanager.clientv1.model -o /local/out/android

### Generate the QT client

sudo docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli generate -i /local/swagger.yaml -l qt5cpp -o /local/out/qt --additional-properties cppNamespace=ssmv1
