from flask import Blueprint, request, jsonify
from app.db import get_connection
import os
from werkzeug.utils import secure_filename
import re

def validate_gst_number(gst_number):
    """
    Validate GST number format.
    Format: XXAAAAA0000A1Z5
    - First 2 characters: State code (01-37)
    - Next 10 characters: PAN number
    - 12th character: Entity type (1-9)
    - 13th character: Z
    - 14th character: Checksum
    """
    # Remove any spaces or special characters
    gst_number = gst_number.replace(' ', '').upper()
    
    # Check if length is correct (15 characters)
    if len(gst_number) != 15:
        return False
    
    # Check state code (first 2 digits)
    if not gst_number[:2].isdigit() or int(gst_number[:2]) < 1 or int(gst_number[:2]) > 37:
        return False
    
    # Check PAN-like part (next 10 characters)
    if not gst_number[2:12].isalnum():
        return False
    
    # Check entity type (12th character)
    if not gst_number[11].isdigit() or int(gst_number[11]) < 1 or int(gst_number[11]) > 9:
        return False
    
    # Check 13th character is Z
    if gst_number[12] != 'Z':
        return False
    
    # Check last character is alphanumeric
    if not gst_number[13].isalnum():
        return False
    
    return True

def validate_pan_number(pan_number):
    """
    Validate PAN number format.
    Format: ABCDE1234E
    - First 5 characters: Uppercase letters
    - Next 4 characters: Digits
    - Last character: Uppercase letter
    """
    # Remove any spaces and convert to uppercase
    pan_number = pan_number.replace(' ', '').upper()
    
    # Check if length is correct
    if len(pan_number) != 10:
        return False
    
    # Check first 5 characters are letters
    if not pan_number[:5].isalpha():
        return False
    
    # Check next 4 characters are digits
    if not pan_number[5:9].isdigit():
        return False
    
    # Check last character is a letter
    if not pan_number[9].isalpha():
        return False
    
    return True

api_blueprint = Blueprint('api', __name__)

# Company CRUD
@api_blueprint.route('/api/companies', methods=['GET'])
def get_companies():
    """Get all companies"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM companies ORDER BY company_id")
    companies = cur.fetchall()
    
    cur.close()
    conn.close()
    
    formatted_companies = []
    for company in companies:
        formatted_companies.append({
            'company_id': company[0],
            'company_name': company[1],
            'pan_number': company[2],
            'gst_number': company[3],
            'mca_reg_details': company[4],
            'address': company[5],
            'notes': company[6],
            "createdAt": company[7].strftime("%a, %d %b %Y %H:%M:%S %Z"),
            "updatedAt": company[8].strftime("%a, %d %b %Y %H:%M:%S %Z")
        })
    
    return jsonify(formatted_companies)

@api_blueprint.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get a specific company by ID"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM companies WHERE company_id = %s", (company_id,))
        company = cur.fetchone()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
            
        return jsonify({
            'company_id': company[0],
            'company_name': company[1],
            'pan_number': company[2],
            'gst_number': company[3],
            'mca_reg_details': company[4],
            'address': company[5],
            'notes': company[6],
            'created_at': company[7].strftime("%a, %d %b %Y %H:%M:%S %Z"),
            'updated_at': company[8].strftime("%a, %d %b %Y %H:%M:%S %Z")
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@api_blueprint.route('/api/companies', methods=['POST'])
def create_company():
    """Create a new company"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['company_name', 'pan_number']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: ' + ', '.join(required_fields)}), 400
        
        # Validate GST number format
        gst_number = data.get('gst_number')
        if gst_number:
            if not validate_gst_number(gst_number):
                return jsonify({
                    'error': 'Invalid GST number format',
                    'details': 'GST number should be in the format: XXAAAAA0000A1Z5',
                    'example': '27AAAAA0000A1Z5'
                }), 400
        
        # Validate PAN number format
        pan_number = data.get('pan_number')
        if not pan_number or not validate_pan_number(pan_number):
            return jsonify({
                'error': 'Invalid PAN number format',
                'details': 'PAN number should be in the format: ABCDE1234E',
                'example': 'ABCDE1234E'
            }), 400
        
        # Check if company already exists
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            # Check if company name already exists
            cur.execute("SELECT company_id FROM companies WHERE company_name = %s", (data['company_name'],))
            if cur.fetchone():
                return jsonify({'error': 'Company with this name already exists'}), 400
                
            # Check if PAN number already exists
            cur.execute("SELECT company_id FROM companies WHERE pan_number = %s", (data['pan_number'],))
            if cur.fetchone():
                return jsonify({'error': 'PAN number already exists'}), 400
                
            # Insert new company
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
            
            new_company = cur.fetchone()
            conn.commit()
            
            return jsonify({
                'company_id': new_company[0],
                'company_name': new_company[1],
                'pan_number': new_company[2],
                'gst_number': new_company[3],
                'mca_reg_details': new_company[4],
                'address': new_company[5],
                'notes': new_company[6],
                'created_at': new_company[7].strftime("%a, %d %b %Y %H:%M:%S %Z"),
                'updated_at': new_company[8].strftime("%a, %d %b %Y %H:%M:%S %Z")
            }), 201
            
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'error': 'Bad request: ' + str(e)}), 400

@api_blueprint.route('/api/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    """Update an existing company"""
    data = request.get_json()
    
    # Validate GST number if provided
    gst_number = data.get('gst_number')
    if gst_number and not validate_gst_number(gst_number):
        return jsonify({'error': 'Invalid GST number format. Format should be: XXAAAAA0000A1Z5'}), 400
    
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
        
        updated_company = cur.fetchone()
        
        if not updated_company:
            return jsonify({'error': 'Company not found'}), 404
            
        conn.commit()
        
        return jsonify({
            'company_id': updated_company[0],
            'company_name': updated_company[1],
            'pan_number': updated_company[2],
            'gst_number': updated_company[3],
            'mca_reg_details': updated_company[4],
            'address': updated_company[5],
            'notes': updated_company[6],
            'created_at': updated_company[7].strftime("%a, %d %b %Y %H:%M:%S %Z"),
            'updated_at': updated_company[8].strftime("%a, %d %b %Y %H:%M:%S %Z")
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@api_blueprint.route('/api/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    """Delete a company"""
    if company_id is None:
        return jsonify({'error': 'Company ID is required'}), 400
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM companies WHERE company_id = %s RETURNING company_id", (company_id,))
        deleted_id = cur.fetchone()
        
        if not deleted_id:
            return jsonify({'error': 'Company not found'}), 404
            
        conn.commit()
        return jsonify({'message': 'Company deleted successfully'}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
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
