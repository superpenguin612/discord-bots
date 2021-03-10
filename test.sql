CREATE TABLE reaction_roles (
    id BIGSERIAL NOT NULL,
    message_id VARCHAR(18) NOT NULL,
    role_id VARCHAR(50) NOT NULL,
    emoji VARCHAR(50) NOT NULL
)