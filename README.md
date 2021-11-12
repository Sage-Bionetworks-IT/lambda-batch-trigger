# lambda-batch-utils
An AWS lambda containing utility functions for AWS batch

## Development

### Contributions
Contributions are welcome.

### Requirements
Run `pipenv install --dev` to install both production and development
requirements, and `pipenv shell` to activate the virtual environment. For more
information see the [pipenv docs](https://pipenv.pypa.io/en/latest/).

After activating the virtual environment, run `pre-commit install` to install
the [pre-commit](https://pre-commit.com/) git hook.

### Create a local build

```shell script
$ sam build
```

### Run unit tests
Tests are defined in the `tests` folder in this project. Use PIP to install the
[pytest](https://docs.pytest.org/en/latest/) and run unit tests.

```shell script
$ python -m pytest tests/ -v
```

### Run integration tests
Running integration tests
[requires docker](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local-start-api.html)

```shell script
$ sam local invoke HelloWorldFunction --event events/event.json
```

## Deployment

### Deploy Lambda to S3
Deployments are sent to the
[Sage cloudformation repository](https://bootstrap-awss3cloudformationbucket-19qromfd235z9.s3.amazonaws.com/index.html)
which requires permissions to upload to Sage
`bootstrap-awss3cloudformationbucket-19qromfd235z9` and
`essentials-awss3lambdaartifactsbucket-x29ftznj6pqw` buckets.

```shell script
sam package --template-file .aws-sam/build/template.yaml \
  --s3-bucket essentials-awss3lambdaartifactsbucket-x29ftznj6pqw \
  --output-template-file .aws-sam/build/lambda-batch-utils.yaml

aws s3 cp .aws-sam/build/lambda-batch-utils.yaml s3://bootstrap-awss3cloudformationbucket-19qromfd235z9/lambda-batch-utils/master/
```

## Publish Lambda

### Private access
Publishing the lambda makes it available in your AWS account.  It will be accessible in
the [serverless application repository](https://console.aws.amazon.com/serverlessrepo).

```shell script
sam publish --template .aws-sam/build/lambda-batch-utils.yaml
```

### Public access
Making the lambda publicly accessible makes it available in the
[global AWS serverless application repository](https://serverlessrepo.aws.amazon.com/applications)

```shell script
aws serverlessrepo put-application-policy \
  --application-id <lambda ARN> \
  --statements Principals=*,Actions=Deploy
```

## Install Lambda into AWS

### CFN Nested Stack
We recommend installing this lambda as a nested cloudformation stack.

Add this snippet to the parent cloudformation stack:

```yaml
LambdaBatchUtils:
  Type: 'AWS::CloudFormation::Stack'
  Properties:
    TemplateURL: 'https://bootstrap-awss3cloudformationbucket-19qromfd235z9.s3.amazonaws.com/lambda-batch-utils/master/lambda-batch-utils.yaml'
    Parameters:
      JOB_NAME: !Sub '${AWS::StackName}-my-job'
      JOB_QUEUE: !Ref JobQueue
      JOB_DEFINITION: !Ref JobDefition
```

Then deploy the parent stack.

### Sceptre
Alternatively it can be deployed with [sceptre](https://github.com/Sceptre/sceptre) by creating the following
file config/prod/lambda-batch-utils.yaml

```yaml
template:
  type: http
  url: https://bootstrap-awss3cloudformationbucket-19qromfd235z9.s3.amazonaws.com/lambda-batch-utils/master/lambda-batch-utils.yaml
stack_name: "lambda-batch-utils"
stack_tags:
  Department: "Platform"
  Project: "Infrastructure"
  OwnerEmail: "it@sagebase.org"
parameters:
  JobName: my-batch-job
  JobQueue: !stack_output_external script-runner::JobQueueArn
  JobDefinition: !stack_output_external script-runner::JobDefinitionArn
```

Install the lambda using sceptre:
```shell script
sceptre --var "profile=my-profile" --var "region=us-east-1" launch prod/lambda-batch-utils.yaml
```


### AWS Console
Steps to deploy from AWS console.

1. Login to AWS
2. Access the
[serverless application repository](https://console.aws.amazon.com/serverlessrepo)
-> Available Applications
3. Select application to install
4. Enter Application settings
5. Click Deploy

## Releasing

We have setup our CI to automate a releases.  To kick off the process just create
a tag (i.e 0.0.1) and push to the repo.  The tag must be the same number as the current
version in [template.yaml](template.yaml).  Our CI will do the work of deploying and publishing
the lambda.
