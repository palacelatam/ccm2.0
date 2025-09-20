Compiled with problems:
×
ERROR in src/components/grids/ConfirmationsGrid.tsx:170:58
TS2339: Property 'getGridElement' does not exist on type 'GridApi<any>'.
    168 |       // IMPORTANT: First check if the click is within THIS grid component
    169 |       // by checking if gridRef exists and contains the target
  > 170 |       if (!gridRef.current?.api || !gridRef.current?.api.getGridElement) {
        |                                                          ^^^^^^^^^^^^^^
    171 |         return;
    172 |       }
    173 |
ERROR in src/components/grids/ConfirmationsGrid.tsx:174:47
TS2339: Property 'getGridElement' does not exist on type 'GridApi<any>'.
    172 |       }
    173 |
  > 174 |       const gridElement = gridRef.current.api.getGridElement();
        |                                               ^^^^^^^^^^^^^^
    175 |       if (!gridElement || !gridElement.contains(target)) {
    176 |         return; // Click is outside this grid, ignore it
    177 |       }