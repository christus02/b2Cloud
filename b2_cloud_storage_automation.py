#!/usr/bin/env python
'''
    Script to automate the Entire B2 Cloud Storage account for Study Of Christ (studyofchrist.com)
'''

import base64
import json
import urllib2
import sys

__copyright__ = "This is currently copyrighted to Raghul Christus (chris.lazaras@gmail.com)"
__credits__ = ["Jesus Christ"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Raghul Christus"
__email__ = "chris.lazaras@gmail.com"
__status__ = "Production"


# NAMING CONVENTIONS
# All the entities should be strictly named with Camel case starting with lower case

def authorizeAccount(accountId, key):

    ''' Function to Authorize the B2 Account and return necessary parameters
        for this script to run

        Input Arguments:
        accountId : Provide the account ID from B2
        key       : Provide the account application key from B2 Account

        Return Arguments:
        outDict   : Returns a dictionary containing required account information

    '''

    #Combine both the Account ID and the Key
    idAndKey = accountId+':'+key
    basicAuthString = 'Basic ' + base64.b64encode(idAndKey)
 
    #Add to authorization header
    headers = { 'Authorization': basicAuthString }

    #API URL to authorize the account
    authorizeUrl = 'https://api.backblazeb2.com/b2api/v1/b2_authorize_account'

    request = urllib2.Request(
        authorizeUrl,
        headers = headers
        )

    response = urllib2.urlopen(request)

    if (response.getcode() == 200):
        print ("Authorization to B2 account is SuccessFull")
        responseData = json.loads(response.read())
        response.close()

        outDict = dict()
        outDict['authorizationToken'] = responseData['authorizationToken']
        outDict['apiUrl'] = responseData['apiUrl']
        outDict['downloadUrl'] = responseData['downloadUrl']
        outDict['minimumPartSize'] = responseData['minimumPartSize']

        return(outDict);
    else:
        print ("Authorization Failed to B2 account. Please check the credentails")
        return(None);

def downloadById(accountAuthToken,downloadUrl,fileId,localFilePath):

    ''' Function to Download a File from B2 account using the File ID

        Input Arguments:
        accountAuthToken   : Authorization Token returned from account Authorization API
        downloadUrl        : Download URL returned from account Authorization API
        fileId             : File ID of the file to be download from B2
        localFilePath      : Local absoulte path to where the file should be downloaded

        Return Arguments:
        Currently None

    '''

    headers = {
        'Authorization': accountAuthToken
        }
    url = downloadUrl + '/b2api/v1/b2_download_file_by_id?fileId=' + fileId
    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request)
    data = response.read()
    with open(localFilePath, "wb") as download:
        download.write(data)

    response.close()

    return(None)

def downloadByName(accountAuthToken,downloadUrl,bucketName,fileName,localFilePath):

    ''' Function to download a file by its name in a bucket
    '''

    headers = {
        'Authorization': accountAuthToken
        }
    url = downloadUrl + '/file/' + bucketName + '/' + fileName

    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request)

    if (response.getcode() == 200):
        print ("Download Successful")

        data = response.read()
        with open(localFilePath, "wb") as download:
            download.write(data)
        response.close()

    else:
        print ("Download Failed")
        return (None)


def getFileInfo(apiUrl, fileId, accountAuthToken):

    ''' Function to get the Information of a File using its ID
    '''

    request = urllib2.Request(
        apiUrl+'/b2api/v1/b2_get_file_info',
        json.dumps({ 'fileId' : fileId }),
        headers = { 'Authorization': accountAuthToken }
    )

    response = urllib2.urlopen(request)

    if (response.getcode() == 200):
        print("Got Information of the specified File Successfully")

        outDict = dict()
        responseData = json.loads(response.read())
        outDict['accountId'] = responseData['accountId'] 
        outDict['bucketId'] = responseData['bucketId'] 
        outDict['contentLength'] = responseData['contentLength'] # int data type
        outDict['contentSha1'] = responseData['contentSha1'] 
        outDict['contentType'] = responseData['contentType'] 
        outDict['fileId'] = responseData['fileId'] 
        outDict['fileInfo'] = responseData['fileInfo'] 
        outDict['fileName'] = responseData['fileName'] 
        
        response.close()

        return(outDict)
    else:
        print("Error in Fetching information regarding the specified file")
        return(None)

def usage():

     usage_str = """ SCRIPT USAGE: 
    {} accountID accountKey [optionalArgs]
                 """.format(sys.argv[0])
    
     print (usage_str)



if __name__ == '__main__':

    if (len(sys.argv) >= 2):
        accountId = sys.argv[1]
        accountKey = sys.argv[2]
    else:
        usage()
        exit(0)
        

    downloadFileId = '4_z1f6abee52698187b59c70017_f11735400d3d595c3_d20170517_m160830_c001_v0001019_t0013'
    localFilePath = '/var/tmp/'

    account = authorizeAccount(accountId, accountKey);
    if (account == None):
        print("Account Login Failed - Exiting")
        exit(0)

    print ("Getting File Info")
    fileInfo = getFileInfo(account['apiUrl'],downloadFileId,account['authorizationToken'])
    
    print ("Printing the File Information got from API");
    for key in fileInfo.keys():
        print ("The Key is {} and the Value is {}".format(key,fileInfo[key]))

    print ("Downloading by Name")
    downloadByName(account['authorizationToken'],account['downloadUrl'],'studyofchrist','After_gym_casual.jpg',localFilePath+'downloadedByName.jpg')

    print ("Downloading file by ID")
    downloadById(account['authorizationToken'], account['downloadUrl'], downloadFileId,localFilePath+'downloadedById.jpg');

