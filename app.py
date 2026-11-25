import math
import os

from flask import Flask, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from model import Group, Measures, MeterName, Site, SubGroup, Unit, get_session


app = Flask(__name__, static_folder="static", static_url_path="/static")

db_host = 'localhost'
db_user = 'vajnar'
db_password = 'AldebaraN7#'
db_name = 'pte'

REFERENCE_FIELDS = {
    "siteId": Site,
    "groupId": Group,
    "subGroupId": SubGroup,
    "unitId": Unit,
    "meterNameId": MeterName,
}

@app.post("/api/measures")
def create_measure():
    payload = request.get_json(silent=True)
    if not isinstance(payload, list) or not payload:
        return jsonify(error="Request body must be a non-empty JSON array"), 400

    measures = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            return jsonify(error=f"Item {index} must be a JSON object"), 400

        reference_ids = {field: item.get(field) for field in REFERENCE_FIELDS}
        oid = item.get("id")
        value = item.get("value")
        timestamp_ms = item.get("timestampMs")
        entered_by = item.get("enteredBy")

        if not isinstance(oid, str) or not oid.strip():
            return jsonify(error=f"Item {index}: 'OID' must be a non-empty string"), 400
        for field, reference_id in reference_ids.items():
            if isinstance(reference_id, bool) or not isinstance(reference_id, int) or not 1 <= reference_id <= 2**31 - 1:
                return jsonify(error=f"Item {index}: '{field}' must be a positive 32-bit integer"), 400
        try:
            valid_value = (
                not isinstance(value, bool)
                and isinstance(value, (int, float))
                and math.isfinite(value)
            )
        except OverflowError:
            valid_value = False
        if not valid_value:
            return jsonify(error=f"Item {index}: 'value' must be a finite number"), 400
        if (
            isinstance(timestamp_ms, bool)
            or not isinstance(timestamp_ms, int)
            or not -(2**63) <= timestamp_ms < 2**63
        ):
            return jsonify(error=f"Item {index}: 'timestampMs' must be a signed 64-bit integer"), 400
        if not isinstance(entered_by, str) or not entered_by.strip():
            return jsonify(error=f"Item {index}: 'enteredBy' must be a non-empty string"), 400

        measures.append(
            Measures(
                OID=oid.strip(),
                **reference_ids,
                value=value,
                timestampMs=timestamp_ms,
                enteredBy=entered_by.strip(),
            )
        )

    if not db_user or not db_password:
        app.logger.error("DB_USER and DB_PASSWORD must be configured")
        return jsonify(error="Database is not configured"), 503

    session = None
    try:
        session = get_session(db_host, db_user, db_password, db_name)
        for field, model in REFERENCE_FIELDS.items():
            ids = {getattr(measure, field) for measure in measures}
            existing_ids = {row[0] for row in session.query(model.id).filter(model.id.in_(ids)).all()}
            if ids - existing_ids:
                return jsonify(error=f"Unknown {field}: {sorted(ids - existing_ids)}"), 400
        session.add_all(measures)
        session.commit()
        return jsonify(ids=[measure.id for measure in measures], count=len(measures)), 201
    except IntegrityError:
        if session is not None:
            session.rollback()
        app.logger.info("Rejected measure due to a database integrity constraint")
        return jsonify(error="Measure conflicts with existing data or reference values"), 409
    except SQLAlchemyError:
        if session is not None:
            session.rollback()
        app.logger.exception("Failed to insert measure")
        return jsonify(error="Unable to save measure"), 500
    finally:
        if session is not None:
            session.close()


@app.get("/api/measures/<user_id>")
def get_user_measures(user_id):
    session = None
    try:
        session = get_session(db_host, db_user, db_password, db_name)
        measures = session.query(Measures).filter(Measures.enteredBy == user_id).all()
        return jsonify(
            [
                {
                    "id": measure.OID,
                    "siteId": measure.siteId,
                    "groupId": measure.groupId,
                    "subGroupId": measure.subGroupId,
                    "unitId": measure.unitId,
                    "meterNameId": measure.meterNameId,
                    "value": measure.value,
                    "timestampMs": measure.timestampMs,
                    "enteredBy": measure.enteredBy,
                }
                for measure in measures
            ]
        ), 200
    except SQLAlchemyError:
        app.logger.exception("Failed to retrieve measures")
        return jsonify(error="Unable to retrieve measures"), 500
    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
