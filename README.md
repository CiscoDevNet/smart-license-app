# Smart License Provisioning App

## Introduction  

Smart License provisioning app is an application written in python to automate smart licensing related workflows for a list of Cisco Enterprise product instances running IOS-XE. There are two types of workflows supported:

* Product instances with internet connectivity: 
Workflow for registration of Cisco enterprise networking products with Cisco Smart Software Manager (CSSM) running in Cisco cloud. Using this app network administrators can register a bulk of devices with CSSM with a few clicks instead of touching all devices one by one. 
* Product instances without internet connectivity:
This app can automate Specific License Reservation (SLR) workflow for products deployed in network that does not have  connectivity to CSSM.
  
## Prerequisite
The following are required to run the app:
* CCO/Cisco.com account(If you don't have, [register](https://idreg.cloudapps.cisco.com/idreg/guestRegistration.do))
* Valid Smart Account(SA) and Virtual Account in CSSM(If you don't have, contact your Cisco Account Manager)
* Access to Cisco MuleSoft API Server(Refer to Installation for more details)

## Documentation
For Installation and User Guide, refer to <a href="https://developer.cisco.com/pubhub/docs/1826/new" target="_blank">Cisco DevNet - Smart License Provisioning App</a>