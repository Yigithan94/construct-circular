from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from models import Criterion, SubCriterion, CriterionEvaluation

class CriterionForm(FlaskForm):
    name = StringField('Criterion Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description')
    weight = FloatField('Weight', validators=[
        DataRequired(),
        NumberRange(min=0, max=1, message='Weight must be between 0 and 1')
    ])
    is_cost = BooleanField('Is Cost Criterion')
    submit = SubmitField('Save Criterion')

    def validate_name(self, field):
        criterion = Criterion.query.filter_by(name=field.data).first()
        if criterion and (not hasattr(self, 'criterion_id') or criterion.id != self.criterion_id):
            raise ValidationError('A criterion with this name already exists')

class SubCriterionForm(FlaskForm):
    name = StringField('Sub-criterion Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description')
    weight = FloatField('Weight', validators=[
        DataRequired(),
        NumberRange(min=0, max=1, message='Weight must be between 0 and 1')
    ])
    submit = SubmitField('Update Sub-criterion')

    def __init__(self, criterion_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.criterion_id = criterion_id
        if not kwargs.get('obj'):  # If this is a new sub-criterion
            self.submit.label.text = 'Create Sub-criterion'

    def validate_name(self, field):
        if self.criterion_id:
            sub_criterion = SubCriterion.query.filter_by(
                name=field.data, 
                criterion_id=self.criterion_id
            ).first()
            if sub_criterion and (not hasattr(self, 'sub_criterion_id') or 
                               sub_criterion.id != self.sub_criterion_id):
                raise ValidationError('A sub-criterion with this name already exists for this criterion')

class AlternativeEvaluationForm(FlaskForm):
    """Form for evaluating alternatives against criteria using fuzzy numbers"""
    low = FloatField('Low Value', validators=[
        DataRequired(),
        NumberRange(min=0, message='Value cannot be negative')
    ])
    medium = FloatField('Medium Value', validators=[
        DataRequired(),
        NumberRange(min=0, message='Value cannot be negative')
    ])
    high = FloatField('High Value', validators=[
        DataRequired(),
        NumberRange(min=0, message='Value cannot be negative')
    ])
    submit = SubmitField('Save Evaluation')

    def validate(self):
        if not super().validate():
            return False

        if not (self.low.data <= self.medium.data <= self.high.data):
            self.low.errors.append('Fuzzy values must satisfy: low ≤ medium ≤ high')
            return False

        return True