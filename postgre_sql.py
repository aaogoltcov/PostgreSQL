from pprint import pprint
import psycopg2


def create_db():  # создает таблицы
    cursor.execute("DROP TABLE IF EXISTS Student CASCADE;"
                   "DROP TABLE IF EXISTS Course CASCADE;"
                   "DROP TABLE IF EXISTS StudentCourse CASCADE;"

                   "CREATE TABLE IF NOT EXISTS Student ("
                   "id serial PRIMARY KEY not null, "
                   "name varchar(100) not null, "
                   "gpa numeric(10,2), "
                   "birth timestamp with time zone);"

                   "CREATE TABLE IF NOT EXISTS Course ("
                   "id serial PRIMARY KEY not null, "
                   "name varchar(100) not null);"
                   "INSERT into Course (id, name) values(100, 'Frontend');"
                   "INSERT into Course (id, name) values(200, 'Backend');"
                   "INSERT into Course (id, name) values(300, 'Python');"
                   "INSERT into Course (id, name) values(400, 'JavaScript');"
                   "INSERT into Course (id, name) values(500, 'SQL');"

                   "CREATE TABLE IF NOT EXISTS StudentCourse ("
                   "id serial PRIMARY KEY, "
                   "student_id INTEGER REFERENCES Student(id), "
                   "course_id INTEGER REFERENCES Course(id));")
    print("Table Student created")
    print("Master Table Course created and filled")
    print("Reference Table StudentCourse created")
    print("Список доступных курсов:")
    cursor.execute("SELECT * FROM Course;")
    pprint(cursor.fetchall())


def get_students(course_id):  # возвращает студентов определенного курса
    cursor.execute("SELECT Student.name, "
                   "Student.gpa,"
                   "Course.name FROM Student "
                   "JOIN StudentCourse ON StudentCourse.student_id = Student.id "
                   "JOIN Course ON StudentCourse.course_id = Course.id "
                   "WHERE Course.id = %s;", (course_id,))
    pesponse = cursor.fetchall()
    if pesponse:
        for i, item in enumerate(pesponse):
            print(f"{i + 1}-й пользователь: ")
            for key, value in {'Name': item[0], 'GPA': item[1], 'Course': item[2]}.items():
                print(f"\t{key}: {value}")
    else:
        print("Такой записи не существует")


def add_students(course_id, students):  # создает студентов и записывает их на курс
    add_student(student=students)
    cursor.execute("INSERT into StudentCourse (course_id, student_id) "
                   "SELECT %s, id FROM Student "
                   "WHERE name = %s "
                   "AND birth = %s;",
                   (course_id, students['name'], students['birth']))


def add_student(student):  # просто создает студента
    cursor.execute("INSERT into Student (name, gpa, birth) values(%s, %s, %s);",
                   (student['name'], student['gpa'], student['birth']))
    return cursor


def get_student(student_id):
    cursor.execute("SELECT Student.name, "
                   "Student.gpa,"
                   "Course.name FROM Student "
                   "JOIN StudentCourse ON StudentCourse.student_id = Student.id "
                   "LEFT OUTER JOIN Course ON StudentCourse.course_id = Course.id "
                   "WHERE Student.id = %s;", (student_id,))
    response = cursor.fetchall()
    for key, value in {'Name': response[0][0], 'GPA': response[0][1], 'Course': response[0][2]}.items():
        print(f"\t{key}: {value}")


HELP = "HELP TUTORIAL: " \
       "\nadds    - добавить студентов и записать их на курс \n" \
       "add     - добавить студента \n" \
       "gets    - получить информацию о студента с определенного курса \n" \
       "get     - получить информацию о студенте и курсе \n" \
       "q       - выйти\n"


def main():
    global cursor
    dbname = "test_db"
    command = str()

    with psycopg2.connect(
            dbname=dbname,
            user="test",
            password="test") as connection:
        print(f"Подключились к БД {dbname}")
        with connection.cursor() as cursor:
            create_db()
            while command != "q":
                command = input("Введите команду (q - выйти, help - список команд): ")
                if command == "help":
                    print(HELP)
                elif command == "adds" or command == "add":
                    add_command = str()
                    while add_command != "n" or not add_command:
                        student_name = input("Имя студента: ")
                        student_gpa = input("Балл студента: ")
                        student_birthday = input("ДР студента (1980-02-01): ")
                        student_info = dict(name=student_name, gpa=student_gpa, birth=student_birthday)
                        try:
                            if command == "adds":
                                student_course_id = int(input("ID курса студента: "))
                            else:
                                student_course_id = None
                        except ValueError:
                            student_course_id = None
                        add_students(course_id=student_course_id, students=student_info)
                        if student_info and student_course_id:
                            add_command = input("Добавить еще студента и курсы (y/n): ")
                        else:
                            add_command = input("Добавить еще студента (y/n): ")
                elif command == "gets" or command == "get":
                    get_command = str()
                    while get_command != "n" or not get_command:
                        try:
                            if command == "get":
                                student_id = int(input("ID студента: "))
                                get_student(student_id=student_id)
                                get_command = input("Посмотреть еще студента (y/n): ")
                            elif command == "gets":
                                course_id = int(input("ID курса: "))
                                get_students(course_id=course_id)
                                get_command = input("Посмотреть еще курс (y/n): ")
                        except (IndexError, ValueError):
                            print("Такой записи не существует")


main()
