-- Run once after creating the tables, before editing the reference data.
INSERT INTO sites (name) VALUES ('Jesenice'), ('Bela');
INSERT INTO meter_groups (name) VALUES ('SPTE'), ('Kotli'), ('Glavni'), ('Vodarna');
INSERT INTO subgroups (name) VALUES
    ('Biomasa'), ('Panterm'), ('Bosch'), ('Loos'),
    ('SPTE 1'), ('SPTE 2'), ('SPTE 3'), ('SPTE 4'),
    ('SPTE 5'), ('SPTE 6'), ('SPTE 7'), ('VVK 1'), ('VVK 2');
INSERT INTO units (name) VALUES ('kWh'), ('MWh'), ('Nm3'), ('m3'), ('h'), ('bar'), ('°C');
INSERT INTO meter_names (name) VALUES ('Števec zagonov'), ('Števec ur');
