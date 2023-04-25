DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

SET TIMEZONE='UTC';

CREATE TABLE users 
(
    id              int         not null            primary key,
    topics          int[],
    companion       int                             default -1,
    active_topic    int                             default -1
);

CREATE SEQUENCE topics_id_sequence
    start 1
    increment 1;
CREATE TABLE topics
(
    id              int         not null            primary key,
    author          int         not null,
    text            text        not null,
    companion       int                             default -1,
    -- Additional features
    opened          boolean                         default FALSE,
    -- Fancy tracking information
    discussed_times int                             default 0,
    rating          int                             default 0
)

-- To drop all connections:
-- SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'discuss' AND pid <> pg_backend_pid();
