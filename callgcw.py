#!/usr/bin/python
######################################################################################################################
#  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.                                           #
#                                                                                                                    #
#  Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance        #
#  with the License. A copy of the License is located at                                                             #
#                                                                                                                    #
#      http://aws.amazon.com/asl/                                                                                    #
#                                                                                                                    #
#  or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES #
#  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    #
#  and limitations under the License.                                                                                #
######################################################################################################################

import boto3
import logging
import string, os, sys
import time
import platform
from argparse import ArgumentParser
import codecs


CW_REGION = "ap-southeast-2"

CURRENTOS = platform.system()
if CURRENTOS == "Linux":
    import ConfigParser
    cf = ConfigParser.ConfigParser()
elif CURRENTOS == "Windows":
    import configparser
    cf = configparser.ConfigParser()
else:
    logging.error("The platform %s " % (CURRENTOS) + " is not supported.")
    exit()

# Main
def call_gcw(p_region, p_account, p_mode, p_statistics, p_period, p_starttime, p_endtime, p_output, sts_credentials):
    sys.path.append('getcloudwatchmetrics.py')
    import getcloudwatchmetrics

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')

    ec2 = boto3.client(
        'ec2',
        region_name=CW_REGION,
        aws_access_key_id=sts_credentials['Credentials']['AccessKeyId'],
        aws_secret_access_key=sts_credentials['Credentials']['SecretAccessKey'],
        aws_session_token=sts_credentials['Credentials']['SessionToken']
        )
    awsregions = ec2.describe_regions()['Regions']
    print awsregions
    #region = [str(x) for x in p_region.split(' ')]
    account = p_account
    mode = p_mode
    statistics = p_statistics
    period = int(p_period) * 60
    startTime = int(p_starttime) * 60 * 60 * 1000
    endTime = int(p_endtime) * 60 * 60 * 1000
    outputName = p_output

    
    ls_today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    ls_combined_csv = ls_today + "-before" + str(p_starttime) +"hour-with" + str(p_period) + "min.csv"
    
    logging.info("Writing CW data to file {}".format(ls_combined_csv)) # debug

    outfile = codecs.open(ls_combined_csv, 'a', encoding='utf-8')
    outfile.write(
        u"\"{0}\",\"{1}\",\"{2}\",\"{3}\",\"{4}\",\"{5}\",\"{6}\",\"{7}\",\"{8}\",\"{9}\",\"{10}\",\"{11}\",\"{12}\",\"{13}\",\"{14}\",\"{15}\"\n".format(
            "humanReadableTimestamp", "timestamp", "accountId", "az", "instanceId", "instanceType", "instanceTags",
            "ebsBacked", "volumeIds", "instanceLaunchTime", "humanReadableInstanceLaunchTime", "CPUUtilization",
            "NetworkIn", "NetworkOut", "DiskReadOps", "DiskWriteOps"))
    outfile.close()
    #separate multiple regions to call pt-cwatch.py one region by one region
    for i in awsregions:
        ls_single_region = i['RegionName']
        print ls_single_region
        if ls_single_region <> 'ap-southeast-1':
            ls_region_array = []
            ls_region_array.append(ls_single_region)
            ls_outputfile_name = outputName + "-in-" + ls_single_region + ".csv"
            getcloudwatchmetrics.download_metrics(ls_region_array, account, mode, statistics, period, startTime, endTime, ls_outputfile_name, sts_credentials)

            if CURRENTOS == "Linux":
                os.system('cat ' + ls_outputfile_name + ' >> ' + ls_combined_csv)
                os.system('rm -rf ' + ls_outputfile_name)
            elif CURRENTOS == "Windows":
                os.system('type ' + ls_outputfile_name + ' >> ' + ls_combined_csv)
                os.system('del ' + ls_outputfile_name)

    return ls_combined_csv # this file will be appended with cloudwatch data until the last aws account in list, where it will uploaded to S3