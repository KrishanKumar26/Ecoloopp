INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Generating static SQL
INFO  [alembic.runtime.migration] Will assume transactional DDL.
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INFO  [alembic.runtime.migration] Running upgrade  -> 7ca5a8ba1aa1, Initial schema: 6 tables with relationships and constraints
-- Running upgrade  -> 7ca5a8ba1aa1

CREATE TYPE userrole AS ENUM ('USER', 'COLLECTOR', 'ADMIN');

CREATE TABLE users (
    user_id UUID NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    phone VARCHAR(20), 
    password_hash TEXT NOT NULL, 
    role userrole NOT NULL, 
    eco_points INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    deleted_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (user_id), 
    UNIQUE (phone)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_role ON users (role);

CREATE TABLE classifications (
    classification_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    category VARCHAR(100) NOT NULL, 
    confidence_score NUMERIC(4, 3) NOT NULL, 
    safety_tips TEXT[] NOT NULL, 
    estimated_weight_kg NUMERIC(5, 2), 
    raw_label VARCHAR(255) NOT NULL, 
    image_urls TEXT[] NOT NULL, 
    user_confirmed BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (classification_id), 
    FOREIGN KEY(user_id) REFERENCES users (user_id)
);

CREATE INDEX ix_classifications_category ON classifications (category);

CREATE INDEX ix_classifications_user_id ON classifications (user_id);

CREATE TABLE collectors (
    collector_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    business_name VARCHAR(255) NOT NULL, 
    license_number VARCHAR(100), 
    address TEXT NOT NULL, 
    lat NUMERIC(9, 6) NOT NULL, 
    lng NUMERIC(9, 6) NOT NULL, 
    rating NUMERIC(2, 1) NOT NULL, 
    accepted_categories TEXT[] NOT NULL, 
    is_active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (collector_id), 
    FOREIGN KEY(user_id) REFERENCES users (user_id), 
    UNIQUE (license_number), 
    UNIQUE (user_id)
);

CREATE INDEX idx_collectors_location ON collectors (lat, lng);

CREATE TYPE pickupstatus AS ENUM ('PENDING', 'ACCEPTED', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED');

CREATE TABLE pickups (
    pickup_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    collector_id UUID, 
    classification_id UUID, 
    item_description TEXT NOT NULL, 
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    address_street VARCHAR(255) NOT NULL, 
    address_city VARCHAR(100) NOT NULL, 
    address_state VARCHAR(100) NOT NULL, 
    address_pincode VARCHAR(20) NOT NULL, 
    address_lat NUMERIC(9, 6) NOT NULL, 
    address_lng NUMERIC(9, 6) NOT NULL, 
    otp VARCHAR(6) NOT NULL, 
    otp_expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    status pickupstatus NOT NULL, 
    cancellation_reason TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (pickup_id), 
    FOREIGN KEY(classification_id) REFERENCES classifications (classification_id), 
    FOREIGN KEY(collector_id) REFERENCES collectors (collector_id), 
    FOREIGN KEY(user_id) REFERENCES users (user_id)
);

CREATE INDEX ix_pickups_collector_id ON pickups (collector_id);

CREATE INDEX ix_pickups_scheduled_at ON pickups (scheduled_at);

CREATE INDEX ix_pickups_status ON pickups (status);

CREATE INDEX ix_pickups_user_id ON pickups (user_id);

CREATE TABLE eco_point_transactions (
    transaction_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    pickup_id UUID, 
    points INTEGER NOT NULL, 
    reason VARCHAR(255) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (transaction_id), 
    FOREIGN KEY(pickup_id) REFERENCES pickups (pickup_id), 
    FOREIGN KEY(user_id) REFERENCES users (user_id), 
    UNIQUE (pickup_id)
);

CREATE INDEX ix_eco_point_transactions_user_id ON eco_point_transactions (user_id);

CREATE TABLE recycler_slots (
    slot_id UUID NOT NULL, 
    collector_id UUID NOT NULL, 
    starts_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    ends_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    is_booked BOOLEAN NOT NULL, 
    pickup_id UUID, 
    PRIMARY KEY (slot_id), 
    CONSTRAINT check_slot_time_range CHECK (ends_at > starts_at), 
    FOREIGN KEY(collector_id) REFERENCES collectors (collector_id), 
    FOREIGN KEY(pickup_id) REFERENCES pickups (pickup_id), 
    UNIQUE (pickup_id)
);

CREATE INDEX ix_recycler_slots_collector_id ON recycler_slots (collector_id);

INSERT INTO alembic_version (version_num) VALUES ('7ca5a8ba1aa1') RETURNING alembic_version.version_num;

COMMIT;

