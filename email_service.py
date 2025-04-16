import os
import logging
from flask import render_template, current_app, request
from app import mail, app
from flask_mail import Message
from datetime import datetime

logger = logging.getLogger(__name__)

def get_email_templates():
    """
    Haal alle beschikbare e-mailtemplates op met hun inhoud
    
    Returns:
        dict: Een dictionary met template_id als key en template-inhoud als value
    """
    templates = {
        'payment_reminder': {
            'subject': 'Betalingsherinnering voor factuur {invoice_number}',
            'body': '''
                <p>Beste {customer_name},</p>
                <p>Dit is een vriendelijke herinnering dat factuur <strong>{invoice_number}</strong> met een totaalbedrag van <strong>€{total_amount:.2f}</strong> vervalt op <strong>{due_date}</strong>.</p>
                <p>Als u de betaling reeds heeft uitgevoerd, kunt u deze e-mail als niet verzonden beschouwen.</p>
                <p>Met vriendelijke groet,<br>{company_name}</p>
            '''
        },
        'thank_you': {
            'subject': 'Bedankt voor uw betaling',
            'body': '''
                <p>Beste {customer_name},</p>
                <p>Hartelijk dank voor uw betaling van factuur <strong>{invoice_number}</strong> met een totaalbedrag van <strong>€{total_amount:.2f}</strong>.</p>
                <p>We stellen uw zakelijke relatie zeer op prijs.</p>
                <p>Met vriendelijke groet,<br>{company_name}</p>
            '''
        },
        'welcome': {
            'subject': 'Welkom bij {company_name}',
            'body': '''
                <p>Beste {customer_name},</p>
                <p>Hartelijk welkom als klant bij {company_name}. We kijken uit naar een prettige samenwerking.</p>
                <p>Als u vragen heeft, aarzel dan niet om contact met ons op te nemen.</p>
                <p>Met vriendelijke groet,<br>{company_name}</p>
            '''
        },
        'invoice': {
            'subject': 'Factuur {invoice_number}',
            'body': '''
                <p>Beste {customer_name},</p>
                <p>Hierbij ontvangt u factuur <strong>{invoice_number}</strong> met een totaalbedrag van <strong>€{total_amount:.2f}</strong>, te voldoen voor <strong>{due_date}</strong>.</p>
                <p>U kunt de factuur betalen door het bedrag over te maken naar:</p>
                <p>
                    <strong>IBAN:</strong> NL00 INGB 0000 0000 00<br>
                    <strong>T.n.v.:</strong> {company_name}<br>
                    <strong>O.v.v.:</strong> {invoice_number}
                </p>
                <p>Met vriendelijke groet,<br>{company_name}</p>
            '''
        },
        'general': {
            'subject': '{subject}',
            'body': '''
                <p>Beste {customer_name},</p>
                <p>{content}</p>
                <p>Met vriendelijke groet,<br>{company_name}</p>
            '''
        }
    }
    
    return templates

def send_email(to_email, subject, content):
    """
    Verstuur een e-mail via SendGrid of simuleer verzending bij ontwikkeling
    
    Args:
        to_email: E-mailadres van de ontvanger
        subject: Onderwerp van de e-mail
        content: HTML inhoud van de e-mail
        
    Returns:
        bool: True als het versturen is gelukt, anders False
    """
    try:
        # Controleer of we in een productie- of ontwikkelomgeving zitten
        if not app.config.get('MAIL_PASSWORD'):
            # Simuleer verzending in ontwikkelomgeving (geen echte e-mail)
            logger.info(f"Simuleer versturen e-mail naar {to_email}")
            logger.info(f"Onderwerp: {subject}")
            logger.info(f"Inhoud: {content[:100]}...")
            return True
        
        # Verstuur de e-mail in productieomgeving
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=content,
            sender=app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        logger.info(f"E-mail succesvol verzonden naar {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Fout bij versturen e-mail: {e}")
        return False

def send_invoice_email(invoice):
    """
    Stuurt een e-mail naar de klant met informatie over de factuur.
    
    Args:
        invoice: Het Invoice-object dat moet worden verzonden
        
    Returns:
        bool: True als het versturen is gelukt, anders False
    """
    # Haal de klantgegevens op
    customer = invoice.customer
    
    # Formateer de datums
    issue_date = invoice.issue_date.strftime('%d-%m-%Y')
    due_date = invoice.due_date.strftime('%d-%m-%Y')
    
    # Haal de template op
    templates = get_email_templates()
    template = templates.get('invoice')
    
    # Vervang de placeholders
    subject = template['subject'].format(
        invoice_number=invoice.invoice_number
    )
    
    # Stel de inhoud samen op basis van de template
    content = template['body'].format(
        customer_name=customer.name,
        invoice_number=invoice.invoice_number,
        total_amount=invoice.total_amount,
        issue_date=issue_date,
        due_date=due_date,
        company_name=app.config.get('COMPANY_NAME', 'Uw Bedrijf')
    )
    
    # Verstuur de e-mail
    return send_email(customer.email, subject, content)

def send_contract_email(contract):
    """
    Stuurt een e-mail naar de klant met informatie over het contract en een link om te ondertekenen.
    
    Args:
        contract: Het Contract-object dat moet worden verzonden
        
    Returns:
        bool: True als het versturen is gelukt, anders False
    """
    # Haal de klantgegevens op
    customer = contract.customer
    
    # Genereer de ondertekenings-URL
    signing_url = f"{request.host_url.rstrip('/')}/contracts/sign/{contract.signing_url}"
    
    # Stel de inhoud samen
    subject = f"Contract: {contract.title}"
    
    content = f"""
    <p>Beste {customer.name},</p>
    <p>Hierbij ontvangt u het contract "{contract.title}" ter ondertekening.</p>
    <p>U kunt het contract bekijken en ondertekenen via de volgende link:</p>
    <p><a href="{signing_url}">{signing_url}</a></p>
    <p>Met vriendelijke groet,<br>{app.config.get('COMPANY_NAME', 'Uw Bedrijf')}</p>
    """
    
    # Verstuur de e-mail
    success = send_email(customer.email, subject, content)
    
    # Update contract status en verzenddatum als de e-mail is verzonden
    if success:
        contract.status = 'verzonden'
        contract.sent_at = datetime.utcnow()
        
    return success

def send_custom_email(to_email, subject, content, customer_name=None, template_id=None):
    """
    Stuurt een aangepaste e-mail naar een klant.
    
    Args:
        to_email: E-mailadres van de ontvanger
        subject: Onderwerp van de e-mail
        content: Inhoud van de e-mail
        customer_name: Naam van de klant (optioneel)
        template_id: ID van een voorgedefinieerde template (optioneel)
        
    Returns:
        bool: True als het versturen is gelukt, anders False
    """
    # Als een template is gespecificeerd, gebruik deze
    if template_id:
        templates = get_email_templates()
        template = templates.get(template_id)
        
        if template:
            # Vervang de placeholders in het onderwerp
            email_subject = template['subject'].format(
                subject=subject,
                company_name=app.config.get('COMPANY_NAME', 'Uw Bedrijf')
            )
            
            # Vervang de placeholders in de inhoud
            email_content = template['body'].format(
                customer_name=customer_name or "klant",
                content=content,
                company_name=app.config.get('COMPANY_NAME', 'Uw Bedrijf')
            )
            
            return send_email(to_email, email_subject, email_content)
    
    # Geen template of onbekende template, stuur een eenvoudige e-mail
    email_content = f"""
    <p>Beste {customer_name or "klant"},</p>
    <p>{content}</p>
    <p>Met vriendelijke groet,<br>{app.config.get('COMPANY_NAME', 'Uw Bedrijf')}</p>
    """
    
    return send_email(to_email, subject, email_content)