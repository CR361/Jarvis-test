from flask import render_template, redirect, url_for, flash, request
from app import app, db
from models import ChecklistItem, Contractor
from forms import ChecklistItemForm, ContractorForm

def register_checklist_routes(app):
    @app.route('/checklist', methods=['GET'])
    def checklist():
        """Toon de checklist met alle openstaande en voltooide items"""
        # Haal alle checklist items op, gesorteerd op status (niet voltooid eerst)
        checklist_items = ChecklistItem.query.order_by(ChecklistItem.is_completed, ChecklistItem.created_at.desc()).all()
        
        # Tel statistieken
        total_items = len(checklist_items)
        completed_items = sum(1 for item in checklist_items if item.is_completed)
        
        # Krijg alle aannemers voor de filters
        contractors = Contractor.query.order_by(Contractor.name).all()
        
        return render_template('checklist.html', 
                             checklist_items=checklist_items,
                             total_items=total_items,
                             completed_items=completed_items,
                             completion_percentage=int(completed_items / max(total_items, 1) * 100),
                             contractors=contractors)
    
    @app.route('/checklist/item/<int:item_id>/complete', methods=['POST'])
    def complete_checklist_item(item_id):
        """Markeer een checklist item als voltooid"""
        item = ChecklistItem.query.get_or_404(item_id)
        
        # Verander de status van het item
        if item.is_completed:
            item.mark_incomplete()
            flash('Item gemarkeerd als niet voltooid.', 'info')
        else:
            item.mark_completed()
            flash('Item gemarkeerd als voltooid!', 'success')
        
        # Sla de wijzigingen op
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Fout bij bijwerken checklist item: {e}")
            flash('Er is een fout opgetreden bij het bijwerken van het item.', 'danger')
        
        # Bepaal de terugkeer-URL (indien van een factuur of klant afkomstig)
        return_url = request.form.get('return_url')
        if return_url:
            return redirect(return_url)
        
        return redirect(url_for('checklist'))
    
    @app.route('/checklist/item/<int:item_id>/edit', methods=['GET', 'POST'])
    def edit_checklist_item(item_id):
        """Bewerk een checklist item"""
        item = ChecklistItem.query.get_or_404(item_id)
        
        # Haal alle aannemers op voor dropdown
        contractors = Contractor.query.order_by(Contractor.name).all()
        
        # Creëer formulier en zet huidige waarden
        form = ChecklistItemForm(obj=item, contractors=contractors)
        
        # Voor een lege waarde in contractor_id (als er geen aannemer is toegewezen)
        if not item.contractor_id:
            form.contractor_id.data = ''
        
        if form.validate_on_submit():
            # Update de item gegevens
            item.notes = form.notes.data
            item.is_completed = form.is_completed.data
            
            # Update de aannemer als die is geselecteerd
            if form.contractor_id.data:
                item.contractor_id = int(form.contractor_id.data)
            else:
                item.contractor_id = None
            
            # Werk de voltooiingsdatum bij indien nodig
            if form.is_completed.data and not item.completed_at:
                item.mark_completed()
            elif not form.is_completed.data and item.completed_at:
                item.mark_incomplete()
            
            # Sla de wijzigingen op
            try:
                db.session.commit()
                flash('Checklist item succesvol bijgewerkt!', 'success')
                return redirect(url_for('checklist'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Fout bij bijwerken checklist item: {e}")
                flash('Er is een fout opgetreden bij het bijwerken van het item.', 'danger')
        
        return render_template('edit_checklist_item.html', form=form, item=item)
    
    @app.route('/contractors', methods=['GET'])
    def contractor_list():
        """Toon alle aannemers"""
        contractors = Contractor.query.order_by(Contractor.name).all()
        return render_template('contractor_list.html', contractors=contractors)
    
    @app.route('/contractors/create', methods=['GET', 'POST'])
    def create_contractor():
        """Maak een nieuwe aannemer aan"""
        form = ContractorForm()
        
        if form.validate_on_submit():
            contractor = Contractor(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                specialty=form.specialty.data,
                notes=form.notes.data
            )
            
            try:
                db.session.add(contractor)
                db.session.commit()
                flash('Aannemer succesvol toegevoegd!', 'success')
                return redirect(url_for('contractor_list'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Fout bij aanmaken aannemer: {e}")
                flash('Er is een fout opgetreden bij het aanmaken van de aannemer.', 'danger')
        
        return render_template('create_contractor.html', form=form)
    
    @app.route('/contractors/<int:contractor_id>/edit', methods=['GET', 'POST'])
    def edit_contractor(contractor_id):
        """Bewerk een aannemer"""
        contractor = Contractor.query.get_or_404(contractor_id)
        form = ContractorForm(obj=contractor)
        
        if form.validate_on_submit():
            form.populate_obj(contractor)
            
            try:
                db.session.commit()
                flash('Aannemer succesvol bijgewerkt!', 'success')
                return redirect(url_for('contractor_list'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Fout bij bijwerken aannemer: {e}")
                flash('Er is een fout opgetreden bij het bijwerken van de aannemer.', 'danger')
        
        return render_template('edit_contractor.html', form=form, contractor=contractor)
    
    @app.route('/contractors/<int:contractor_id>/delete', methods=['POST'])
    def delete_contractor(contractor_id):
        """Verwijder een aannemer"""
        contractor = Contractor.query.get_or_404(contractor_id)
        
        # Controleer of de aannemer geen taken heeft
        if len(contractor.assigned_tasks) > 0:
            flash('Deze aannemer kan niet worden verwijderd omdat er nog taken aan hem/haar zijn toegewezen.', 'danger')
            return redirect(url_for('contractor_list'))
        
        try:
            db.session.delete(contractor)
            db.session.commit()
            flash('Aannemer succesvol verwijderd.', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Fout bij verwijderen aannemer: {e}")
            flash('Er is een fout opgetreden bij het verwijderen van de aannemer.', 'danger')
            
        return redirect(url_for('contractor_list'))