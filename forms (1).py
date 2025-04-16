from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, DateField, SelectField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
import re
from datetime import datetime, timedelta

class CustomerForm(FlaskForm):
    name = StringField('Naam', validators=[DataRequired(), Length(max=100)])
    company = StringField('Bedrijfsnaam', validators=[Length(max=100)])
    kvk_number = StringField('KVK-nummer', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Telefoonnummer', validators=[Length(max=20)])
    address = StringField('Adres', validators=[Length(max=200)])
    city = StringField('Plaats', validators=[Length(max=100)])
    postal_code = StringField('Postcode', validators=[Length(max=20)])
    country = StringField('Land', validators=[Length(max=100)], default='Nederland')
    notes = TextAreaField('Notities')
    
    def validate_kvk_number(self, field):
        # Optional validation for Dutch KVK numbers (8 digits)
        if field.data and field.data.strip():
            # Remove spaces and dashes
            kvk = re.sub(r'[\s-]', '', field.data)
            
            # Check if it's a valid 8-digit number
            if not re.match(r'^\d{8}$', kvk):
                raise ValidationError('KVK-nummer moet 8 cijfers bevatten')

class CustomerSearchForm(FlaskForm):
    search = StringField('Zoeken')

class InvoiceForm(FlaskForm):
    customer_id = SelectField('Klant', coerce=int, validators=[DataRequired()])
    issue_date = DateField('Factuurdatum', validators=[DataRequired()], default=datetime.utcnow)
    due_date = DateField('Vervaldatum', validators=[DataRequired()], default=lambda: datetime.utcnow() + timedelta(days=30))
    notes = TextAreaField('Notities')

class InvoiceItemForm(FlaskForm):
    description = StringField('Omschrijving', validators=[DataRequired()])
    quantity = FloatField('Aantal', validators=[DataRequired()], default=1)
    unit_price = FloatField('Prijs per eenheid', validators=[DataRequired()])

class MarkInvoicePaidForm(FlaskForm):
    payment_date = DateField('Betaaldatum', validators=[DataRequired()], default=datetime.utcnow)

class CommunicationForm(FlaskForm):
    type = SelectField('Type', choices=[
        ('email', 'E-mail'),
        ('telefoon', 'Telefoongesprek'),
        ('vergadering', 'Vergadering'),
        ('notitie', 'Interne notitie'),
        ('anders', 'Anders')
    ], validators=[DataRequired()])
    subject = StringField('Onderwerp', validators=[Length(max=200)])
    content = TextAreaField('Inhoud', validators=[DataRequired()])
    date = DateField('Datum', validators=[DataRequired()], default=datetime.utcnow)

class ContractForm(FlaskForm):
    title = StringField('Titel', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Inhoud', validators=[DataRequired()])

class EmailForm(FlaskForm):
    customer_id = SelectField('Klant', coerce=int, validators=[DataRequired()])
    subject = StringField('Onderwerp', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Inhoud', validators=[DataRequired()])
    template = SelectField('Template', choices=[
        ('', 'Selecteer een template (optioneel)'),
        ('payment_reminder', 'Betalingsherinnering'),
        ('thank_you', 'Bedankt voor uw betaling'),
        ('welcome', 'Welkom als nieuwe klant'),
        ('invoice', 'Factuur verzenden'),
        ('general', 'Algemene communicatie')
    ])
    
class ContractorForm(FlaskForm):
    """Formulier voor het aanmaken en bewerken van aannemers"""
    name = StringField('Naam', validators=[DataRequired(), Length(max=100)])
    email = StringField('E-mail', validators=[Email(), Length(max=100)])
    phone = StringField('Telefoonnummer', validators=[Length(max=20)])
    specialty = StringField('Specialiteit', validators=[Length(max=100)])
    notes = TextAreaField('Notities')
    
class ChecklistItemForm(FlaskForm):
    """Formulier voor het bewerken van checklist items"""
    contractor_id = SelectField('Aannemer', validators=[Optional()], default='')
    is_completed = BooleanField('Voltooid')
    notes = TextAreaField('Notities')
    
    def __init__(self, *args, **kwargs):
        super(ChecklistItemForm, self).__init__(*args, **kwargs)
        # Verwijder de coerce functie omdat we ook lege waardes moeten kunnen verwerken
        # We zullen de conversie naar int in de route code doen