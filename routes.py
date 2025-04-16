from flask import render_template, redirect, url_for, flash, request, abort
from datetime import datetime, timedelta
from app import app, db
from models import Customer, Invoice, InvoiceItem, Communication, Contract, ChecklistItem, Contractor

@app.route('/')
def index():
    """Home pagina / dashboard"""
    current_date = datetime.now().date()
    
    # Voorbeeld data voor dashboard (moet worden aangepast aan echte data)
    recent_customers = Customer.query.order_by(Customer.id.desc()).limit(5).all()
    recent_invoices = Invoice.query.order_by(Invoice.issue_date.desc()).limit(5).all()
    unpaid_invoices = Invoice.query.filter_by(is_paid=False).order_by(Invoice.due_date).limit(5).all()
    pending_contracts = Contract.query.filter(Contract.status.in_(['concept', 'verzonden'])).order_by(Contract.updated_at.desc()).limit(5).all()
    recent_communications = Communication.query.order_by(Communication.date.desc()).limit(5).all()
    
    # Statistieken voor dashboard
    total_customers = Customer.query.count()
    total_invoices = Invoice.query.count()
    unpaid_total = Invoice.query.filter_by(is_paid=False).count()
    overdue_invoices = Invoice.query.filter(Invoice.is_paid==False, Invoice.due_date < current_date).count()
    
    # Bereken totaal openstaand bedrag
    total_outstanding = 0.0
    for invoice in Invoice.query.filter_by(is_paid=False).all():
        total_outstanding += invoice.total_amount
    
    # Bereken omzet statistieken
    invoiced_current_month = 0
    invoiced_previous_month = 0
    
    # Huidige maand en jaar
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Vorige maand en jaar
    if current_month == 1:
        previous_month = 12
        previous_year = current_year - 1
    else:
        previous_month = current_month - 1
        previous_year = current_year
    
    return render_template('root_templates/dashboard.html', 
                          recent_customers=recent_customers,
                          recent_invoices=recent_invoices,
                          unpaid_invoices=unpaid_invoices,
                          pending_contracts=pending_contracts,
                          recent_communications=recent_communications,
                          total_customers=total_customers,
                          total_invoices=total_invoices,
                          unpaid_total=unpaid_total,
                          overdue_invoices=overdue_invoices,
                          invoiced_current_month=invoiced_current_month,
                          invoiced_previous_month=invoiced_previous_month,
                          current_date=current_date,
                          total_outstanding=total_outstanding,
                          invoice_count=total_invoices,
                          customer_count=total_customers)

# Klanten routes
@app.route('/customers')
def customer_list():
    """Toon een lijst van alle klanten"""
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('customers/index.html', customers=customers)

@app.route('/customers/create', methods=['GET', 'POST'])
def customer_create():
    """Maak een nieuwe klant aan"""
    from forms import CustomerForm
    
    form = CustomerForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            company=form.company.data,
            email=form.email.data,
            phone=form.phone.data,
            kvk_number=form.kvk_number.data,
            address=form.address.data,
            postal_code=form.postal_code.data,
            city=form.city.data,
            country=form.country.data,
            notes=form.notes.data
        )
        db.session.add(customer)
        try:
            db.session.commit()
            flash('Klant succesvol aangemaakt.', 'success')
            return redirect(url_for('customer_view', customer_id=customer.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij het aanmaken van de klant: {str(e)}', 'danger')
    
    return render_template('customers/create.html', form=form)

@app.route('/customers/<int:customer_id>')
def customer_view(customer_id):
    """Bekijk een specifieke klant"""
    from datetime import datetime
    
    customer = Customer.query.get_or_404(customer_id)
    
    # Haal de communicatie, facturen en contracten voor deze klant op
    communications = Communication.query.filter_by(customer_id=customer_id).order_by(Communication.date.desc()).all()
    invoices = Invoice.query.filter_by(customer_id=customer_id).order_by(Invoice.issue_date.desc()).all()
    contracts = Contract.query.filter_by(customer_id=customer_id).order_by(Contract.updated_at.desc()).all()
    
    # Bereken totalen
    total_revenue = sum(invoice.total_amount for invoice in invoices)
    outstanding_amount = sum(invoice.total_amount for invoice in invoices if not invoice.is_paid)
    
    # Huidige datum voor vergelijking met vervaldatums
    current_date = datetime.now().date()
    
    return render_template('root_templates/customer_view.html', 
                          customer=customer,
                          communications=communications,
                          invoices=invoices,
                          contracts=contracts,
                          total_revenue=total_revenue,
                          outstanding_amount=outstanding_amount,
                          current_date=current_date)

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
def customer_edit(customer_id):
    """Bewerk een klant"""
    from forms import CustomerForm
    
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer)
    
    if request.method == 'POST' and form.validate_on_submit():
        # Update de klant met formulierdata
        form.populate_obj(customer)
        
        try:
            db.session.commit()
            flash('Klant succesvol bijgewerkt.', 'success')
            return redirect(url_for('customer_view', customer_id=customer.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij het bijwerken van de klant: {str(e)}', 'danger')
    
    return render_template('customers/edit.html', customer=customer, form=form)

@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    """Verwijder een klant"""
    customer = Customer.query.get_or_404(customer_id)
    
    # Controleert of er nog openstaande facturen zijn
    unpaid_invoices = Invoice.query.filter_by(customer_id=customer_id, is_paid=False).all()
    if unpaid_invoices:
        flash(f'Kan klant niet verwijderen omdat er nog {len(unpaid_invoices)} onbetaalde facturen zijn.', 'danger')
        return redirect(url_for('customer_view', customer_id=customer_id))
    
    # Verwijder alle gekoppelde communicatie
    Communication.query.filter_by(customer_id=customer_id).delete()
    
    # Verwijder alle gekoppelde contracten
    Contract.query.filter_by(customer_id=customer_id).delete()
    
    # Verwijder alle gekoppelde facturen
    Invoice.query.filter_by(customer_id=customer_id).delete()
    
    # Verwijder de klant
    db.session.delete(customer)
    
    try:
        db.session.commit()
        flash('Klant succesvol verwijderd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fout bij het verwijderen van de klant: {str(e)}', 'danger')
    
    return redirect(url_for('customer_list'))

# Facturen routes
@app.route('/invoices')
def invoice_list():
    """Toon een lijst van alle facturen"""
    from datetime import datetime
    current_date = datetime.now().date()
    
    status = request.args.get('status')
    if status == 'paid':
        invoices = Invoice.query.filter_by(is_paid=True).order_by(Invoice.issue_date.desc()).all()
    elif status == 'unpaid':
        invoices = Invoice.query.filter_by(is_paid=False).order_by(Invoice.due_date).all()
    else:
        invoices = Invoice.query.order_by(Invoice.issue_date.desc()).all()
    return render_template('invoices/index.html', invoices=invoices, status=status, current_date=current_date)

@app.route('/invoices/create', methods=['GET', 'POST'])
def create_invoice():
    """Maak een nieuwe factuur aan"""
    from datetime import datetime, timedelta
    
    customers = Customer.query.order_by(Customer.name).all()
    today = datetime.now().date()
    due_date = today + timedelta(days=30)  # Standaard vervaldatum: 30 dagen vanaf nu
    recent_invoices = Invoice.query.order_by(Invoice.issue_date.desc()).limit(5).all()
    
    if request.method == 'POST':
        # Hier komt de formulier verwerking
        pass
    
    return render_template('invoices/create.html', 
                          customers=customers,
                          today=today,
                          due_date=due_date,
                          recent_invoices=recent_invoices)

@app.route('/invoices/<int:invoice_id>')
def invoice_view(invoice_id):
    """Bekijk een specifieke factuur"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('root_templates/invoice_view.html', invoice=invoice)

@app.route('/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
def invoice_edit(invoice_id):
    """Bewerk een factuur"""
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('invoices/edit.html', invoice=invoice)

# Contracten routes
@app.route('/contracts')
def contract_list():
    """Toon een lijst van alle contracten"""
    contracts = Contract.query.order_by(Contract.updated_at.desc()).all()
    return render_template('contracts/index.html', contracts=contracts)

@app.route('/contracts/create', methods=['GET', 'POST'])
def create_contract():
    """Maak een nieuw contract aan"""
    from forms import ContractForm
    
    # Haal alle klanten op
    customers = Customer.query.order_by(Customer.name).all()
    
    # Als er een specifieke klant is geselecteerd
    customer_id = request.args.get('customer_id')
    if customer_id:
        customer = Customer.query.get_or_404(int(customer_id))
        form = ContractForm()
        
        # Verwerk het formulier (POST)
        if request.method == 'POST' and form.validate_on_submit():
            contract = Contract(
                customer_id=customer.id,
                title=form.title.data,
                content=form.content.data,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status='concept'  # Standaard status is concept
            )
            db.session.add(contract)
            try:
                db.session.commit()
                flash('Contract succesvol aangemaakt.', 'success')
                return redirect(url_for('contract_view', contract_id=contract.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Fout bij het aanmaken van het contract: {str(e)}', 'danger')
        
        return render_template('contracts/create.html', customer=customer, form=form)
    
    # Anders toon een lijst van klanten om te selecteren
    return render_template('contracts/select_customer.html', customers=customers)

@app.route('/contracts/<int:contract_id>')
def contract_view(contract_id):
    """Bekijk een specifiek contract"""
    contract = Contract.query.get_or_404(contract_id)
    customer = Customer.query.get(contract.customer_id)
    return render_template('root_templates/contract_view.html', contract=contract, customer=customer)

@app.route('/contracts/<int:contract_id>/edit', methods=['GET', 'POST'])
def contract_edit(contract_id):
    """Bewerk een contract"""
    contract = Contract.query.get_or_404(contract_id)
    customer = Customer.query.get(contract.customer_id)
    return render_template('contracts/edit.html', contract=contract, customer=customer)

@app.route('/contracts/<int:contract_id>/sign', methods=['GET', 'POST'])
def contract_sign(contract_id):
    """Onderteken een contract"""
    from datetime import datetime
    
    contract = Contract.query.get_or_404(contract_id)
    customer = Customer.query.get(contract.customer_id)
    
    # Controleer of het contract al is ondertekend
    if contract.status == 'ondertekend':
        return render_template('contracts/sign.html', contract=contract, customer=customer, can_sign=False)
    
    # Voor POST-verzoeken (wanneer het formulier wordt verzonden)
    if request.method == 'POST':
        signature_data = request.form.get('signature_data')
        signed_by = request.form.get('signed_by')
        
        if not signature_data or not signed_by:
            flash('Vul alle verplichte velden in en plaats uw handtekening.', 'danger')
            return render_template('contracts/sign.html', contract=contract, customer=customer, can_sign=True)
        
        # Bijwerken van het contract
        contract.status = 'ondertekend'
        contract.signature_data = signature_data
        contract.signed_by = signed_by
        contract.signed_at = datetime.now()
        
        try:
            db.session.commit()
            flash('Contract succesvol ondertekend.', 'success')
            return render_template('contracts/sign.html', contract=contract, customer=customer, just_signed=True, can_sign=False)
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij het ondertekenen van het contract: {str(e)}', 'danger')
    
    # Voor GET-verzoeken
    return render_template('contracts/sign.html', contract=contract, customer=customer, can_sign=True)

@app.route('/contracts/<int:contract_id>/delete', methods=['POST'])
def delete_contract(contract_id):
    """Verwijder een contract"""
    contract = Contract.query.get_or_404(contract_id)
    customer_id = contract.customer_id
    
    try:
        db.session.delete(contract)
        db.session.commit()
        flash('Contract succesvol verwijderd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fout bij het verwijderen van het contract: {str(e)}', 'danger')
    
    return redirect(url_for('customer_view', customer_id=customer_id))

# Communicatie routes
@app.route('/communications/<int:communication_id>/delete', methods=['POST'])
def delete_communication(communication_id):
    """Verwijder een communicatie-item"""
    communication = Communication.query.get_or_404(communication_id)
    customer_id = communication.customer_id
    
    try:
        db.session.delete(communication)
        db.session.commit()
        flash('Communicatie succesvol verwijderd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fout bij het verwijderen van communicatie: {str(e)}', 'danger')
    
    return redirect(url_for('customer_view', customer_id=customer_id))

# Emails routes
@app.route('/emails')
def email_list():
    """Toon een lijst van alle emails"""
    emails = Communication.query.filter_by(type='email').order_by(Communication.date.desc()).all()
    return render_template('emails/index.html', emails=emails)

@app.route('/emails/create', methods=['GET', 'POST'])
def email_create():
    """Maak een nieuwe email aan"""
    from forms import EmailForm
    
    form = EmailForm()
    customers = Customer.query.order_by(Customer.name).all()
    
    # Vul de customer ID dropdown
    form.customer_id.choices = [(c.id, f"{c.name} ({c.email})") for c in customers]
    
    if request.method == 'POST' and form.validate_on_submit():
        # Hier zou de echte formulierverwerking en e-mail verzending gebeuren
        
        # Maak een nieuwe communicatie-record in de database
        communication = Communication(
            customer_id=form.customer_id.data,
            type='email',
            subject=form.subject.data,
            content=form.content.data,
            date=datetime.now()
        )
        db.session.add(communication)
        try:
            db.session.commit()
            flash('E-mail succesvol verstuurd en opgeslagen.', 'success')
            return redirect(url_for('email_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij het opslaan van de e-mail: {str(e)}', 'danger')
    
    # Voor een GET request of als het formulier niet gevalideerd kan worden
    return render_template('emails/create.html', form=form, customers=customers)

@app.route('/emails/<int:email_id>')
def email_view(email_id):
    """Bekijk een specifieke email"""
    email = Communication.query.get_or_404(email_id)
    return render_template('emails/view.html', email=email)

# Backup routes
@app.route('/backup')
def backup_index():
    """Toon backup opties"""
    from datetime import datetime
    import os
    import time
    import shutil
    import logging
    
    # Aanmaken van een back-up directory als deze nog niet bestaat
    backup_dir = os.path.join(os.getcwd(), 'backups')
    code_dir = os.path.join(backup_dir, 'code')
    templates_dir = os.path.join(backup_dir, 'templates')
    data_dir = os.path.join(backup_dir, 'data')
    static_dir = os.path.join(backup_dir, 'static')
    root_dir = os.path.join(backup_dir, 'root_files')
    
    # Zorg ervoor dat alle directories bestaan
    os.makedirs(code_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(root_dir, exist_ok=True)
    
    # Lijst van beschikbare back-ups genereren
    backend_files = []
    template_files = []
    data_files = []
    static_files = []
    other_files = []
    
    # Genereer een timestamp voor deze backup sessie
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Log voor debugging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Maak backup met timestamp: {timestamp}")
    
    # Maak een volledige backup van alle bestanden in de root directory
    for file in os.listdir(os.getcwd()):
        if os.path.isfile(os.path.join(os.getcwd(), file)):
            if file.endswith(('.py', '.html', '.js', '.css', '.json')):
                file_path = os.path.join(os.getcwd(), file)
                file_size = os.path.getsize(file_path)
                
                # Kopieer belangrijke Python bestanden naar de code directory voor directe download
                if file.endswith('.py'):
                    # Sla de hoofdbestanden ook direct op in de code map
                    py_dest_path = os.path.join(code_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as src_file:
                            content = src_file.read()
                            
                        with open(py_dest_path, 'w', encoding='utf-8') as dest_file:
                            dest_file.write(content)
                        
                        logger.info(f"Python bestand gekopieerd naar code directory: {file}")
                    except Exception as e:
                        logger.error(f"Fout bij het kopiëren van Python bestand naar code dir: {file}: {e}")
                
                # Kopieer naar root_files directory
                dest_path = os.path.join(root_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as src_file:
                        content = src_file.read()
                        
                    with open(dest_path, 'w', encoding='utf-8') as dest_file:
                        dest_file.write(content)
                    
                    # Bepaal de juiste categorie voor het bestand
                    if file.endswith('.py'):
                        category = 'code'
                        target_list = backend_files
                    elif file.endswith('.html'):
                        category = 'templates'
                        target_list = template_files
                    elif file.endswith(('.js', '.css')):
                        category = 'static'
                        target_list = static_files
                    elif file.endswith('.json'):
                        category = 'data'
                        target_list = data_files
                    else:
                        category = 'other'
                        target_list = other_files
                    
                    # Voeg bestandsinfo toe aan de juiste lijst
                    target_list.append({
                        'name': file,
                        'path': os.path.join('root_files', file),
                        'size': f"{file_size / 1024:.1f} KB",
                        'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d-%m-%Y %H:%M')
                    })
                except Exception as e:
                    logger.error(f"Fout bij het kopiëren van {file}: {e}")
                    
    # Backup templates directory
    if os.path.exists('templates'):
        for root, dirs, files in os.walk('templates'):
            for file in files:
                if file.endswith('.html'):
                    source_path = os.path.join(root, file)
                    rel_path = os.path.relpath(source_path, 'templates')
                    target_dir = os.path.join(templates_dir, os.path.dirname(rel_path))
                    os.makedirs(target_dir, exist_ok=True)
                    target_path = os.path.join(templates_dir, rel_path)
                    
                    try:
                        with open(source_path, 'r', encoding='utf-8') as src_file:
                            content = src_file.read()
                            
                        with open(target_path, 'w', encoding='utf-8') as dest_file:
                            dest_file.write(content)
                            
                        file_size = os.path.getsize(source_path)
                        
                        template_files.append({
                            'name': rel_path,
                            'path': os.path.join('templates', rel_path),
                            'size': f"{file_size / 1024:.1f} KB",
                            'date': datetime.fromtimestamp(os.path.getmtime(source_path)).strftime('%d-%m-%Y %H:%M')
                        })
                    except Exception as e:
                        logger.error(f"Fout bij het kopiëren van {source_path}: {e}")
    
    # Backup static directory
    if os.path.exists('static'):
        for root, dirs, files in os.walk('static'):
            for file in files:
                if file.endswith(('.js', '.css')):
                    source_path = os.path.join(root, file)
                    rel_path = os.path.relpath(source_path, 'static')
                    target_dir = os.path.join(static_dir, os.path.dirname(rel_path))
                    os.makedirs(target_dir, exist_ok=True)
                    target_path = os.path.join(static_dir, rel_path)
                    
                    try:
                        with open(source_path, 'r', encoding='utf-8') as src_file:
                            content = src_file.read()
                            
                        with open(target_path, 'w', encoding='utf-8') as dest_file:
                            dest_file.write(content)
                            
                        file_size = os.path.getsize(source_path)
                        
                        static_files.append({
                            'name': rel_path,
                            'path': os.path.join('static', rel_path),
                            'size': f"{file_size / 1024:.1f} KB",
                            'date': datetime.fromtimestamp(os.path.getmtime(source_path)).strftime('%d-%m-%Y %H:%M')
                        })
                    except Exception as e:
                        logger.error(f"Fout bij het kopiëren van {source_path}: {e}")
    
    # Maak database backup
    if not data_files:
        try:
            # Export database gegevens
            from backup_service import get_all_data
            backup_data = get_all_data()
            
            # Sla gegevens op als JSON-bestand
            db_json_path = os.path.join(data_dir, f"database_backup_{timestamp}.json")
            with open(db_json_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
                
            file_size = os.path.getsize(db_json_path)
            data_files.append({
                'name': os.path.basename(db_json_path),
                'path': os.path.join('data', os.path.basename(db_json_path)),
                'size': f"{file_size / 1024:.1f} KB",
                'date': datetime.now().strftime('%d-%m-%Y %H:%M')
            })
        except Exception as e:
            logger.error(f"Fout bij het maken van database backup: {e}")
    
    logger.info(f"Backup voltooid met timestamp: {timestamp}")
    
    return render_template('root_templates/backup_download.html',
                          timestamp=timestamp,
                          backup_dir=backup_dir,
                          backup_time=datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                          backend_files=backend_files,
                          template_files=template_files,
                          data_files=data_files,
                          static_files=static_files,
                          other_files=other_files)

@app.route('/backup/download/<timestamp>/<path:filename>')
def download_backup_file(timestamp, filename):
    """Download een backup bestand"""
    import os
    from flask import send_from_directory, abort
    
    # Controleert of het bestand bestaat en of het in een van de backup mappen zit
    backup_dir = os.path.join(os.getcwd(), 'backups')
    file_path = os.path.join(backup_dir, filename)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        abort(404, description="Bestand niet gevonden")
    
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/backup/download-js/<timestamp>/<path:filename>')
def download_backup_as_js(timestamp, filename):
    """Download een backup bestand als JavaScript/Node.js code"""
    import os
    from flask import send_file, abort, make_response
    from python_to_js_converter import convert_python_to_js
    from js_converter_optimizer import optimize_js_code
    import tempfile
    
    # Controleert of het bestand bestaat en of het in een van de backup mappen zit
    backup_dir = os.path.join(os.getcwd(), 'backups')
    file_path = os.path.join(backup_dir, filename)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        abort(404, description="Bestand niet gevonden")
    
    # Controleer of het een bestand is dat we kunnen converteren
    allowed_extensions = ['.py', '.html', '.js', '.css', '.json', '.sql']
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension not in allowed_extensions:
        abort(400, description="Alleen Python, HTML, JS, CSS, JSON en SQL bestanden kunnen naar JavaScript worden geconverteerd")
    
    try:
        # Lees het broncode bestand
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Bepaal de originele bestandsnaam
        original_filename = os.path.basename(file_path)
        
        # Speciale behandeling voor contract_templates bestanden
        if 'contract_templates' in original_filename and file_extension == '.py':
            # Gebruik een vooraf ingevulde versie met de juiste functies en exports
            js_code = convert_python_to_js(source_code, file_extension, filename=original_filename)
        else:
            # Normale conversie voor andere bestandstypen
            js_code = convert_python_to_js(source_code, file_extension)
            
            # Vervang de placeholder voor bestandsnaam met de echte bestandsnaam
            js_code = js_code.replace('PYTHON_ORIGINAL_FILENAME', original_filename)
            
            # Optimaliseer de JavaScript code voor Node.js compatibiliteit
            js_code = optimize_js_code(js_code, original_filename)
        
        # Maak een tijdelijk bestand voor het JavaScript resultaat
        with tempfile.NamedTemporaryFile(delete=False, suffix='.js') as tmp:
            tmp.write(js_code.encode('utf-8'))
            tmp_path = tmp.name
        
        # Bepaal de nieuwe bestandsnaam
        js_filename = os.path.splitext(original_filename)[0] + '.js'
        
        # Stuur het bestand als download
        response = make_response(send_file(tmp_path, as_attachment=True, 
                                         download_name=js_filename,
                                         mimetype='application/javascript'))
        
        # Verwijder het tijdelijke bestand na het verzenden
        @response.call_on_close
        def cleanup():
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
        return response
        
    except Exception as e:
        app.logger.error(f"Fout bij het converteren naar JavaScript: {str(e)}")
        abort(500, description=f"Fout bij het converteren naar JavaScript: {str(e)}")

# Checklist routes
@app.route('/checklist')
def checklist():
    """Toon de checklist met alle openstaande en voltooide items"""
    items = ChecklistItem.query.order_by(ChecklistItem.position).all()
    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template('checklist/index.html', items=items, contractors=contractors)

@app.route('/checklist/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_checklist_item(item_id):
    """Bewerk een checklist item"""
    item = ChecklistItem.query.get_or_404(item_id)
    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template('checklist/edit_item.html', item=item, contractors=contractors)

# Aannemers routes
@app.route('/contractors')
def contractor_list():
    """Toon alle aannemers"""
    contractors = Contractor.query.order_by(Contractor.name).all()
    return render_template('contractors/index.html', title="Aannemers", contractors=contractors)

@app.route('/contractors/create', methods=['GET', 'POST'])
def create_contractor():
    """Maak een nieuwe aannemer aan"""
    from forms import ContractorForm
    
    form = ContractorForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        contractor = Contractor(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            specialty=form.specialty.data,
            notes=form.notes.data
        )
        db.session.add(contractor)
        try:
            db.session.commit()
            flash('Aannemer succesvol aangemaakt.', 'success')
            return redirect(url_for('contractor_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij het aanmaken van de aannemer: {str(e)}', 'danger')
    
    return render_template('contractors/create.html', form=form)

@app.route('/contractors/<int:contractor_id>/edit', methods=['GET', 'POST'])
def edit_contractor(contractor_id):
    """Bewerk een aannemer"""
    from forms import ContractorForm
    
    contractor = Contractor.query.get_or_404(contractor_id)
    form = ContractorForm(obj=contractor)
    
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(contractor)
        try:
            db.session.commit()
            flash('Aannemer succesvol bijgewerkt.', 'success')
            return redirect(url_for('contractor_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij het bijwerken van de aannemer: {str(e)}', 'danger')
    
    return render_template('contractors/edit.html', contractor=contractor, form=form, title="Aannemer Bewerken")

@app.route('/contractors/<int:contractor_id>/delete', methods=['POST'])
def delete_contractor(contractor_id):
    """Verwijder een aannemer"""
    contractor = Contractor.query.get_or_404(contractor_id)
    
    # Controleer of er nog taken aan deze aannemer zijn toegewezen
    assigned_tasks = ChecklistItem.query.filter_by(contractor_id=contractor_id).all()
    if assigned_tasks:
        flash(f'Kan aannemer niet verwijderen omdat er nog {len(assigned_tasks)} taken zijn toegewezen.', 'danger')
        return redirect(url_for('contractor_list'))
    
    db.session.delete(contractor)
    try:
        db.session.commit()
        flash('Aannemer succesvol verwijderd.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fout bij het verwijderen van de aannemer: {str(e)}', 'danger')
    
    return redirect(url_for('contractor_list'))