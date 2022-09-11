import psycopg2
from flask import Flask
from flask import redirect, render_template, request

app = Flask(__name__)
users_list = []

@app.route('/')
def index():
    conn = psycopg2.connect(database="P_DATABASE", user="P_USER", password="P_PASSWORD", host="P_HOST", port="P_PORT")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT uid, last_name_val, first_name_val, middle_name_val, street_val, build, build_k, apartment, telephone "
        "FROM main join last_name on main.last_name=last_name.last_name_id "
        "join first_name on main.first_name=first_name.first_name_id "
        "join middle_name on main.middle_name=middle_name.middle_name_id "
        "join street on main.street=street.street_id;")

    users_list.clear()
    for row in cursor.fetchall():
        user_dict = {'uid': row[0],
                     'last_name': row[1],
                     'first_name': row[2],
                     'middle_name': row[3],
                     'street': row[4],
                     'build': row[5],
                     'build_k': row[6],
                     'apartment': row[7],
                     'telephone': row[8]}
        users_list.append(user_dict)

    return redirect('http://127.0.0.1:5000/users')


@app.route('/users/')
def users():
    return render_template('list.html', users_list=users_list)


@app.route('/users/add/', methods=['get', 'post'])
def user_add():
    conn = psycopg2.connect(database="xacgkxus", user="xacgkxus", password="9AzfJBSkoEPCNVUPoBpkt5uU1AnuY8lD",
                        host="balarama.db.elephantsql.com", port="5432")
    cursor = conn.cursor()

    if request.method == 'POST':
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        street = request.form.get('street')
        build = request.form.get('build')
        build_k = request.form.get('build_k')
        apartment = request.form.get('apartment')
        telephone = request.form.get('telephone')

        personal_data = {'last_name': last_name,
                         'first_name': first_name,
                         'middle_name': middle_name,
                         'street': street,
                         'build': build,
                         'build_k': build_k,
                         'apartment': apartment,
                         'telephone': telephone}

        for k in personal_data.keys():
            if personal_data[k] is None:
                personal_data[k] = "null"

        sql_list = [f"SELECT count(last_name_id) FROM last_name WHERE last_name_val='{personal_data['last_name']}'",
                    f"SELECT count(first_name_id) FROM first_name WHERE first_name_val='{personal_data['first_name']}'",
                    f"SELECT count(middle_name_id) FROM middle_name WHERE middle_name_val='{personal_data['middle_name']}'",
                    f"SELECT count(street_id) FROM street WHERE street_val='{personal_data['street']}'"]

        sql_insert_list = [f"INSERT INTO last_name (last_name_val) VALUES ('{personal_data['last_name']}');",
                           f"INSERT INTO first_name (first_name_val) VALUES ('{personal_data['first_name']}');",
                           f"INSERT INTO middle_name (middle_name_val) VALUES ('{personal_data['middle_name']}');",
                           f"INSERT INTO street (street_val) VALUES ('{personal_data['street']}');"]
        i = 0
        for sql_checking in sql_list:
            data = []
            cursor.execute(sql_checking, data)
            results = cursor.fetchone()
            conn.commit()
            if results[0] == 0:
                cursor.execute(sql_insert_list[i])
                print("вставка произошла")
            i += 1

        # запрос в main
        sql_query = f"INSERT INTO main (build, build_k, apartment, telephone, last_name, first_name, middle_name, street) VALUES(" \
                    f"{personal_data['build']}, {personal_data['build_k']}, {personal_data['apartment']}, {personal_data['telephone']}," \
                    f"(SELECT last_name_id from last_name where last_name_val='{personal_data['last_name']}')," \
                    f"(SELECT first_name_id from first_name where first_name_val='{personal_data['first_name']}')," \
                    f"(SELECT middle_name_id from middle_name where middle_name_val='{personal_data['middle_name']}')," \
                    f"(SELECT street_id from street where street_val='{personal_data['street']}'));"

        cursor.execute(sql_query)
        conn.commit()

    return render_template('add.html')


@app.route('/user/<user_id>')
def user(user_id):
    user = ''
    for i in users_list:
        if str(i['uid']) == user_id:
            user = i
    return render_template('user_info.html', user=user)

