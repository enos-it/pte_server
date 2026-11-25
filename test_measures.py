import unittest
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, event
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

import app as server
from model import Base, Group, Measures, MeterName, Site, SubGroup, Unit


@compiles(DOUBLE, "sqlite")
def compile_mysql_double_for_sqlite(_type, _compiler, **_kwargs):
    return "FLOAT"


class MeasuresTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        with self.engine.begin() as connection:
            sql = Path(__file__).with_name("reference_data.sql").read_text(encoding="utf-8")
            for statement in sql.split(";"):
                if statement.strip():
                    connection.exec_driver_sql(statement)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session_patch = patch.object(server, "get_session", side_effect=lambda *args: self.Session())
        self.session_patch.start()
        self.addCleanup(self.session_patch.stop)
        self.addCleanup(self.engine.dispose)
        self.client = server.app.test_client()
        self.measure = {
            "id": "oid-1",
            "siteId": 1,
            "groupId": 1,
            "subGroupId": 1,
            "unitId": 1,
            "meterNameId": 1,
            "value": 12.5,
            "timestampMs": 123,
            "enteredBy": "user",
        }

    def test_create_and_read_measure(self):
        response = self.client.post("/api/measures", json=[self.measure])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["count"], 1)
        response = self.client.get("/api/measures/user")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        result = response.json[0]
        self.assertEqual(float(result.pop("value")), self.measure["value"])
        self.assertEqual(result, {key: value for key, value in self.measure.items() if key != "value"})

    def test_invalid_and_unknown_reference_ids_reject_batch(self):
        for field in server.REFERENCE_FIELDS:
            for invalid in (None, True, 0, 2**31, "1", 999):
                with self.subTest(field=field, invalid=invalid):
                    bad_measure = dict(self.measure, id="bad", **{field: invalid})
                    response = self.client.post("/api/measures", json=[self.measure, bad_measure])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn(field, response.json["error"])
        session = self.Session()
        try:
            self.assertEqual(session.query(Measures).count(), 0)
        finally:
            session.close()

    def test_duplicate_oid_rejects_batch(self):
        self.assertEqual(self.client.post("/api/measures", json=[self.measure]).status_code, 201)
        response = self.client.post(
            "/api/measures", json=[dict(self.measure, id="new"), self.measure]
        )
        self.assertEqual(response.status_code, 409)
        session = self.Session()
        try:
            self.assertEqual(session.query(Measures).count(), 1)
        finally:
            session.close()

    def test_reference_values_are_editable_and_foreign_keys_are_enforced(self):
        session = self.Session()
        try:
            for model in (Site, Group, SubGroup, Unit, MeterName):
                session.add(model(name="Custom"))
            session.commit()
            ids = {field: session.query(model).filter_by(name="Custom").one().id
                   for field, model in server.REFERENCE_FIELDS.items()}
        finally:
            session.close()

        self.assertEqual(self.client.post("/api/measures", json=[dict(self.measure, **ids)]).status_code, 201)
        session = self.Session()
        try:
            site = session.query(Site).filter_by(id=ids["siteId"]).one()
            site.name = "Renamed"
            session.commit()
            session.delete(site)
            with self.assertRaises(IntegrityError):
                session.commit()
            session.rollback()
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
