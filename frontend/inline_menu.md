Here is the functionality required for the inline menu on the "Status" column. This menu should appear when you do a right-click on a cell in that column. The inline menu format should be a centralised component in terms of style, because I want to have consistent styling across the application.
First of all, there should be two options which are 'tagged' and 'resolved'. If the user clicks on either of these options, the status value for the clicked row should switch to “Tagged” or “Resolved”. This should be saved to the database on the corresponding email document. “Tagged” values in the status column should be orange text, and "Resolved" should be light blue text. There should also be an option in the inline menu for 'Undo'. 'Undo' simply returns it back to the previous status, whatever that was.
Beneath these three options there should be a dividing line and then another menu option which says "Mailback". Mailback should generates an email from the local email client of the user, presumably using a "mail to" type command. The email would have the To field as the sender of the email in the row that has been clicked upon. confirmaciones_dev@servicios.palace.cl should be in cc. The subject of the email should be “Confirmation of <trade_number_placeholder” - use the trade number of the row selected by the user. If there are discrepancies, the body of the email should read as follows:
“Dear <counterparty_name>,
With regards to trade number <trade_number>, <company name> has the following observations:
Bold: <field_with_discrepancy_n>:
Your value: <email_field_n_value>
Our value: <matched_trade_field_n_value>
Regards,
<company_name>”
If there are no discrepancies, the body of the email should read as follows:
“Dear <counterparty_name>,
With regards to trade number <trade_number>, <company name> confirms the trade as informed by you.
Regards,
<company_name>”
This email should simply open on the user’s email client, but not be sent until they manually do so.


Answers to your questions:
1) Yes, I think it should update the status field in the trade record within the email confirmation record. 
2) We should just track the immediate previous status, so one level of undo. And we should do this within memory, this isn't necessary to save in the database. Unless, of course, you think the implementation is simpler that way. If there is no previous version, i.e., there's nothing in memory, then obviously we can just grey out or disable that menu item of undo. 
3) Yes, the company name should come from the logged-in user's organisation name. You can link that from the user's org ID and then the name on the client object. Discrepancies you can just apply that when the status is difference or tagged or resolved.
4) Yes, only appear when right-clicking on the status column specifically. 
5) It changes the text, not the cell colour, only the text, and without needing to refresh, yes. 
6) I don't know. Probably we use the client_service, but can you give me some more information on that please before I make a final decision? What is it currently being used for, and would this functionality be consistent with that? 