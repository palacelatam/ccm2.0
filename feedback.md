Compiled with problems:
×
ERROR in src/components/grids/ConfirmationsGrid.tsx:749:64
TS2304: Cannot find name 'tradeData'.
    747 |           console.log('🔍 DEBUG Settlement Icon - settlementInstructionError (direct):', emailData?.settlementInstructionError);
    748 |           console.log('🔍 DEBUG Settlement Icon - llmExtractedData:', emailData?.llmExtractedData);
  > 749 |           console.log('🔍 DEBUG Settlement Icon - tradeData:', tradeData);
        |                                                                ^^^^^^^^^
    750 |           console.log('🔍 DEBUG Settlement Icon - hasAutoError:', hasAutoError);
    751 |           console.log('🔍 DEBUG Settlement Icon - storagePath:', storagePath);
    752 |           console.log('🔍 DEBUG Settlement Icon - hasError (manual):', hasError);