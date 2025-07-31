### Bank Administration Panel

The Bank Administration Panel is the only configuration panel that bank users have access to. They also will have access to a reporting function, but that is separate from the Administration Panel.  
The Administration Panel should have the following tabs:  
1) Settlement Instructions Letters (Cartas de Instrucción in Spanish, probably something similar in Portuguese)  
2) Client Segmentation

---

#### Settlement Instructions Letters Tab

The Settlement Instructions Letters tab should be set out as a table, in a similar manner and style to the Settlement tab that we currently have for clients, as these are essentially rules.  
The table should have the following fields:

- Active (On/Off checkbox, readonly on the main table, editable when editing)  
- Priority (integer)  
- Settlement Instruction Rule Name  
- Client Segment  
- Product  
- Clickable Word document icon representing the template for the document.  
- Actions (pencil edit and trash can delete icons)  

The table should be grouped by Client Segment, including a group for “No Specific Segment” and ordered by priority. Just like on the Settlement tab for clients it should be possible to drag and drop the rules to change the priority.  
When the user clicks on the Word icon, the right third side of the screen should display a preview of the document (shrinking the table), indicating the main text and placeholders for values that will be populated automatically based on the individual trade. The user can close this preview and the full table will fill the width of the screen again.  
For a new rule, or editing an existing one, it should be possible to upload a new Word document, and to delete an existing one (without deleting the rule).

---

#### Client Segmentation Tab

The Client Segmentation tab should have the following layout:  
It should also be set out in a table format, similar to the Accounts tab for the clients.  
In this case the user should have the ability to define (add/edit/delete) client segments as much as they like.  
They should be presented with a list of available clients (names and IDs in XX.XXX.XXX-X format, you can make up some dummy data, but use 76, 77, 78 or 79 for the first two values and 0-9 or K for the last value) and they should have a smart way of assigning the clients to specific segments.  
Each client should only belong to one segment, and it is valid for a client not to belong to any segment.
