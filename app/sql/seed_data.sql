-- Insert sample company data
INSERT INTO companies (company_name, pan_number, gst_number, mca_reg_details, address, notes)
VALUES 
    ('Tech Solutions Pvt Ltd', 'PAN123456789', 'GST123456789', 'MCA123456789', 
     '123 Tech Street, Cyber City, Techland', 'Leading technology solutions provider'),
    ('Finance Corp', 'PAN987654321', 'GST987654321', 'MCA987654321',
     '456 Finance Avenue, Business District, Financeland', 'Corporate finance solutions'),
    ('Retail World', 'PAN567891234', 'GST567891234', 'MCA567891234',
     '789 Retail Plaza, Shopping District, Retailville', 'Multi-brand retail chain'),
    ('HealthCare Services', 'PAN111222333', 'GST111222333', 'MCA111222333',
     '100 Medical Road, Health City, Healthland', 'Comprehensive healthcare solutions'),
    ('Construction Co.', 'PAN222333444', 'GST222333444', 'MCA222333444',
     '200 Building Street, Construction Zone, Buildland', 'Construction and infrastructure');

-- Insert sample company documents
INSERT INTO company_documents (company_id, document_name, file_path, uploaded_by)
VALUES 
    (1, 'Tech Solutions - PAN Card', 'uploads/tech_solutions_pan.pdf', 'admin'),
    (1, 'Tech Solutions - GST Certificate', 'uploads/tech_solutions_gst.pdf', 'admin'),
    (1, 'Tech Solutions - MCA Registration', 'uploads/tech_solutions_mca.pdf', 'admin'),
    (2, 'Finance Corp - PAN Card', 'uploads/finance_corp_pan.pdf', 'admin'),
    (2, 'Finance Corp - GST Certificate', 'uploads/finance_corp_gst.pdf', 'admin'),
    (3, 'Retail World - PAN Card', 'uploads/retail_world_pan.pdf', 'admin'),
    (3, 'Retail World - GST Certificate', 'uploads/retail_world_gst.pdf', 'admin'),
    (4, 'HealthCare Services - PAN Card', 'uploads/healthcare_services_pan.pdf', 'admin'),
    (4, 'HealthCare Services - GST Certificate', 'uploads/healthcare_services_gst.pdf', 'admin'),
    (5, 'Construction Co. - PAN Card', 'uploads/construction_co_pan.pdf', 'admin'),
    (5, 'Construction Co. - GST Certificate', 'uploads/construction_co_gst.pdf', 'admin');
