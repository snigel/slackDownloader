#!/usr/bin/env python2

import requests
import time
from slacker import Slacker

#token='your-token-goes-here'
slack = Slacker(token)

#Get users
response = slack.users.list()
users = response.body['members']
id2user = {}
for u in users:
  id2user[u["id"].encode("utf-8")] = u["name"].encode("utf-8")


#Get files
response = slack.files.list()
files = response.body['files']
amount = len(files)
total = 0

while (amount > 0):
  total = total + amount
  print "Will download " + str(amount) + " files."

  count = 0
  for file in files:
    count = count+1
    timestamp = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(float(file['timestamp'])))
    user = id2user[file['user']]
    fname = file['name']
    file_id = file['id']
    filename = timestamp + "_" + user + "_" + fname

    #Handle dropbox files by downloading thumbnail from slack.
    if 'url_private_download' in file:
      url = file['url_private_download']
    else:
      print "No download url, grabbing thumbnail 1024"
      url = file['thumb_1024']
      print url

    print "Downloading " + str(count) + " of " + str(amount) + ", " + filename
    #Download file.
    r = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
    if r.status_code == 200:
      with open("./"+filename, 'wb') as f:
        for chunk in r:
          f.write(chunk)
        #Delete files that has been downloaded.
        slack.files.delete(file['id'])
        print "Deleted:    " + str(count) + " of " + str(amount) + ", " + filename
    else:
      print "Error!: " + r.status_code

  #Reset counter and download next chunk of 100 files.
  print "Downloaded/removed " + str(amount) + " of files."
  response = slack.files.list()
  files = response.body['files']
  amount = len(files)

print "Done! downloaded and deleted " + str(total) + " files."
