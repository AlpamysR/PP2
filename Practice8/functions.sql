CREATE OR REPLACE FUNCTION search_pattern(pattern TEXT)
RETURNS TABLE(id INT, name TEXT, surname TEXT, phone TEXT) AS
$$
BEGIN
    RETURN QUERY
    SELECT *
    FROM phonebook p
    WHERE p.name ILIKE '%' || pattern || '%'
       OR p.surname ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_paginated(limit_val INT, offset_val INT)
RETURNS TABLE(id INT, name TEXT, surname TEXT, phone TEXT) AS
$$
BEGIN
    RETURN QUERY
    SELECT *
    FROM phonebook
    ORDER BY id
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;    