Cloudflared provides an option to tunnel any type of service to the internet. For a VPS or a local computer, users can directly host their local port to the internet. However, when it comes to Kubernetes, routing a service (svc) to the internet without a LoadBalancerIP becomes more complex. Fortunately, Cloudflared offers a solution to host these services via tunneling. Let’s go through the steps to achieve this.

Step 1: Install Cloudflared Packages on Debian

sudo apt install cloudflared
Step 2: Login to cloudflared & get the cert.pem “certificate file” .

cloudflared tunnel login

Step 3: Create a cloudflared tunnel using the cmd.

cloudflared tunnel create example-tunnel

After the above cmd is inserted Json file will be generated .Json file store the information of cloudflared credentials.

Above steps is required to get the credential from cloudflared.

I am taking kind cluster as a demo cluster, however steps will be same for server cluster also.

Apply the manifest file from the repository link

kubectl apply -f manifest/

Need to port forward the cloudflared-api ,for REST-api

kubectl port-forward pod/cloudflared-api-deployment-5b59dcc659-cpmmv 8081:8081 -n default
List down all the route with payload

1.POST: http://0.0.0.0:8081/v1/domain/setup

“certpem” payload need to be base64 encoded.TunnelIDData is json provided by cloudflared when user login.

{
"TunnelIDData": {
"AccountTag": "7412b2d59622a47fed36e28f145",
"TunnelSecret": "SeW3FH5vvq7ANWGcMW/PEDAvSwk2oOkGjTyN",
"TunnelID": "2e86e4f1–562d-4089–88da-87580c"
},
"certpem": "XSmtOVGcwTlRVd0xXWmlPR05qTVdKbApNVGt3TURRek9UWTJZamMxTWpSak5XTmhOalZsTVRObU5tRXpaR1F6TVdKaU1EaGxZamxrTVRaa1pHTXpNVGt4ClpHRTJOR00zTm1VM016VmpZMlpsWVRJME1UZzRPVEJtT1dVMVpEZzJaR1UyTWpneE9XSmhNR0kzTVRNNE5tRTEKTmpWbVlXRmhPRFkxTURnelltTXdOR05tWkRnME0yTTRPR0prWVRnNU1HSTFaVGd5TURkak16azNORFJqWWpZeApZemxrWXpjNVpHWWlMQ0poY0dsVWIydGxiaUk2SW1wclNrZDNPWGxCZEdRM1FsWk9NWFo0VEZaUVNuTnZWRkZICmRUWlJUazloU1Y5MU9EWTBiRjhpZlE9PQotLS0tLUVORCBBUkdPIFRVTk5FTCBUT0tFTi0tLS0tCg=="
}
2.POST: http://0.0.0.0:8081/v1/domain/add-dns

{
"hostname":"phpmyadmin-tunnel.example.com",
"service":"http://my-phpmyadmin:80"
}
3.GET:http://0.0.0.0:8081/v1/domain/list-dns

5.POST: http://0.0.0.0:8081/v1/domain/remove-dns

{
"hostname": "phpmyadmin-tunnel.example.com"
}
Note: the ingress rules, with a tunnel — you must add a catch all ingress rule else you’ll get an error.User can add ingress rules using REST-api endpoint

Once all the pods are in a ready state and the domain has been added using the REST API, you can proceed to add the domain to Cloudflare. For the domain test123.example.com, you need to create a CNAME record. The CNAME record should have the following format:

Name: test123
Target: 2e86e4f1-562d-4089-88da-87580caa5daf.cfargotunnel.com
Make sure to append cfargotunnel.com to the target for every domain.


Github link:

https://umesh-khatiwada/cloudflared-dns-propagation (github.com)

Contact Information
If you have some Questions, would like to have a friendly chat or just network to not miss any topics, then don’t use the comment function at medium, just feel free to add me to your LinkedIn 🤙 network!