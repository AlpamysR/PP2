import re
import json
import os
 
def parse_receipt(text):
    receipt = {}
 
    # Extract date and time
    date_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})', text)
    if date_match:
        receipt['date'] = date_match.group(1)
        receipt['time'] = date_match.group(2)
 
    # Extract payment method and total
    card_match = re.search(r'Банковская карта:\s*([\d\s]+)', text)
    if card_match:
        receipt['payment_method'] = 'Bank Card'
        receipt['payment_amount'] = float(card_match.group(1).replace(' ', ''))
 
    total_match = re.search(r'ИТОГО:\s*([\d\s]+)', text)
    if total_match:
        receipt['total'] = float(total_match.group(1).replace(' ', ''))
 
    vat_match = re.search(r'в т\.ч\. НДС 12%:\s*([\d\s]+)', text)
    if vat_match:
        receipt['vat_12pct'] = float(vat_match.group(1).replace(' ', ''))
 
    # Extract store info
    bin_match = re.search(r'БИН\s+(\d+)', text)
    if bin_match:
        receipt['store_bin'] = bin_match.group(1)
 
    store_match = re.search(r'Филиал ТОО\s+(.+)', text)
    if store_match:
        receipt['store_name'] = store_match.group(1).strip()
 
    address_match = re.search(r'г\.\s*[\w-]+,Казахстан,\s*(.+)', text)
    if address_match:
        receipt['address'] = address_match.group(0).strip()
 
    # Extract products
    lines = text.split('\n')
    products = []
    i = 0
    while i < len(lines):
        num_match = re.match(r'^(\d+)\.$', lines[i].strip())
        if num_match:
            item_num = int(num_match.group(1))
            name_lines = []
            i += 1
            while i < len(lines):
                qty_match = re.match(r'^([\d\s]+),000\s*x\s*([\d\s]+),00$', lines[i].strip())
                if qty_match:
                    qty = float(qty_match.group(1).replace(' ', ''))
                    unit_price = float(qty_match.group(2).replace(' ', ''))
                    i += 1
                    total_line = lines[i].strip() if i < len(lines) else ''
                    total_match2 = re.match(r'^([\d\s]+),00$', total_line)
                    total_price = float(total_match2.group(1).replace(' ', '')) if total_match2 else qty * unit_price
                    i += 1
                    if i < len(lines) and lines[i].strip() == 'Стоимость':
                        i += 1
                    products.append({
                        'item': item_num,
                        'name': ' '.join(name_lines).strip(),
                        'quantity': qty,
                        'unit_price': unit_price,
                        'total_price': total_price
                    })
                    break
                else:
                    name_lines.append(lines[i].strip())
                    i += 1
        else:
            i += 1
 
    receipt['products'] = products
    receipt['product_count'] = len(products)
    receipt['calculated_total'] = sum(p['total_price'] for p in products)
 
    return receipt
 
 
def main():
    # Get current folder of the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
 
    # Input and output files (relative to script folder)
    input_file = os.path.join(base_dir, 'raw.txt')          # put your input file here
    output_file = os.path.join(base_dir, 'receipt_parsed.json') # JSON output
 
    # Check if input exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
 
    # Read input
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
 
    receipt = parse_receipt(text)
 
    # Print receipt
    print("=" * 60)
    print("PARSED RECEIPT")
    print("=" * 60)
    print(f"Store:          {receipt.get('store_name', 'N/A')}")
    print(f"Date:           {receipt.get('date', 'N/A')} {receipt.get('time', 'N/A')}")
    print(f"Address:        {receipt.get('address', 'N/A')}")
    print(f"Payment Method: {receipt.get('payment_method', 'N/A')}")
    print()
    print(f"{'#':<4} {'Product':<50} {'Qty':>5} {'Price':>10} {'Total':>10}")
    print("-" * 82)
    for p in receipt['products']:
        print(f"{p['item']:<4} {p['name'][:50]:<50} {p['quantity']:>5.0f} {p['unit_price']:>10.2f} {p['total_price']:>10.2f}")
    print("-" * 82)
    print(f"{'TOTAL:':<62} {receipt.get('total', 0):>10.2f}")
    print(f"{'Calculated Total:':<62} {receipt.get('calculated_total', 0):>10.2f}")
    print(f"{'VAT 12%:':<62} {receipt.get('vat_12pct', 0):>10.2f}")
    print()
 
    # Save JSON output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
 
    print(f"JSON saved to {output_file}")
 
 
if __name__ == '__main__':
    main()
