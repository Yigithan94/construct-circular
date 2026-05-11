from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.orm import validates
from typing import Dict, List, Tuple, Optional
from flask import current_app
import enum

# Conditional NumPy import to handle system dependency issues
try:
    import numpy as np
    NUMPY_AVAILABLE = True
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        NumpyArray = np.ndarray
    else:
        NumpyArray = np.ndarray
except ImportError as e:
    print(f"NumPy import failed: {e}")
    NUMPY_AVAILABLE = False
    np = None
    NumpyArray = None

# Conditional TOPSIS import
try:
    from topsis import FuzzyTOPSIS
    TOPSIS_AVAILABLE = True
except ImportError as e:
    print(f"TOPSIS import failed: {e}")
    TOPSIS_AVAILABLE = False
    FuzzyTOPSIS = None

class UserRole(enum.Enum):
    COMPANY = "company"
    CONTRACTOR = "contractor"

    def __str__(self):
        return self.value

class ProjectStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ApplicationStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.Enum(UserRole), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Company-specific fields
    company_name = db.Column(db.String(100))
    company_description = db.Column(db.Text)

    # Contractor-specific fields
    contractor_specialization = db.Column(db.String(100))
    contractor_experience = db.Column(db.Integer)  # Years of experience

    # Relationships
    projects = db.relationship('Project', backref='user', lazy=True)
    applications = db.relationship('ProjectApplication', backref='contractor', lazy=True)

    def is_administrator(self):
        return self.is_admin

    def is_company(self):
        return self.role == UserRole.COMPANY

    def is_contractor(self):
        return self.role == UserRole.CONTRACTOR

    @validates('role')
    def validate_role(self, key, role):
        if isinstance(role, str):
            return UserRole(role.lower())
        return role

# Association tables for many-to-many relationships
project_criteria = db.Table('project_criteria',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('criterion_id', db.Integer, db.ForeignKey('criterion.id'))
)

project_subcriteria = db.Table('project_subcriteria',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('sub_criterion_id', db.Integer, db.ForeignKey('sub_criterion.id'))
)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    expectations = db.Column(db.Text)  # Detailed project requirements
    budget_range_min = db.Column(db.Float)  # Minimum budget
    budget_range_max = db.Column(db.Float)  # Maximum budget
    start_date = db.Column(db.DateTime)  # Project start date
    deadline = db.Column(db.DateTime)  # Project deadline
    location = db.Column(db.String(200))  # Project location
    owner_note = db.Column(db.Text)  # Owner's note for TOPSIS report
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.OPEN)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Many-to-many relationships
    selected_criteria = db.relationship('Criterion', 
        secondary=project_criteria,
        backref=db.backref('projects', lazy=True)
    )
    selected_subcriteria = db.relationship('SubCriterion',
        secondary=project_subcriteria,
        backref=db.backref('projects', lazy=True)
    )
    documents = db.relationship('Document', backref='project', lazy=True)
    alternatives = db.relationship('Alternative', backref='project', lazy=True)
    applications = db.relationship('ProjectApplication', backref='project', lazy=True)

    """
    Key methods in the Project model for TOPSIS calculation:
    """

    def calculate_topsis_matrix(self):
        """
        Calculate the enhanced fuzzy TOPSIS decision matrix for this project

        Returns:
            Tuple containing:
            - Array of relative closeness coefficients (or None if calculation not possible)
            - Dictionary with intermediate results (or None if calculation not possible)
        """
        if not NUMPY_AVAILABLE or not TOPSIS_AVAILABLE:
            print("NumPy or TOPSIS not available - calculations disabled")
            return None, None
            
        return None, None  # Simplified for now to prevent startup errors

        # Populate matrices
        for j, crit in enumerate(criteria):
            # Set criterion weights
            weights_matrix[j] = [
                crit.weight_low or crit.weight,
                crit.weight_medium or crit.weight,
                crit.weight_high or crit.weight
            ]
            is_cost[j] = crit.is_cost

            for i, alt in enumerate(alternatives):
                evaluation = CriterionEvaluation.query.filter_by(
                    alternative_id=alt.id,
                    criterion_id=crit.id
                ).first()

                if evaluation:
                    decision_matrix[i, j] = [
                        evaluation.low,
                        evaluation.medium,
                        evaluation.high
                    ]

        # Calculate enhanced Fuzzy TOPSIS
        try:
            if not TOPSIS_AVAILABLE:
                print("TOPSIS not available - calculation disabled")
                return None, None
                
            topsis = FuzzyTOPSIS(
                criteria_weights=weights_matrix,
                is_cost=is_cost,
                decision_matrix=decision_matrix
            )
            rankings, details = topsis.calculate()
            return rankings, details
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in TOPSIS calculation: {str(e)}")
            return None, None

    def get_ranked_alternatives(self) -> List[Dict]:
        """
        Get alternatives ranked by their TOPSIS scores

        Returns:
            List of dictionaries containing alternative details and scores
        """
        rankings, details = self.calculate_topsis_matrix()
        if rankings is None:
            return []

        ranked_alternatives = []
        for i, alt in enumerate(alternatives):
            ranked_alternatives.append({
                'id': alt.id,
                'name': alt.name,
                'description': alt.description,
                'score': float(rankings[i]),
                'rank': len(rankings) - i
            })

        # Sort by score in descending order
        ranked_alternatives.sort(key=lambda x: x['score'], reverse=True)

        # Update ranks after sorting
        for i, alt in enumerate(ranked_alternatives, 1):
            alt['rank'] = i

        return ranked_alternatives

class ProjectApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    cover_letter = db.Column(db.Text)
    proposed_duration = db.Column(db.Integer)  # Duration in days
    proposed_budget = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    topsis_score = db.Column(db.Float)  # Added field for TOPSIS evaluation score

    # Relationships
    documents = db.relationship('Document', backref='application', lazy=True)
    evaluations = db.relationship('CriterionEvaluation', backref='application', lazy=True)
    decision_scores = db.relationship('DecisionMatrix', backref='project_application', lazy=True)


class Criterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    weight = db.Column(db.Numeric(5,3), nullable=False)
    is_cost = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Fuzzy weight components
    weight_low = db.Column(db.Numeric(5,3))
    weight_medium = db.Column(db.Numeric(5,3))
    weight_high = db.Column(db.Numeric(5,3))

    # Update relationship to include default ordering
    sub_criteria = db.relationship('SubCriterion', backref='criterion', lazy=True)
    documents = db.relationship('Document', backref='criterion', lazy=True)
    evaluations = db.relationship('CriterionEvaluation', backref='criterion', lazy=True)

    @validates('weight', 'weight_low', 'weight_medium', 'weight_high')
    def validate_weight(self, key, weight):
        if weight is not None and not 0 <= float(weight) <= 1:
            raise ValueError(f'{key} must be between 0 and 1')
        return weight

class SubCriterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    weight = db.Column(db.Numeric(8,6), nullable=False)  # Changed from (5,3) to (8,6) for 6 decimal places
    detail_weight = db.Column(db.Numeric(8,6), default=1.0)  # Detay analiz için ağırlık değeri
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)

    # Fuzzy weight components - also update precision
    weight_low = db.Column(db.Numeric(8,6))
    weight_medium = db.Column(db.Numeric(8,6))
    weight_high = db.Column(db.Numeric(8,6))
    
    # KPI özel değerlendirme alanı - TOPSIS hesaplamasına dahil edilmeyecek
    has_kpi = db.Column(db.Boolean, default=False)
    kpi_name = db.Column(db.String(100))
    kpi_description = db.Column(db.Text)

    @validates('weight', 'weight_low', 'weight_medium', 'weight_high')
    def validate_weight(self, key, weight):
        if weight is not None and not 0 <= float(weight) <= 1:
            raise ValueError(f'{key} must be between 0 and 1')
        return weight

class Alternative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evaluations = db.relationship('CriterionEvaluation', backref='alternative', lazy=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=True)
    sub_criterion_id = db.Column(db.Integer, db.ForeignKey('sub_criterion.id'), nullable=True)
    application_id = db.Column(db.Integer, db.ForeignKey('project_application.id'), nullable=True)

    @validates('file_type')
    def validate_file_type(self, key, file_type):
        allowed_types = {'pdf', 'docx', 'doc', 'txt'}
        if file_type.lower() not in allowed_types:
            raise ValueError(f'File type {file_type} not allowed. Allowed types: {", ".join(allowed_types)}')
        return file_type.lower()

class CriterionEvaluation(db.Model):
    """Stores fuzzy evaluations for alternatives against criteria"""
    id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(db.Integer, db.ForeignKey('alternative.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)
    sub_criterion_id = db.Column(db.Integer, db.ForeignKey('sub_criterion.id'), nullable=True)
    application_id = db.Column(db.Integer, db.ForeignKey('project_application.id'), nullable=True)

    # Fuzzy number components
    low = db.Column(db.Float, nullable=False)
    medium = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates('low', 'medium', 'high')
    def validate_fuzzy_numbers(self, key, value):
        if value < 0:
            raise ValueError(f'{key} cannot be negative')
        if key == 'low' and hasattr(self, 'medium') and self.medium is not None and value > self.medium:
            raise ValueError('Low value must be less than or equal to medium value')
        if key == 'high' and hasattr(self, 'medium') and self.medium is not None and value < self.medium:
            raise ValueError('High value must be greater than or equal to medium value')
        return value

class KeyPerformanceIndicator(db.Model):
    """Stores KPI definitions for sub-criteria"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ai_evaluation_criteria = db.Column(db.Text, nullable=True, 
                           comment="AI değerlendirmesi için özel kriterler ve talimatlar")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sub_criterion_id = db.Column(db.Integer, db.ForeignKey('sub_criterion.id'), nullable=False)
    use_ai_evaluation = db.Column(db.Boolean, default=False, 
                          comment="AI ile otomatik değerlendirmeyi etkinleştir")
    
    # Relationships
    sub_criterion = db.relationship('SubCriterion', backref='kpi_definitions', lazy=True)
    documents = db.relationship('KPIDocument', backref='kpi', lazy=True, cascade='all, delete-orphan')

class KPIDocument(db.Model):
    """Stores contractor uploaded documents for KPIs"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI değerlendirme sonuçları
    ai_evaluated = db.Column(db.Boolean, default=False)
    ai_score = db.Column(db.Integer, nullable=True)  # 1-7 arası puan
    ai_explanation = db.Column(db.Text, nullable=True)  # AI açıklaması
    
    # Foreign keys
    kpi_id = db.Column(db.Integer, db.ForeignKey('key_performance_indicator.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('project_application.id'), nullable=False)
    
    # Relationships
    application = db.relationship('ProjectApplication', backref='kpi_documents', lazy=True)

class KPIScore(db.Model):
    """Stores KPI scores for contractor applications"""
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('project_application.id'), nullable=False)
    kpi_id = db.Column(db.Integer, db.ForeignKey('key_performance_indicator.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # Score between 1-7
    manually_edited = db.Column(db.Boolean, default=False)  # True if owner manually changed the AI score
    ai_explanation = db.Column(db.Text, nullable=True)  # AI explanation for the score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    kpi = db.relationship('KeyPerformanceIndicator', backref='scores', lazy=True)
    application = db.relationship('ProjectApplication', backref='kpi_scores', lazy=True)
    
    @validates('score')
    def validate_score(self, key, score):
        if not isinstance(score, int) or score < 1 or score > 7:
            raise ValueError('Score must be an integer between 1 and 7')
        return score

class DecisionMatrix(db.Model):
    """Stores decision matrix scores for contractor applications"""
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('project_application.id'), nullable=False)
    sub_criterion_id = db.Column(db.Integer, db.ForeignKey('sub_criterion.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # Score between 1-7
    manually_edited = db.Column(db.Boolean, default=False)  # True if owner manually changed the score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sub_criterion = db.relationship('SubCriterion', backref='decision_scores', lazy=True)

    @validates('score')
    def validate_score(self, key, score):
        if not isinstance(score, int) or score < 1 or score > 7:
            raise ValueError('Score must be an integer between 1 and 7')
        return score