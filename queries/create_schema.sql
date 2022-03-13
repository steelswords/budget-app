CREATE TABLE IF NOT EXISTS categories(
    name varchar(200) not null,
    table_order smallint,
    description varchar(1000),
    primary key(name),
    UNIQUE(name)
);

CREATE TABLE IF NOT EXISTS expenses (
    year smallint not null,
    month smallint not null,
    day smallint not null,
    amount numeric,
    category varchar(200) references categories(name),
    description varchar(500),
    UNIQUE(year, month, day, amount, category)
);

CREATE TABLE IF NOT EXISTS budgetbuckets(
    category varchar(200) references categories(name),
    year smallint not null,
    January numeric,
    February numeric,
    March numeric,
    April numeric,
    May numeric,
    June numeric,
    July numeric,
    August numeric,
    September numeric,
    October numeric,
    November numeric,
    December numeric,
    UNIQUE(category, year)
);
