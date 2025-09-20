1) Update GCP description doc for Cloud Tasks and Gmail stuff. DONE
2) Not using locale files, language text in python files.
3) Document ngrok and include in startup script to alert if not present. DONE
4) Cloud Tasks to identify incoming emails, instead of current polling (SSE)
5) Field Names on dispute emails
6) Allow correction of individual fields.
7) Fix upload of already matched trades in client upload.
8) Use email addresses saved by user in the client admin page for the automated emails DONE
9) Fix Buy/Sell determination in prompt DONE (I THINK)
10) Locales in other parts of the program (general tidy up, lots still in English or Spanish hardcoded)
11) Deal with uploaded .msg file which only has email display name, not an email address.
12) Move Guardar Confirmation button up on Client Admin screen, it is not noticeable. DONE
13) Complete SMS implementation, waiting on Twilio
14) Preview of template on grid and detail page.
15) Check the decorators are in place on all API calls (I don't think so).
16) Automated upload of mandates into settlement rules
17) Determine full workflow between states. Prob Confirmation OK isn't final step, should be Completed or something similar. Also, Resolved shouldn't exist. Difference -> Tagged -> Confirmation OK -> Completed.
18) In searching for settlement instruction templates it seems to use the bank name, make it lower case and put hyphens between and use this as the bank-id. This seems incredibly fragile. DONE
19) What happens if an email comes in and the client trade data hasn't yet been uploaded?
20) Fix settlement rule matching on entrega física. Not finding the rule in settlement_instruction_service.py. DONE
21) Put options to mark as confirmed via portal.
22) Implement reading and processing email confirmation via Bank portal
23) Implement EOD including checks and controls
24) Implement reporting
25) Implement download of JSON or CSV