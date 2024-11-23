-- Create tables for properties database

-- Admin table
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    phone_number TEXT NOT NULL,
    fullname TEXT NOT NULL,
    ic_number TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Report table
CREATE TABLE aiReport (
    reportID INTEGER PRIMARY KEY AUTOINCREMENT,
    reportFilePath TEXT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Announcements table
CREATE TABLE announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Banner Images table
CREATE TABLE bannerImages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_info_id INTEGER,
    image_path TEXT NOT NULL,
    FOREIGN KEY (system_info_id) REFERENCES systemInformation(id)
);

-- Combined Properties table
CREATE TABLE combined_properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL,
    longitude REAL,
    status INTEGER DEFAULT 1,
    addressLine1 TEXT,
    addressLine2 TEXT,
    postcode TEXT,
    city TEXT,
    state TEXT,
    sqft INTEGER,
    price REAL,
    description TEXT,
    image_path TEXT
);

-- Daily Check-in Status table
CREATE TABLE dailyCheckInStatus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rentalID INTEGER NOT NULL,
    date DATE NOT NULL,
    checkInStatus INTEGER NOT NULL,
    FOREIGN KEY (rentalID) REFERENCES rental(id),
    UNIQUE(rentalID, date)
);

-- Feedback table
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    comment TEXT,
    timestamp TEXT,
    subject TEXT,
    rentalID INTEGER REFERENCES rental(rentalID)
);

-- Payment Records table
CREATE TABLE payment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rentalID INTEGER,
    payment_method TEXT,
    cardholder_name TEXT,
    card_number TEXT,
    expire_date TEXT,
    cvc TEXT,
    receipt TEXT,
    payment_period TEXT,  -- Format: YYYY-MM
    payment_date DATE,    -- Date when payment was made
    payment_time TIME,    -- Time when payment was made
    FOREIGN KEY (rentalID) REFERENCES rental(rentalID)
);

-- Rental table
CREATE TABLE rental (
    rentalID INTEGER PRIMARY KEY AUTOINCREMENT,
    combined_properties_id INTEGER NOT NULL,
    tenantID INTEGER NOT NULL,
    startDate TEXT NOT NULL,
    endDate TEXT NOT NULL,
    rentalAmount REAL NOT NULL,
    stallPurpose TEXT NOT NULL,
    stallName TEXT NOT NULL,
    startOperatingTime TEXT NOT NULL,
    endOperatingTime TEXT NOT NULL,
    isApprove INTEGER DEFAULT 0,
    FOREIGN KEY (tenantID) REFERENCES tenants(tenantID),
    FOREIGN KEY (combined_properties_id) REFERENCES combined_properties(id)
);

-- System Information table
CREATE TABLE systemInformation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_agreement TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    api_key TEXT,
    passcode TEXT DEFAULT '0000'
);

-- Tenants table
CREATE TABLE tenants (
    tenantID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    fullName TEXT NOT NULL,
    ICNumber TEXT NOT NULL,
    emailAddress TEXT NOT NULL,
    phoneNumber TEXT NOT NULL,
    password TEXT NOT NULL,
    ICImagePath TEXT NOT NULL,
    FaceImagePath TEXT NOT NULL,
    icProblem TEXT,
    profile_image TEXT
);

-- Verification Failed Tenant Pictures table
CREATE TABLE verificationFailedTenantPictures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rentalID INTEGER,
    date TEXT,
    imagePath TEXT,
    FOREIGN KEY (rentalID) REFERENCES rental(rentalID)
); 