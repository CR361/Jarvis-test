from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, send_file, session
from app import app, db
from models import Customer, Invoice, InvoiceItem, Communication, Contract, ChecklistItem, Contractor
from forms import (
    CustomerForm, CustomerSearchForm, InvoiceForm, InvoiceItemForm, 
    CommunicationForm, ContractForm, MarkInvoicePaidForm, EmailForm,
    ContractorForm, ChecklistItemForm
)
from email_service import send_invoice_email, send_contract_email, send_custom_email, get_email_templates
from contract_templates import get_templates
from backup_service import create_backup
from checklist_routes import register_checklist_routes
import os
import json
from werkzeug.utils import secure_filename

def register_routes(app):
    # Dashboard route
    @app.route('/')
    def dashboard():
        # Get counts for dashboard stats
        customer_count = Customer.query.count()
        invoice_count = Invoice.query.count()
        
        # Get recent invoices
        recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
        
        # Get unpaid invoices
        unpaid_invoices = Invoice.query.filter_by(is_paid=False).order_by(Invoice.due_date).limit(5).all()
        
        # Get recent communications
        recent_communications = Communication.query.order_by(Communication.date.desc()).limit(5).all()
        
        # Total outstanding amount
        total_outstanding = db.session.query(db.func.sum(Invoice.total_amount - Invoice.amount_paid))\
            .filter_by(is_paid=False).scalar() or 0
            
        # Get contracts that need action
        pending_contracts = Contract.query.filter(Contract.status.in_(['concept', 'verzonden'])).order_by(Contract.updated_at.desc()).limit(5).all()
        
        # Huidige datum voor template
        current_date = datetime.now().date()
        
        return render_template('dashboard.html', 
                              customer_count=customer_count,
                              invoice_count=invoice_count,
                              recent_invoices=recent_invoices,
                              unpaid_invoices=unpaid_invoices,
                              recent_communications=recent_communications,
                              total_outstanding=total_outstanding,
                              pending_contracts=pending_contracts,
                              current_date=current_date)

    # Customer routes
    @app.route('/customers', methods=['GET'])
    def customer_list():
        search_form = CustomerSearchForm(request.args)
        
        # Start with all customers
        query = Customer.query
        
        # Apply search filters if provided
        if search_form.search.data:
            search_term = f"%{search_form.search.data}%"
            query = query.filter(
                (Customer.name.ilike(search_term)) |
                (Customer.email.ilike(search_term)) |
                (Customer.company.ilike(search_term)) |
                (Customer.kvk_number.ilike(search_term))
            )
            
        # Apply sort order
        sort_by = request.args.get('sort_by', 'name')
        if sort_by == 'name':
            query = query.order_by(Customer.name)
        elif sort_by == 'company':
            query = query.order_by(Customer.company)
        elif sort_by == 'created_at':
            query = query.order_by(Customer.created_at.desc())
        
        # Huidige datum voor template
        current_date = datetime.now().date()
        
        customers = query.all()
        return render_template('customers/index.html', 
                            customers=customers, 
                            search_form=search_form,
                            current_date=current_date)

    @app.route('/customers/create', methods=['GET', 'POST'])
    def create_customer():
        form = CustomerForm()
        if form.validate_on_submit():
            customer = Customer(
                name=form.name.data,
                company=form.company.data,
                kvk_number=form.kvk_number.data,
                email=form.email.data,
                phone=form.phone.data,
                address=form.address.data,
                city=form.city.data,
                postal_code=form.postal_code.data,
                country=form.country.data,
                notes=form.notes.data
            )
            db.session.add(customer)
            try:
                db.session.commit()
                flash('Klant succesvol aangemaakt!', 'success')
                return redirect(url_for('customer_view', customer_id=customer.id))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error creating customer: {e}")
                flash('Er is een fout opgetreden bij het aanmaken van de klant.', 'danger')
        
        return render_template('customers/create.html', form=form)

    @app.route('/customers/<int:customer_id>', methods=['GET'])
    def customer_view(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        
        # Get related data
        invoices = Invoice.query.filter_by(customer_id=customer_id).order_by(Invoice.created_at.desc()).all()
        communications = Communication.query.filter_by(customer_id=customer_id).order_by(Communication.date.desc()).all()
        contracts = Contract.query.filter_by(customer_id=customer_id).order_by(Contract.updated_at.desc()).all()
        
        # Huidige datum voor template
        current_date = datetime.now().date()
        
        return render_template('customers/view.html', 
                              customer=customer, 
                              invoices=invoices,
                              communications=communications,
                              contracts=contracts,
                              current_date=current_date)

    @app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
    def edit_customer(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        form = CustomerForm(obj=customer)
        
        if form.validate_on_submit():
            form.populate_obj(customer)
            try:
                db.session.commit()
                flash('Klantgegevens succesvol bijgewerkt!', 'success')
                return redirect(url_for('customer_view', customer_id=customer.id))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error updating customer: {e}")
                flash('Er is een fout opgetreden bij het bijwerken van de klantgegevens.', 'danger')
                
        return render_template('customers/edit.html', form=form, customer=customer)

    @app.route('/customers/<int:customer_id>/delete', methods=['POST'])
    def delete_customer(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        try:
            db.session.delete(customer)
            db.session.commit()
            flash('Klant is succesvol verwijderd.', 'success')
            return redirect(url_for('customer_list'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting customer: {e}")
            flash('Kan de klant niet verwijderen. Controleer of er nog gekoppelde records zijn.', 'danger')
            return redirect(url_for('customer_view', customer_id=customer_id))
    
    # Invoice routes
    @app.route('/invoices', methods=['GET'])
    def invoice_list():
        # Filter options
        status_filter = request.args.get('status', '')
        
        # Start with all invoices
        query = Invoice.query.join(Customer)
        
        # Apply status filter if provided
        if status_filter == 'unpaid':
            query = query.filter_by(is_paid=False)
        elif status_filter == 'paid':
            query = query.filter_by(is_paid=True)
        elif status_filter == 'overdue':
            query = query.filter_by(is_paid=False).filter(Invoice.due_date < datetime.utcnow().date())
            
        # Apply sort order
        sort_by = request.args.get('sort_by', 'date')
        if sort_by == 'date':
            query = query.order_by(Invoice.issue_date.desc())
        elif sort_by == 'customer':
            query = query.order_by(Customer.name)
        elif sort_by == 'amount':
            query = query.order_by(Invoice.total_amount.desc())
            
        # Huidige datum voor template
        today = datetime.now().date()
        
        invoices = query.all()
        
        # Calculate totals for summary
        total_amount = sum(invoice.total_amount for invoice in invoices)
        paid_amount = sum(invoice.total_amount for invoice in invoices if invoice.is_paid)
        unpaid_amount = total_amount - paid_amount
        
        return render_template('invoices/index.html', 
                             invoices=invoices, 
                             status_filter=status_filter,
                             current_date=today,
                             today=today,
                             total_amount=total_amount,
                             paid_amount=paid_amount,
                             unpaid_amount=unpaid_amount)

    @app.route('/invoices/create', methods=['GET', 'POST'])
    def create_invoice():
        # Get customers for dropdown (nodig vóór het maken van het formulier)
        customers = Customer.query.order_by(Customer.name).all()
        
        # Huidige datum en vervaldag (30 dagen later) voor nieuwe factuur
        today = datetime.now().date()
        due_date = today + timedelta(days=30)
        
        # Maak formulier met choices en standaarddatums
        form = InvoiceForm()
        form.issue_date.data = today
        form.due_date.data = due_date
        form.customer_id.choices = [(c.id, f"{c.name} ({c.company if c.company else c.email})") for c in customers]
        
        # Dynamically manage invoice items
        if request.method == 'POST':
            # Zorg dat het formulier de customer_id keuzes heeft voor validatie
            form.customer_id.choices = [(c.id, f"{c.name} ({c.company if c.company else c.email})") for c in customers]
            
            # Get all item form data
            item_descriptions = request.form.getlist('item_description[]')
            item_quantities = request.form.getlist('item_quantity[]')
            item_unit_prices = request.form.getlist('item_unit_price[]')
            
            if form.validate():
                # Generate invoice number
                last_invoice = Invoice.query.order_by(Invoice.id.desc()).first()
                invoice_number = f"INV-{datetime.now().year}-{(last_invoice.id + 1 if last_invoice else 1):04d}"
                
                # Create invoice
                invoice = Invoice(
                    invoice_number=invoice_number,
                    customer_id=form.customer_id.data,
                    issue_date=form.issue_date.data,
                    due_date=form.due_date.data,
                    notes=form.notes.data,
                    total_amount=0  # Will calculate from items
                )
                
                db.session.add(invoice)
                
                # Add invoice items
                total_amount = 0
                for i in range(len(item_descriptions)):
                    if item_descriptions[i].strip():  # Only add non-empty items
                        quantity = float(item_quantities[i])
                        unit_price = float(item_unit_prices[i])
                        item = InvoiceItem(
                            invoice=invoice,
                            description=item_descriptions[i],
                            quantity=quantity,
                            unit_price=unit_price
                        )
                        db.session.add(item)
                        total_amount += quantity * unit_price
                
                # Update invoice total
                invoice.total_amount = total_amount
                
                try:
                    db.session.commit()
                    flash('Factuur succesvol aangemaakt!', 'success')
                    return redirect(url_for('invoice_view', invoice_id=invoice.id))
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error creating invoice: {e}")
                    flash('Er is een fout opgetreden bij het aanmaken van de factuur.', 'danger')
        
        # Get customers for dropdown
        customers = Customer.query.order_by(Customer.name).all()
        
        # Initialize with one empty item
        items = [InvoiceItemForm()]
        
        return render_template('invoices/create.html', form=form, items=items, customers=customers)

    @app.route('/invoices/<int:invoice_id>', methods=['GET'])
    def invoice_view(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        mark_paid_form = MarkInvoicePaidForm()
        
        # Huidige datum toevoegen voor template
        current_date = datetime.now().date()
        
        return render_template('invoices/view.html', 
                             invoice=invoice, 
                             mark_paid_form=mark_paid_form,
                             current_date=current_date)

    @app.route('/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
    def edit_invoice(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        
        # Get customers for dropdown (nodig vóór het maken van het formulier)
        customers = Customer.query.order_by(Customer.name).all()
        
        # Maak formulier met choices
        form = InvoiceForm(obj=invoice)
        form.customer_id.choices = [(c.id, f"{c.name} ({c.company if c.company else c.email})") for c in customers]
        
        if request.method == 'POST':
            # Zorg dat het formulier de customer_id keuzes heeft voor validatie
            form.customer_id.choices = [(c.id, f"{c.name} ({c.company if c.company else c.email})") for c in customers]
            
            # Get all item form data
            item_ids = request.form.getlist('item_id[]')
            item_descriptions = request.form.getlist('item_description[]')
            item_quantities = request.form.getlist('item_quantity[]')
            item_unit_prices = request.form.getlist('item_unit_price[]')
            
            if form.validate():
                # Update invoice
                form.populate_obj(invoice)
                
                # Track items to be deleted
                existing_item_ids = [str(item.id) for item in invoice.items]
                items_to_delete = [item_id for item_id in existing_item_ids if item_id not in item_ids]
                
                # Delete removed items
                for item_id in items_to_delete:
                    item = InvoiceItem.query.get(item_id)
                    if item:
                        db.session.delete(item)
                
                # Update or add items
                total_amount = 0
                for i in range(len(item_descriptions)):
                    if item_descriptions[i].strip():  # Only process non-empty items
                        quantity = float(item_quantities[i])
                        unit_price = float(item_unit_prices[i])
                        
                        # Check if item exists
                        if i < len(item_ids) and item_ids[i]:
                            # Update existing item
                            item = InvoiceItem.query.get(item_ids[i])
                            if item:
                                item.description = item_descriptions[i]
                                item.quantity = quantity
                                item.unit_price = unit_price
                        else:
                            # Add new item
                            item = InvoiceItem(
                                invoice=invoice,
                                description=item_descriptions[i],
                                quantity=quantity,
                                unit_price=unit_price
                            )
                            db.session.add(item)
                        
                        total_amount += quantity * unit_price
                
                # Update invoice total
                invoice.total_amount = total_amount
                
                try:
                    db.session.commit()
                    flash('Factuur succesvol bijgewerkt!', 'success')
                    return redirect(url_for('invoice_view', invoice_id=invoice.id))
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error updating invoice: {e}")
                    flash('Er is een fout opgetreden bij het bijwerken van de factuur.', 'danger')
        
        # Get customers for dropdown
        customers = Customer.query.order_by(Customer.name).all()
        
        return render_template('invoices/edit.html', form=form, invoice=invoice, customers=customers)

    @app.route('/invoices/<int:invoice_id>/mark-paid', methods=['POST'])
    def mark_invoice_paid(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        form = MarkInvoicePaidForm()
        
        if form.validate_on_submit():
            invoice.is_paid = True
            invoice.amount_paid = invoice.total_amount
            invoice.payment_date = form.payment_date.data
            
            try:
                db.session.commit()
                flash('Factuur gemarkeerd als betaald!', 'success')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error marking invoice as paid: {e}")
                flash('Er is een fout opgetreden bij het markeren van de factuur als betaald.', 'danger')
                
        return redirect(url_for('invoice_view', invoice_id=invoice_id))

    @app.route('/invoices/<int:invoice_id>/send', methods=['POST'])
    def send_invoice(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        success = send_invoice_email(invoice)
        
        if success:
            # Voeg invoice items toe aan de checklist
            invoice.add_items_to_checklist()
            db.session.commit()
            flash('Factuur succesvol verzonden naar de klant! Items zijn toegevoegd aan de checklist.', 'success')
        else:
            flash('Er is een fout opgetreden bij het verzenden van de factuur.', 'danger')
            
        return redirect(url_for('invoice_view', invoice_id=invoice_id))

    @app.route('/invoices/<int:invoice_id>/delete', methods=['POST'])
    def delete_invoice(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        try:
            db.session.delete(invoice)
            db.session.commit()
            flash('Factuur is succesvol verwijderd.', 'success')
            return redirect(url_for('invoice_list'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting invoice: {e}")
            flash('Kan de factuur niet verwijderen.', 'danger')
            return redirect(url_for('invoice_view', invoice_id=invoice_id))
    
    # Communication routes
    @app.route('/communications', methods=['GET'])
    def communications_list():
        # Filter options
        type_filter = request.args.get('type', '')
        
        # Start with all communications
        query = Communication.query.join(Customer)
        
        # Apply type filter if provided
        if type_filter:
            query = query.filter_by(type=type_filter)
            
        # Apply sort order
        sort_by = request.args.get('sort_by', 'date')
        if sort_by == 'date':
            query = query.order_by(Communication.date.desc())
        elif sort_by == 'customer':
            query = query.order_by(Customer.name)
        elif sort_by == 'type':
            query = query.order_by(Communication.type)
            
        communications = query.all()
        
        # Huidige datum voor template
        current_date = datetime.now().date()
        
        return render_template('communications/index.html', 
                             communications=communications, 
                             current_date=current_date)
    @app.route('/customers/<int:customer_id>/communications/create', methods=['GET', 'POST'])
    def create_communication(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        form = CommunicationForm()
        
        if form.validate_on_submit():
            communication = Communication(
                customer_id=customer.id,
                type=form.type.data,
                subject=form.subject.data,
                content=form.content.data,
                date=form.date.data
            )
            
            db.session.add(communication)
            try:
                db.session.commit()
                flash('Communicatie succesvol geregistreerd!', 'success')
                return redirect(url_for('customer_view', customer_id=customer.id))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error creating communication: {e}")
                flash('Er is een fout opgetreden bij het registreren van de communicatie.', 'danger')
        
        return render_template('communications/create.html', form=form, customer=customer)

    @app.route('/communications/<int:communication_id>/delete', methods=['POST'])
    def delete_communication(communication_id):
        communication = Communication.query.get_or_404(communication_id)
        customer_id = communication.customer_id
        
        try:
            db.session.delete(communication)
            db.session.commit()
            flash('Communicatie succesvol verwijderd.', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting communication: {e}")
            flash('Er is een fout opgetreden bij het verwijderen van de communicatie.', 'danger')
            
        return redirect(url_for('customer_view', customer_id=customer_id))
    
    # Contract routes
    @app.route('/contracts', methods=['GET'])
    def contract_list():
        # Filter options
        status_filter = request.args.get('status', '')
        
        # Start with all contracts
        query = Contract.query.join(Customer)
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter_by(status=status_filter)
            
        # Apply sort order
        sort_by = request.args.get('sort_by', 'date')
        if sort_by == 'date':
            query = query.order_by(Contract.created_at.desc())
        elif sort_by == 'customer':
            query = query.order_by(Customer.name)
        elif sort_by == 'status':
            query = query.order_by(Contract.status)
            
        contracts = query.all()
        
        # Haal alle klanten op voor het dropdown menu
        customers = Customer.query.order_by(Customer.name).all()
        
        # Huidige datum voor template
        current_date = datetime.now().date()
        
        return render_template('contracts/index.html', 
                              contracts=contracts, 
                              status_filter=status_filter,
                              customers=customers,
                              current_date=current_date)

    @app.route('/customers/<int:customer_id>/contracts/create', methods=['GET', 'POST'])
    def create_contract(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        form = ContractForm()
        
        # Get contract templates
        templates = get_templates()
        
        if form.validate_on_submit():
            # Create new contract
            contract = Contract(
                customer_id=customer.id,
                title=form.title.data,
                content=form.content.data,
                status='concept'
            )
            
            db.session.add(contract)
            try:
                db.session.commit()
                flash('Contract succesvol aangemaakt!', 'success')
                return redirect(url_for('contract_view', contract_id=contract.id))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error creating contract: {e}")
                flash('Er is een fout opgetreden bij het aanmaken van het contract.', 'danger')
        
        return render_template('contracts/create.html', form=form, customer=customer, templates=templates)

    @app.route('/contracts/<int:contract_id>', methods=['GET'])
    def contract_view(contract_id):
        contract = Contract.query.get_or_404(contract_id)
        
        # Huidige datum voor template
        current_date = datetime.now().date()
        
        return render_template('contracts/view.html', 
                             contract=contract,
                             current_date=current_date)

    @app.route('/contracts/<int:contract_id>/send', methods=['POST'])
    def send_contract(contract_id):
        contract = Contract.query.get_or_404(contract_id)
        
        # Check if contract can be sent
        if contract.status not in ['concept', 'geweigerd']:
            flash('Dit contract kan niet worden verzonden. Controleer de status.', 'danger')
            return redirect(url_for('contract_view', contract_id=contract_id))
        
        # Send contract via email
        success = send_contract_email(contract)
        
        if success:
            # Update contract status and sent date
            contract.status = 'verzonden'
            contract.sent_at = datetime.utcnow()
            
            try:
                db.session.commit()
                # Check of we in simulatiemodus zitten voor aangepaste melding
                if not os.environ.get('SENDGRID_API_KEY'):
                    flash('Contract succesvol verzonden naar de klant! (simulatiemodus)', 'success')
                else:
                    flash('Contract succesvol verzonden naar de klant!', 'success')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error updating contract status: {e}")
                flash('Er is een fout opgetreden bij het bijwerken van de contractstatus.', 'danger')
        else:
            # Check of we in simulatiemodus zitten
            if os.environ.get('SENDGRID_API_KEY'):
                flash('Er is een fout opgetreden bij het verzenden van het contract.', 'danger')
            else:
                flash('Contract is gemarkeerd als verzonden (simulatiemodus). In productie zou een echte e-mail verzonden worden.', 'warning')
                # Update contract status en sent_at in simulatiemodus
                contract.status = 'verzonden'
                contract.sent_at = datetime.utcnow()
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error updating contract status in simulation mode: {e}")
            
        return redirect(url_for('contract_view', contract_id=contract_id))

    @app.route('/contracts/sign/<signing_url>', methods=['GET', 'POST'])
    def sign_contract(signing_url):
        contract = Contract.query.filter_by(signing_url=signing_url).first_or_404()
        
        # Huidige datum voor de template
        current_date = datetime.utcnow().date()
        
        # Check if contract can be signed
        if contract.status != 'verzonden':
            if contract.status == 'ondertekend':
                flash('Dit contract is al ondertekend.', 'info')
            else:
                flash('Dit contract kan niet worden ondertekend. Controleer de status.', 'danger')
            return render_template('contracts/sign.html', contract=contract, can_sign=False, current_date=current_date)
        
        if request.method == 'POST':
            signature_data = request.form.get('signature_data')
            signed_by = request.form.get('signed_by')
            
            if not signature_data or not signed_by:
                flash('Handtekening en naam zijn vereist.', 'danger')
                return render_template('contracts/sign.html', contract=contract, can_sign=True, current_date=current_date)
            
            # Update contract with signature
            contract.signature_data = signature_data
            contract.signed_by = signed_by
            contract.signed_at = datetime.utcnow()
            contract.signed_ip = request.remote_addr
            contract.status = 'ondertekend'
            
            try:
                db.session.commit()
                flash('Contract succesvol ondertekend!', 'success')
                return render_template('contracts/sign.html', contract=contract, can_sign=False, just_signed=True, current_date=current_date)
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error signing contract: {e}")
                flash('Er is een fout opgetreden bij het ondertekenen van het contract.', 'danger')
                return render_template('contracts/sign.html', contract=contract, can_sign=True, current_date=current_date)
        
        return render_template('contracts/sign.html', contract=contract, can_sign=True, current_date=current_date)

    @app.route('/contracts/<int:contract_id>/delete', methods=['POST'])
    def delete_contract(contract_id):
        contract = Contract.query.get_or_404(contract_id)
        customer_id = contract.customer_id
        
        try:
            db.session.delete(contract)
            db.session.commit()
            flash('Contract succesvol verwijderd.', 'success')
            return redirect(url_for('customer_view', customer_id=customer_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting contract: {e}")
            flash('Er is een fout opgetreden bij het verwijderen van het contract.', 'danger')
            return redirect(url_for('contract_view', contract_id=contract_id))
    
    # Global dictionary om de backup files bij te houden, per timestamp
    backup_files_registry = {}
    
    # Backup route
    @app.route('/backup', methods=['POST'])
    def backup():
        try:
            # Maak een backup met alle individuele bestanden
            backup_dir, backup_files = create_backup()
            
            # Pak de timestamp uit de map naam
            timestamp = os.path.basename(backup_dir).replace('jarvis_backup_', '')
            
            # Sla de backup informatie op in de globale registry
            backup_files_registry[timestamp] = {
                'backup_dir': backup_dir,
                'backup_files': backup_files,
                'backup_time': datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
            }
            
            # Stuur de gebruiker door naar de backup_files pagina
            flash('Backup is succesvol gemaakt. Je kunt nu de bestanden individueel downloaden.', 'success')
            return redirect(url_for('backup_files', timestamp=timestamp))
        except Exception as e:
            app.logger.error(f"Error creating backup: {e}")
            flash('Er is een fout opgetreden bij het maken van een backup.', 'danger')
            return redirect(url_for('dashboard'))
    
    @app.route('/backup/files/<timestamp>', methods=['GET'])
    def backup_files(timestamp):
        """Toont een lijst met alle backup bestanden die gedownload kunnen worden"""
        if timestamp not in backup_files_registry:
            flash('Er is geen recente backup beschikbaar. Maak eerst een backup.', 'warning')
            return redirect(url_for('dashboard'))
        
        backup_data = backup_files_registry[timestamp]
        backup_dir = backup_data['backup_dir']
        backup_files = backup_data['backup_files']
        backup_time = backup_data['backup_time']
        
        # Sorteer bestanden per type
        backend_files = [f for f in backup_files if f['type'] == 'Backend']
        data_files = [f for f in backup_files if f['type'] == 'Data']
        template_files = [f for f in backup_files if f['type'] == 'Template']
        static_files = [f for f in backup_files if f['type'] == 'Static']
        nodejs_files = [f for f in backup_files if f['type'] == 'NodeJS']
        other_files = [f for f in backup_files if f['type'] not in ['Backend', 'Data', 'Template', 'Static', 'NodeJS']]
        
        # Controleer of er Node.js export beschikbaar is
        has_nodejs_export = any(f for f in backup_files if f['type'] == 'NodeJS')
        
        # Zoek de basis directory van de Node.js export
        nodejs_dir = None
        if has_nodejs_export:
            for file in nodejs_files:
                if file.get('is_nodejs_root', False):
                    nodejs_dir = os.path.dirname(file['path'])
                    break
        
        return render_template('backup_direct_download.html',
                               timestamp=timestamp,
                               backup_dir=backup_dir,
                               backend_files=backend_files,
                               data_files=data_files,
                               template_files=template_files,
                               static_files=static_files,
                               nodejs_files=nodejs_files,
                               has_nodejs_export=has_nodejs_export,
                               nodejs_dir=nodejs_dir,
                               other_files=other_files,
                               backup_time=backup_time)
    
    @app.route('/backup/download/<timestamp>/<path:filename>', methods=['GET'])
    def download_backup_file(timestamp, filename):
        """Download een specifiek bestand uit de backup"""
        try:
            if timestamp not in backup_files_registry:
                flash('Er is geen recente backup beschikbaar. Maak eerst een backup.', 'warning')
                return redirect(url_for('dashboard'))
            
            backup_files = backup_files_registry[timestamp]['backup_files']
            
            # Zoek het bestand in de backup files
            file_path = None
            for file in backup_files:
                if file['path'] == filename:
                    file_path = file['path']
                    break
            
            if not file_path or not os.path.exists(file_path):
                flash('Het opgevraagde bestand bestaat niet.', 'danger')
                return redirect(url_for('backup_files', timestamp=timestamp))
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=os.path.basename(file_path)
            )
        except Exception as e:
            app.logger.error(f"Error downloading backup file: {e}")
            flash('Er is een fout opgetreden bij het downloaden van het bestand.', 'danger')
            return redirect(url_for('backup_files', timestamp=timestamp))
    
    # Email routes
    @app.route('/emails', methods=['GET'])
    def email_list():
        # Haal alle klanten op voor dropdown
        customers = Customer.query.order_by(Customer.name).all()
        
        # Haal recente e-mail communicaties op
        communications = Communication.query.filter_by(type='email').order_by(Communication.date.desc()).limit(20).all()
        
        # Controleer of er e-mail communicaties zijn
        has_email_comms = any(comm.type == 'email' for comm in communications)
        
        # Haal alle beschikbare e-mail templates op
        email_templates = get_email_templates()
        
        # Huidige datum voor template
        today = datetime.now().date()
        
        return render_template('emails/index.html', 
                               customers=customers, 
                               communications=communications, 
                               has_email_comms=has_email_comms,
                               templates=email_templates,
                               today=today)
    
    @app.route('/emails/create', methods=['GET', 'POST'])
    def create_email():
        form = EmailForm()
        
        # Haal klanten op voor dropdown
        customers = Customer.query.order_by(Customer.name).all()
        form.customer_id.choices = [(c.id, f"{c.name} ({c.email})") for c in customers]
        
        # Verwerk template parameter (uit de index pagina)
        if request.method == 'GET' and request.args.get('template'):
            form.template.data = request.args.get('template')
            
            # Als een klant is geselecteerd
            if request.args.get('customer_id'):
                form.customer_id.data = int(request.args.get('customer_id'))
                
        return render_template('emails/create.html', form=form, customers=customers)
    
    @app.route('/emails/send', methods=['POST'])
    def send_email():
        form = EmailForm()
        
        # Haal klanten op voor dropdown (nodig voor form validatie)
        customers = Customer.query.order_by(Customer.name).all()
        form.customer_id.choices = [(c.id, f"{c.name} ({c.email})") for c in customers]
        
        if form.validate_on_submit():
            try:
                # Haal klantgegevens op
                customer = Customer.query.get_or_404(form.customer_id.data)
                
                # Verstuur e-mail
                success = send_custom_email(
                    to_email=customer.email,
                    subject=form.subject.data,
                    content=form.content.data,
                    customer_name=customer.name,
                    template_id=form.template.data if form.template.data else None
                )
                
                if success:
                    # Registreer de e-mail als communicatie
                    communication = Communication(
                        customer_id=customer.id,
                        type='email',
                        subject=form.subject.data,
                        content=form.content.data,
                        date=datetime.utcnow()
                    )
                    db.session.add(communication)
                    db.session.commit()
                    
                    flash('E-mail succesvol verzonden!', 'success')
                    return redirect(url_for('email_list'))
                else:
                    # Check of we in simulatiemodus zitten
                    if os.environ.get('SENDGRID_API_KEY'):
                        flash('Er is een fout opgetreden bij het verzenden van de e-mail. Controleer de SENDGRID_API_KEY.', 'danger')
                    else:
                        flash('E-mail succesvol geregistreerd in simulatiemodus. In productie zou de e-mail daadwerkelijk verzonden worden.', 'warning')
            except Exception as e:
                app.logger.error(f"Error sending email: {e}")
                flash('Er is een fout opgetreden bij het verzenden van de e-mail.', 'danger')
        
        return render_template('emails/create.html', form=form, customers=customers)
