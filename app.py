from flask import Flask, escape, request, jsonify
from ariadne.constants import PLAYGROUND_HTML
from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
import json

type_defs = load_schema_from_path("schema.graphql")

student_id = 0
class_id = 0
DB={
    "students" : [],
    "classes" : []
}

# Query
# Create QueryType instance for Query type defined in our schema
query = QueryType()

# Assign our resolver function to its "allstudents" field.
@query.field("allstudents")
def resolve_allstudents(*_):
    return DB["students"]

@query.field("students")
def resolve_students(*_,id = None):
    for s in DB["students"]:
        if s["id"] == id:
            return s
    return None

@query.field("allclasses")
def resolve_allclasses(*_):
    return DB["classes"]

@query.field("classes")
def resolve_classes(*_, id = None):
    for c in DB["classes"]:
        if c["id"] == id:
            return c
    return None

# Student
students = ObjectType("Students")
student_payload = ObjectType("StudentPayload")
# Classes
classes = ObjectType("Classes")
class_payload = ObjectType("ClassPayload")

# Mutation
mutation = MutationType()

@mutation.field("createStudent")
def resolve_create_student(*_,name):
    try:
        global student_id
        DB["students"].append({"id":student_id,"name":name})
        student_id = student_id + 1
        return {
            "status": True,
            "student": DB["students"][-1]
        }
    except:
        return {
            "status": False,
            "error": "error"
        }

@mutation.field("createClass")
def resolve_create_class(*_, name):
    try:
        global class_id
        DB["classes"].append({"id":class_id,"name":name,"students":[]})
        class_id = class_id + 1
        return {
            "status": True,
            "class":  DB["classes"][-1]
        }
    except:
        return {
            "status": False,
            "error": "error"
        }

@mutation.field("addStudentToClass")
def resolve_add_student_to_class(_, info, student_id, class_id):
    tmp_student = {}
    flag = 0
    for s in DB["students"]:
        if s["id"] == student_id:
            tmp_student = s
            flag = 1
            break

    if flag == 0:
        return {
            "status": False,
            "error": "Invalid student_id"
        }

    tmp_class = {}
    for c in DB["classes"]:
        if c["id"] == class_id:
            tmp_class = c
            flag = 2
            c["students"].append(tmp_student)
            break
    if flag == 2 :
        return {
            "status": True,
            "class": tmp_class
            }
    else:
        return {
            "status": False,
            "error": "Invalid class_id"
        }
    

schema  = make_executable_schema(type_defs, query,students, student_payload, classes, class_payload, mutation)
app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)




