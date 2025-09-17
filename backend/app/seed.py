SEMESTER_DATA = {
    1: [
        (1, "ENGL100", "FUNCTIONAL ENGLISH", 3),
        (2, "MATH108", "Calculus & Analytical Geometry", 3),
        (3, "COMP102", "Programming Fundamentals", 4),
        (4, "COMP110", "Discrete Structures", 3),
        (5, "COMP113", "AICT", 3),
        (6, "BEHS102", "Life and Learning - I", 1),
        (7, "CALC100", "Pre-Calculus - I", 3),
        (8, "CALC101", "Pre-Calculus - II", 3),
    ],
    2: [
        (1, "EXPR100", "Expository Writing", 3),
        (2, "COMP111", "Object Oriented Programming", 4),
        (3, "PHYS124", "Applied Physics", 3),
        (4, "COMP303", "Database Systems", 4),
        (5, "MATH209", "Linear Algebra", 3),
        (6, "ISLM100", "Islamic Studies", 2),
    ],
    3: [
        (1, "COMP231", "Data Structures", 4),
        (2, "COMP232", "Artificial Intelligence", 3),
        (3, "COMP233", "Computer Networks", 3),
        (4, "COMP134", "Digital Logic Design", 3),
        (5, "COMP316", "Software Engineering", 3),
        (6, "STAT205", "Probability & Statistics", 3),
    ],
    4: [
        (1, "COMP236", "Computer Organization & Assembly Language", 3),
        (2, "COMP234", "Information Security", 3),
        (3, "COMP238", "Advanced Database Management Systems", 3),
        (4, "COMP241", "Introduction to Data Science", 3),
        (5, "COMP313", "Theory of Automata", 3),
        (6, "MATH111", "Multivariable Calculus", 3),
    ],
    5: [
        (1, "MNGT204", "Introduction to Management", 2),
        (2, "COMP331", "Cloud Computing", 3),
        (3, "COMP332", "Computer Architecture", 3),
        (4, "COMP333", "Operating Systems", 3),
        (5, "COMP334", "HCI & Computer Graphics", 3),
        (6, "COMP240", "Machine Learning", 3),
    ],
    6: [
        (1, "COMP336", "Web Technologies", 3),
        (2, "COMP338", "Compiler Construction", 3),
        (3, "COMP339", "Numerical Analysis", 3),
        (4, "COMP340", "Parallel & Distributed Computing", 3),
        (5, "COMP341", "Cyber Security", 3),
        (6, "COMP231", "Data Structures", 4),
        (7, "COMP202", "Data Structures & Algorithms", 4),
        (8, "STAT205", "Probability & Statistics", 3),
    ],
    7: [
        (1, "COMP431", "Analysis of Algorithms", 3),
        (2, "COMP432", "Mobile Application Development", 3),
        (3, "MNGT301", "Principles of Marketing", 3),
        (4, "ENGL200", "Technical & Business Writing", 3),
        (5, "ENTR100", "Entrepreneurship", 2),
        (6, "COMP498", "Final Year Project - I", 3),
    ],
    8: [
        (1, "ICOP100", "Ideology & Constitution of Pakistan", 2),
        (2, "COMP433", "Professional Practices", 2),
        (3, "CAVE100", "Civics and Community Engagement", 2),
        (4, "COMP499", "Final Year Project - II", 3),
    ],
}

def _ordinal(n: int) -> str:
    return (
        f"{n}st Semester" if n == 1 else
        f"{n}nd Semester" if n == 2 else
        f"{n}rd Semester" if n == 3 else
        f"{n}th Semester"
    )

def seed(db, Semester, Course):
    # Idempotent seeding
    from sqlalchemy import select
    for n in range(1, 9):
        name = _ordinal(n)
        sem = db.execute(select(Semester).where(Semester.name == name)).scalars().first()
        if not sem:
            sem = Semester(name=name)
            db.add(sem)
            db.commit()
            db.refresh(sem)

        existing_codes = {c.course_code for c in sem.courses}
        for sr, code, cname, ch in SEMESTER_DATA[n]:
            if code not in existing_codes:
                db.add(Course(
                    semester_id=sem.id,
                    sr_no=sr,
                    course_code=code,
                    course_name=cname,
                    credit_hours=ch
                ))
        db.commit()