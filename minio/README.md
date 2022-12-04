I found it useful to deploy min.io locally using the directions in the Kubernetes tutorial. This gave me a standalone environment that didn't need access to Google Object Store or S3.

To do this, just follow the directions in the Kubernetes tutorial and set up an ExternalName service definition -- that will let you specify the Min.io host as minio in your applications.

We've copied that specification and the Helm configuration file from the Kubernetes tutorial -- if you modify things, you might want to document that here.
