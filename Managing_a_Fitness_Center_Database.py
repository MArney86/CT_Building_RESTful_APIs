from password import sql_password
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

#Task 2
class MemberSchema(ma.Schema):
    id = fields.Integer(requires=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "age")

#Task 3
class SessionSchema(ma.Schema):
    session_id = fields.Integer(requires=True)
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

#Task 2
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

#Task 3
session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

#connection to mysql
def get_db_connection():
    #login details
    db_name = 'fitness_center_db'
    user = 'root'
    password = sql_password
    host = 'localhost'

    #attempt the connection with error handling
    try:
        #make connection with MySQL
        conn = mysql.connector.connect(
            database=db_name,
            user = user,
            password = password,
            host = host
        )

        return conn
    
    #Error during connection
    except Error as e:
        print(f"\033[7mError: {e}\033[0m")
        return None

#Default route
@app.route('/')
def home():
    return 'Welcome to the Fitness Center Management System!'

#Task 2
#Get all members
@app.route("/members", methods=["GET"])
def get_members():
    try:
        #establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #SQL query to fetch all members
        query = "Select * FROM members"

        #executing the query
        cursor.execute(query)

        #fetching the results and preparing for JSON response
        members = cursor.fetchall()

        #Use Marshmallow to format the JSON Response
        return members_schema.jsonify(members)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Add new member    
@app.route('/members', methods=['POST'])
def add_member():
    try:
        #Validate and deserialize using Marshmallow input data sent by client
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        
        #Establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #new member details
        new_member = (member_data['id'], member_data['name'], member_data['age'])

        #SQL query to add new member
        query = "INSERT INTO Members (id, name, age) VALUES (%s, %s, %s)"

        #execute query
        cursor.execute(query, new_member)
        conn.commit()

        #Successful addition of the new member
        cursor.close()
        conn.close
        return jsonify({"message": "New member added successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Update a member
@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        #Validate and deserialize using Marshmallow input data sent by client
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        
        #Establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #new member details
        updated_member = (member_data['id'], member_data['name'], member_data['age'], id)

        #SQL query to add new member
        query = "UPDATE Members SET id =  %s, name = %s, age = %s WHERE id = %s"

        #execute query
        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member updated successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Delete a member
@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        
        #Establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #new member details
        member_to_remove = (id,)

        #test that member actually exists
        cursor.execute("SELECT * FROM Members WHERE id = %s", member_to_remove)
        member = cursor.fetchall()

        if not member:
            return jsonify({"error": "Member not found"}), 404
        
        #SQL query to delete a member
        query = "DELETE FROM Members WHERE id = %s"

        #execute query
        cursor.execute(query, member_to_remove)
        conn.commit()

        return jsonify({"message": "Member removed successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Task 3
#display all sessions
@app.route("/workoutsessions", methods=["GET"])
def get_sessions():
    try:
        #establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #SQL query to fetch all members
        query = "Select * FROM WorkoutSessions"

        #executing the query
        cursor.execute(query)

        #fetching the results and preparing for JSON response
        sessions = cursor.fetchall()

        #Use Marshmallow to format the JSON Response
        return sessions_schema.jsonify(sessions)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#display a specific session
@app.route("/workoutsessions/<int:session_id>", methods=["GET"])
def get_session(session_id):
    try:
        #establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #SQL query to fetch all members
        query = "Select * FROM WorkoutSessions WHERE session_id = %s"

        #executing the query
        cursor.execute(query, (session_id,))

        #fetching the results and preparing for JSON response
        session = cursor.fetchall()

        #Use Marshmallow to format the JSON Response
        return sessions_schema.jsonify(session)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#display sessions from a specific member
@app.route("/workoutsessions/member/<int:session_id>", methods=["GET"])
def get_member_sessions(session_id):
    try:
        #establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #SQL query to fetch all members
        query = "Select * FROM WorkoutSessions WHERE member_id = %s"

        #executing the query
        cursor.execute(query, (session_id,))

        #fetching the results and preparing for JSON response
        session = cursor.fetchall()

        #Use Marshmallow to format the JSON Response
        return sessions_schema.jsonify(session)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Add new Workout Session    
@app.route('/workoutsessions', methods=['POST'])
def add_session():
    try:
        #Validate and deserialize using Marshmallow input data sent by client
        session_data = session_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        
        #Establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #new member details
        new_session = (session_data['session_id'], session_data['member_id'], session_data['session_date'], session_data['session_time'], session_data['activity'])

        #SQL query to add new member
        query = "INSERT INTO WorkoutSessions (session_id, member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s, %s)"

        #execute query
        cursor.execute(query, new_session)
        conn.commit()

        #Successful addition of the new member
        cursor.close()
        conn.close
        return jsonify({"message": "New session added successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Update Workout Session
@app.route("/workoutsessions/<int:session_id>", methods=["PUT"])
def update_session(session_id):
    try:
        #Validate and deserialize using Marshmallow input data sent by client
        session_data = session_schema.load(request.json)

    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        
        #Establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #new member details
        updated_session = (session_data['session_id'], session_data['member_id'], session_data['session_date'], session_data['session_time'], session_data['activity'], session_id)

        #SQL query to update a session
        query = "UPDATE WorkoutSessions SET session_id = %s, member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id = %s"

        #execute query
        cursor.execute(query, updated_session)
        conn.commit()

        return jsonify({"message": "Member updated successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Delete Workout Session    
@app.route("/workoutsessions/<int:session_id>", methods=["DELETE"])
def delete_session(session_id):
    try:
        
        #Establishing connection to the database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        #new member details
        session_to_remove = (session_id,)

        cursor.execute("SELECT * FROM WorkoutSessions WHERE session_id = %s", session_to_remove)
        session = cursor.fetchall()

        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        #SQL query to delete a session
        query = "DELETE FROM WorkoutSessions WHERE session_id = %s"

        #execute query
        cursor.execute(query, session_to_remove)
        conn.commit()

        return jsonify({"message": "Session removed successfully"}), 200
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)