# changeMerakiPSKsGUI
A GUI where network admins can select multiple SSIDs to change the PSKs. This saves time since on the Meraki Dashboard, you can only change one at a time. Can select the organization, the network(s), then multiple SSIDs to change. The user can optionally input their email address so that an email or message on Webex Teams will be sent to them notifying that the changes were made.

![/IMAGES/logic.png](/IMAGES/logic.png)





## Contacts
* Yashar Asgari
* Jason Mah

## Solution Components
* Flask
*  Docker
*  Meraki Dashboard APIs
*  Webex Teams APIs
*  UI Kit
*  Python
*  HTML
*  CSS

## Installation/Configuration

Option 1: 

1. Pull down the project into a python virtual environment

```
git clone https://github.com/gve-sw/changeMerakiPSKsGUI.git
```

2. Install required packages

```
pip install -r requirements.txt
```

3. Launch flask application

```
python views.py
```


Option 2:

1. Install Docker - https://docs.docker.com/get-docker/

2. Pull down the project
```
git clone https://github.com/gve-sw/changeMerakiPSKsGUI.git
```
3. Run Docker image
```
docker-compose up
```


## Usage
Navigate to [localhost:5000](http://localhost:5000) to use the app.

Enter a Meraki API Key from the Meraki API dashboard then click "Submit" - https://documentation.meraki.com/zGeneral_Administration/Other_Topics/The_Cisco_Meraki_Dashboard_API#:~:text=Enable%20API%20access,-For%20access%20to&text=After%20enabling%20the%20API%2C%20go,API%20key%20on%20your%20profile.

![/IMAGES/login.png](/IMAGES/login.png)

Select the organization in order to view its networks
![/IMAGES/login.png](/IMAGES/org.png)


Select the network(s) you want to change the SSID configuration of
![/IMAGES/login.png](/IMAGES/networks.png)

By default, all SSIDs in the chosen network(s) will be selected to have their PSKs changed. You can deselect as well.
Lastly, type in the desired PSK and (optionally) input your email address. You can select to be notified by Webex Teams or Email when the changes are complete

![/IMAGES/login.png](/IMAGES/ssid.png)


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
