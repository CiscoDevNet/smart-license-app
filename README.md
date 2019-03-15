# Smart License Provisioning App

## Introduction  

Smart License provisioning app is an application written in Python to automate smart licensing related workflows for Cisco Enterprise product instances running IOS-XE. There are two types of workflows supported:

* Product instances with internet connectivity: 
Workflow for registration of Cisco enterprise networking products with Cisco Smart Software Manager (CSSM) running in Cisco cloud. Using this app, network administrators can register a bulk list of devices with CSSM with a few clicks instead of touching all devices one by one. 
* Product instances without internet connectivity:
This app can automate Specific License Reservation (SLR) workflow for products deployed in network that does not have connectivity to CSSM.
  
## Prerequisite
The following are required to run the app:
* CCO/Cisco.com account (If you don't have,  <a href="https://idreg.cloudapps.cisco.com/idreg/guestRegistration.do" target="_blank">register</a>
* Valid Smart Account (SA) and Virtual Account in CSSM (If you don't have, contact your Cisco Account Manager)
* Access to Cisco MuleSoft API Server (Refer to Installation for more details)

## Running the App  
This application can be run on a mac OS, Linux or Windows.
The following is required to run the app:
 * Python3 environment
 * NodeJS environment
 * App Source Code

For installation details, go to [Installation](docs/installation.md).  
  
## Using the App  
Once the set up is complete and the app is running, user needs to use a browser to launch the app.

To perform License Registration using the app, refer to [User Guide](docs/userguide.md).  
  
For Frequently Asked Questions - refer to [FAQ](docs/faq.md)


