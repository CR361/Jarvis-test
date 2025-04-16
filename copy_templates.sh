#!/bin/bash

# Checklist templates
echo "Kopiëren checklist templates..."
cp ./checklist.html ./templates/checklist/index.html
cp ./edit_checklist_item.html ./templates/checklist/edit_item.html

# Aannemers templates
echo "Kopiëren aannemers templates..."
cp ./contractor_list.html ./templates/contractors/index.html
cp ./create_contractor.html ./templates/contractors/create.html
cp ./edit_contractor.html ./templates/contractors/edit.html

# Backup templates
echo "Kopiëren backup templates..."
cp "./backup_direct_download (1).html" ./templates/backup/download.html

# Klanten templates
echo "Kopiëren klanten templates..."
cp "./index (1) (1).html" ./templates/customers/index.html
cp "./create (1) (1).html" ./templates/customers/create.html
cp "./edit (1) (1).html" ./templates/customers/edit.html
cp "./view (1) (1).html" ./templates/customers/view.html

# Facturen templates
echo "Kopiëren facturen templates..."
cp "./index (2) (1).html" ./templates/invoices/index.html
cp "./create (2) (1).html" ./templates/invoices/create.html
cp "./edit (2) (1).html" ./templates/invoices/edit.html
cp "./view (2) (1).html" ./templates/invoices/view.html

# Contracten templates
echo "Kopiëren contracten templates..."
cp "./index (3) (1).html" ./templates/contracts/index.html
cp "./create (3) (1).html" ./templates/contracts/create.html
cp "./edit (3) (1).html" ./templates/contracts/edit.html
cp "./view (3) (1).html" ./templates/contracts/view.html
cp "./sign (1) (1).html" ./templates/contracts/sign.html

# Email templates
echo "Kopiëren email templates..."
cp "./index (4) (1).html" ./templates/emails/index.html
cp "./create (4) (1).html" ./templates/emails/create.html
cp "./view (4) (1).html" ./templates/emails/view.html

echo "Alle templates gekopieerd!"
