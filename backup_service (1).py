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
    
    timestamp = datetime.datetime.now()
    formatted_date = timestamp.strftime("%d-%m-%Y %H:%M:%S")
    
    # Begin met het bouwen van het HTML-bestand
    html_content = f"""<!DOCTYPE html>
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

    <div id="code-tab" class="tab-content active">
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
"""
    
    # Voeg bestanden toe per groep
    for group_name, files in file_groups.items():
        html_content += f'        <h2>{group_name}</h2>\n'
        for file in files:
            file_id = file['name'].replace('.', '-').replace('/', '-')
            file_type = file.get('type', 'Overig')
            
            html_content += f"""        <div class="code-section">
            <div class="file-header">
                <span>{file['name']}</span>
                <span class="file-type">{file_type}</span>
            </div>
            <pre class="code-container">
"""
            
            try:
                with open(file['path'], 'r', encoding='utf-8') as f:
                    code_content = f.read()
                    # Escape HTML characters
                    code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    html_content += code_content
            except Exception as e:
                html_content += f"Error reading file: {str(e)}"
            
            html_content += """            </pre>
        </div>
"""
    
    # Data tab content - geef alle database gegevens weer
    html_content += """    </div>

    <div id="data-tab" class="tab-content">
        <h2>Database Gegevens</h2>
        <p>Deze sectie bevat alle data uit de database, geserialiseerd in JSON-formaat. Deze data kan worden gebruikt om het systeem te herstellen.</p>
        
        <!-- Database gegevens -->
"""

    # Voeg database gegevens toe
    if 'customers' in backup_data and backup_data['customers']:
        html_content += """        <div class="data-section">
            <h3>Klanten ({count})</h3>
""".format(count=len(backup_data['customers']))

        for customer in backup_data['customers']:
            html_content += f"""            <div class="data-item">
                <div class="data-header">
                    <span class="data-name">{customer.get('name', 'Onbekende klant')}</span>
                    <span class="data-id">ID: {customer.get('id', 'N/A')}</span>
                </div>
                <div>
                    <p><strong>Bedrijf:</strong> {customer.get('company', 'N/A')}</p>
                    <p><strong>KVK:</strong> {customer.get('kvk_number', 'N/A')}</p>
                    <p><strong>Email:</strong> {customer.get('email', 'N/A')}</p>
                    <p><strong>Telefoon:</strong> {customer.get('phone', 'N/A')}</p>
                    <p><strong>Adres:</strong> {customer.get('address', '')} {customer.get('postal_code', '')} {customer.get('city', '')} {customer.get('country', '')}</p>
                </div>
            </div>
"""
        html_content += "        </div>\n"

    if 'invoices' in backup_data and backup_data['invoices']:
        html_content += """        <div class="data-section">
            <h3>Facturen ({count})</h3>
""".format(count=len(backup_data['invoices']))

        for invoice in backup_data['invoices']:
            status_badge = ""
            if invoice.get('is_paid'):
                status_badge = '<span class="badge badge-success">Betaald</span>'
            else:
                status_badge = '<span class="badge badge-warning">Openstaand</span>'
                
            html_content += f"""            <div class="data-item">
                <div class="data-header">
                    <span class="data-name">Factuur {invoice.get('invoice_number', 'N/A')} {status_badge}</span>
                    <span class="data-id">ID: {invoice.get('id', 'N/A')}</span>
                </div>
                <div>
                    <p><strong>Klant ID:</strong> {invoice.get('customer_id', 'N/A')}</p>
                    <p><strong>Datum:</strong> {invoice.get('issue_date', 'N/A')}</p>
                    <p><strong>Vervaldatum:</strong> {invoice.get('due_date', 'N/A')}</p>
                    <p><strong>Bedrag:</strong> €{invoice.get('total_amount', '0.00')}</p>
                    <p><strong>Notities:</strong> {invoice.get('notes', 'Geen notities')}</p>
                </div>
            </div>
"""
        html_content += "        </div>\n"

    if 'contracts' in backup_data and backup_data['contracts']:
        html_content += """        <div class="data-section">
            <h3>Contracten ({count})</h3>
""".format(count=len(backup_data['contracts']))

        for contract in backup_data['contracts']:
            status = contract.get('status', 'concept')
            status_badge = ""
            if status == 'concept':
                status_badge = '<span class="badge badge-warning">Concept</span>'
            elif status == 'verzonden':
                status_badge = '<span class="badge badge-info">Verzonden</span>'
            elif status == 'ondertekend':
                status_badge = '<span class="badge badge-success">Ondertekend</span>'
            elif status == 'geweigerd':
                status_badge = '<span class="badge badge-danger">Geweigerd</span>'
                
            html_content += f"""            <div class="data-item">
                <div class="data-header">
                    <span class="data-name">{contract.get('title', 'Onbekend contract')} {status_badge}</span>
                    <span class="data-id">ID: {contract.get('id', 'N/A')}</span>
                </div>
                <div>
                    <p><strong>Klant ID:</strong> {contract.get('customer_id', 'N/A')}</p>
                    <p><strong>Aangemaakt:</strong> {contract.get('created_at', 'N/A')}</p>
                    <p><strong>Ondertekend:</strong> {contract.get('signed_at', 'Niet ondertekend')}</p>
                </div>
                <div class="data-content">
                    <h4>Inhoud:</h4>
                    <div style="background: #f9f9f9; padding: 10px; border-radius: 5px; white-space: pre-wrap;">{contract.get('content', 'Geen inhoud beschikbaar')}</div>
                </div>
            </div>
"""
        html_content += "        </div>\n"

    # Voeg ook de ruwe JSON data toe als verborgen veld (voor eenvoudige restore)
    html_content += """
        <!-- Volledige JSON data (verborgen) -->
        <div style="display: none;" id="full-database-backup">
"""
    json_data = json.dumps(backup_data, ensure_ascii=False, indent=2)
    # Escape voor HTML
    json_data = json_data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    html_content += json_data
    html_content += """
        </div>
    </div>

    <div id="info-tab" class="tab-content">
        <h2>Restore Instructies</h2>
        <div class="data-section">
            <h3>Hoe te herstellen</h3>
            <p>Volg deze stappen om het Jarvis systeem te herstellen vanuit deze backup:</p>
            <ol>
                <li>Maak een nieuw Replit Python project aan</li>
                <li>Installeer de benodigde dependencies:
                    <ul>
                        <li>Flask</li>
                        <li>Flask-SQLAlchemy</li>
                        <li>Flask-Mail</li>
                        <li>Flask-WTF</li>
                        <li>WTForms</li>
                        <li>email-validator</li>
                        <li>gunicorn</li>
                        <li>psycopg2-binary</li>
                        <li>sendgrid</li>
                    </ul>
                </li>
                <li>Kopieer elke bestand uit de "Applicatiecode" tab naar het juiste bestand in je project</li>
                <li>Stel een PostgreSQL database in met de secrets DATABASE_URL</li>
                <li>Zorg ervoor dat de directory-structuur correct is, inclusief:
                    <ul>
                        <li>/templates (voor HTML templates)</li>
                        <li>/static (voor CSS, JS en andere static bestanden)</li>
                        <li>/static/css</li>
                        <li>/static/js</li>
                        <li>/backups (zal automatisch aangemaakt worden)</li>
                    </ul>
                </li>
                <li><strong>Nieuw in v1.1: Automatische gegevensimport</strong> - Download dit backupbestand en plaats het in de 'backups' map van je nieuwe project. De gegevens worden automatisch geïmporteerd wanneer de applicatie opstart en de database leeg is.</li>
                <li>Start de applicatie door het commando "gunicorn --bind 0.0.0.0:5000 main:app" uit te voeren</li>
            </ol>
            <p>De database zal automatisch worden geïnitialiseerd wanneer de applicatie voor het eerst wordt gestart. Als dit backupbestand aanwezig is in de 'backups' map, worden alle klanten, facturen, contracten en communicaties automatisch geïmporteerd.</p>
        </div>
    </div>

    <script>
        // Simple tab switching functionality
        function switchTab(tabId) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show the selected tab
            document.getElementById(tabId).classList.add('active');
            
            // Update the active tab button
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Find the tab button that was clicked and make it active
            document.querySelectorAll('.tab').forEach(tab => {
                if (tab.getAttribute('onclick').includes(tabId)) {
                    tab.classList.add('active');
                }
            });
        }
        
        // On page load, activate the first tab
        document.addEventListener('DOMContentLoaded', function() {
            switchTab('code-tab');
        });
    </script>
</body>
</html>
"""

    # Schrijf de HTML naar bestand
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    app.logger.info(f"Complete backup gemaakt: {backup_path}")
    return backup_path

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
    
    # Maak JSON bestand met database gegevens
    data_json_path = os.path.join(backup_dir, 'database_data.json')
    with open(data_json_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
    # Maak Node.js versie van de database gegevens
    nodejs_export_path = os.path.join(backup_dir, 'nodejs_export')
    os.makedirs(nodejs_export_path, exist_ok=True)
    
    # Maak de main app.js file
    app_js_path = os.path.join(nodejs_export_path, 'app.js')
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write("""// JARVIS - Node.js Backup Export
const express = require('express');
const path = require('path');
const fs = require('fs');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 3000;

// Set view engine to EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware
app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Import data
const data = require('./data');

// Routes
app.get('/', (req, res) => {
  res.render('dashboard', { 
    title: 'Dashboard',
    customers: data.customers,
    invoices: data.invoices,
    communications: data.communications,
    contracts: data.contracts
  });
});

app.get('/customers', (req, res) => {
  res.render('customers', { 
    title: 'Klanten',
    customers: data.customers
  });
});

app.get('/invoices', (req, res) => {
  res.render('invoices', { 
    title: 'Facturen',
    invoices: data.invoices,
    customers: data.customers
  });
});

app.get('/contracts', (req, res) => {
  res.render('contracts', { 
    title: 'Contracten',
    contracts: data.contracts,
    customers: data.customers
  });
});

app.get('/communications', (req, res) => {
  res.render('communications', { 
    title: 'Communicatie',
    communications: data.communications,
    customers: data.customers
  });
});

// Start server
app.listen(port, () => {
  console.log(`JARVIS Node.js versie draait op http://localhost:${port}`);
});
""")
    
    # Maak package.json
    package_json_path = os.path.join(nodejs_export_path, 'package.json')
    with open(package_json_path, 'w', encoding='utf-8') as f:
        f.write("""{
  "name": "jarvis-nodejs",
  "version": "1.0.0",
  "description": "JARVIS CRM systeem - Node.js versie",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js"
  },
  "dependencies": {
    "body-parser": "^1.20.2",
    "ejs": "^3.1.9",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
""")
    
    # Maak data.js voor de database gegevens
    data_js_path = os.path.join(nodejs_export_path, 'data.js')
    with open(data_js_path, 'w', encoding='utf-8') as f:
        f.write(f"// JARVIS - Geëxporteerde data - {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n")
        
        # Converteer de data naar JavaScript objecten
        f.write("const customers = " + json.dumps(backup_data['customers'], ensure_ascii=False, indent=2) + ";\n\n")
        f.write("const invoices = " + json.dumps(backup_data['invoices'], ensure_ascii=False, indent=2) + ";\n\n")
        f.write("const invoice_items = " + json.dumps(backup_data['invoice_items'], ensure_ascii=False, indent=2) + ";\n\n")
        f.write("const communications = " + json.dumps(backup_data['communications'], ensure_ascii=False, indent=2) + ";\n\n")
        f.write("const contracts = " + json.dumps(backup_data['contracts'], ensure_ascii=False, indent=2) + ";\n\n")
        
        # Exporteer de data
        f.write("module.exports = {\n")
        f.write("  customers,\n")
        f.write("  invoices,\n")
        f.write("  invoice_items,\n")
        f.write("  communications,\n")
        f.write("  contracts\n")
        f.write("};\n")
    
    # Maak een README.md voor de Node.js export
    readme_md_path = os.path.join(nodejs_export_path, 'README.md')
    with open(readme_md_path, 'w', encoding='utf-8') as f:
        f.write(f"""# JARVIS Node.js Export

Deze map bevat een Node.js versie van het JARVIS CRM systeem, geëxporteerd op {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}.

## Installatie

1. Zorg ervoor dat Node.js is geïnstalleerd op je systeem
2. Open een terminal in deze directory
3. Voer het volgende commando uit:

```bash
npm install
```

## Starten van de applicatie

```bash
npm start
```

De applicatie is nu beschikbaar op http://localhost:3000

## Ontwikkelen

```bash
npm run dev
```

Dit start de applicatie met nodemon, waardoor wijzigingen automatisch worden gedetecteerd.

## Structuur

- `app.js`: De hoofdapplicatie
- `data.js`: Alle geëxporteerde data uit het JARVIS systeem
- `views/`: EJS templates voor de frontend (nog aan te maken)
- `public/`: Statische bestanden zoals CSS en client-side JavaScript
""")
    
    # Maak de views en public directory
    views_dir = os.path.join(nodejs_export_path, 'views')
    public_dir = os.path.join(nodejs_export_path, 'public')
    os.makedirs(views_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)
    
    # Maak een eenvoudige dashboard.ejs template
    dashboard_ejs_path = os.path.join(views_dir, 'dashboard.ejs')
    with open(dashboard_ejs_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS - <%= title %></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">JARVIS</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/customers">Klanten</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/invoices">Facturen</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/contracts">Contracten</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/communications">Communicatie</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="jumbotron bg-light p-5 rounded">
            <h1 class="display-4">JARVIS Dashboard</h1>
            <p class="lead">Node.js versie van het JARVIS CRM systeem</p>
            <hr class="my-4">
            <p>Dit is een geëxporteerde versie van de JARVIS database in Node.js formaat.</p>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-3">
                <div class="card text-white bg-primary mb-3">
                    <div class="card-header">Klanten</div>
                    <div class="card-body">
                        <h5 class="card-title"><%= customers.length %></h5>
                        <p class="card-text">Totaal aantal klanten</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success mb-3">
                    <div class="card-header">Facturen</div>
                    <div class="card-body">
                        <h5 class="card-title"><%= invoices.length %></h5>
                        <p class="card-text">Totaal aantal facturen</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-info mb-3">
                    <div class="card-header">Contracten</div>
                    <div class="card-body">
                        <h5 class="card-title"><%= contracts.length %></h5>
                        <p class="card-text">Totaal aantal contracten</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-warning mb-3">
                    <div class="card-header">Communicatie</div>
                    <div class="card-body">
                        <h5 class="card-title"><%= communications.length %></h5>
                        <p class="card-text">Totaal aantal communicaties</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/js/script.js"></script>
</body>
</html>
""")
    
    # Maak een stylecss en script.js
    css_dir = os.path.join(public_dir, 'css')
    js_dir = os.path.join(public_dir, 'js')
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)
    
    with open(os.path.join(css_dir, 'style.css'), 'w', encoding='utf-8') as f:
        f.write("""/* JARVIS - Node.js Export Styles */
body {
    font-family: 'Arial', sans-serif;
    background-color: #f5f5f5;
}

.navbar-brand {
    font-weight: bold;
    letter-spacing: 2px;
}

.jumbotron {
    background-color: #f8f9fa;
    padding: 2rem;
}
""")
    
    with open(os.path.join(js_dir, 'script.js'), 'w', encoding='utf-8') as f:
        f.write("""// JARVIS - Node.js Export Scripts
document.addEventListener('DOMContentLoaded', function() {
    console.log('JARVIS Node.js versie geladen!');
});
""")
    
    # Maak JSON bestand met database gegevens
    data_json_path = os.path.join(backup_dir, 'database_data.json')
    with open(data_json_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    app.logger.info(f"Database JSON backup gemaakt: {data_json_path}")
    
    # Maak een README bestand
    readme_path = os.path.join(backup_dir, 'README.txt')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""JARVIS BACKUP v1.1 - {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}

Deze map bevat een volledige backup van het Jarvis systeem.
Alle bestanden zijn in hun originele staat opgeslagen en kunnen direct 
in een nieuw project worden geplaatst.

Inhoud:
- Python backend bestanden (*.py)
- HTML templates (templates/*.html)
- Static bestanden (CSS, JS, etc.)
- Database gegevens (database_data.json)

Voor automatische import van de database:
1. Plaats het complete backupbestand in de 'backups' map van je nieuwe Jarvis project
2. Start de applicatie - de gegevens worden automatisch geïmporteerd bij de eerste start
""")
    
    # Maak een lijst voor alle bestanden in de backup
    backup_files = []
    
    # Voeg database JSON bestand toe aan de lijst
    rel_data_path = os.path.relpath(data_json_path, os.getcwd())
    backup_files.append({
        'name': 'database_data.json', 
        'path': rel_data_path,
        'display_name': 'Database Gegevens (JSON)',
        'type': 'Data',
        'size': os.path.getsize(data_json_path)
    })
    
    # Voeg README bestand toe aan de lijst
    rel_readme_path = os.path.relpath(readme_path, os.getcwd())
    backup_files.append({
        'name': 'README.txt', 
        'path': rel_readme_path,
        'display_name': 'Readme Bestand',
        'type': 'Info',
        'size': os.path.getsize(readme_path)
    })
    
    # Voeg Node.js bestanden toe aan de lijst
    nodejs_export_dir = os.path.join(backup_dir, 'nodejs_export')
    if os.path.exists(nodejs_export_dir):
        app.logger.info(f"Node.js export directory gevonden: {nodejs_export_dir}")
        for root, dirs, files in os.walk(nodejs_export_dir):
            rel_path = os.path.relpath(root, os.getcwd())
            for file in files:
                file_path = os.path.join(rel_path, file)
                
                # Markeer app.js als de root file voor de Node.js export
                is_root = (file == 'app.js' and root == nodejs_export_dir)
                
                backup_files.append({
                    'name': os.path.relpath(file_path, backup_dir),
                    'path': file_path,
                    'display_name': os.path.relpath(file_path, backup_dir),
                    'type': 'NodeJS',
                    'is_nodejs_root': is_root,
                    'size': os.path.getsize(file_path)
                })
                
                app.logger.debug(f"Node.js bestand toegevoegd aan backup lijst: {file_path}")
    
    # Kopieer alle code bestanden als aparte bestanden
    for file in code_files:
        # Maak het pad voor het backup bestand
        target_path = os.path.join(backup_dir, file['name'])
        
        # Zorg ervoor dat de directory structuur bestaat
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        try:
            # Kopieer de inhoud
            with open(file['path'], 'r', encoding='utf-8') as source:
                content = source.read()
                
            with open(target_path, 'w', encoding='utf-8') as target:
                target.write(content)
            
            # Gebruik relatief pad voor de bestandslijst
            rel_target_path = os.path.relpath(target_path, os.getcwd())
                
            # Voeg bestand toe aan de lijst
            backup_files.append({
                'name': file['name'],
                'path': rel_target_path,
                'display_name': file['name'],
                'type': file.get('type', 'Overig'),
                'size': os.path.getsize(target_path)
            })
                
            app.logger.debug(f"Bestand gekopieerd naar backup: {file['name']}")
        except Exception as e:
            app.logger.error(f"Fout bij het kopiëren van {file['name']}: {e}")
    
    return backup_files
