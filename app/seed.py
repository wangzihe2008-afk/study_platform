from . import db
from .models import Topic, ExampleQuestion, ExerciseQuestion


def seed_data():
    if Topic.query.first():
        return

    samples = [
        {
            'country': 'Canada',
            'province': 'Ontario',
            'subject': 'Math',
            'grade': '10',
            'knowledge_point': 'Quadratic Functions',
            'requirement': 'Understand vertex form, standard form, direction of opening, axis of symmetry, and transformations of quadratic graphs according to Ontario curriculum expectations.',
            'explanation': 'A quadratic function usually has the form y = ax² + bx + c or y = a(x-h)² + k. The sign of a determines whether the parabola opens up or down. The values h and k give the vertex in vertex form.',
            'examples': [
                {
                    'difficulty': '一般',
                    'title': 'Find the vertex',
                    'question': 'For y = (x-3)^2 + 4, find the vertex and direction of opening.',
                    'solution': 'This is already in vertex form y = a(x-h)^2 + k. So h = 3 and k = 4, which means the vertex is (3, 4). Since a = 1 > 0, the parabola opens upward.',
                    'exam_tips': 'Recognize vertex form directly. The sign in the bracket is opposite of h.',
                    'country_version': 'Canada'
                },
                {
                    'difficulty': '较难',
                    'title': 'Transformations',
                    'question': 'Describe the transformations from y = x^2 to y = -2(x+1)^2 + 5.',
                    'solution': 'Compared with y = x^2: shift left 1, vertical stretch by factor 2, reflect in x-axis, then shift up 5.',
                    'exam_tips': 'Read transformations from vertex form and remember the inside sign rule.',
                    'country_version': 'Canada'
                },
                {
                    'difficulty': '超难',
                    'title': 'Convert and analyze',
                    'question': 'Convert y = x^2 - 6x + 5 to vertex form and state the vertex.',
                    'solution': 'Complete the square: y = x^2 - 6x + 9 - 9 + 5 = (x-3)^2 - 4. Vertex is (3, -4).',
                    'exam_tips': 'For full marks, show each step of completing the square clearly.',
                    'country_version': 'Canada'
                }
            ],
            'exercises': [
                {
                    'difficulty': '一般',
                    'title': 'Basic vertex practice',
                    'question': 'Find the vertex of y = (x + 2)^2 - 7.',
                    'standard_answer': 'Vertex is (-2, -7).',
                    'marking_points': '1 mark for correct h, 1 mark for correct k, 1 mark for writing the vertex correctly.'
                },
                {
                    'difficulty': '较难',
                    'title': 'Opening and vertex',
                    'question': 'For y = -3(x - 1)^2 + 6, state the vertex and direction of opening.',
                    'standard_answer': 'Vertex is (1, 6). Since a = -3, the parabola opens downward.',
                    'marking_points': '2 marks for vertex, 1 mark for identifying a negative coefficient, 1 mark for correct opening direction.'
                }
            ]
        },
        {
            'country': 'Canada',
            'province': 'Ontario',
            'subject': 'Physics',
            'grade': '10',
            'knowledge_point': 'Velocity and Acceleration',
            'requirement': 'Distinguish speed, velocity, and acceleration; solve simple uniform acceleration problems.',
            'explanation': 'Velocity includes direction, while speed does not. Acceleration measures change in velocity over time. Common formula: a = (vf - vi) / t.',
            'examples': [
                {
                    'difficulty': '一般',
                    'title': 'Simple acceleration',
                    'question': 'A car increases velocity from 10 m/s to 20 m/s in 5 s. Find acceleration.',
                    'solution': 'a = (20 - 10) / 5 = 2 m/s².',
                    'exam_tips': 'Write the formula first, substitute values, then include units.',
                    'country_version': 'Canada'
                }
            ],
            'exercises': [
                {
                    'difficulty': '一般',
                    'title': 'Acceleration calculation',
                    'question': 'An object changes velocity from 4 m/s to 16 m/s in 3 s. Find acceleration.',
                    'standard_answer': 'a = (16 - 4) / 3 = 4 m/s².',
                    'marking_points': '1 mark formula, 1 mark substitution, 1 mark correct answer and unit.'
                }
            ]
        },
        {
            'country': 'Canada',
            'province': 'Ontario',
            'subject': 'Chemistry',
            'grade': '10',
            'knowledge_point': 'Atomic Structure',
            'requirement': 'Identify protons, neutrons, electrons, and basic atomic notation.',
            'explanation': 'Atoms are made of a nucleus containing protons and neutrons, with electrons around the nucleus. Atomic number gives the number of protons.',
            'examples': [
                {
                    'difficulty': '一般',
                    'title': 'Count subatomic particles',
                    'question': 'How many protons are in an atom with atomic number 8?',
                    'solution': 'Atomic number equals number of protons, so there are 8 protons.',
                    'exam_tips': 'Atomic number always gives proton count.',
                    'country_version': 'Canada'
                }
            ],
            'exercises': [
                {
                    'difficulty': '一般',
                    'title': 'Atomic number practice',
                    'question': 'An atom has atomic number 11. How many protons does it have?',
                    'standard_answer': 'It has 11 protons.',
                    'marking_points': '1 mark for recognizing atomic number equals proton count, 1 mark for correct answer.'
                }
            ]
        }
    ]

    for item in samples:
        topic = Topic(
            country=item['country'],
            province=item['province'],
            subject=item['subject'],
            grade=item['grade'],
            knowledge_point=item['knowledge_point'],
            requirement=item['requirement'],
            explanation=item['explanation'],
        )
        db.session.add(topic)
        db.session.flush()

        for ex in item['examples']:
            db.session.add(ExampleQuestion(topic_id=topic.id, **ex))
        for exr in item['exercises']:
            db.session.add(ExerciseQuestion(topic_id=topic.id, **exr))

    db.session.commit()
