"""
tests/test_ownership.py — Cross-user data isolation tests.

User B is logged in trying to access / modify records owned by User A.
Every route must return 403 or 404.  The record must remain unchanged in DB.
"""
import pytest
from app.models import (
    Achievement, Certification, Education, Extracurricular,
    Internship, Project, Skill,
)


# Map from module URL slug -> (Model, lookup helper attribute)
MODULES = [
    ("education",       Education),
    ("skills",          Skill),
    ("certifications",  Certification),
    ("projects",        Project),
    ("internships",     Internship),
    ("achievements",    Achievement),
    ("extracurriculars",Extracurricular),
]


def _first_id(app, model, user_dict):
    """Return the id of the first record owned by user_dict, inside the app context."""
    with app.app_context():
        record = model.query.filter_by(user_id=user_dict["id"]).first()
        assert record is not None, f"No {model.__name__} found for {user_dict['name']}"
        return record.id


@pytest.mark.parametrize("module_name,model", MODULES)
def test_user_b_cannot_edit_user_a_record(app, auth_client_b, user_a, module_name, model):
    """GET edit page for another user's record must return 403 or 404."""
    item_id = _first_id(app, model, user_a)
    resp = auth_client_b.get(f"/profile/{module_name}/{item_id}/edit")
    assert resp.status_code in (403, 404), (
        f"{module_name}: expected 403/404, got {resp.status_code}"
    )


@pytest.mark.parametrize("module_name,model", MODULES)
def test_user_b_cannot_delete_user_a_record(app, auth_client_b, user_a, module_name, model):
    """
    POST delete for another user's record must be rejected (403 or 404)
    and the record must still exist in the database.
    """
    item_id = _first_id(app, model, user_a)
    resp = auth_client_b.post(
        f"/profile/{module_name}/{item_id}/delete",
        follow_redirects=False,
    )
    assert resp.status_code in (403, 404), (
        f"{module_name}: expected 403/404 on delete, got {resp.status_code}"
    )
    # Confirm the record was NOT deleted.
    with app.app_context():
        still_there = model.query.get(item_id)
        assert still_there is not None, (
            f"{module_name} record {item_id} was wrongly deleted!"
        )
