# globalise-typoscript

The resulting data is available on [dataverse](https://hdl.handle.net/10622/LVOQTG).

```
"path_to_inpute" "\path\to\file" out -l nld --psm 11 tsv
```

# Workflow

### Step 1
Preprocess material using `pre-process.py`
- Increases contrast
- enlarges image
- makes it grayscale

### Step 2
Inference tables using our custom Transkribus table model, which was trained on 111 pages of Ground Truth.

### Step 3
Manual inspection of pages to add any cells the table-recognition has missed.

### Step 4
Automatic inference of the baselines using Transkribus 'Universal Lines' model, with these deviations from the standard settings:
- Keep existing text regions
- Split lines on region border

### Step 5
Automatic inference of the text using Transkribus OCR model 'Transkribus Print M1'

### Step 6
Export the results as a spreadsheet.

## The following steps are taken automatically by `folder_pipeline.py` 

### Step 7
Add inventory numbers to the rows of the spreadsheet, crossreferencing the names of the image with 'png_files_list.csv'.

### Step 8
Add the information on locations mentioned in inventory titles to the spreadsheet, based on 'archival_info_locations.json'. For inventory number 1204-1207, there was no relevant location information. Instead, these have manually been added based on the archival description: the Cape, Mauritus, Perzië & Surat for 1204, 1205, and 'Kanton' for 1207. For 1206, it's the Cape, Mauritus, Perzië & Surat for inv. no 4230-4360, the Cape for 4361-4366 and the Cape + Rio de la Goa for 4367-4370.

## The following steps are taken in Excel
### Step 9
Add a new row to the excel sheet that keeps track of titles that are in ALL CAPS.
      
Ex., taken from F2 where E2 is 'doc_name':
```
=EXACT(UPPER(E2),E2)
```
     
Then, the sheet is filtered on rows where F is TRUE.

The resulting list is classified in column H, in the following manner:
- If the doc_name refers to a 'kantoor' that is in the row's locations added in step 8, the name of that kantoor is added in that row's column H.
- Otherwise, if the doc_name does not give information about a kantoor, 'STOP' is added in that row's column H.

### Step 10
A formula is used to add the kantoor-information to as many rows as possible:
```
=IF(
    ISNUMBER(FIND(";", L3)),
    IF(
        AND(ISBLANK(H3), K3=K2),
        G2,
        IF(
            ISNUMBER(FIND(H3, L3)),
            H3,
            IF(
                H3="STOP",
                "",
                "error"
            )
        )
    ),
    L3
)
```

#### Comment on inventory number 1204, 1205 and 1206:
We know from the archive that these contain more than just the Cape and Mauritius, but the headings are too inconsistent to give them more specific kantoren. Step 10 was not done for these.

#### Explanation of the Formula

This formula is designed to process and evaluate the content of various cells based on certain conditions. Here's what it does step by step:

1. **Checks if the inventory number (column K) is still the same as in the last row**
2. **Checks for a Semicolon in the Inventory Title**  
   The formula starts by checking if there is a semicolon (`;`) in the c`'The places mentioned in the inventory title'` (column `L`).  
   - **Condition:** `ISNUMBER(FIND(";", L3))`
   - If `TRUE` (a semicolon exists), it proceeds to further checks.  
   - If `FALSE` (no semicolon exists), the formula simply returns the value of column `L` (`'The places mentioned in the inventory title'`), as there is only one.

3. **Handles the Case Where a Semicolon is Found**  
   If a semicolon exists, the formula evaluates `'The manually classified kantoor'` (column `H`):
   - **Condition:** `ISBLANK(H3)`  
     - If column `H` is blank and the inventory number is still the same, it repeats the previous value` (column `G`).

4. **Checks for Matching Content**  
   If column `H` is not blank, it checks if the value in column `H` is present in column `L` (`'The places mentioned in the inventory title'`):
   - **Condition:** `ISNUMBER(FIND(H3, L3))`
     - If `TRUE`, it returns the value from column `H` (`'The manually classified kantoor'`).

5. **Handles the Special Case "STOP"**  
   If the value in column `H` is `"STOP"`, the formula returns an empty string (`""`).

6. **Returns "Error" for Unmatched Cases**  
   If none of the above conditions are met, the formula returns `"error"`.


### Step 11
In order to check if the page numbers are correct, the following checks are performed. 
Legend: S = Starting number, E = End number
- Condition 1: Are S and E numerical values?
  ```
  =IFERROR(VALUE(I2), "FALSE")
  =IFERROR(VALUE(J2), "FALSE")
  ```
- Condition 2: Is there a value for both S and E?
  ```
  =IF(ISNUMBER(K2), IF(ISNUMBER(L2), "TRUE", "FALSE"), "FALSE")
  ```
- Condition 3: Is S equal to or lower than E?
  ```
  =IF(L2>=K2, "TRUE", "FALSE")
  ```
- Condition 4: Is E lower than or equal to the next row's value of S, if the inventory number is the same for both rows?
  ```
  =IF(P2=P3, IF(L2<=K3, "TRUE", "FALSE"), "TRUE")
  ```

If so, we can assume this rows values are likely correct.

### Step 12
Based on this we can introduce a new rule:
- If condition 2 is not met because E is missing, but the next row does have an S that meets all four conditions, E equals the S of the next row minus 1.
```
=IF(L2="FALSE", IF(P3="TRUE", K3-1, "FALSE"), "FALSE")
```

### step 13
using the notebook `add_years` we've added years taken from the EAD through 'archival_info.json'. There is an earliest and latest year, to describe cases where the inventory number spans multiple years.

## The following steps are taken in Excel
### Step 14
By filtering the folionumbers from largest to smallest and vice versa, unreasonably high and low page numbers were detected and manually corrected to more likely variants were possible. The same rules as used in step 9 and 10 were applied. The original documents were not checked to verify these changes.

### Step 15
By filtering the folionumbers for folionumbers that are a float rather than an integer, unlikely page numbers were manually corrected to more likely variants were possible. The same rules as used in step 9 and 10 were applied. The original documents were not checked to verify these changes.

### Step 16
By filtering the folionumbers for numbers that ended in a variant of recto or verso, unlikely page numbers were manually corrected to more likely variants were possible. The same rules as used in step 9 and 10 were applied. The original documents were not checked to verify these changes.

## Description of files
### png_files_list.csv
This file contains manual annotations mapping image names to the inventory numbers they describe. Manual annotation was necessary because the inventory numbers were added to the page at a later date using pencil, in an unpredictable manner, making manual annotation much faster than trying to figure out an algorithm that could pick up on these.

### archival_info_locations.json
This file comes from the inventarization and metadata repo and is used to add location info to the spreadsheet.

### add geo to tanap
Used to add geographical information to the TANAP data, similar to step 8


