# AWS Cost Optimization: EC2 Right Sizing
**THIS IS A PERSONAL PROJECT. Not an official Amazon solution!**

Based on the AWS solution "Cost Optimization: EC2 Right Sizing". Please see the main solution for the [Cost Optimization: EC2 Right Sizing](https://aws.amazon.com/answers/account-management/cost-optimization-ec2-right-sizing/).


## Prerequisites

To grab data from multiple AWS accounts, this solution uses an IAM role from an administrator account (where you launch the cloudformation stack) that assumes into *n* child accounts. This is possible because of:
>For example, if you switch to RoleA, IAM uses your original user or federated role credentials to determine if you are allowed to assume RoleA. If you then switch to RoleB *while you are using RoleA*, IAM still uses your **original** user or federated role credentials to authorize the switch, not the credentials for RoleA.  
[source AWS doc link](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-console.html)

Good news is that one half of the equation is already done (the administrator account's IAM role used by EC2 worker). You will now need to create a new IAM role in each of the target accounts (including in the administrator account itself) to allow cross account role assumption.

Tip: Use an automated resource deployment method such as CloudFormation [StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs.html) to deploy new AWS resources such as IAM roles in a scalable and consistent way.

Each of the following items has to be configured for the solution to work.
1. Name of the IAM role has to be the **same** across all AWS accounts (ie. cost-optimization-get-cw-data). The name of the role will be used later as a CloudFormation input to feed into the code.
2. IAM Role with the following permissions 
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "MultiAccountCostOptimization",
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```
3. IAM Role's Trust Relationship with the following policy document. Replace **\<AdministratorAWSAccountID\>** with your 12 digit account ID

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    },
    {
      "Sid": "AllowingCrossAccountCWScraper",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<AdministratorAWSAccountID>:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
**Remember**, the above IAM role has to be created for the administrator account as well as the EC2 worker assumes into itself as well.

## Instructions

Once the IAM roles has been configured in each AWS Accounts, launch a new CloudFormation stack in the administrator account using the cost-optimization-ec2-right-sizing.json template in this repo.

In the launch parameters, input the AWS accounts and the name of the AWS Role that was configured in prerequisites.

The stack will take about 20min to finish (more for larger number of AWS accounts), with the results stored in the S3Bucket in the Resources tab.

## Python source code

- callgcw.py
- deleteandterminate.py
- getcloudwatchmetrics.py
- run-rightsizing-redshift.py

## Troubleshooting
Log files are exported to the CloudWatch Logs log group cost-optimization-ec2-right-sizing, log streams:
{instance_id}/cfn-init.log
{instance_id}/run-rightsizing-redshift.log
{instance_id}/deleteandterminate.log

Log files are also located locally on the solution created EC2 instance (if you chose to not terminate resources):
/var/log/cfn-init.log
/tmp/run-rightsizing-redshift.log
/tmp/deleteandterminate.log



***

Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
