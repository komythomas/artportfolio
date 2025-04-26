from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
import logging

from . import pages_bp
from .forms import PageForm
from portfolio.models import Page # Modèle Page
from portfolio import db
# Importer les helpers depuis utils.py
from portfolio.utils import slugify, save_file, delete_file, get_absolute_path 

logger = logging.getLogger(__name__)

# Route pour lister les pages
@pages_bp.route('/')
@login_required
def list_pages():
    pages = Page.query.order_by(Page.display_order, Page.title).all()
    return render_template('admin/pages/list.html', pages=pages, page_title="Pages management")

# Routes pour créer une nouvelle page (GET pour afficher le formulaire, POST pour traiter)
@pages_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_page():
    form = PageForm()
    if form.validate_on_submit():
        # Générer le slug si non fourni
        page_slug = form.slug.data if form.slug.data else slugify(form.title.data)
        # Vérifier l'unicité du slug généré
        if Page.query.filter_by(slug=page_slug).first():
             flash(f"Le slug '{page_slug}' existe déjà ou ne peut être généré automatiquement de manière unique. Veuillez en fournir un manuellement.", "danger")
             return render_template('admin/pages/form.html', form=form, page_title="Nouvelle Page", current_cover_image=None)

        # Sauvegarder l'image de couverture si fournie
        cover_image_path = None
        if form.cover_image.data:
            cover_image_path = save_file(form.cover_image.data, prefix=f"page_{page_slug}")
            if cover_image_path is None: # Erreur lors de la sauvegarde
                 # Le message d'erreur est déjà flashé dans save_file
                 return render_template('admin/pages/form.html', form=form, page_title="Nouvelle Page", current_cover_image=None)

        # Créer la nouvelle page
        new_page = Page(
            title=form.title.data,
            slug=page_slug,
            content=form.content.data,
            cover_image_path=cover_image_path,
            display_order=form.display_order.data,
            is_visible=form.is_visible.data,
            meta_description=form.meta_description.data
        )
        
        try:
            db.session.add(new_page)
            db.session.commit()
            logger.info(f"Page created: {new_page.title} (ID: {new_page.id})")
            flash('Page créée avec succès!', 'success')
            return redirect(url_for('pages.list_pages'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating page: {e}", exc_info=True)
            # Si l'erreur est due à une contrainte unique sur le slug (double sécurité)
            if "UNIQUE constraint failed" in str(e):
                 flash(f"Erreur: Le slug '{page_slug}' existe déjà. Veuillez choisir un autre titre ou slug.", 'danger')
            else:
                 flash(f"Erreur lors de la création de la page: {e}", 'danger')
            # Nettoyer le fichier uploadé si l'enregistrement échoue
            if cover_image_path:
                delete_file(cover_image_path)
                 
    elif form.errors:
         logger.warning(f"Page form validation errors on create: {form.errors}")
         flash("Le formulaire contient des erreurs.", "danger")

    return render_template('admin/pages/form.html', form=form, page_title="New page", current_cover_image=None)

# Routes pour éditer une page existante
@pages_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(id):
    page = Page.query.get_or_404(id)
    form = PageForm(obj=page) # Pré-remplir le formulaire avec les données de la page

    if form.validate_on_submit():
        # Générer le slug si non fourni (ou si titre changé et slug vidé)
        page_slug = form.slug.data if form.slug.data else slugify(form.title.data)
        # Vérification unicité du slug (excluant la page actuelle) gérée dans form.validate_slug

        old_cover_image_path = page.cover_image_path # Sauver l'ancien chemin
        new_cover_image_path = page.cover_image_path # Initialiser avec l'ancien

        # Gérer l'upload de la nouvelle image
        if form.cover_image.data:
            saved_path = save_file(form.cover_image.data, prefix=f"page_{page_slug}")
            if saved_path is None: # Erreur lors de la sauvegarde
                 return render_template('admin/pages/form.html', form=form, page=page, page_title=f"Modifier: {page.title}", current_cover_image=get_absolute_path(old_cover_image_path))
            new_cover_image_path = saved_path

        # Mettre à jour les champs de la page
        page.title = form.title.data
        page.slug = page_slug
        page.content = form.content.data
        page.display_order = form.display_order.data
        page.is_visible = form.is_visible.data
        page.cover_image_path = new_cover_image_path # Peut être le nouveau chemin ou l'ancien si pas de nouvel upload
        page.meta_description = form.meta_description.data
        
        try:
            db.session.commit()
             # Supprimer l'ancienne image SEULEMENT si une nouvelle a été uploadée ET si elle est différente
            if new_cover_image_path != old_cover_image_path and old_cover_image_path:
                 delete_file(old_cover_image_path)
                 
            logger.info(f"Page updated: {page.title} (ID: {page.id})")
            flash('Page mise à jour avec succès!', 'success')
            return redirect(url_for('pages.list_pages'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating page ID {id}: {e}", exc_info=True)
            if "UNIQUE constraint failed" in str(e):
                 flash(f"Erreur: Le slug '{page_slug}' existe déjà. Veuillez choisir un autre titre ou slug.", 'danger')
            else:
                 flash(f"Erreur lors de la mise à jour de la page: {e}", 'danger')
            # Si erreur DB, il faut potentiellement nettoyer le nouveau fichier uploadé (si différent)
            if new_cover_image_path != old_cover_image_path:
                 delete_file(new_cover_image_path)


    elif form.errors:
         logger.warning(f"Page form validation errors on edit (ID: {id}): {form.errors}")
         flash("Le formulaire contient des erreurs.", "danger")

    current_cover_image_url = url_for('static', filename=page.cover_image_path) if page.cover_image_path else None
    return render_template('admin/pages/form.html', 
                            form=form, 
                            page=page, # Passer l'objet page pour l'affichage (ex: titre actuel)
                            page_title=f"Modifier: {page.title}",
                            current_cover_image=current_cover_image_url)


# Route pour supprimer une page (via POST pour sécurité)
@pages_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_page(id):
    page = Page.query.get_or_404(id)
    page_title = page.title # Garder le titre pour le message flash
    
    # Supprimer l'image de couverture associée
    if page.cover_image_path:
        delete_file(page.cover_image_path) # La fonction gère les erreurs internes

    try:
        db.session.delete(page)
        db.session.commit()
        logger.info(f"Page deleted: {page_title} (ID: {id})")
        flash(f'La page "{page_title}" a été supprimée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting page ID {id}: {e}", exc_info=True)
        flash(f'Erreur lors de la suppression de la page "{page_title}": {e}', 'danger')
        
    return redirect(url_for('pages.list_pages'))