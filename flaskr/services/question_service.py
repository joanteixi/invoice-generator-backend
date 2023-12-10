import os
from llm import llm, prompt_templates

from flask import  current_app
from flaskr.models.document_model import Document
from flaskr.models.question_model import Question
from flaskr.models.answers_model import Answers
from flaskr.extensions import db

def chat_document(document: Document, question, question_type, temperature, model) -> None:
    
    question_object = Question(question=question, question_type=question_type, public_id='pregunta_id')
    engine, usage, pricing, response = ask_gpt(document = document, questions = [question_object],  temperature=temperature, model=model)
    
    return engine, usage, pricing, response

def persist_chat_document(document: Document, questions: [Question], temperature, jwt_identity, model='gpt3'):
    errors = []
    gpt_answer = ''
    total_pricing = 0
    total_tokens = 0
    
    engine, usage, pricing, response = ask_gpt(document, questions, temperature, model)
    if 'answer' in response.keys():
        errors.append(document.public_id)

    for question_id, gpt_answer in response.items():
        total_pricing += pricing
        total_tokens += usage['total_tokens']
        
        answer = Answers(document_id=document.public_id,
                document_type=document.type_,
                question_id=question_id,
                engine=engine,
                temperature = temperature,
                answer=gpt_answer,
                pricing=pricing,
                tokens=usage['total_tokens'],
                created_by=jwt_identity) #get_jwt_identity()
        db.session.add(answer)
    db.session.commit()
    
    return gpt_answer, errors, total_pricing, total_tokens



def ask_gpt(document: Document, questions: [Question], temperature, model='gpt3'):
    file_name = document.name

    questions = get_questions(questions)
        
    # si el documento tiene embeding, es porqué es largo.
    if document.doc_vdb:
        #if doc is embedded, use always gpt4
        model = 'gpt4'
        vdb_directory = os.path.join(current_app.instance_path, current_app.config['APP_VDB_STORE'])             
        engine, usage, pricing, response = llm.vdb_query_all(
            document=document, 
            questions=questions, 
            vdb_directory=vdb_directory, 
            model=model, 
            temperature=temperature
            )

    # si el documento no tiene embedding se envía entero a OpenAI
    else:
        ocr_directory = os.path.join(current_app.instance_path, current_app.config['APP_OCR_STORE'])
        file = os.path.join(ocr_directory, file_name)            

        with open(os.path.join(f'{file}.txt'), 'rb') as f:
            text  = f.read().decode('utf-8')

        engine, usage, pricing, response = llm.chat_gpt(text, questions, temperature, model)
    
    return  engine, usage, pricing, response


def get_questions(question_list: [Question]):
    """
    Returns a list of formatted questions with their respective keys.

    Args:
        question_list (list): A list of Question objects.

    Returns:
        list: A list of formatted questions with their respective keys.
    """
    
    sql_types = prompt_templates.get_sql_types()
    
    return [f'Pregunta: {q.question}, Formato de Respuesta: {sql_types[q.question_type]}, Key: {q.public_id}' for q in question_list]
