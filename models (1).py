from datetime import datetime, timedelta
import secrets
from app import db

class Customer(db.Model):
    """Model voor klantgegevens"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    kvk_number = db.Column(db.String(20))
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default="Nederland")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoices = db.relationship('Invoice', backref='customer', lazy=True, cascade="all, delete-orphan")
    communications = db.relationship('Communication', backref='customer', lazy=True, cascade="all, delete-orphan")
    checklist_items = db.relationship('ChecklistItem', backref='customer', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.name} ({self.id})>"

    def total_outstanding(self):
        """Bereken het totale openstaande bedrag van onbetaalde facturen"""
        return sum(invoice.amount_due() for invoice in self.invoices if not invoice.is_paid)

    def total_invoiced(self):
        """Bereken het totaal gefactureerde bedrag"""
        return sum(invoice.total_amount for invoice in self.invoices)

class Invoice(db.Model):
    """Model voor factuurgegevens"""
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    is_paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} ({self.id})>"

    def amount_due(self):
        """Bereken het resterende verschuldigde bedrag"""
        return self.total_amount - self.amount_paid

    def status(self):
        """Geef de status van de factuur terug"""
        today = datetime.utcnow().date()
        if self.is_paid:
            return "Betaald"
        elif self.due_date < today:
            return "Verlopen"
        else:
            return "Openstaand"
            
    def add_items_to_checklist(self):
        """Voeg alle items van deze factuur toe aan de checklist"""
        for item in self.items:
            if not item.checklist_item:
                checklist_item = ChecklistItem(
                    customer_id=self.customer_id,
                    invoice_item_id=item.id,
                    description=item.description,
                    created_at=datetime.utcnow()
                )
                db.session.add(checklist_item)

# Aannemers voor het toewijzen van taken
class Contractor(db.Model):
    """Model voor aannemers die taken kunnen uitvoeren"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    specialty = db.Column(db.String(100))  # bijv. loodgieter, elektricien, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relatie met checklist items
    assigned_tasks = db.relationship('ChecklistItem', backref='assigned_contractor', lazy=True)
    
    def __repr__(self):
        return f"<Contractor {self.name} ({self.id})>"

class ChecklistItem(db.Model):
    """Model voor checklist items (taken) gebaseerd op factuuritems"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    invoice_item_id = db.Column(db.Integer, db.ForeignKey('invoice_item.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('contractor.id'), nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        status = "Voltooid" if self.is_completed else "Openstaand"
        return f"<ChecklistItem {self.description} ({status})>"
    
    def mark_completed(self):
        """Markeer dit item als voltooid"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
    
    def mark_incomplete(self):
        """Markeer dit item als niet voltooid"""
        self.is_completed = False
        self.completed_at = None
    
    def assign_contractor(self, contractor_id):
        """Wijs een aannemer toe aan dit item"""
        self.contractor_id = contractor_id

class InvoiceItem(db.Model):
    """Model voor factuuritems"""
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    
    # Relatie met checklist items
    checklist_item = db.relationship('ChecklistItem', backref='invoice_item', uselist=False)

    def __repr__(self):
        return f"<InvoiceItem {self.description} ({self.id})>"

    def total(self):
        """Bereken de totale prijs voor dit item"""
        return self.quantity * self.unit_price

class Communication(db.Model):
    """Model voor het bijhouden van communicatie met klanten"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # email, telefoon, vergadering, etc.
    subject = db.Column(db.String(200))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Communication {self.type} with {self.customer_id} on {self.date}>"

class Contract(db.Model):
    """Model voor contracten die klanten kunnen ondertekenen"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='concept')  # concept, verzonden, ondertekend, geweigerd
    signing_url = db.Column(db.String(255), unique=True)

    signature_data = db.Column(db.Text)  # Opslag van de handtekening (als base64 data URL)
    signed_at = db.Column(db.DateTime)
    signed_by = db.Column(db.String(100))
    signed_ip = db.Column(db.String(45))  # IPv6 adres kan tot 45 karakters zijn

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime)

    customer = db.relationship('Customer', backref=db.backref('contracts', lazy=True, cascade="all, delete-orphan"))

    def __init__(self, **kwargs):
        super(Contract, self).__init__(**kwargs)
        if not self.signing_url:
            self.signing_url = secrets.token_urlsafe(32)

    def __repr__(self):
        return f"<Contract {self.title} voor klant {self.customer_id}>"

    def status_display(self):
        """Geef de status in Nederlands terug"""
        statuses = {
            'concept': 'Concept',
            'verzonden': 'Verzonden',
            'ondertekend': 'Ondertekend',
            'geweigerd': 'Geweigerd'
        }
        return statuses.get(self.status, self.status.title())
