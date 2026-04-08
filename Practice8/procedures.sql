CREATE OR REPLACE PROCEDURE insert_or_update_user(
    p_name TEXT,
    p_surname TEXT,
    p_phone TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM phonebook
        WHERE name = p_name AND surname = p_surname
    ) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE name = p_name AND surname = p_surname;
    ELSE
        INSERT INTO phonebook(name, surname, phone)
        VALUES (p_name, p_surname, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_users(
    names TEXT[],
    surnames TEXT[],
    phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    invalid_data TEXT[] := '{}';
BEGIN
    FOR i IN 1..array_length(names, 1) LOOP

        IF phones[i] ~ '^[0-9]{10,15}$' THEN
            INSERT INTO phonebook(name, surname, phone)
            VALUES (names[i], surnames[i], phones[i]);
        ELSE
            invalid_data := array_append(invalid_data, names[i] || ' ' || phones[i]);
        END IF;

    END LOOP;

    RAISE NOTICE 'Invalid data: %', invalid_data;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_user(
    p_value TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = p_value
       OR phone = p_value;
END;
$$;