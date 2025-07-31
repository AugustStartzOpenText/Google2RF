import csv
import sys
from pathlib import Path

def combine_name_fields(first, middle, last):
    parts = [part.strip() for part in [first, middle, last] if part and part.strip()]
    return ' '.join(parts)

def categorize_phone(label, value):
    # this function categorizes phone numbers based on if the label contains "fax" we might need to adjust this logic later
    if not value or not value.strip():
        return None, None
    
    label_lower = label.lower() if label else ""
    phone_type = "fax" if "fax" in label_lower else "voice"
    return phone_type, value.strip()

def clean_field(field):
    #Clean fields by removing extra whitespace and normalizing newlines.
    if not field:
        return ''
    # Replace multiple newlines with single space and strip
    cleaned = ' '.join(field.replace('\n', ' ').replace('\r', ' ').split())
    return cleaned

def convert_contacts_fax_only(input_file, output_file):
    #Convert the CSV to the new RF format - FAX NUMBERS ONLY."""
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            # Define the new format headers
            headers = ["ID", "NAME", "COMPANY", "ADDRESS", "CITYSTATE", "FAX1", "FAX2", "VOICE1", "VOICE2", "BILLCODE1", "BILLCODE2", "NOTES"]
            writer = csv.DictWriter(outfile, fieldnames=headers, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            contact_id = 1
            for row in reader:
                # Combine name fields
                name = combine_name_fields(
                    row.get('First Name', ''),
                    row.get('Middle Name', ''),
                    row.get('Last Name', '')
                )
                
                # Skip rows without a name or if it's just empty/whitespace
                if not name or not name.strip():
                    continue
                
                # Process phone numbers first to check for fax
                phones = []
                for i in range(1, 5):  
                    label_key = f'Phone {i} - Label'
                    value_key = f'Phone {i} - Value'
                    
                    label = row.get(label_key, '')
                    value = row.get(value_key, '')
                    
                    phone_info = categorize_phone(label, value)
                    if phone_info[0]:  # If we have a valid phone
                        phones.append(phone_info)
                
                # Separate fax and voice numbers
                fax_numbers = [phone[1] for phone in phones if phone[0] == 'fax']
                voice_numbers = [phone[1] for phone in phones if phone[0] == 'voice']
                
                # SKIP CONTACTS WITHOUT FAX NUMBERS
                if not fax_numbers:
                    continue
                
                # Get company
                company = clean_field(row.get('Organization Name', ''))
                
                # Combine address fields
                street = clean_field(row.get('Address 1 - Street', ''))
                city = clean_field(row.get('Address 1 - City', ''))
                region = clean_field(row.get('Address 1 - Region', ''))
                postal = clean_field(row.get('Address 1 - Postal Code', ''))
                
                address = street
                citystate_parts = [part for part in [city, region, postal] if part]
                citystate = f"{city}, {region} {postal}".strip().strip(',').strip() if citystate_parts else ''
                
                # Always use just a space for notes, why i don't know but RF wants it
                notes = ' '
                
                # Create the output row
                output_row = {
                    'ID': contact_id,
                    'NAME': name.strip(),
                    'COMPANY': company,
                    'ADDRESS': address,
                    'CITYSTATE': citystate,
                    'FAX1': fax_numbers[0] if len(fax_numbers) > 0 else '',
                    'FAX2': fax_numbers[1] if len(fax_numbers) > 1 else '',
                    'VOICE1': voice_numbers[0] if len(voice_numbers) > 0 else '',
                    'VOICE2': voice_numbers[1] if len(voice_numbers) > 1 else '',
                    'BILLCODE1': '',  # not used in this conversion but we can add it later if needed
                    'BILLCODE2': '',  
                    'NOTES': notes
                }
                
                writer.writerow(output_row)
                contact_id += 1
    
    print(f"Fax-only conversion complete! {contact_id - 1} contacts with fax numbers converted.")
    print(f"Output saved to: {output_file}")

if __name__ == '__main__':
    input_file = 'sample.csv'
    output_file = 'converted_contacts_fax_only.csv'
    

    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    convert_contacts_fax_only(input_file, output_file)