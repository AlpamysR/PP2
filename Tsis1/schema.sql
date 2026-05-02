-- 1. Groups table (Family, Work, Friend, Other)
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups (name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT DO NOTHING;

-- 2. Contacts table
--    Create fresh if it does not exist at all ...
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--    ... then safely add every column that Practice 8 may be missing.
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS name       VARCHAR(100) NOT NULL DEFAULT 'unknown';
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS email      VARCHAR(100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS birthday   DATE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS group_id   INTEGER REFERENCES groups(id) ON DELETE SET NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 3. Phones table (1-to-many with contacts)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);