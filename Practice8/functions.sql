CREATE OR REPLACE FUNCTION search_contacts(p TEXT)
RETURNS TABLE(name TEXT, phone TEXT, email TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.phone, c.email
    FROM contacts c
    WHERE c.name ILIKE '%' || p || '%'
       OR c.phone ILIKE '%' || p || '%'
       OR c.email ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_val INT, offset_val INT)
RETURNS TABLE(name TEXT, phone TEXT, email TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.phone, c.email
    FROM contacts c
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;
