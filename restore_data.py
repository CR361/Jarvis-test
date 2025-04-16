import os
import json
import logging
from datetime import datetime
from app import app, db
from models import Customer, Invoice, InvoiceItem, Communication, Contract

logger = logging.getLogger(__name__)

def import_from_backup_data(backup_data):
    """
    Importeert gegevens uit de backup data naar de database.
    
    Args:
        backup_data: Dictionary met de backup data
    
    Returns:
        bool: True als de import succesvol was, anders False
    """
    try:
        # Maak eerst alle klanten aan
        customer_mapping = {}  # Mapping van oude ID naar nieuwe ID
        
        if 'customers' in backup_data and backup_data['customers']:
            for customer_data in backup_data['customers']:
                # Check of deze klant al bestaat (door email te controleren)
                existing = Customer.query.filter_by(email=customer_data.get('email')).first()
                if existing:
                    # Klant bestaat al, sla oude ID -> nieuwe ID mapping op
                    customer_mapping[customer_data.get('id')] = existing.id
                    continue
                
                # Maak nieuwe klant aan
                customer = Customer(
                    name=customer_data.get('name'),
                    company=customer_data.get('company'),
                    kvk_number=customer_data.get('kvk_number'),
                    email=customer_data.get('email'),
                    phone=customer_data.get('phone'),
                    address=customer_data.get('address'),
                    city=customer_data.get('city'),
                    postal_code=customer_data.get('postal_code'),
                    country=customer_data.get('country', 'Nederland'),
                    notes=customer_data.get('notes')
                )
                db.session.add(customer)
                db.session.flush()  # Nodig om de ID te krijgen voordat we commit doen
                
                # Sla oude ID -> nieuwe ID mapping op
                customer_mapping[customer_data.get('id')] = customer.id
                
            db.session.commit()
            logger.info(f"Geimporteerd: {len(customer_mapping)} klanten")
        
        # Maak facturen aan
        invoice_mapping = {}  # Mapping van oude ID naar nieuwe ID
        
        if 'invoices' in backup_data and backup_data['invoices']:
            for invoice_data in backup_data['invoices']:
                old_customer_id = invoice_data.get('customer_id')
                
                # Verkrijg nieuwe klant ID
                if old_customer_id in customer_mapping:
                    new_customer_id = customer_mapping[old_customer_id]
                else:
                    # Als er geen mapping is, sla deze factuur over
                    logger.warning(f"Geen bijbehorende klant gevonden voor factuur {invoice_data.get('invoice_number')}")
                    continue
                
                # Controleer of de factuur al bestaat
                existing = Invoice.query.filter_by(invoice_number=invoice_data.get('invoice_number')).first()
                if existing:
                    # Factuur bestaat al, sla oude ID -> nieuwe ID mapping op
                    invoice_mapping[invoice_data.get('id')] = existing.id
                    continue
                
                # Parse datums
                issue_date = None
                due_date = None
                payment_date = None
                
                if invoice_data.get('issue_date'):
                    try:
                        issue_date = datetime.fromisoformat(invoice_data.get('issue_date'))
                    except:
                        pass
                
                if invoice_data.get('due_date'):
                    try:
                        due_date = datetime.fromisoformat(invoice_data.get('due_date'))
                    except:
                        pass
                
                if invoice_data.get('payment_date'):
                    try:
                        payment_date = datetime.fromisoformat(invoice_data.get('payment_date'))
                    except:
                        pass
                
                # Maak nieuwe factuur aan
                invoice = Invoice(
                    invoice_number=invoice_data.get('invoice_number'),
                    customer_id=new_customer_id,
                    issue_date=issue_date,
                    due_date=due_date,
                    total_amount=invoice_data.get('total_amount', 0.0),
                    amount_paid=invoice_data.get('amount_paid', 0.0),
                    is_paid=invoice_data.get('is_paid', False),
                    payment_date=payment_date,
                    notes=invoice_data.get('notes')
                )
                db.session.add(invoice)
                db.session.flush()
                
                # Sla oude ID -> nieuwe ID mapping op
                invoice_mapping[invoice_data.get('id')] = invoice.id
                
            db.session.commit()
            logger.info(f"Geimporteerd: {len(invoice_mapping)} facturen")
            
        # Maak factuuritems aan
        if 'invoice_items' in backup_data and backup_data['invoice_items']:
            item_count = 0
            for item_data in backup_data['invoice_items']:
                old_invoice_id = item_data.get('invoice_id')
                
                # Verkrijg nieuwe factuur ID
                if old_invoice_id in invoice_mapping:
                    new_invoice_id = invoice_mapping[old_invoice_id]
                else:
                    # Als er geen mapping is, sla dit item over
                    continue
                
                # Maak nieuw factuuritem aan
                item = InvoiceItem(
                    invoice_id=new_invoice_id,
                    description=item_data.get('description'),
                    quantity=item_data.get('quantity', 1),
                    unit_price=item_data.get('unit_price', 0.0)
                )
                db.session.add(item)
                item_count += 1
                
            db.session.commit()
            logger.info(f"Geimporteerd: {item_count} factuuritems")
            
        # Maak communicatie-items aan
        if 'communications' in backup_data and backup_data['communications']:
            comm_count = 0
            for comm_data in backup_data['communications']:
                old_customer_id = comm_data.get('customer_id')
                
                # Verkrijg nieuwe klant ID
                if old_customer_id in customer_mapping:
                    new_customer_id = customer_mapping[old_customer_id]
                else:
                    # Als er geen mapping is, sla dit item over
                    continue
                
                # Parse datum
                comm_date = None
                if comm_data.get('date'):
                    try:
                        comm_date = datetime.fromisoformat(comm_data.get('date'))
                    except:
                        pass
                
                # Maak nieuw communicatie-item aan
                communication = Communication(
                    customer_id=new_customer_id,
                    type=comm_data.get('type', 'notitie'),
                    subject=comm_data.get('subject'),
                    content=comm_data.get('content'),
                    date=comm_date or datetime.utcnow()
                )
                db.session.add(communication)
                comm_count += 1
                
            db.session.commit()
            logger.info(f"Geimporteerd: {comm_count} communicatie-items")
            
        # Maak contracten aan
        if 'contracts' in backup_data and backup_data['contracts']:
            contract_count = 0
            for contract_data in backup_data['contracts']:
                old_customer_id = contract_data.get('customer_id')
                
                # Verkrijg nieuwe klant ID
                if old_customer_id in customer_mapping:
                    new_customer_id = customer_mapping[old_customer_id]
                else:
                    # Als er geen mapping is, sla dit item over
                    continue
                
                # Controleer of het contract al bestaat (op basis van titel en klant)
                existing = Contract.query.filter_by(
                    customer_id=new_customer_id, 
                    title=contract_data.get('title')
                ).first()
                
                if existing:
                    continue
                
                # Parse datums
                created_at = None
                updated_at = None
                sent_at = None
                signed_at = None
                
                if contract_data.get('created_at'):
                    try:
                        created_at = datetime.fromisoformat(contract_data.get('created_at'))
                    except:
                        pass
                        
                if contract_data.get('updated_at'):
                    try:
                        updated_at = datetime.fromisoformat(contract_data.get('updated_at'))
                    except:
                        pass
                        
                if contract_data.get('sent_at'):
                    try:
                        sent_at = datetime.fromisoformat(contract_data.get('sent_at'))
                    except:
                        pass
                        
                if contract_data.get('signed_at'):
                    try:
                        signed_at = datetime.fromisoformat(contract_data.get('signed_at'))
                    except:
                        pass
                
                # Maak nieuw contract aan
                contract = Contract(
                    customer_id=new_customer_id,
                    title=contract_data.get('title'),
                    content=contract_data.get('content'),
                    status=contract_data.get('status', 'concept'),
                    signing_url=contract_data.get('signing_url'),
                    signature_data=contract_data.get('signature_data'),
                    signed_at=signed_at,
                    signed_by=contract_data.get('signed_by'),
                    signed_ip=contract_data.get('signed_ip'),
                    created_at=created_at,
                    updated_at=updated_at,
                    sent_at=sent_at
                )
                db.session.add(contract)
                contract_count += 1
                
            db.session.commit()
            logger.info(f"Geimporteerd: {contract_count} contracten")
            
        return True
    
    except Exception as e:
        logger.error(f"Fout bij importeren van gegevens: {e}")
        db.session.rollback()
        return False

def check_for_backup_json():
    """
    Zoekt naar JSON-backupbestanden en importeert data indien gevonden.
    """
    try:
        # Zoek naar JSON-backupbestanden in de hoofdmap
        possible_files = [
            os.path.join(os.getcwd(), 'database_data.json'),
            os.path.join(os.getcwd(), 'database_data (1).json')
        ]
        
        json_path = None
        for file_path in possible_files:
            if os.path.exists(file_path):
                json_path = file_path
                break
                
        if json_path:
            logger.info(f"JSON backupbestand gevonden: {json_path}")
            
            # Controleer of er al gegevens in de database zijn
            if Customer.query.count() == 0:
                logger.info(f"Database is leeg, importeren van gegevens uit {json_path}")
                
                # Laad de JSON-data
                with open(json_path, 'r', encoding='utf-8') as f:
                    try:
                        backup_data = json.load(f)
                        if import_from_backup_data(backup_data):
                            logger.info("Gegevens succesvol geïmporteerd uit JSON-backup")
                            return True
                    except json.JSONDecodeError:
                        logger.error(f"Ongeldig JSON-formaat in {json_path}")
            else:
                logger.info("Database bevat al gegevens, import overgeslagen")
        else:
            logger.info("Geen JSON-backupbestand gevonden in de hoofdmap")
    except Exception as e:
        logger.error(f"Fout bij controleren op JSON-backups: {e}")
    
    return False

def check_for_backup_html():
    """
    Zoekt naar HTML-backupbestanden in de map 'backups' en 
    de hoofdmap, en importeert data indien gevonden.
    """
    backup_dirs = [
        os.path.join(os.getcwd(), 'backups'),  # Standaard backup map
        os.getcwd(),  # Hoofdmap voor het geval een gebruiker het daar heeft geplaatst
    ]
    
    backup_files = []
    
    # Zoek voor alle HTML-bestanden die mogelijk een backup zijn
    for directory in backup_dirs:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith('.html') and 'jarvis_complete_backup' in file.lower():
                    backup_files.append(os.path.join(directory, file))
    
    if not backup_files:
        logger.info("Geen backup bestanden gevonden om te importeren")
        return
    
    # Sorteer bestanden op aanmaakdatum (nieuwste eerst)
    backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Probeer elk backupbestand uit te lezen en te importeren
    for backup_file in backup_files:
        logger.info(f"Probeer backup te importeren uit {backup_file}")
        
        try:
            # Lees het bestand en zoek het JSON data-gedeelte
            with open(backup_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Zoek naar het JSON-gedeelte
                start_marker = '<div style="display: none;" id="full-database-backup">'
                end_marker = '</div>'
                
                if start_marker in content:
                    start_index = content.find(start_marker) + len(start_marker)
                    end_index = content.find(end_marker, start_index)
                    
                    if start_index < end_index:
                        json_data = content[start_index:end_index].strip()
                        backup_data = json.loads(json_data)
                        
                        # Controleer of de database leeg is voordat we importeren
                        if Customer.query.count() == 0:
                            logger.info(f"Database is leeg, importeren van gegevens uit {os.path.basename(backup_file)}")
                            if import_from_backup_data(backup_data):
                                logger.info("Gegevens succesvol geïmporteerd uit backup")
                                return
                        else:
                            logger.info("Database bevat al gegevens, import overgeslagen")
                            return
        except Exception as e:
            logger.error(f"Fout bij verwerken van backupbestand {backup_file}: {e}")
    
    logger.info("Geen geldige backup bestanden gevonden om te importeren")

# Dit wordt uitgevoerd bij het importeren van de module
def init_app():
    """Initialiseer de app en probeer de data te importeren indien nodig"""
    with app.app_context():
        # Controleer of er al gegevens in de database zijn
        if Customer.query.count() == 0:
            logger.info("Database is leeg, controleren op backups...")
            # Eerst probeer een JSON-backup te laden
            if not check_for_backup_json():
                # Als dat niet lukt, probeer HTML-backups
                check_for_backup_html()
        else:
            logger.info("Database bevat al gegevens, geen import nodig")