from flask import Blueprint, request, jsonify
from flask_cors import CORS
from flaskr.extensions import db
from flaskr.models.concept_model import Concept

bp = Blueprint('concepts', __name__, url_prefix='/api/concepts')
CORS(bp)

@bp.route('', methods=['GET'])
def get_all_concepts():
    concepts = Concept.query.all()
    result = []
    
    for concept in concepts:
        concept_data = concept.as_dict()
        result.append(concept_data)
    
    return jsonify(result)


@bp.route('', methods=['POST'])
def create_concept():
    data = request.get_json()
    new_concept = Concept(name=data['name'])
    db.session.add(new_concept)
    db.session.commit()
    
    return {'id': new_concept.id}, 201

@bp.route('<int:id>', methods=['GET'])
def get_concept(id):
    concept = Concept.query.get(id)
    if concept is None:
        return {'error': 'Concept not found'}, 404
    
    return {'id': concept.id, 'name': concept.name, 'created_at': concept.created_at}

@bp.route('<int:id>', methods=['PUT'])
def update_concept(id):
    data = request.get_json()
    concept = Concept.query.get(id)
    if concept is None:
        return {'error': 'Concept not found'}, 404
    concept.name = data['name']
    db.session.commit()
    
    return {'id': concept.id, 'name': concept.name, 'created_at': concept.created_at}

@bp.route('<int:id>', methods=['DELETE'])
def delete_concept(id):
    concept = Concept.query.get(id)
    if concept is None:
        return {'error': 'Concept not found'}, 404
    db.session.delete(concept)
    db.session.commit()
    
    return {}, 204