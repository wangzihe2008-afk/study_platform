import json
from .models import db, CurriculumUnit, QuizQuestion
from .data_seed import CURRICULUM_DATA, QUESTION_BANK

def dump_json(v):
    return json.dumps(v, ensure_ascii=False)

def seed_all():
    if CurriculumUnit.query.count() == 0:
        for row in CURRICULUM_DATA:
            db.session.add(CurriculumUnit(
                country=row["country"],
                province=row["province"],
                grade=row["grade"],
                subject=row["subject"],
                unit=row["unit"],
                requirements_json=dump_json(row["requirements"]),
                content=row["content"],
                resources_json=dump_json(row["resources"]),
            ))
    if QuizQuestion.query.count() == 0:
        for q in QUESTION_BANK:
            db.session.add(QuizQuestion(**q))
    db.session.commit()
