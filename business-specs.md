# Application Specifications

## Context

**Palace** is a technology company that designs and builds applications for banks, with a specific focus on the **Sales & Trading desks** within these institutions. The purpose of this document is to define the specifications for a new application aimed not at internal bank users, but rather at the **clients** of these Sales desks.

The target users of the application will include a wide spectrum of companies serviced by Sales desks — from **large institutional clients** to **small and medium-sized enterprises (SMEs)**. As such, the application will need to cater to a variety of use cases, workflows, and levels of sophistication.

## Overview: Client Confirmation Manager 2.0

The application, tentatively named **Client Confirmation Manager 2.0**, is designed primarily for **bank clients based in Chile** who trade foreign exchange (FX) instruments with banks. These instruments include:

- FX Spot
- FX Forwards
- FX Swaps

### Current Workflow

Today, these trades are typically agreed through a variety of channels:

- Telephone
- Chat platforms
- Web portals
- Other electronic channels

Once a trade is agreed, both the client and the bank record the trade in their respective systems. Subsequently — anywhere from minutes to hours later — the bank sends a **confirmation email** to the client.

### Client Pain Point

Clients often operate with multiple banks (2–5 or more), and therefore receive confirmation emails in **multiple formats** and **at varying times**. This makes it difficult to:

- Centralize confirmations
- Validate trade details quickly
- Detect discrepancies efficiently

### Purpose of the Application

The core function of Client Confirmation Manager 2.0 is to:

1. **Automatically receive** confirmation emails from multiple banks.
2. **Parse and extract** trade details from those emails.
3. **Compare** the extracted data with the client’s internal records.
4. **Confirm** that all details match — or
5. **Identify and flag** discrepancies.
6. **Generate a response** to return to the bank highlighting any issues found.

This process streamlines trade confirmation and reduces operational risk for clients.

---

## Value Proposition for Banks

Although the application is designed for **client use**, banks also derive clear benefits from encouraging adoption. In fact, **Sales desks** at these banks are intended to serve as a **key distribution channel**, promoting the application to their clients.

### Benefits to Banks

- **Streamlined confirmation workflows**: A more digitized and consistent process across clients.
- **Reduced operational risk**: Fewer manual errors and follow-ups due to a standardized process.
- **Improved client satisfaction**: Clients benefit from a better experience and are more likely to favor banks offering this solution.

### Commercial Model

- **Clients receive a discount** on the application license if they **opt-in to share data** with their banks.
- The **shared data** includes:
    - All trades the client has confirmed via the application.
    - **Anonymized counterparty details** — i.e., each bank can see that the client has traded with other banks, but **not which banks specifically**.
- In exchange, **banks pay Palace a license fee** to access this **aggregated, anonymized transaction data**.

This allows banks to:

- Better understand client behavior, needs, and preferences.
- Benchmark their share of wallet without breaching confidentiality.
- Inform strategic decisions based on real market activity.

---

## Technical Considerations

The application will be developed as a **Software-as-a-Service (SaaS)** platform, hosted primarily on **Google Cloud Platform (GCP)**. The frontend will be written primarily in React and the backend in Python. Application administration persistence will be in a No-SQL database (Firestore), as will trade and confirmation data for day-to-day and reporting purposes. AI models will be accessed via VertexAI. The frontend will be hosted on Firebase, and the backend on Cloud Run, which will take containerized Docker images from Google Cloud Artifact Registry. Decorators will be used on backend APIs to ensure that only authorised users can execute the APIs. Google Data Loss Prevention and Key Management Services will be employed to protect sensitive data. Service Accounts will be used to execute actions as needed, using the principle of minimum access. The architecture and implementation will emphasize the following principles:

### Modularity

- The system will be built in a **modularized fashion**, enabling scalability and maintainability.
- Clear separation of concerns between components such as ingestion, parsing, comparison, user interface, and analytics.
- There should be a frontend directory and a backend directory within the root of the project. Each directory structure beneath these directories should follow architectural best practices.

### Security

- **Enterprise-grade data security and information protection** are fundamental.
- Compliance with best practices for encryption, access control, auditing, and secure storage.
- OAuth and SSO should be enabled, although the initial version should use User/Password on Firebase.

### Agent-Based Design

- Where applicable, the application will leverage **autonomous agents** or microservices to handle discrete parts of the workflow (e.g., email ingestion, data extraction, anomaly detection, reporting).
- This approach supports flexibility, improved fault isolation, and potential integration with LLM-based agents or AI tools in the future.

### Locales

- All user-facing text and information should be presented by default in Spanish, but the user should have the ability to switch languages (consider English and Portuguese) by clicking flags at the top of the application.

### UX principles

- The UX of the application is a very high priority. We should always be conscious of making the UX as frictionless and delightful as possible.
- The application should use CSS to centralise as many design features as possible in order to maximise consistency.
- The application should be in dark mode, with a top banner reserved for the Palace logo on the top-left and general admin, report or settings options aligned top-right.
- Text should be Manrope font.
- AG Grids should be used to display the trade data and confirmation data. Inline menus should be available on the grids to display actions and further information on right-click.

---

## Client User Roles Overview

### User Roles

- **Standard User**: Interacts with the application to view, verify, and reconcile trade data.
- **Admin User**: Manages settings, integrations, and user permissions. A single user may hold both roles.

## Client User Workflow Overview

### Application Layout (Standard User)

- **Bottom Panel**: A configurable data grid showing all client trade data over a user-defined period. The source here is the information uploaded from the client system, via CSV, Excel or in the future via a REST API.
- **Top Left Panel**: A display of trades that the application has identified from the client trade data which it considers to be the trades referred to in the bank confirmation emails.
- **Top Right Panel**: A grid summarizing the data extracted from each of the confirmation emails received from various banks, in the format of individual trades. Each record in this grid should be matched to a record in the top left panel or, if no trade in the client trade data can be identified, it should have the status "Unrecognised".

### Pre-Comparison Workflow

1. **Trade Activity**: The client performs FX trades throughout the day with multiple banks. This is done outside of the application itself.
2. **Email Routing**: Confirmation emails from banks are sent to each of the clients. For the initial version of this application these emails will be forwarded to a Palace controlled-central email address (e.g., `confirmaciones@palace.cl`).
3. **Email Ingestion**: The application monitors the email folder for new emails. Each time a new mail is received, the application will initiate its process.
4. **Content Extraction**: The application extracts text from the email body and/or attached PDF.
5. **LLM-Powered Parsing**: An LLM is used to structure the extracted content into a consistent and pre-defined trade data format. It should be considered that multiple trades could be referred to in the same email or pdf file.
6. **Trade Comparison**: Parsed data is compared against the trades uploaded by the client via Excel/CSV (and in future, APIs or other sources).
7. **Reconciliation**: Matches and mismatches are presented to the user for validation or flagging. This view is available in the main user application on the client side, and is also logged into the daily report.

### Post-Comparison Workflow

Once the application performs the comparison between extracted confirmation details and internal client records, if a Full Match is detected:

1. The system checks whether **Auto-Confirmation** is enabled for matched trades for the client. If enabled, the system waits for the **configurable delay period** (e.g., 30 seconds) before creating an email indicating confirmation of the trade and sending it back to the bank.
2. The system checks if the **Carta de Instrucción** feature is activated in the Admin Page. If so, the corresponding bank’s **template** for the Carta de Instrucción (a settlement instruction letter) is used and the system completes the template using:
    - Trade data extracted from the email
    - Supplementary data uploaded by the client (e.g., settlement instructions, account numbers)
    - Selection and population of the template are rule-based (e.g., by currency, product, bank).
    - The completed Carta de Instrucción is attached to the auto-confirmation email, if required.
    
    This is then attached to the email if appropriate.
    
3. The record for this trade is updated and will be available to daily and other reports and queries.

If a discrepancy is found between the confirmation and the client’s internal record:

1. The system highlights the **fields in conflict** and provides an explanation of **why** the data is considered mismatched.
2. The system checks whether **Auto-Confirmation** is enabled for disputed trades for the client. If enabled, the system waits for the **configurable delay period** (e.g., 30 seconds) before creating an email indicating the dispute of the trade, the fields in dispute and sending it back to the bank.
3. The user can also right-click on the record and select the Verify option from the inline menu. Here they can paste the negotiation text from a chat, email, or other source. The application uses an LLM to extract trade intent from this text and performs a **three-way comparison**:
    1. Bank confirmation
    2. Client system entry
    3. User-submitted negotiation content

## Client Admin User Overview

### Application Layout

- Main Admin Page: The main admin page will have toggles which allow the user to manage the following points:
    - Turn On/Off data sharing with banks
    - Turn On/Off Autoconfirm on matched trades, which entails the generation and sending of an automated email back to the bank indicating the confirmation of the trade. There will also be a field to configure the amount of time to wait before automatically sending the confirmation email back to the bank.
    - Turn On/Off Auto Carta Instrucción on matched trades, which entails the generation of a Carta de Instrucción document based on the appropriate template uploaded by the bank and the data provided by matching the rules configured by the client admin user.
    - Turn On/Off Autoconfirm on disputed trades, which entails the generation and sending of an automated email back to the bank indicating the fields of the trade where there is a discrepancy. There will also be a field to configure the amount of time to wait before automatically sending the confirmation email back to the bank.
    - Turn On/Off Email Confirmed Trade Alert, together with the email address, or list of destination email addresses
    - Turn On/Off Email Disputed Trade Alert, together with the email address, or list of destination email addresses
    - Turn On/Off WhatsApp Confirmed Trade Alert, together with the phone numbers, or list of destination phone numbers
    - Turn On/Off Email Disputed Trade Alert, together with the phone numbers, or list of destination phone numbers
- Settlement Instructions Page:
    - A list of rules which allows the admin user to enter conditions to determine the account number to be used to settle a specific type of trade (and therefore entered into a Carta de Instrucción). Conditions should consider fields such as “Contraparte”, “Producto”, “Moneda Flujo”, “Dirección” (Entrante/Saliente) and map to an account number and bank name. The conditions should not be mandatory. Rules can be copied, edited, disabled, or deleted. A new rule can be added, including as a copy of an existing rule.
    - A list of bank names and account numbers, which is used to populate the rules section.
- Trade Data Mapping Page:
    - A page which allows an Admin User to upload a CSV or XLSX format of their trade data to the system. This then calls an LLM which will map the fields to the known and expected data format used within the application, as well as perform a test mapping. The proposed mapping can then be saved (and edited, disabled, deleted, copied) for this particular client with a unique name. The user will see the list of mappings they have configured. This mapping ruleset will be used by the application each time it refreshes the trade data via a client upload.

## Bank Admin User Overview

### Application Layout

- Main Admin Page: The bank has very limited admin capabilities. Essentially they have two options:
    1. Manage Carta de Instrucción templates. This allows the bank admin user to upload .docx formats for Settlement Instruction templates, with placeholders for client_name, trade_date, currency, account_number, etc. A line should be in place for each set of conditions that make up a rule that maps to a single template. For example, these conditions could be “Contraparte”, “Producto”, “Monedas Operación”, “Segmento”, etc. The conditions should not be mandatory. Rules can be copied, edited, disabled, or deleted. A new rule can be added, including as a copy of an existing rule.
    2. Manage Client segments. One of the fields for the templates is the Segmento. Therefore the Bank Admin should have the ability to define segments and assign the clients in the system (identified by ID and name) to the different segments. Segments can be added, removed, edited, etc, and clients can be added or removed from different segments.
- Reports Page: The bank has two options:
    - Overview dashboard which gives general summary-level information, which can be filtered by client, product, date range.
    - Trades AG Grid which shows all of the trades in the system, filterable and sortable. Names of other banks should not be visible.

---