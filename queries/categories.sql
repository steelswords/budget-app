INSERT INTO categories (name, table_order)
VALUES
    ('Food', 1),
    ('Tristan - WTF', 2),
    ('Mar - WTF', 3),
    ('Household Discretionary', 4),
    ('Date', 5),
    ('Eating Out', 6),
    ('Clothes', 7),    
    ('Tech Budget', 8),
    ('Decorations', 9),
    ('Gifts', 10),
    ('Furniture', 11),
    ('Gas', 12),
    ('Laundry', 13),
    ('Haircuts', 14),
    ('Medical', 15),
    ('Classroom', 16),
    ('Birthday Budget', 17),
    ('Down payment', 18),
    ('Vacation', 19),
    ('Rent', 20),
    ('Car Maintenance', 21),
    ('Health Insurance', 22),
    ('Car Payment', 23),
    ('Phone Bill', 24),
    ('Car insurance', 25),
    ('Gas Power', 26),
    ('Electricity', 27),
    ('Retirement Contribution', 28),
    ('Savings Contribution', 29),
    ('Christmas Budget', 30),
    ('Christmas Siblings', 31),
    ('Business Travel', 32),
    ('Other', 33)
ON CONFLICT (name) DO NOTHING;
