import datetime
import json
from flask import request, jsonify
from timeline import *
from improvement import *
from skill_allocation import *

def get_employees():
    q =  " prefix foaf:   <http://xmlns.com/foaf/spec/> "
    q += " SELECT distinct (str(?n) as ?employeeNames) "
    q += " WHERE{"
    q += "   GRAPH <http://localhost:8890/MyWorkForce> {"
    q += "     ?p foaf:name ?n."
    q += "   }"
    q += " }"
    res = helpers.query(q)
    data = json.dumps(res)
    return data

@app.route('/timeline/')
def get_skill_timeline():
    """Selects all employees with the given skill that are active at the company."""
    today = datetime.datetime.today().date()
    skillURI = str("http://data.europa.eu/esco/skill/" + request.args.get("skillid"))

    q =  """ prefix esco: <http://data.europa.eu/esco/model#>
             prefix skosxl: <http://www.w3.org/2008/05/skos-xl#>
             prefix default: <http://example.org/MyCompany/>
             prefix foaf: <http://xmlns.com/foaf/spec/>

             SELECT distinct ?name ?sDate ?aDate ?eDate
             WHERE{
                 GRAPH <http://mu.semte.ch/application>{
                     ?employee default:hasSkill ?skillemp.
                     ?employee foaf:name ?name.
                     ?skillemp esco:hasSkill <%s>.
                     ?employee default:function ?function.
                     ?function default:startDate ?sDate.
                     ?skillemp default:acquired ?aDate.
                 OPTIONAL{
                     ?function default:endDate ?date.
                 } BIND(IF(BOUND(?date), ?date, %s ) AS ?eDate)
             }
         }""" % (skillURI, sparql_escape(today))

    data = helpers.query(q)
    bindings = data["results"]["bindings"]
    tl = Timeline()
    for b in bindings:
        e = TimelineElement(b["aDate"]["value"], b["sDate"]["value"], b["eDate"]["value"])
        tl.add_element(e)
    if tl.has_elements():
        return jsonify(tl.createTimeLine())
    else:
        return jsonify({'data': []})


def get_occupation_bubble():
    pass

@app.route('/skills/')
def all_skills():
    q = """ prefix esco: <http://data.europa.eu/esco/model#>
            prefix skosxl: <http://www.w3.org/2008/05/skos-xl#>
            prefix default: <http://example.org/MyCompany/>
            SELECT distinct (?skill as ?skillURI) (str(?literal) as ?skillName) ?id
            WHERE{
                GRAPH <http://mu.semte.ch/application>{
                    ?skill a esco:Skill.
                    ?skill ^esco:hasSkill ?se.
                    ?se a default:EmployeeSkill.
                    ?skill skos:prefLabel ?literal.
                    ?skill <http://mu.semte.ch/vocabularies/core/uuid> ?id.
                }
            }"""
    res = helpers.query(q)
    data = res["results"]["bindings"]
    jobj = {"data":[]}
    for e in data:
        jobj["data"].append({
            "attributes": {
                "name": e["skillName"]["value"]
            },
            "id": e["id"]["value"],
            "type": "skills"
        })
    helpers.log("recent")
    return jsonify(jobj)


@app.route('/occupations/')
def get_all_occupations():
    q = """ prefix esco: <http://data.europa.eu/esco/model#>
            prefix skosxl: <http://www.w3.org/2008/05/skos-xl#>
            prefix default: <http://example.org/MyCompany/>
            SELECT distinct (?occ as ?occURI) (str(?literal) as ?occName) ?id
            WHERE{
                GRAPH <http://mu.semte.ch/application>{
                    ?so a default:EmployeeFunction.
                    ?so esco:hasOccupation ?occ.
                    ?occ skos:prefLabel ?literal.
                    ?occ <http://mu.semte.ch/vocabularies/core/uuid> ?id.
                }
            }"""
    res = helpers.query(q)
    data = res["results"]["bindings"]
    jobj = {"data": []}
    for e in data:
        jobj["data"].append({
            "attributes": {
                "name": e["occName"]["value"]
            },
            "id": e["id"]["value"],
            "type": "occupations"
        })
    helpers.log("recent")
    return jsonify(jobj)


@app.route('/improvements/')
def get_inprovement():
    today = datetime.datetime.today().date()

    q = """
        prefix esco: <http://data.europa.eu/esco/model#>
        prefix skosxl: <http://www.w3.org/2008/05/skos-xl#>
        prefix default: <http://example.org/MyCompany/>
        prefix foaf: <http://xmlns.com/foaf/spec/>
        prefix mu:  <http://mu.semte.ch/vocabularies/core/>
        prefix skos: <http://www.w3.org/2004/02/skos/core#>

        SELECT distinct ?skillName ?skillID ?empName ?empID ?occ ?sDate ?aDate ?eDate (str(?occN) as ?occupation)
        WHERE{
            ?employee default:hasSkill ?skillemp.
            ?employee mu:uuid ?empID.
            ?employee foaf:name ?empName.

            ?employee default:function ?function.
            ?function esco:hasOccupation ?occ.
            ?occ skos:prefLabel ?occN.

            ?skillemp esco:hasSkill ?skill.
            ?skill mu:uuid ?skillID.
            ?skill skos:prefLabel ?skillName.
            ?skillemp default:acquired ?aDate.

            ?employee default:function ?function.
            ?function default:startDate ?sDate.

            OPTIONAL{
                    ?function default:endDate ?date.
             } BIND(IF(BOUND(?date), ?date, %s ) AS ?eDate)
        }
        """ % (sparql_escape(today))

    data = helpers.query(q)
    bindings = data["results"]["bindings"]
    for b in bindings:
        acquired = b["aDate"]["value"]
        start = b["sDate"]["value"]
        end = b["eDate"]["value"]
        if start <= acquired <= end:
            EmployeeImprovements(b["empID"]["value"], b["empName"]["value"], b["occupation"]["value"])
            SkillImprovements(b["skillID"]["value"], b["skillName"]["value"])

    if Improvement.has_elements():
        return jsonify({'data': Improvement.get_all_improvements()})
    else:
        return jsonify({'data': []})
