![Apikama](.github/logo.png?raw=true "Apikama logo")
======

## Getting Started

This API is quick and easy to use, reducing the complexity of working with the native client API. The first required step is generating your encrypted server string. 

This string contains the **host**, **SSL flag**, **HTTP port**, and **secret server key**. However, sending the server key over HTTPS is dangerous for several reasons, including:

- The server key is exposed in server logs
- The key appears in browser history
- The key is visible in URLs, making it vulnerable to accidental sharing
- The key gets cached at various points along the request path
- The key may be captured by analytics and error tracking systems

Fortunately, this API has already taken care of that for you. Use the built-in  [utility encrypter](https://www.cockroachlabs.com/docs/stable/start-a-local-cluster.html#before-you-begin) endpoint to generate an encrypted version of your server string, which you'll then use for all API calls with that specific server configuration. 

Enter your server string in the following format:

**127.0.0.1:7350:0:somekey**

Think of it as your personal API key—keep it safe and secure.

## Next?
