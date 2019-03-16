# Smart Licensing Bulk Provisioning Sample App

## Introduction  

The Smart Licensing Bulk Provisioning Sample App is a sample Python application designed to illustrate how two sets of Cisco APIs can be combined to deliver end-to-end licensing workflow automation.  It automates Smart Licensing registration for Cisco Enterprise product instances running IOS-XE. Workflows supported:
 
* Product instances with internet connectivity:  
Workflow for registration of Cisco enterprise networking products with Cisco Smart Software Manager (CSSM), which runs in the Cisco cloud.  Illustrates how Network Administrators can register a list of devices with CSSM as a batch operation, rather than individually.  
* Product instances without internet connectivity:  
Illustrates how Network Administrators can apply Specific License Reservations (SLRs) to a list of devices that do not have connectivity to CSSM.  
  
## Prerequisite

The following are required to run the Sample App:
* CCO/Cisco.com account (If you don't have one,  [register](https://idreg.cloudapps.cisco.com/idreg/guestRegistration.do))
* Valid Smart Account (SA) and Virtual Account in CSSM (If you don't have these, contact your Cisco Account Manager)
* IOS-XE devices running Smart Licensing-enabled image versions, and the relevant licenses for these devices in the SA/VA mentioned above
* Access to the Cisco MuleSoft API Server (Refer to Installation Guide for more details)

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

## Note on Data
The Smart Licensing Bulk Provisioning Sample App leverages a local datastore to enable device communication retries throughout the batch processing.  

We recommend that Customers apply their organization’s security best practices to this datastore.  
 
As is the case with any sample source code, developers may opt for alternate batch processing methods as they incorporate the API calls into their own projects.  
 
Local Datastore Specifics:
* Datastore is [SQLite](https://sqlite.org/), included in the Python distribution
* Datastore is implemented as a flat file which may be deleted after batch processing
* Data stored:
  * Per Device
    * Device IP Address
    * Device login username
    * Device login password
    * Smart Account Name
    * Smart Account Domain
    * Virtual Account Name
    * License Entitlement Tag (for SLR only)
    * License Count (for SLR only)
    * TFTP Server (for SLR only)
    * TFTP Server Path (for SLR only)