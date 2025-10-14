Section 1:
-	In the initial version of this, we will have simple Bank templates. I will not provide banks with access to upload and edit their templates, rather I will modify these manually. I will retain the bank users for the time being and administer the templates with these accounts, but the banks for the time being will not be able to log onto this application.
Section 2:
-	You have written in section 2.2 “Target: Small to medium banks and financial institutions” and “Target: Large banks with strict regulatory requirements”. Note that the target clients here are not banks, but are clients of banks. Ideally I’d like to have a single Shared multi-tenant infrastructure, separated at application level (i.e. everything is pooled), although I’m not yet sure if that is entirely viable. Everything would be SaaS pricing. Compliance priority is absolutely ISO 27001, although not bad to be prepared for SOC 2 also.
Section 3:
-	I appreciate your description of the Organization Structure in 3.1. Am I understanding correctly that the only project I have in there is CCM-DEV-POOL? Please feel free to use gcloud CLI commands to verify whatever you need here and ensure the structure you are describing is correct.
-	Continuing from the previous point, I would appreciate a little more colour around the whole organisation structure, environments, projects, etc. That I have set up is not really sure why it's set up that way. I'm not saying it's a bad thing; I just don't have any understanding of it.
-	Same with the Network Architecture in 3.2. One thing I am aware of regarding networks is that I need to have some kind of white lists to ensure that only authorised clients are able to access the URL within their IP address range. If you try and access it from a non-whitelisted IP setup, then you can't get in. Is this what you are referring to in “6.2.1 Cloud Armor: DDoS protection and IP allowlisting”?
-	I also don't really understand the restrictions that you mentioned in 3.3. I'd appreciate a bit more colour there as well, please
Section 5:
-	On 5.1.2 data retention… I don't know where you've got those numbers from.
-	On 5.1.3, CMEK implementation, I don't really understand this point very much, so please provide some more colour.
-	
Section 6:
-	On 6.1.2, Role-Based Access Control (RBAC), please consider the following sub-points:
o	Client Admin: Full access to trade data and administration data, for that specific client. Full user of the application to monitor and confirm trades
o	Client User: Only access to trade and confirmation data. Full user of the application to monitor and confirm trades.
o	Bank Admin: Access only to upload settlement instruction document templates and applicable rules. In the current version of the application we will remove the segment definition functionality. All settlement instruction templates will belong to all segments.
-	In 6.2.1 what are you referring to in API Gateway: Rate limiting and quota management?
-	Please explain 6.3.1, You're speaking in Chinese.
-	In 6.4.1 is there a tool that can do this logging for me? Especially application logs, I’m guessing the others come as standard in GCP.
-	In 6.4.2, Compliance priority is absolutely ISO 27001, although not bad to be prepared for SOC 2 also. PCI DSS is not on my radar.
-	I don’t think I need to be GDPR ready, I’m not targeting the EU.
Section 7:
-	You mention gmail-email-processor@ccm-dev-pool.iam in 7.1.1. Remember that ccm-dev-pool is a development environment project.
-	I think 7.1.2 we currently have polling to look into the gmail account every 30 seconds and start processing if new emails arrive. However, I don't think this is the correct way of doing it in production. Do you have any better suggestions? I'm very concerned about having multiple things running synchronously, race conditions, etc. As we have more and more clients come on board and therefore are receiving more and more emails concurrently, we need to be able to pick them up and run with them on their own without causing conflicts as one process is waiting for another process to finish.
-	7.2 Whilst our development environment is indeed set up as you mention, I need to change this. We should be going through Vertex AI by default, and we should be using Claude Sonnet 4.5 as our preferred model. Our fallback should be Gemini 2.5 Pro. Also through Vertex AI. We should not be going directly through the API for Claude or any other models. I know that's how we have it in development at the moment, but that needs to change.
-	7.3 We do indeed have some very initial placeholder code for SMS through Twilio, but that's been hard to get up and running, so I'm certainly open to alternatives there. I can’t see me using this for 2FA, but yes for alerts as you mention.
-	For a future version, I need to add in another integration. This will be with the Central Bank of Chile. They have some APIs where I can go and get the value of the “Dólar Observado” on a daily basis. So I only need to call that API, get the data, and save it locally once a day. That is an API that we need to include here as well.
Section 8:
-	8.1, sounds reasonable but I have insufficient knowledge to judge whether the sizing you’ve proposed is right for this use case or not.
-	No way of evaluating your proposals for 8.3 and 8.4 either, please provide more colour.
Sections 9, 10, 11, 12, 13:
-	Same here, no idea, please provide more colour
-	Do we need a load balancer at this point?
-	Please bear in mind that right now we are pre-prod, we have 0 clients. Whilst obviously we do aim to scale, we don’t need to overscale at this point.
-	The cost monitoring numbers you propose are MASSIVE, there is no way I should get anywhere near those. Bear in mind that currently in Dev I’m probably around USD 10 per month.
Section 14:
-	The sequence may well be correct but please remove any timeframes, they are notoriously flaky. We can do stuff much faster than that.
-	Remove section 14.2 (Client Onboarding Process)

*****OTHER CONSIDERATIONS*****

1) Login: Firebase with 2FA -> creates JWT. Is it worth doing SSO or not?
2) I think we've already covered this but all backend endpoints should be protected by a decorator which checks JWT against Firebase. Do you agree? Have we covered this already?
3) We should be using Service Accounts as much as possible, and Zero-Trust Security is a key principle.
4) I'm thinking about using Google DLP to encrypt (via DEKs and KMS) client names and bank names so that no sensitive info goes to the LLM, but I'm not sure whether this is worth it or even if it will cause me some headaches.


