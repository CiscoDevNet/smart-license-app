# Frequently Asked Questions

<a href="https://www.cisco.com/c/dam/en/us/products/collateral/software/smart-accounts/q-and-a-c67-741561.pdf" target="_blank">Cisco Smart Licensing FAQ</a>

[1. Why is launching application in a browser showing privacy error?](#privary-error)  
  
  
### 1. Why is launching application in a browser showing privacy error?  <a name="privary-error"></a>
The Application is configured to use a Self-Signed certificate. Since self-signed certificate is trusted by the browser by default, you are seeing the privacy error. Once the self-signed certificate is made trusted one, you will not see the error, it is just a warning.  

The communication between front-end and the back-end is secured by TLS/SSL. A PKI certificate is required to enable TLS/SSL, hence the app code is using a self-signed certificate by default. 

