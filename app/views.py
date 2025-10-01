from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, Response
from flask_babel import get_locale, _
from flask_login import login_user, logout_user, login_required, current_user
from .forms import VideoUploadForm, LoginForm, RegistrationForm, OcrForm
from .models import User, db
from werkzeug.utils import secure_filename
from . import app, logger
import os
import threading
import time
import json
from .video_processor import VideoProcessor
from .ocr import extract_text, extract_urls

dir_path = os.path.dirname(os.path.realpath(__file__))

ALLOWED_EXTENSIONS = set(['mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'])
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# Global dictionary to store processing status
processing_status = {}

@app.route('/')
@login_required
def index():
    form = VideoUploadForm()
    return render_template('index.html', form=form)

@app.route('/process', methods=['POST'])
@login_required
def process_video():
    form = VideoUploadForm()
    
    if form.validate_on_submit():
        video_file = form.video_file.data
        model = form.model.data
        src_language = form.src_language.data
        dest_language = form.dest_language.data
        translation_method = form.translation_method.data
        
        if video_file and allowed_file(video_file.filename):
            filename = secure_filename(video_file.filename)
            upload_path = current_app.config['UPLOAD_FOLDER']
            saved_path = os.path.join(upload_path, filename)
            video_file.save(saved_path)
            
            # Generate unique job ID
            job_id = f"{int(time.time())}_{filename}"
            
            # Initialize processing status
            processing_status[job_id] = {
                'status': 'processing',
                'progress': 0,
                'current_step': 'Starting...',
                'captions': [],
                'error': None
            }
            
            # Start processing in background thread
            processor = VideoProcessor()
            thread = threading.Thread(
                target=processor.process_media,
                args=(saved_path, job_id, model, src_language, dest_language, processing_status, translation_method)
            )
            thread.daemon = True
            thread.start()
            
            return redirect(url_for('processing', job_id=job_id))
        else:
            flash('Invalid file type. Please upload a video file.', 'error')
    
    return render_template('index.html', form=form)

@app.route('/processing/<job_id>')
@login_required
def processing(job_id):
    return render_template('processing.html', job_id=job_id)

@app.route('/status/<job_id>')
@login_required
def get_status(job_id):
    if job_id in processing_status:
        return jsonify(processing_status[job_id])
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/results/<job_id>')
@login_required
def results(job_id):
    if job_id in processing_status:
        status = processing_status[job_id]
        if status['status'] == 'completed':
            return render_template('results.html', 
                                 job_id=job_id, 
                                 captions=status['captions'],
                                 original_captions=status.get('original_captions', []),
                                 translated_captions=status.get('translated_captions', []),
                                 original_filename=status.get('original_filename', ''))
        else:
            return redirect(url_for('processing', job_id=job_id))
    else:
        flash('Job not found', 'error')
        return redirect(url_for('index'))

@app.route('/help')
@login_required
def help():
    return render_template('help.html')


@app.route('/set_language/<language>')
def set_language(language=None):
    if language and language in current_app.config['LANGUAGES']:
        from flask import session
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), 'error')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', title=_('Sign In'), form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now registered!'), 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title=_('Register'), form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/ocr')
@login_required
def ocr():
    form = OcrForm()
    return render_template('ocr.html', form=form)

@app.route('/process_ocr', methods=['POST'])
@login_required
def process_ocr():
    form = OcrForm()
    
    if form.validate_on_submit():
        image_file = form.image_file.data
        extract_urls_flag = form.extract_urls.data
        
        if image_file and allowed_image_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            upload_path = current_app.config['UPLOAD_FOLDER']
            saved_path = os.path.join(upload_path, filename)
            image_file.save(saved_path)
            
            try:
                # Extract text from image
                extracted_text = extract_text(saved_path)
                
                # Extract URLs if requested
                urls = []
                if extract_urls_flag:
                    urls = extract_urls(saved_path)
                
                return render_template('ocr_results.html', 
                                     original_filename=filename,
                                     extracted_text=extracted_text,
                                     urls=urls,
                                     extract_urls=extract_urls_flag)
                
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'error')
                return render_template('ocr.html', form=form)
            finally:
                # Clean up uploaded file
                if os.path.exists(saved_path):
                    os.remove(saved_path)
        else:
            flash('Invalid file type. Please upload an image file.', 'error')
    
    return render_template('ocr.html', form=form)
