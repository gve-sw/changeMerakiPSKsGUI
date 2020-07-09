""" Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import json
import requests
import datetime
import os
import sys
from subprocess import run,PIPE
from flask import Flask, Blueprint, render_template
from flask_debug import Debug
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)




global data
global org_id
global network_id
global network_name
global ssid_id
global headers
global url
global meraki_key
global date
global globalSsids
global ssidNetworkMapping
global ssidList
global networkNametoIdMapping

url = "https://dashboard.meraki.com/api/v0/"
data = {}
headers = {}
org_id = None
network_id = None
network_name = None
ssid_id = None
ssidNetworkMapping = {}
ssidList = []
networkNametoIdMapping = {}

#Used to display time within container
def get_system_time():
    current_time=datetime.datetime.now().strftime("The current system time and date is %I:%M%p on %A, %B %d, %Y.")
    return current_time

@app.route('/')
def index():
    return render_template ('login.html')

def org_request():
    global org_id

    request_url = url

    try:
        response = requests.request("GET", url + "organizations", headers=headers)
        org_data = json.loads(response.text)
        data['org'] = org_data
    except:
        return render_template ('login.html')


    if org_id is None:
        org_id = org_data[0]['id']

def network_request():
    global network_id
    global network_name
    global networkNametoIdMapping
    print("org id ", org_id)

    try:
        request_url = url + "organizations/" + org_id + "/networks"
        response = requests.request("GET", request_url, headers=headers)
        
        print('netrespone', response.text)
        network_data = json.loads(response.text)
        
        data['network'] = network_data
        for network in network_data:
            print("in loop")
            networkNametoIdMapping[network["id"]] = network["name"]
    except:
        return render_template ('login.html')

    if network_id is None:
        network_id = network_data[0]['id']
        network_name = network_data[0]['name']


@app.route('/meraki')
def meraki():
    try:

        org_request()
        network_request()
        data["ssid"] = {"name":"Choose Org and", "enabled": "Network so SSIDs appear"}
        return render_template('meraki.html', ssids = data['ssid'], orgs = data['org'], networks = data['network'],id_network = network_id,network_name=network_name,date=get_system_time())

    except:
        return render_template ('login.html',date=get_system_time())


@app.route('/meraki/<org>')
def meraki_org(org):
    global org_id
    org_id = org

    org_request()
    network_request()
    
    data["ssid"] = {"name":"Choose Org and", "enabled": "Network so SSIDs appear"}
    return render_template('meraki.html', ssids = data['ssid'], orgs = data['org'], networks = data['network'],id_network = network_id,network_name=network_name,date=get_system_time())

@app.route('/meraki/org/<network>')
def meraki_network(network):
    try:

        global network_id
        global network_name

        network_id = network
        network_name = next(item for item in data['network'] if item["id"] == network)["name"]


        org_request()
        network_request()
        
     

    except:
        return render_template ('login.html')

    return render_template('meraki.html', ssids = data['ssid'], orgs = data['org'], networks = data['network'], id_network = network_id, network_name=network_name,date=get_system_time())

@app.route('/meraki/<network_id>/<ssid_id>')
def meraki_id():
    global network_id
    global network_name
    return render_template('meraki.html', ssids = data['ssid'], orgs = data['org'], networks = data['network'],id_network = network_id,network_name=network_name,date=get_system_time())

@app.route('/meraki', methods=['POST'])
def meraki_post():
    try:
        global headers
        global meraki_key

        documents =[]
        code = request.form.get("code")
        print("this is the code",code)
        if code == '1':
            meraki_key = request.form.get("key")
            headers['X-Cisco-Meraki-API-Key'] = meraki_key
            print("headers", headers)
        if code == '2':
            switch = request.form.get("switch")

            if switch is None:
                print("off")
            else:
                print("on")

            send_collection(request,meraki_key,network_id,switch)
        #code 3 indicates that you submitted request for schedule of an ssid
        if code == '3':
            ssid_identifier = str(request.form['value']).split('+')[1] + "_" + network_id + "_" + str(request.form['value']).split('+')[0]

            collection_list = db.list_collection_names()

            if ssid_identifier in collection_list:

                collection = db[ssid_identifier]

                cursor = collection.find({})
                for document in cursor:
                    print("------------------------------")
                    print(document)
                    documents.append(document)
                #initialize start and end time array, and append values to it based
                #on what was obtained from DB in documents variable
                k=0
                schedule_start=[[] for i in range(7)]
                schedule_end=[[] for i in range(7)]
                for i in documents:
                    for j in i.get('start_times'):
                        schedule_start[k].append(j)
                    for j in i.get('end_times'):
                        schedule_end[k].append(j)
                    k=k+1
                #return as json to jquery request, which is then manipulated to show existing ssid schedules
                return  jsonify({"start_times":schedule_start, "end_times":schedule_end,"toggle":documents[0]["switch"]})#jsonify({'data': render_template('meraki.html', ssids = data['ssid'], orgs = data['org'], networks = data['network'],id_network = network_id, network_name=network_name,date=get_system_time(), test = test)})


            else:
                #if no schedule exists in DB, return empty start and end time lists to jquery request.
                #this is needed to clear all inputs when changing ssids if no schedule entry already exists
                print("Not in the database")
                schedule_start=[[""] for i in range(7)]
                schedule_end=[[""] for i in range(7)]
                return jsonify({"start_times":schedule_start, "end_times":schedule_end,"toggle":"on"})#jsonify({'collection':"No SSID Entry"})

        org_request()
        data["network"] = {"name":"choose organization to see networks"}
        data["ssid"] = {"name":"Choose Org and", "enabled": "Network so SSIDs appear"}
        print('org', data["org"])
        print('networ', data["network"])
        return render_template('meraki.html', ssids = data['ssid'], orgs = data['org'], networks = data['network'],id_network = network_id, network_name=network_name,date=get_system_time())

    except Exception as e:
        print('err logging in',e)
        return render_template ('login.html')


@app.route('/selectedNetworks', methods=['POST'])
def selectedNetworks():
    networkIds = request.json['data']
    #print("networks ", networkIds)
    global ssidList 
    global networkNametoIdMapping #a dictionary created to map network id (key) to network names (value) for viewing on gui next to the ssids
    print("network id to name mapping", networkNametoIdMapping)
    ssidList= []
    headers1 = {}
    headers1["Content-Type"] = "application/json"
    headers1["Accept"] = "application/json"
    headers1["Authorization"] = "Bearer "+meraki_key
    for network in networkIds:
        response = requests.request("GET", "https://api-mp.meraki.com/api/v1" + "/networks/" + str(network) + "/wireless/ssids", headers=headers1)
        if type(json.loads(response.text)) == dict:
            print(response.text, 'network', network) #"error":this endpoint only supports wireless networks
        else:
            ssidData = json.loads(response.text)
            for ssid1 in ssidData:
                ssid1["networkName"] = networkNametoIdMapping[str(network)]
            ssidList += ssidData #adds to list if network has ssids, error dict if it doesnt 
            for ssid in ssidData:
                ssidNetworkMapping[ssid['name']] = str(network)
                
    
    return render_template('meraki.html', ssids = ssidList, orgs = data['org'], networks = data['network'],id_network = network_id, network_name=network_name)


@app.route('/changePSK', methods=['POST'])
def changePSK():
    print("here in changepsk")
    print("global vra", ssidNetworkMapping)
    ssidNames = request.form.getlist("ssidNames[]")
    alertType = request.form.get("alert")
    print("alert", alertType)
    newPSK = request.form.get("psk")
    destEmail = request.form.get("email")
    headers1 = {}
    headers1["Content-Type"] = "application/json"
    headers1["Accept"] = "application/json"
    headers1["Authorization"] = "Bearer "+meraki_key

    #save ssids that are chosen to then send with put request
    chosenSSIDs = []
    for ssid in ssidNames:
        response = requests.request("GET", "https://api-mp.meraki.com/api/v1" + "/networks/" + ssidNetworkMapping[ssid] + "/wireless/ssids", headers=headers1)
        ssid_data = json.loads(response.text)
        for ssid1 in ssidList:
            if(ssid == ssid1['name']):
                chosenSSIDs.append(ssid1)
    print("chosen ssids", chosenSSIDs) #error above json decode
    results = []
    for ssid in chosenSSIDs:

        data1= {"name" : ssid["name"], "enabled" : ssid["enabled"], "authMode" : ssid["authMode"], "psk" : newPSK, "encryptionMode" : ssid["encryptionMode"], "wpaEncryptionMode":ssid["wpaEncryptionMode"]}
        
        url = "https://api-mp.meraki.com/api/v1" + "/networks/"+ssidNetworkMapping[ssid['name']] + "/wireless/ssids/"+ str(ssid["number"])
        print("url ", url)
        print("data ", json.dumps(data1))
        
        print("headers, ", json.dumps(headers1))
        response = requests.request("PUT", url, headers = headers1, data = json.dumps(data1))
        results.append(response.text)
        print(response.status_code, response.text)
    
    returnObj = ''
    if response.status_code == int(200):
        # returnObj = json.loads(json.dumps({"Success!" : results}))
        returnObj = {"changedSSIDs":results}
    else:
        returnObj = json.loads(json.dumps({"Error code ": response.status_code, "message": response.text}))
    
     # Sends an email using gmail server
    def send_email(destination_address, source_address, password, subject, message):
        email_message = MIMEMultipart()
        email_message['subject'] = subject
        email_message['From'] = source_address
        email_message['To'] = destination_address
        message_body = MIMEText(message, 'html')
        email_message.attach(message_body)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(source_address, password)
        server.sendmail(source_address, destination_address, email_message.as_string())
        server.quit()
    #if user inputted an email address to send response to, send it AND webex teams
    if len(destEmail) != 0:
        if alertType == "Email":
            resultStr = ''.join(results)
            send_email(destEmail, "email@gmail.com", "password", "PSK Has Been Changed", resultStr)
        elif alertType == "Teams":

            botHeader = {"Content-Type":"application/json", "Authorization": "Bearer xxxxxxzz"}
            webexData = {"toPersonEmail" : destEmail, "markdown": json.dumps(returnObj)}
            response1 = requests.request("POST", "https://webexapis.com/v1/messages", headers= botHeader, data = json.dumps(webexData))
            
    return str(response.status_code)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
