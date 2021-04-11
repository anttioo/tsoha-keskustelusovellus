create table boards (
    id        serial               not null primary key,
    name      text                 not null,
    is_public boolean default true not null
);

create unique index boards_name_uindex on boards (name);

create table users (
    id       serial not null primary key,
    username text   not null,
    password text   not null
);

create unique index users_username_uindex on users (username);

create table threads (
    id         serial  not null primary key,
    name       text,
    board_id   integer not null references boards on update cascade on delete cascade,
    created_by integer not null references users on update restrict on delete cascade
);

create table messages (
    id         serial  not null primary key,
    content    text,
    created_at timestamp,
    thread_id  integer references threads on update cascade on delete cascade,
    author_id  integer not null
);

create table private_board_users (
    id       serial  not null primary key,
    board_id integer not null references boards on update cascade on delete cascade,
    user_id  integer not null references users on update cascade on delete cascade
);





