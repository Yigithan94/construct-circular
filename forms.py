from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SubmitField, SelectField, 
    PasswordField, BooleanField, IntegerField, DateTimeField,
    FloatField, SelectMultipleField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from models import User, UserRole, SubCriterion
from flask_babel import lazy_gettext as _l
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[
        DataRequired(),
        Email(message=_l('Please enter a valid email address'))
    ])
    password = PasswordField(_l('Password'), validators=[
        DataRequired()
    ])
    role = SelectField(_l('Login Type'), choices=[
        ('company', _l('As Owner')),
        ('contractor', _l('As Contractor'))
    ], validators=[DataRequired()])
    submit = SubmitField(_l('Login'))

class CompanyRegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[
        DataRequired(),
        Length(min=2, max=20, message=_l('Username must be between 2 and 20 characters'))
    ])
    email = StringField(_l('Email'), validators=[
        DataRequired(),
        Email(message=_l('Please enter a valid email address'))
    ])
    password = PasswordField(_l('Password'), validators=[
        DataRequired(),
        Length(min=6, message=_l('Password must be at least 6 characters long'))
    ])
    confirm_password = PasswordField(_l('Confirm Password'), validators=[
        DataRequired(),
        EqualTo('password', message=_l('Passwords must match'))
    ])
    company_name = StringField(_l('Owner Name'), validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    company_description = TextAreaField(_l('Owner Description'))
    submit = SubmitField(_l('Register as Owner'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('Email already registered. Please choose a different one.'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('Username already taken. Please choose a different one.'))

class ContractorRegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[
        DataRequired(),
        Length(min=2, max=20, message=_l('Username must be between 2 and 20 characters'))
    ])
    email = StringField(_l('Email'), validators=[
        DataRequired(),
        Email(message=_l('Please enter a valid email address'))
    ])
    password = PasswordField(_l('Password'), validators=[
        DataRequired(),
        Length(min=6, message=_l('Password must be at least 6 characters long'))
    ])
    confirm_password = PasswordField(_l('Confirm Password'), validators=[
        DataRequired(),
        EqualTo('password', message=_l('Passwords must match'))
    ])
    contractor_specialization = StringField(_l('Specialization'), validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    contractor_experience = IntegerField(_l('Years of Experience'), validators=[
        DataRequired(),
        NumberRange(min=0, max=100)
    ])
    submit = SubmitField(_l('Register as Contractor'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('Email already registered. Please choose a different one.'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('Username already taken. Please choose a different one.'))

class ProjectForm(FlaskForm):
    name = StringField(_l('Project Name'), validators=[
        DataRequired(message=_l('Project name is required')),
        Length(min=2, max=100, message=_l('Name must be between 2 and 100 characters'))
    ])
    description = TextAreaField(_l('Project Description'))
    expectations = TextAreaField(_l('Project Expectations'), validators=[
        DataRequired(message=_l('Please describe your project expectations'))
    ])
    start_date = DateTimeField(_l('Project Start Date'), 
        format='%Y-%m-%d', 
        validators=[DataRequired(message=_l('Please set a project start date'))]
    )
    deadline = DateTimeField(_l('Project Deadline'), 
        format='%Y-%m-%d', 
        validators=[DataRequired(message=_l('Please set a project deadline'))]
    )
    location = StringField(_l('Project Location'), validators=[
        DataRequired(),
        Length(max=200)
    ])
    submit = SubmitField(_l('Create Project'))

    def validate_start_date(self, field):
        if field.data <= datetime.now():
            raise ValidationError(_l('Start date must be in the future'))
    
    def validate_deadline(self, field):
        if field.data <= datetime.now():
            raise ValidationError(_l('Deadline must be in the future'))
        if hasattr(self, 'start_date') and self.start_date.data and field.data <= self.start_date.data:
            raise ValidationError(_l('Deadline must be after the start date'))

class CompanyProfileForm(FlaskForm):
    company_name = StringField(_l('Owner Name'), validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    company_description = TextAreaField(_l('Owner Description'))
    submit = SubmitField(_l('Update Profile'))

class ProjectApplicationForm(FlaskForm):
    cover_letter = TextAreaField(_l('Cover Letter'), validators=[
        Length(max=5000, message=_l('Cover letter must be at most 5000 characters'))
    ])
    submit = SubmitField(_l('Submit Application'))
    save_draft = SubmitField(_l('Save as Draft'))

    def __init__(self, project=None, *args, **kwargs):
        super(ProjectApplicationForm, self).__init__(*args, **kwargs)
        self.project = project

class SubCriterionForm(FlaskForm):
    name = StringField(_l('Sub-criterion Name'), validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField(_l('Description'))
    weight = FloatField(_l('Weight'), validators=[
        DataRequired(),
        NumberRange(min=0, max=1, message=_l('Weight must be between 0 and 1'))
    ])
    detail_weight = FloatField(_l('Detay Ağırlık'), validators=[
        DataRequired(),
        NumberRange(min=0, max=10, message=_l('Detay ağırlık 0 ile 10 arasında olmalıdır'))
    ])
    
    # KPI ayarı
    has_kpi = BooleanField(_l('Define KPI for this Sub-criterion'))
    
    submit = SubmitField(_l('Update Sub-criterion'))

    def __init__(self, criterion_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.criterion_id = criterion_id

    def validate_name(self, field):
        if self.criterion_id:
            sub_criterion = SubCriterion.query.filter_by(
                name=field.data, 
                criterion_id=self.criterion_id
            ).first()
            if sub_criterion and (not hasattr(self, 'sub_criterion_id') or 
                               sub_criterion.id != self.sub_criterion_id):
                raise ValidationError(_l('A sub-criterion with this name already exists for this criterion'))

class KPIDefinitionForm(FlaskForm):
    """Form for defining Key Performance Indicators"""
    name = StringField(_l('KPI Name'), validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField(_l('KPI Description'))
    
    # AI değerlendirme alanları
    use_ai_evaluation = BooleanField(_l('Enable AI Evaluation'))
    ai_evaluation_criteria = TextAreaField(_l('AI Evaluation Criteria'), 
        description=_l('Detail the specific criteria for evaluating this KPI. This helps the AI understand how to score uploaded documents.'))
    
    submit = SubmitField(_l('Add KPI'))
    
    def __init__(self, sub_criterion_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sub_criterion_id = sub_criterion_id

class CSRFForm(FlaskForm):
    """A simple form for CSRF protection"""
    submit = SubmitField(_l('Submit'))