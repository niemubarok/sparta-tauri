-- Sparta Parking System - Member Management Database Schema
-- This script creates tables for member management system

-- ============================================
-- MEMBER TYPES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS member_types (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) DEFAULT 'REGULAR', -- VIP, PREMIUM, REGULAR, CORPORATE
    price DECIMAL(12,2) NOT NULL DEFAULT 0,
    area_type VARCHAR(20) DEFAULT 'residential', -- residential, commercial
    max_vehicles INTEGER DEFAULT 1,
    duration_months INTEGER DEFAULT 12,
    operating_hours_start TIME DEFAULT '00:00:00',
    operating_hours_end TIME DEFAULT '23:59:59',
    description TEXT,
    facilities TEXT, -- JSON array of facilities
    benefits TEXT, -- JSON array of benefits  
    access_areas TEXT, -- JSON array of accessible areas
    status INTEGER DEFAULT 1, -- 1=active, 0=inactive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- ============================================
-- MEMBERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS members (
    id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(20) UNIQUE NOT NULL, -- Generated member ID (e.g., MBR202412001)
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    address TEXT,
    identity_number VARCHAR(50), -- KTP/ID number
    member_type_id VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, overdue
    notes TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    photo_url VARCHAR(255), -- URL to member photo
    qr_code VARCHAR(255), -- QR code for member
    status INTEGER DEFAULT 1, -- 1=active, 0=inactive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50),
    FOREIGN KEY (member_type_id) REFERENCES member_types(id) ON DELETE RESTRICT
);

-- ============================================
-- MEMBER VEHICLES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS member_vehicles (
    id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL, -- Mobil, Motor, Truk, Bus
    license_plate VARCHAR(20) NOT NULL,
    brand VARCHAR(50),
    model VARCHAR(50),
    color VARCHAR(30),
    year INTEGER,
    description TEXT,
    status INTEGER DEFAULT 1, -- 1=active, 0=inactive
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    UNIQUE KEY unique_license_plate (license_plate, status)
);

-- ============================================
-- MEMBER TRANSACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS member_transactions (
    id VARCHAR(50) PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL, -- Reference to main transaction
    member_id VARCHAR(50) NOT NULL,
    vehicle_id VARCHAR(50),
    entry_time TIMESTAMP,
    exit_time TIMESTAMP,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) DEFAULT 0,
    discount_type VARCHAR(20), -- percentage, fixed, free
    notes TEXT,
    status INTEGER DEFAULT 1, -- 1=completed, 0=cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE RESTRICT,
    FOREIGN KEY (vehicle_id) REFERENCES member_vehicles(id) ON DELETE SET NULL
);

-- ============================================
-- MEMBER PAYMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS member_payments (
    id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL,
    payment_type VARCHAR(20) NOT NULL, -- registration, renewal, penalty
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(20), -- cash, transfer, card, ewallet
    payment_date TIMESTAMP,
    due_date DATE,
    reference_number VARCHAR(50),
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, overdue, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE RESTRICT
);

-- ============================================
-- MEMBER ACCESS LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS member_access_log (
    id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL,
    vehicle_id VARCHAR(50),
    gate_id VARCHAR(20), -- Entry/exit gate
    access_type VARCHAR(10) NOT NULL, -- entry, exit
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    plate_number VARCHAR(20),
    recognized_by VARCHAR(20), -- manual, alpr, card
    operator_id VARCHAR(20),
    notes TEXT,
    status INTEGER DEFAULT 1,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE RESTRICT,
    FOREIGN KEY (vehicle_id) REFERENCES member_vehicles(id) ON DELETE SET NULL
);

-- ============================================
-- MEMBER CARD TABLE (for physical cards/tags)
-- ============================================
CREATE TABLE IF NOT EXISTS member_cards (
    id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL,
    card_number VARCHAR(50) UNIQUE NOT NULL,
    card_type VARCHAR(20) DEFAULT 'rfid', -- rfid, barcode, qr
    issue_date DATE NOT NULL,
    expiry_date DATE,
    status INTEGER DEFAULT 1, -- 1=active, 0=inactive, 2=lost, 3=damaged
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- ============================================
-- MEMBER BENEFITS USAGE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS member_benefit_usage (
    id VARCHAR(50) PRIMARY KEY,
    member_id VARCHAR(50) NOT NULL,
    benefit_type VARCHAR(50) NOT NULL, -- valet, wash, discount, etc
    usage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount_used DECIMAL(10,2),
    description TEXT,
    transaction_ref VARCHAR(50),
    status INTEGER DEFAULT 1,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE RESTRICT
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Members table indexes
CREATE INDEX IF NOT EXISTS idx_members_member_id ON members(member_id);
CREATE INDEX IF NOT EXISTS idx_members_phone ON members(phone);
CREATE INDEX IF NOT EXISTS idx_members_email ON members(email);
CREATE INDEX IF NOT EXISTS idx_members_type ON members(member_type_id);
CREATE INDEX IF NOT EXISTS idx_members_status ON members(status);
CREATE INDEX IF NOT EXISTS idx_members_dates ON members(start_date, end_date);

-- Member vehicles indexes
CREATE INDEX IF NOT EXISTS idx_member_vehicles_member ON member_vehicles(member_id);
CREATE INDEX IF NOT EXISTS idx_member_vehicles_plate ON member_vehicles(license_plate);
CREATE INDEX IF NOT EXISTS idx_member_vehicles_type ON member_vehicles(vehicle_type);

-- Member transactions indexes
CREATE INDEX IF NOT EXISTS idx_member_transactions_member ON member_transactions(member_id);
CREATE INDEX IF NOT EXISTS idx_member_transactions_date ON member_transactions(entry_time);
CREATE INDEX IF NOT EXISTS idx_member_transactions_status ON member_transactions(status);

-- Member payments indexes
CREATE INDEX IF NOT EXISTS idx_member_payments_member ON member_payments(member_id);
CREATE INDEX IF NOT EXISTS idx_member_payments_status ON member_payments(status);
CREATE INDEX IF NOT EXISTS idx_member_payments_date ON member_payments(payment_date);

-- Member access log indexes
CREATE INDEX IF NOT EXISTS idx_member_access_member ON member_access_log(member_id);
CREATE INDEX IF NOT EXISTS idx_member_access_time ON member_access_log(access_time);
CREATE INDEX IF NOT EXISTS idx_member_access_plate ON member_access_log(plate_number);

-- Member cards indexes
CREATE INDEX IF NOT EXISTS idx_member_cards_member ON member_cards(member_id);
CREATE INDEX IF NOT EXISTS idx_member_cards_number ON member_cards(card_number);
CREATE INDEX IF NOT EXISTS idx_member_cards_status ON member_cards(status);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- Active members with vehicles view
CREATE OR REPLACE VIEW view_active_members AS
SELECT 
    m.id,
    m.member_id,
    m.name,
    m.email,
    m.phone,
    m.address,
    mt.name as member_type_name,
    mt.category as member_category,
    m.start_date,
    m.end_date,
    m.payment_status,
    CASE 
        WHEN m.end_date < CURRENT_DATE THEN 'expired'
        WHEN m.end_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'expiring_soon'
        ELSE 'active'
    END as membership_status,
    DATEDIFF(m.end_date, CURRENT_DATE) as days_until_expiry,
    GROUP_CONCAT(
        CONCAT(mv.vehicle_type, ':', mv.license_plate) 
        SEPARATOR ','
    ) as vehicles
FROM members m
LEFT JOIN member_types mt ON m.member_type_id = mt.id
LEFT JOIN member_vehicles mv ON m.id = mv.member_id AND mv.status = 1
WHERE m.status = 1
GROUP BY m.id, m.member_id, m.name, m.email, m.phone, m.address, 
         mt.name, mt.category, m.start_date, m.end_date, m.payment_status;

-- Member statistics view
CREATE OR REPLACE VIEW view_member_statistics AS
SELECT 
    COUNT(*) as total_members,
    COUNT(CASE WHEN status = 1 AND end_date >= CURRENT_DATE THEN 1 END) as active_members,
    COUNT(CASE WHEN end_date <= CURRENT_DATE + INTERVAL '30 days' AND end_date >= CURRENT_DATE THEN 1 END) as expiring_soon,
    COUNT(CASE WHEN end_date < CURRENT_DATE THEN 1 END) as expired_members,
    COUNT(CASE WHEN payment_status = 'pending' THEN 1 END) as pending_payments,
    COUNT(CASE WHEN payment_status = 'overdue' THEN 1 END) as overdue_payments
FROM members 
WHERE status = 1;

-- ============================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================

-- Update timestamp on members table
CREATE TRIGGER IF NOT EXISTS tr_members_updated_at
    BEFORE UPDATE ON members
    FOR EACH ROW
    SET NEW.updated_at = CURRENT_TIMESTAMP;

-- Update timestamp on member_types table
CREATE TRIGGER IF NOT EXISTS tr_member_types_updated_at
    BEFORE UPDATE ON member_types
    FOR EACH ROW
    SET NEW.updated_at = CURRENT_TIMESTAMP;

-- Update timestamp on member_vehicles table
CREATE TRIGGER IF NOT EXISTS tr_member_vehicles_updated_at
    BEFORE UPDATE ON member_vehicles
    FOR EACH ROW
    SET NEW.updated_at = CURRENT_TIMESTAMP;

-- Update timestamp on member_payments table
CREATE TRIGGER IF NOT EXISTS tr_member_payments_updated_at
    BEFORE UPDATE ON member_payments
    FOR EACH ROW
    SET NEW.updated_at = CURRENT_TIMESTAMP;

-- Update timestamp on member_cards table
CREATE TRIGGER IF NOT EXISTS tr_member_cards_updated_at
    BEFORE UPDATE ON member_cards
    FOR EACH ROW
    SET NEW.updated_at = CURRENT_TIMESTAMP;

-- ============================================
-- SAMPLE DATA
-- ============================================

-- Insert default member types
INSERT IGNORE INTO member_types (id, name, category, price, max_vehicles, duration_months, description) VALUES
('mt_regular_001', 'Regular Member', 'REGULAR', 500000.00, 1, 12, 'Paket member regular dengan 1 kendaraan'),
('mt_premium_001', 'Premium Member', 'PREMIUM', 1000000.00, 2, 12, 'Paket member premium dengan 2 kendaraan dan benefit tambahan'),
('mt_vip_001', 'VIP Member', 'VIP', 2000000.00, 3, 12, 'Paket member VIP dengan 3 kendaraan dan semua benefit'),
('mt_corporate_001', 'Corporate Member', 'CORPORATE', 5000000.00, 10, 12, 'Paket member untuk perusahaan dengan multiple kendaraan');

-- ============================================
-- COMMENTS
-- ============================================

ALTER TABLE member_types COMMENT = 'Tabel jenis keanggotaan member';
ALTER TABLE members COMMENT = 'Tabel data utama member';
ALTER TABLE member_vehicles COMMENT = 'Tabel kendaraan yang terdaftar untuk member';
ALTER TABLE member_transactions COMMENT = 'Tabel transaksi parkir member';
ALTER TABLE member_payments COMMENT = 'Tabel pembayaran member (pendaftaran, perpanjangan, dll)';
ALTER TABLE member_access_log COMMENT = 'Tabel log akses member (masuk/keluar)';
ALTER TABLE member_cards COMMENT = 'Tabel kartu/tag fisik member';
ALTER TABLE member_benefit_usage COMMENT = 'Tabel penggunaan benefit member';

-- End of script
