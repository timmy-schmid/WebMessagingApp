To run the application, first ensure all requirements are downloaded. Then run: 

  python3 app.py

This will launch the server at https://127.0.0.1:8080 

For the full functionality of the server use multiple browsers. Once different users have been created on different browers, they will be able to communicate properly. 
This is because the app uses cookies, so you have to use different browsers given cookies are shared across tabs on the same browser.

When the application is run on a browser, the browser will not trust the certificate. This is because it is self-signed. 
To configure the browsers to trust the certificate follow the guide here [https://deliciousbrains.com/ssl-certificate-authority-for-local-https-development/#installing-root-cert] to install the root certififcate.
