-- Table: companies
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    pan_number VARCHAR(20) NOT NULL UNIQUE,
    gst_number VARCHAR(20),
    mca_reg_details VARCHAR(255),
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: company_documents
CREATE TABLE company_documents (
    document_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    document_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_by VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);