import os
import logging
from app import app, mail
from flask import render_template_string
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

def get_email_templates():
    """
    Haal alle beschikbare e-mailtemplates op met hun inhoud
    
    Returns:
        dict: Een dictionary met template_id als key en template-inhoud als value
    """
    return {
        'payment_reminder': {
            'subject': 'Herinnering: Openstaande factuur',
            'content': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #4A76A8; color: white; padding: 20px; }
                    .content { padding: 20px; }
                    .footer { margin-top: 30px; font-size: 0.8em; color: #777; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Betalingsherinnering</h2>
                </div>
                <div class="content">
                    <p>Beste {customer_name},</p>
                    
                    <p>Dit is een vriendelijke herinnering dat uw factuur {invoice_number} met een bedrag van €{invoice_amount} nog niet is voldaan.
                    De factuur had als uiterste betaaldatum {due_date}.</p>
                    
                    <p>Wij verzoeken u vriendelijk om het verschuldigde bedrag zo spoedig mogelijk te voldoen.
                    Als u vragen heeft over deze factuur, neem dan gerust contact met ons op.</p>
                    
                    <p>Met vriendelijke groet,<br>
                    Uw bedrijfsnaam</p>
                </div>
                <div class="footer">
                    <p>Deze e-mail is automatisch gegenereerd, antwoorden op dit bericht worden niet gelezen.</p>
                </div>
            </body>
            </html>
            """
        },
        'thank_you': {
            'subject': 'Bedankt voor uw betaling',
            'content': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #4A76A8; color: white; padding: 20px; }
                    .content { padding: 20px; }
                    .footer { margin-top: 30px; font-size: 0.8em; color: #777; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Betaling Ontvangen</h2>
                </div>
                <div class="content">
                    <p>Beste {customer_name},</p>
                    
                    <p>Hartelijk dank voor uw betaling van factuur {invoice_number} ter waarde van €{invoice_amount}.
                    Wij waarderen uw prompte betaling zeer.</p>
                    
                    <p>Als u vragen heeft of als we u nog ergens anders mee van dienst kunnen zijn, neem dan gerust contact met ons op.</p>
                    
                    <p>Met vriendelijke groet,<br>
                    Uw bedrijfsnaam</p>
                </div>
                <div class="footer">
                    <p>Deze e-mail is automatisch gegenereerd, antwoorden op dit bericht worden niet gelezen.</p>
                </div>
            </body>
            </html>
            """
        },
        'welcome': {
            'subject': 'Welkom als klant',
            'content': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #4A76A8; color: white; padding: 20px; }
                    .content { padding: 20px; }
                    .footer { margin-top: 30px; font-size: 0.8em; color: #777; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Welkom bij ons bedrijf</h2>
                </div>
                <div class="content">
                    <p>Beste {customer_name},</p>
                    
                    <p>Hartelijk welkom als nieuwe klant bij ons bedrijf. Wij zijn blij dat we u mogen verwelkomen en kijken uit naar een prettige samenwerking.</p>
                    
                    <p>Als u vragen heeft, neem dan gerust contact met ons op. We staan u graag te woord.</p>
                    
                    <p>Met vriendelijke groet,<br>
                    Uw bedrijfsnaam</p>
                </div>
                <div class="footer">
                    <p>Deze e-mail is automatisch gegenereerd, antwoorden op dit bericht worden niet gelezen.</p>
                </div>
            </body>
            </html>
            """
        },
        'invoice': {
            'subject': 'Nieuwe factuur {invoice_number}',
            'content': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #4A76A8; color: white; padding: 20px; }
                    .content { padding: 20px; }
                    .footer { margin-top: 30px; font-size: 0.8em; color: #777; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
                    th { background-color: #f2f2f2; }
                    .amount { text-align: right; }
                    .total { font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Factuur {invoice_number}</h2>
                </div>
                <div class="content">
                    <p>Beste {customer_name},</p>
                    
                    <p>Hierbij ontvangt u factuur {invoice_number} met als vervaldatum {due_date}.</p>
                    
                    <table>
                        <tr>
                            <th>Factuurnummer</th>
                            <td>{invoice_number}</td>
                        </tr>
                        <tr>
                            <th>Factuurdatum</th>
                            <td>{issue_date}</td>
                        </tr>
                        <tr>
                            <th>Vervaldatum</th>
                            <td>{due_date}</td>
                        </tr>
                        <tr>
                            <th>Totaalbedrag</th>
                            <td>€ {invoice_amount}</td>
                        </tr>
                    </table>
                    
                    <p>U kunt deze factuur betalen via bankoverschrijving onder vermelding van het factuurnummer.</p>
                    
                    <p>Heeft u vragen over deze factuur? Neem dan gerust contact met ons op.</p>
                    
                    <p>Met vriendelijke groet,<br>
                    Uw bedrijfsnaam</p>
                </div>
                <div class="footer">
                    <p>Deze e-mail is automatisch gegenereerd, antwoorden op dit bericht worden niet gelezen.</p>
                </div>
            </body>
            </html>
            """
        },
        'general': {
            'subject': 'Bericht van uw bedrijf',
            'content': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #4A76A8; color: white; padding: 20px; }
                    .content { padding: 20px; }
                    .footer { margin-top: 30px; font-size: 0.8em; color: #777; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Bericht van uw bedrijf</h2>
                </div>
                <div class="content">
                    <p>Beste {customer_name},</p>
                    
                    <p>Hartelijk dank voor het gebruik van onze diensten.</p>
                    
                    <p>Met vriendelijke groet,<br>
                    Uw bedrijfsnaam</p>
                </div>
                <div class="footer">
                    <p>Deze e-mail is automatisch gegenereerd, antwoorden op dit bericht worden niet gelezen.</p>
                </div>
            </body>
            </html>
            """
        }
    }

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
    # Controleer of SendGrid API key beschikbaar is
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    
    # Als er geen SendGrid API key is, simuleer verzending en schrijf naar logboek
    if not sendgrid_key:
        app.logger.warning("SENDGRID_API_KEY niet gevonden in omgevingsvariabelen - E-mail simulatiemodus ingeschakeld")
        app.logger.info(f"E-mail zou verzonden zijn naar: {to_email}")
        app.logger.info(f"Onderwerp: {subject}")
        
        # Registreer de e-mail als verzonden (voor ontwikkeldoeleinden)
        # In de toekomst kan de e-mail worden opgeslagen in een database
        return True
    
    # Als SendGrid API key wel beschikbaar is, verstuur de e-mail via SendGrid
    try:
        message = Mail(
            from_email=Email("noreply@jarvis-crm.com"),
            to_emails=To(to_email),
            subject=subject
        )
        message.content = Content("text/html", content)
        
        # Verstuur de e-mail
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        
        # Check response status
        if response.status_code >= 200 and response.status_code < 300:
            app.logger.info(f"E-mail succesvol verzonden naar {to_email}")
            return True
        else:
            app.logger.error(f"SendGrid error: status code {response.status_code}")
            app.logger.error(f"SendGrid response body: {response.body}")
            return False
    except Exception as e:
        app.logger.error(f"SendGrid error: {e}")
        return False

def send_invoice_email(invoice):
    """
    Stuurt een e-mail naar de klant met informatie over de factuur.
    
    Args:
        invoice: Het Invoice-object dat moet worden verzonden
        
    Returns:
        bool: True als het versturen is gelukt, anders False
    """
    try:
        # Haal klantgegevens op
        customer = invoice.customer
        
        # Bereid e-mailinhoud voor
        template = get_email_templates()['invoice']
        subject = template['subject'].replace('{invoice_number}', invoice.invoice_number)
        content = template['content']
        content = content.replace('{customer_name}', customer.name)
        content = content.replace('{invoice_number}', invoice.invoice_number)
        content = content.replace('{invoice_amount}', f"{invoice.total_amount:.2f}")
        content = content.replace('{due_date}', invoice.due_date.strftime('%d-%m-%Y'))
        content = content.replace('{issue_date}', invoice.issue_date.strftime('%d-%m-%Y'))
        
        # Verstuur e-mail
        return send_email(
            to_email=customer.email,
            subject=subject,
            content=content
        )
    except Exception as e:
        app.logger.error(f"Error sending invoice email: {e}")
        return False

def send_contract_email(contract):
    """
    Stuurt een e-mail naar de klant met informatie over het contract en een link om te ondertekenen.
    
    Args:
        contract: Het Contract-object dat moet worden verzonden
        
    Returns:
        bool: True als het versturen is gelukt, anders False
    """
    try:
        # Haal klantgegevens op
        customer = contract.customer
        
        # Genereer ondertekenings-URL
        app_url = os.environ.get('REPLIT_APP_URL', 'http://localhost:5000')
        signing_url = f"{app_url}/contracts/sign/{contract.signing_url}"
        
        # HTML template voor het contract e-mailbericht
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
                .header { background-color: #4A76A8; color: white; padding: 20px; }
                .content { padding: 20px; }
                .button { display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 20px; }
                .footer { margin-top: 30px; font-size: 0.8em; color: #777; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Contract: {contract_title}</h2>
            </div>
            <div class="content">
                <p>Beste {customer_name},</p>
                
                <p>Hierbij ontvangt u het contract "{contract_title}" ter ondertekening.</p>
                
                <p>U kunt het contract bekijken en ondertekenen door op onderstaande knop te klikken:</p>
                
                <a href="{signing_url}" class="button">Contract bekijken en ondertekenen</a>
                
                <p style="margin-top: 20px;">Indien de knop niet werkt, kunt u ook de volgende link kopiëren en in uw browser plakken:</p>
                <p>{signing_url}</p>
                
                <p>Heeft u vragen over dit contract? Neem dan gerust contact met ons op.</p>
                
                <p>Met vriendelijke groet,<br>
                Uw bedrijfsnaam</p>
            </div>
            <div class="footer">
                <p>Deze e-mail is automatisch gegenereerd, antwoorden op dit bericht worden niet gelezen.</p>
            </div>
        </body>
        </html>
        """
        
        # Vervang placeholders met actuele waarden
        html_content = html_template.replace('{contract_title}', contract.title)
        html_content = html_content.replace('{customer_name}', customer.name)
        html_content = html_content.replace('{signing_url}', signing_url)
        
        # Verstuur e-mail
        return send_email(
            to_email=customer.email,
            subject=f"Contract ter ondertekening: {contract.title}",
            content=html_content
        )
    except Exception as e:
        app.logger.error(f"Error sending contract email: {e}")
        return False

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
    try:
        # Check of er een template gebruikt moet worden
        if template_id and template_id in get_email_templates():
            template = get_email_templates()[template_id]
            template_content = template['content']
            template_subject = template['subject']
            
            # Vervang placeholders
            if customer_name:
                template_content = template_content.replace('{customer_name}', customer_name)
            else:
                template_content = template_content.replace('{customer_name}', 'Geachte klant')
                
            # Als er geen aangepaste content is, gebruik de template content
            if not content.strip():
                content = template_content
            
            # Als er geen aangepast onderwerp is, gebruik het template onderwerp
            if not subject.strip():
                subject = template_subject
        
        # Verstuur e-mail
        return send_email(
            to_email=to_email,
            subject=subject,
            content=content
        )
    except Exception as e:
        app.logger.error(f"Error sending custom email: {e}")
        return False