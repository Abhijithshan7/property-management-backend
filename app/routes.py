from flask import Blueprint, request, jsonify
from app.db import get_connection
import os
from werkzeug.utils import secure_filename

api_blueprint = Blueprint('api', __name__)

# Company CRUD
@api_blueprint.route('/api/companies', methods=['GET'])
def get_companies():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM companies ORDER BY company_id")
    companies = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify(companies)

@api_blueprint.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM companies WHERE company_id = %s", (company_id,))
    company = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if company:
        return jsonify(company)
    return jsonify({'error': 'Company not found'}), 404

@api_blueprint.route('/api/companies', methods=['POST'])
def create_company():
    data = request.json
    
    required_fields = ['company_name', 'pan_number']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO companies (company_name, pan_number, gst_number, 
            mca_reg_details, address, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            data['company_name'],
            data['pan_number'],
            data.get('gst_number'),
            data.get('mca_reg_details'),
            data.get('address'),
            data.get('notes')
        ))
        
        company = cur.fetchone()
        conn.commit()
        
        return jsonify(company), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@api_blueprint.route('/api/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    data = request.json
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Update only the fields that are provided
        update_fields = []
        params = []
        
        if 'company_name' in data:
            update_fields.append('company_name = %s')
            params.append(data['company_name'])
        if 'pan_number' in data:
            update_fields.append('pan_number = %s')
            params.append(data['pan_number'])
        if 'gst_number' in data:
            update_fields.append('gst_number = %s')
            params.append(data['gst_number'])
        if 'mca_reg_details' in data:
            update_fields.append('mca_reg_details = %s')
            params.append(data['mca_reg_details'])
        if 'address' in data:
            update_fields.append('address = %s')
            params.append(data['address'])
        if 'notes' in data:
            update_fields.append('notes = %s')
            params.append(data['notes'])
            
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
            
        params.append(company_id)
        
        update_query = f"UPDATE companies SET {', '.join(update_fields)} WHERE company_id = %s RETURNING *"
        cur.execute(update_query, params)
        
        company = cur.fetchone()
        conn.commit()
        
        if company:
            return jsonify(company)
        return jsonify({'error': 'Company not found'}), 404
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

@api_blueprint.route('/api/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
        
        if cur.rowcount == 0:
            return jsonify({'error': 'Company not found'}), 404
            
        conn.commit()
        return '', 204
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# Company Documents CRUD
@api_blueprint.route('/api/companies/<int:company_id>/documents', methods=['GET'])
def get_company_documents(company_id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM company_documents WHERE company_id = %s ORDER BY document_id", (company_id,))
    documents = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify(documents)

@api_blueprint.route('/api/companies/<int:company_id>/documents/<int:document_id>', methods=['GET'])
def get_company_document(company_id, document_id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM company_documents WHERE company_id = %s AND document_id = %s", 
               (company_id, document_id))
    document = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if document:
        return jsonify(document)
    return jsonify({'error': 'Document not found'}), 404

@api_blueprint.route('/api/companies/<int:company_id>/documents', methods=['POST'])
def upload_company_document(company_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO company_documents (company_id, document_name, file_path, uploaded_by)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (
                company_id,
                filename,
                file_path,
                request.form.get('uploaded_by', 'System')
            ))
            
            document = cur.fetchone()
            conn.commit()
            
            return jsonify(document), 201
            
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 400
        finally:
            cur.close()
            conn.close()

@api_blueprint.route('/api/companies/<int:company_id>/documents/<int:document_id>', methods=['DELETE'])
def delete_company_document(company_id, document_id):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # First get the file path to delete the physical file
        cur.execute("SELECT file_path FROM company_documents WHERE company_id = %s AND document_id = %s", 
                   (company_id, document_id))
        result = cur.fetchone()
        
        if result:
            file_path = result[0]
            if os.path.exists(file_path):
                os.remove(file_path)
                
            cur.execute("DELETE FROM company_documents WHERE company_id = %s AND document_id = %s", 
                       (company_id, document_id))
            
            if cur.rowcount == 0:
                return jsonify({'error': 'Document not found'}), 404
                
            conn.commit()
            return '', 204
            
        return jsonify({'error': 'Document not found'}), 404
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        cur.close()
        conn.close()

# Original report endpoint
@api_blueprint.route('/api/reports/entity-summary', methods=['GET'])
def get_entity_report():
    entity_id = request.args.get('entity_id')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT txn_date AS date, narration AS description, 
           CASE WHEN credit_amount > 0 THEN 'Bank Credit' ELSE 'Bank Debit' END AS type,
           tt.name AS transaction_type,
           credit_amount, debit_amount,
           ct.remarks
    FROM classified_transactions ct
    JOIN transaction_types tt ON ct.transaction_type_id = tt.transaction_type_id
    WHERE entity_id = %s AND txn_date BETWEEN %s AND %s

    UNION ALL

    SELECT date_of_expense AS date, remarks AS description,
           'Kitty Expense' AS type,
           tt.name AS transaction_type,
           0 AS credit_amount, (amount + margin) AS debit_amount,
           kr.remarks
    FROM kitty_register kr
    JOIN transaction_types tt ON kr.transaction_type_id = tt.transaction_type_id
    WHERE entity_id = %s AND date_of_expense BETWEEN %s AND %s
    ORDER BY date;
    """

    cur.execute(query, (entity_id, from_date, to_date, entity_id, from_date, to_date))
    results = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return jsonify([dict(zip(colnames, row)) for row in results])
