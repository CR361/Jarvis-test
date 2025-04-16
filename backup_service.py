import os
import logging
import json
import datetime
import time
from app import app, db
from models import Customer, Invoice, InvoiceItem, Communication, Contract

def create_backup():
    """
    Maakt een verzameling van alle bestanden die voor backup in aanmerking komen.
    Bereidt de individuele bestanden voor om apart te kunnen downloaden.
    
    Returns:
        tuple: (backup_dir, file_list)
            - backup_dir: pad naar de backup directory
            - file_list: lijst met bestand-informatie voor downloads
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.getcwd(), 'backups')
    
    # Maak de backup directory als deze niet bestaat
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Maak een specifieke map voor deze backup met alle losse bestanden
    backup_dir_name = f'jarvis_backup_{timestamp}'
    individual_backup_dir = os.path.join(backup_dir, backup_dir_name)
    if not os.path.exists(individual_backup_dir):
        os.makedirs(individual_backup_dir)
    
    try:
        # Haal de database gegevens op
        backup_data = get_all_data()
        
        # Maak aparte backup bestanden voor alle code bestanden
        file_list = create_individual_backups(individual_backup_dir, backup_data)
        
        app.logger.info(f"Backup bestanden voorbereid in: {individual_backup_dir}")
        
        return individual_backup_dir, file_list
    except Exception as e:
        app.logger.error(f"Fout bij het voorbereiden van backup bestanden: {e}")
        raise

def get_all_data():
    """Haalt alle data uit de database op in een gestructureerd formaat"""
    
    backup_data = {
        'created_at': datetime.datetime.now().isoformat(),
        'version': '1.1',  # Versie informatie toegevoegd in v1.1
        'customers': [],
        'invoices': [],
        'invoice_items': [],
        'communications': [],
        'contracts': []
    }
    
    # Klanten backup
    customers = Customer.query.all()
    for customer in customers:
        customer_data = {
            'id': customer.id,
            'name': customer.name,
            'company': customer.company,
            'kvk_number': customer.kvk_number,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'city': customer.city,
            'postal_code': customer.postal_code,
            'country': customer.country,
            'notes': customer.notes,
            'created_at': customer.created_at.isoformat() if customer.created_at else None,
            'updated_at': customer.updated_at.isoformat() if customer.updated_at else None
        }
        backup_data['customers'].append(customer_data)
    
    # Facturen backup
    invoices = Invoice.query.all()
    for invoice in invoices:
        invoice_data = {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'customer_id': invoice.customer_id,
            'issue_date': invoice.issue_date.isoformat() if invoice.issue_date else None,
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'total_amount': invoice.total_amount,
            'amount_paid': invoice.amount_paid,
            'is_paid': invoice.is_paid,
            'payment_date': invoice.payment_date.isoformat() if invoice.payment_date else None,
            'notes': invoice.notes,
            'created_at': invoice.created_at.isoformat() if invoice.created_at else None,
            'updated_at': invoice.updated_at.isoformat() if invoice.updated_at else None
        }
        backup_data['invoices'].append(invoice_data)
    
    # Factuuritems backup
    invoice_items = InvoiceItem.query.all()
    for item in invoice_items:
        item_data = {
            'id': item.id,
            'invoice_id': item.invoice_id,
            'description': item.description,
            'quantity': item.quantity,
            'unit_price': item.unit_price
        }
        backup_data['invoice_items'].append(item_data)
    
    # Communicatie backup
    communications = Communication.query.all()
    for comm in communications:
        comm_data = {
            'id': comm.id,
            'customer_id': comm.customer_id,
            'type': comm.type,
            'subject': comm.subject,
            'content': comm.content,
            'date': comm.date.isoformat() if comm.date else None,
            'created_at': comm.created_at.isoformat() if comm.created_at else None
        }
        backup_data['communications'].append(comm_data)
    
    # Contracten backup
    contracts = Contract.query.all()
    for contract in contracts:
        contract_data = {
            'id': contract.id,
            'customer_id': contract.customer_id,
            'title': contract.title,
            'content': contract.content,
            'status': contract.status,
            'signing_url': contract.signing_url,
            'signature_data': contract.signature_data, # Voeg handtekening data toe indien beschikbaar
            'signed_at': contract.signed_at.isoformat() if contract.signed_at else None,
            'signed_by': contract.signed_by,
            'signed_ip': contract.signed_ip,
            'created_at': contract.created_at.isoformat() if contract.created_at else None,
            'updated_at': contract.updated_at.isoformat() if contract.updated_at else None,
            'sent_at': contract.sent_at.isoformat() if contract.sent_at else None
        }
        backup_data['contracts'].append(contract_data)
    
    return backup_data

def create_individual_backups(backup_dir, backup_data):
    """
    Maakt aparte bestanden voor elke code file in de backup.
    Dit maakt het gemakkelijker om individuele bestanden te bekijken of te importeren.
    
    Args:
        backup_dir: Directory waar de aparte bestanden moeten worden opgeslagen
        backup_data: Dictionary met de backup data
        
    Returns:
        list: Lijst met informatie over de aangemaakte bestanden
    """
    # Maak een apart JSON-bestand met alleen de database gegevens
    db_json_path = os.path.join(backup_dir, 'database_data.json')
    with open(db_json_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    # Creëer een HTML-bestand met de volledige backup
    html_backup_path = os.path.join(backup_dir, 'jarvis_complete_backup.html')
    create_complete_backup(html_backup_path, backup_data)
    
    # Voeg nog een speciale download voor directe links toe (een HTML-pagina met links naar bestanden)
    download_links_path = os.path.join(backup_dir, 'direct_downloads.html')
    create_download_links_page(download_links_path, backup_dir)
    
    # Bereid een lijst voor met bestandsinfo voor de frontend
    files_info = [
        {'name': 'database_data.json', 'description': 'Database gegevens (JSON)', 'path': os.path.basename(db_json_path), 'type': 'data'},
        {'name': 'jarvis_complete_backup.html', 'description': 'Complete backup met code en data (HTML)', 'path': os.path.basename(html_backup_path), 'type': 'complete'},
        {'name': 'direct_downloads.html', 'description': 'Download links voor alle bestanden', 'path': os.path.basename(download_links_path), 'type': 'links'}
    ]
    
    return files_info

def create_complete_backup(backup_path, backup_data):
    """
    Maakt een volledig HTML-backup bestand met:
    1. Alle applicatiecode (Python files)
    2. Alle sjabloon-bestanden (templates)
    3. Stylesheets en JavaScript bestanden
    4. Database-gegevens (klanten, facturen, contracten, etc.)
    """
    
    # Alle code-bestanden die in de backup moeten worden opgenomen
    code_files = [
        {'name': 'app.py', 'path': 'app.py', 'type': 'Backend'},
        {'name': 'main.py', 'path': 'main.py', 'type': 'Backend'},
        {'name': 'models.py', 'path': 'models.py', 'type': 'Backend'},
        {'name': 'routes.py', 'path': 'routes.py', 'type': 'Backend'},
        {'name': 'forms.py', 'path': 'forms.py', 'type': 'Backend'},
        {'name': 'backup_service.py', 'path': 'backup_service.py', 'type': 'Backend'},
        {'name': 'email_service.py', 'path': 'email_service.py', 'type': 'Backend'},
        {'name': 'contract_templates.py', 'path': 'contract_templates.py', 'type': 'Backend'},
        {'name': 'restore_data.py', 'path': 'restore_data.py', 'type': 'Backend v1.1'}
    ]
    
    # Voeg templates toe
    templates_dir = os.path.join(os.getcwd(), 'templates')
    if os.path.exists(templates_dir):
        for root, dirs, files in os.walk(templates_dir):
            rel_path = os.path.relpath(root, os.getcwd())
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(rel_path, file)
                    code_files.append({
                        'name': file_path, 
                        'path': file_path,
                        'type': 'Template'
                    })
                    
    # Voeg static files toe (CSS, JS)
    static_dir = os.path.join(os.getcwd(), 'static')
    if os.path.exists(static_dir):
        for root, dirs, files in os.walk(static_dir):
            rel_path = os.path.relpath(root, os.getcwd())
            for file in files:
                if file.endswith(('.css', '.js')):
                    file_path = os.path.join(rel_path, file)
                    code_files.append({
                        'name': file_path, 
                        'path': file_path,
                        'type': 'Static'
                    })
    
    # Bouw het HTML-bestand
    timestamp = datetime.datetime.now()
    formatted_date = timestamp.strftime("%d-%m-%Y %H:%M:%S")
    
    # Begin met het HTML-framework en CSS-stijlen
    html_content = generate_html_header(formatted_date)
    
    # Voeg alle codecontent toe
    html_content += generate_code_content(code_files)
    
    # Voeg database backup json toe in een verborgen div voor gemakkelijk herstel
    html_content += generate_data_content(backup_data)
    
    # Voeg restore instructies toe
    html_content += generate_restore_instructions()
    
    # Voeg JavaScript toe en sluit het HTML-bestand af
    html_content += generate_html_footer()
    
    # Schrijf het volledige HTML-bestand
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return True

def create_download_links_page(backup_path, backup_dir):
    """
    Maakt een eenvoudige HTML-pagina met directe download links voor alle
    bestanden in de backup directory.
    """
    files = []
    
    # Verzamel alle bestanden in de backup directory
    for root, dirs, filenames in os.walk(backup_dir):
        for filename in filenames:
            # Sla dit bestand zelf over
            if filename == os.path.basename(backup_path):
                continue
                
            rel_path = os.path.relpath(os.path.join(root, filename), backup_dir)
            files.append({
                'name': filename,
                'path': rel_path,
                'size': os.path.getsize(os.path.join(root, filename)),
                'modified': os.path.getmtime(os.path.join(root, filename))
            })
    
    # Sorteer bestanden op grootte (grootste eerst)
    files.sort(key=lambda x: x['size'], reverse=True)
    
    # Begin met het bouwen van het HTML-bestand
    html_content = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis - Download Bestanden</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1 {{
            color: #3498db;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .file-list {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .file-list th {{
            background-color: #2c3e50;
            color: white;
            text-align: left;
            padding: 12px;
        }}
        
        .file-list td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        
        .file-list tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        
        .file-list tr:hover {{
            background-color: #e9f7fe;
        }}
        
        .file-size {{
            text-align: right;
            white-space: nowrap;
        }}
        
        .file-date {{
            white-space: nowrap;
            color: #666;
        }}
        
        .download-link {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .download-link:hover {{
            text-decoration: underline;
        }}
        
        .file-type-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-left: 8px;
        }}
        
        .file-type-json {{
            background-color: #4caf50;
            color: white;
        }}
        
        .file-type-html {{
            background-color: #ff9800;
            color: white;
        }}
        
        .note {{
            background-color: #e9f7fe;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>Jarvis CRM - Backup Downloads</h1>
    
    <div class="note">
        <p><strong>Let op:</strong> Deze pagina bevat downloadlinks voor alle bestanden in uw backup. 
        Sla deze bestanden op een veilige plaats op voor toekomstig gebruik.</p>
        <p>Voor een volledige backup met alle code en gegevens, download het "jarvis_complete_backup.html" bestand.</p>
    </div>

    <table class="file-list">
        <thead>
            <tr>
                <th>Bestandsnaam</th>
                <th>Grootte</th>
                <th>Laatst gewijzigd</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # Voeg elke bestand toe aan de tabel
    for file in files:
        # Format bestandsgrootte naar KB/MB
        size_str = format_file_size(file['size'])
        
        # Format laatste wijzigingsdatum
        mod_date = datetime.datetime.fromtimestamp(file['modified']).strftime('%d-%m-%Y %H:%M')
        
        # Bepaal het bestandstype badge
        file_type_class = ""
        file_type_badge = ""
        
        if file['name'].endswith('.json'):
            file_type_class = "file-type-json"
            file_type_badge = '<span class="file-type-badge file-type-json">JSON</span>'
        elif file['name'].endswith('.html'):
            file_type_class = "file-type-html"
            file_type_badge = '<span class="file-type-badge file-type-html">HTML</span>'
        
        html_content += f"""
            <tr>
                <td>
                    <a href="/backup/download/{file['path']}" class="download-link">{file['name']}</a>
                    {file_type_badge}
                </td>
                <td class="file-size">{size_str}</td>
                <td class="file-date">{mod_date}</td>
            </tr>"""
    
    # Sluit de tabel en het HTML-bestand af
    html_content += """
        </tbody>
    </table>
</body>
</html>"""
    
    # Schrijf het HTML-bestand
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def format_file_size(size_in_bytes):
    """Format bestandsgrootte in menselijk leesbaar formaat (KB, MB)"""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"

def generate_html_header(formatted_date):
    """Genereer de HTML header met CSS voor de complete backup"""
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis - Complete Backup</title>
    <style>
        :root {{
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --accent-color: #00c7fe;
            --background-light: #f8f9fa;
            --background-dark: #343a40;
            --text-light: #f8f9fa;
            --text-dark: #212529;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-dark);
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }}
        
        h1, h2, h3, h4 {{
            color: var(--secondary-color);
            font-weight: 600;
        }}
        
        /* JARVIS branding */
        .jarvis-brand {{
            font-family: 'Arial', sans-serif;
            font-weight: bold;
            letter-spacing: 2px;
            color: var(--accent-color);
        }}
        
        pre {{
            background: var(--background-light);
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            border: 1px solid #ddd;
            margin: 0;
            line-height: 1.4;
        }}
        
        /* Header styling */
        .file-header {{
            background: var(--primary-color);
            color: var(--text-light);
            padding: 10px 15px;
            border-radius: 8px 8px 0 0;
            margin-bottom: 0;
            font-weight: 500;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .file-type {{
            background: rgba(255, 255, 255, 0.2);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
        }}
        
        /* Table of contents */
        .toc {{
            background: var(--background-light);
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 20px;
            margin-bottom: 10px;
        }}
        
        .toc > ul {{
            padding-left: 0;
        }}
        
        .toc li {{
            margin-bottom: 8px;
        }}
        
        .toc a {{
            color: var(--primary-color);
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .toc a:hover {{
            color: var(--accent-color);
            text-decoration: underline;
        }}
        
        /* Backup info */
        .backup-info {{
            background: #e9f7fe;
            border-left: 4px solid var(--accent-color);
            padding: 15px 20px;
            margin-bottom: 30px;
            border-radius: 0 8px 8px 0;
        }}
        
        .backup-info h1 {{
            margin-top: 0;
            color: var(--accent-color);
        }}
        
        /* Code and section containers */
        .code-section {{
            margin-bottom: 40px;
        }}
        
        .code-container {{
            margin-top: 0;
            border-radius: 0 0 8px 8px;
        }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            margin-bottom: 30px;
            border-bottom: 1px solid #ddd;
        }}
        
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border: 1px solid transparent;
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            background-color: var(--background-light);
            margin-right: 4px;
            color: var(--text-dark);
        }}
        
        .tab:hover {{
            background-color: #e9ecef;
        }}
        
        .tab.active {{
            background-color: #fff;
            border-color: #ddd;
            border-bottom-color: #fff;
            font-weight: 600;
            color: var(--primary-color);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        /* Data section */
        .data-section {{
            background: var(--background-light);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 40px;
        }}
        
        .data-section h3 {{
            color: var(--primary-color);
            margin-top: 0;
        }}
        
        .data-item {{
            background: #fff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .data-header {{
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }}
        
        .data-name {{
            font-weight: 600;
            color: var(--secondary-color);
        }}
        
        .data-id {{
            color: #6c757d;
            font-size: 0.9rem;
        }}
        
        .data-content {{
            white-space: pre-wrap;
        }}
        
        /* Utility */
        .mb-1 {{ margin-bottom: 0.25rem !important; }}
        .mb-2 {{ margin-bottom: 0.5rem !important; }}
        .mb-3 {{ margin-bottom: 1rem !important; }}
        .mb-4 {{ margin-bottom: 1.5rem !important; }}
        .mb-5 {{ margin-bottom: 3rem !important; }}
        
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .badge-success {{ background: var(--success-color); color: #fff; }}
        .badge-warning {{ background: var(--warning-color); color: #212529; }}
        .badge-danger {{ background: var(--danger-color); color: #fff; }}
        
        /* Scripts section at the end */
        .script-section {{
            margin-top: 50px;
        }}
    </style>
</head>
<body>
    <div class="backup-info">
        <h1 class="jarvis-brand">JARVIS - COMPLETE BACKUP</h1>
        <p><strong>Backup created:</strong> {formatted_date}</p>
        <p><strong>Version:</strong> 1.1</p>
        <p>Deze backup bevat alle code en data van het Jarvis systeem. Bewaar dit bestand veilig voor toekomstig gebruik of herstel.</p>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="switchTab('code-tab')">Applicatiecode</div>
        <div class="tab" onclick="switchTab('data-tab')">Database Gegevens</div>
        <div class="tab" onclick="switchTab('info-tab')">Restore Instructies</div>
    </div>
"""

def generate_code_content(code_files):
    """Genereer het HTML-gedeelte met alle code inhoud"""
    
    html_content = """    <div id="code-tab" class="tab-content active">
        <div class="toc">
            <h2>Inhoudsopgave</h2>
            <ul>
"""
    
    # Groepeer bestanden per type
    file_groups = {}
    for file in code_files:
        file_type = file.get('type', 'Overig')
        if file_type not in file_groups:
            file_groups[file_type] = []
        file_groups[file_type].append(file)
    
    # Voeg inhoudsopgave toe gegroepeerd per type
    for group_name, files in file_groups.items():
        html_content += f'            <li><strong>{group_name}</strong><ul>\n'
        for file in files:
            file_id = file['name'].replace('.', '-').replace('/', '-')
            html_content += f'                <li><a href="#{file_id}">{file["name"]}</a></li>\n'
        html_content += '            </ul></li>\n'
    
    html_content += """            </ul>
        </div>
        
        <!-- Code section starts -->
"""
    
    # Voeg code bestanden toe aan de HTML
    for file in code_files:
        file_path = file['path']
        file_id = file['name'].replace('.', '-').replace('/', '-')
        
        try:
            # Controleer of bestand bestaat
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    
                # Voeg de codeblok toe
                html_content += f'''
        <div class="code-section">
            <div class="file-header">
                <div>{file["name"]}</div>
                <div class="file-type">{file.get("type", "Unknown")}</div>
            </div>
            <pre class="code-container" id="{file_id}">{escape_html(file_content)}</pre>
        </div>
'''
            else:
                html_content += f'''
        <div class="code-section">
            <div class="file-header">
                <div>{file["name"]}</div>
                <div class="file-type">{file.get("type", "Unknown")}</div>
            </div>
            <pre class="code-container" id="{file_id}">Bestand niet gevonden: {file_path}</pre>
        </div>
'''
        except Exception as e:
            html_content += f'''
        <div class="code-section">
            <div class="file-header">
                <div>{file["name"]}</div>
                <div class="file-type">{file.get("type", "Error")}</div>
            </div>
            <pre class="code-container" id="{file_id}">Fout bij lezen van bestand: {str(e)}</pre>
        </div>
'''
    
    html_content += "    </div>\n"
    
    return html_content

def generate_data_content(backup_data):
    """Genereer het HTML-gedeelte met database gegevens"""
    
    # Eerst toevoegen van de volledige data als JSON in een verborgen div
    html_content = f'''
    <div style="display: none;" id="full-database-backup">
{json.dumps(backup_data, ensure_ascii=False, indent=2)}
    </div>
    
    <div id="data-tab" class="tab-content">
        <h2>Database Gegevens</h2>
        <p>Deze sectie bevat alle gegevens uit de database. Klik op "Download Data als JSON" om een download te starten
           van alleen de database gegevens in JSON-formaat voor import in een nieuw systeem.</p>
        
        <button onclick="downloadDatabaseBackup()" class="btn">Download Data als JSON</button>
        
        <div class="data-section">
            <h3>Klanten ({len(backup_data.get("customers", []))})</h3>
'''
    
    # Voeg klantgegevens toe
    customers = backup_data.get("customers", [])
    for customer in customers[:5]:  # Toon alleen de eerste 5 voor kortere pagina
        html_content += f'''
            <div class="data-item">
                <div class="data-header">
                    <div class="data-name">{escape_html(customer.get("name", ""))}</div>
                    <div class="data-id">ID: {customer.get("id", "")}</div>
                </div>
                <div>
                    <div><strong>Bedrijf:</strong> {escape_html(customer.get("company", "") or "N/A")}</div>
                    <div><strong>E-mail:</strong> {escape_html(customer.get("email", ""))}</div>
                    <div><strong>Telefoon:</strong> {escape_html(customer.get("phone", "") or "N/A")}</div>
                </div>
            </div>
'''
    
    if len(customers) > 5:
        html_content += f'''
            <div class="data-item">
                <p>... en {len(customers) - 5} meer klanten</p>
            </div>
'''
    
    # Voeg factuurgegevens toe
    invoices = backup_data.get("invoices", [])
    html_content += f'''
        </div>
        
        <div class="data-section">
            <h3>Facturen ({len(invoices)})</h3>
'''
    
    for invoice in invoices[:5]:  # Toon alleen de eerste 5
        is_paid = invoice.get("is_paid", False)
        status_badge = '<span class="badge badge-success">Betaald</span>' if is_paid else '<span class="badge badge-warning">Open</span>'
        
        html_content += f'''
            <div class="data-item">
                <div class="data-header">
                    <div class="data-name">{escape_html(invoice.get("invoice_number", ""))}</div>
                    <div>{status_badge}</div>
                </div>
                <div>
                    <div><strong>Klant ID:</strong> {invoice.get("customer_id", "")}</div>
                    <div><strong>Uitgiftedatum:</strong> {format_date(invoice.get("issue_date", ""))}</div>
                    <div><strong>Vervaldatum:</strong> {format_date(invoice.get("due_date", ""))}</div>
                    <div><strong>Totaalbedrag:</strong> €{invoice.get("total_amount", 0)}</div>
                </div>
            </div>
'''
    
    if len(invoices) > 5:
        html_content += f'''
            <div class="data-item">
                <p>... en {len(invoices) - 5} meer facturen</p>
            </div>
'''
    
    # Voeg factuuritems toe
    invoice_items = backup_data.get("invoice_items", [])
    html_content += f'''
        </div>
        
        <div class="data-section">
            <h3>Factuuritems ({len(invoice_items)})</h3>
'''
    
    # Voeg samenvatting toe in plaats van alle items
    html_content += f'''
            <div class="data-item">
                <p>Er zijn in totaal {len(invoice_items)} factuuritems gebackupt.</p>
                <p>Download de volledige backup om alle details te bekijken.</p>
            </div>
'''
    
    # Voeg communicatie toe
    communications = backup_data.get("communications", [])
    html_content += f'''
        </div>
        
        <div class="data-section">
            <h3>Communicatie ({len(communications)})</h3>
'''
    
    for comm in communications[:3]:  # Toon alleen enkele voorbeelden
        comm_date = format_date(comm.get("date", ""))
        html_content += f'''
            <div class="data-item">
                <div class="data-header">
                    <div class="data-name">{escape_html(comm.get("subject", "") or comm.get("type", "").title())}</div>
                    <div class="data-id">{comm_date}</div>
                </div>
                <div>
                    <div><strong>Type:</strong> {comm.get("type", "").title()}</div>
                    <div><strong>Klant ID:</strong> {comm.get("customer_id", "")}</div>
                </div>
            </div>
'''
    
    if len(communications) > 3:
        html_content += f'''
            <div class="data-item">
                <p>... en {len(communications) - 3} meer communicatie-items</p>
            </div>
'''
    
    # Voeg contracten toe
    contracts = backup_data.get("contracts", [])
    html_content += f'''
        </div>
        
        <div class="data-section">
            <h3>Contracten ({len(contracts)})</h3>
'''
    
    for contract in contracts[:3]:  # Toon alleen enkele voorbeelden
        html_content += f'''
            <div class="data-item">
                <div class="data-header">
                    <div class="data-name">{escape_html(contract.get("title", ""))}</div>
                    <div class="data-id">Status: {contract.get("status", "").title()}</div>
                </div>
                <div>
                    <div><strong>Klant ID:</strong> {contract.get("customer_id", "")}</div>
                    <div><strong>Gemaakt op:</strong> {format_date(contract.get("created_at", ""))}</div>
                </div>
            </div>
'''
    
    if len(contracts) > 3:
        html_content += f'''
            <div class="data-item">
                <p>... en {len(contracts) - 3} meer contracten</p>
            </div>
'''
    
    html_content += '''
        </div>
    </div>
'''
    
    return html_content

def generate_restore_instructions():
    """Genereer het HTML-gedeelte met restore instructies"""
    
    return '''
    <div id="info-tab" class="tab-content">
        <h2>Restore Instructies</h2>
        
        <div class="data-section">
            <h3>Hoe gebruik je deze backup</h3>
            <p>Deze complete backup bevat zowel alle code van de applicatie als alle gegevens uit de database.
            Er zijn verschillende manieren om deze backup te gebruiken:</p>
            
            <div class="data-item">
                <h4>Optie 1: Restore met de database_data.json</h4>
                <p>Deze methode is het meest geschikt als je al een functionerende installatie hebt en alleen de data wilt herstellen.</p>
                <ol>
                    <li>Download de <strong>database_data.json</strong> uit deze backup.</li>
                    <li>Plaats dit bestand in de hoofdmap van je Jarvis CRM installatie.</li>
                    <li>Start de applicatie - deze zal automatisch de gegevens importeren als de database leeg is.</li>
                </ol>
            </div>
            
            <div class="data-item">
                <h4>Optie 2: Volledige Restore (voor geavanceerde gebruikers)</h4>
                <p>Deze methode is geschikt als je een volledige nieuwe installatie nodig hebt, inclusief alle code:</p>
                <ol>
                    <li>Op het tabblad "Applicatiecode" staan alle bestanden met hun inhoud.</li>
                    <li>Maak handmatig elk bestand aan in je nieuwe project met dezelfde mappenstructuur.</li>
                    <li>Herstel de database gegevens met de database_data.json zoals beschreven in Optie 1.</li>
                </ol>
            </div>
            
            <div class="data-item">
                <h4>Automatisch herstel via HTML-bestand</h4>
                <p>Bij de nieuwste versie van Jarvis CRM wordt automatisch herstellen ondersteund:</p>
                <ol>
                    <li>Plaats dit HTML-bestand in de hoofdmap van een nieuw Jarvis CRM installatie.</li>
                    <li>Start de applicatie - deze zal automatisch herkennen dat er een HTML-backup aanwezig is.</li>
                    <li>De gegevens worden automatisch geïmporteerd als de database leeg is.</li>
                </ol>
            </div>
        </div>
        
        <div class="data-section">
            <h3>Backup Informatie</h3>
            <div class="data-item">
                <p><strong>Versie:</strong> 1.1</p>
                <p><strong>Datum:</strong> <span id="backup-date"></span></p>
                <p><strong>Aantal klanten:</strong> <span id="customer-count"></span></p>
                <p><strong>Aantal facturen:</strong> <span id="invoice-count"></span></p>
                <p><strong>Aantal contracten:</strong> <span id="contract-count"></span></p>
            </div>
        </div>
    </div>
'''

def generate_html_footer():
    """Genereer het HTML-slot met JavaScript functies"""
    
    return '''
    <!-- Scripts -->
    <script>
        // Functie om tabbladen te wisselen
        function switchTab(tabId) {
            // Verwijder 'active' class van alle tabbladen en content
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Voeg 'active' class toe aan het geselecteerde tabblad
            document.querySelectorAll('.tab').forEach(tab => {
                if (tab.getAttribute('onclick').includes(tabId)) {
                    tab.classList.add('active');
                }
            });
            
            // Toon de bijbehorende inhoud
            document.getElementById(tabId).classList.add('active');
        }
        
        // Functie om database backup te downloaden als JSON
        function downloadDatabaseBackup() {
            // Haal de backup data op uit de verborgen div
            const backupJson = document.getElementById('full-database-backup').textContent;
            
            // Maak een Blob van de data
            const blob = new Blob([backupJson], { type: 'application/json' });
            
            // Maak een download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'database_backup_' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
            
            // Trigger de download
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);
        }
        
        // Functie om backup info statistieken te tonen
        function showBackupStats() {
            try {
                // Parse de JSON data
                const backupJson = document.getElementById('full-database-backup').textContent;
                const backupData = JSON.parse(backupJson);
                
                // Toon de gegevens
                document.getElementById('backup-date').textContent = formatISODate(backupData.created_at);
                document.getElementById('customer-count').textContent = backupData.customers ? backupData.customers.length : 0;
                document.getElementById('invoice-count').textContent = backupData.invoices ? backupData.invoices.length : 0;
                document.getElementById('contract-count').textContent = backupData.contracts ? backupData.contracts.length : 0;
            } catch (e) {
                console.error('Error showing backup stats:', e);
            }
        }
        
        // Helper functie om ISO datum te formatteren
        function formatISODate(isoDateString) {
            if (!isoDateString) return 'Onbekend';
            
            try {
                const date = new Date(isoDateString);
                return date.toLocaleDateString('nl-NL', { 
                    day: '2-digit', 
                    month: '2-digit', 
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                return isoDateString;
            }
        }
        
        // Initialiseer na het laden van de pagina
        document.addEventListener('DOMContentLoaded', function() {
            showBackupStats();
        });
    </script>
</body>
</html>
'''

def escape_html(text):
    """Escape HTML karakters in text"""
    if text is None:
        return ""
    
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")

def format_date(iso_date):
    """Format ISO date string naar leesbare datum"""
    if not iso_date:
        return "N/A"
    
    try:
        # Probeer de datum te parsen en formatteren
        date_obj = datetime.datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return date_obj.strftime("%d-%m-%Y")
    except:
        # Bij fouten, gebruik de originele string
        return iso_date