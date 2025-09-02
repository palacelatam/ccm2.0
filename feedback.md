Generating Settlement Instruction Document...
------------------------------------------------------------
  Counterparty: Banco ABC
  Bank ID (mapped): banco-abc
  Client segment ID: None
  Settlement type: Compensación
  Product: Forward
  System will query database for best matching template...
C:\Users\bencl\Proyectos\ccm2.0\backend\src\services\settlement_instruction_service.py:190: UserWarning: Detected filter using positional arguments. Prefer using the 'filter' keyword argument instead.
  query = query.where('settlement_type', '==', settlement_type)
Error downloading template from storage: 'StorageService' object has no attribute 'download_document'
❌ Failed to download template 'Fwd Compensación Template 2' from cloud storage
ERROR: Document generation failed!
  Error: ❌ Failed to download template 'Fwd Compensación Template 2' from cloud storage