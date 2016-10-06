from datetime import datetime
from flask import request, jsonify
from timeline import *
from improvement import *
from skill_allocation import *
from prefixes import prefixes

@app.route('/timeline/')
def get_skill_timeline():
    """Selects all employees with the given skill that are active at the company."""
    today = datetime.today().date()
    skillURI = str("http://data.europa.eu/esco/skill/" + request.args.get("skillid"))

    q = prefixes + """
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

@app.route('/skills/')
def all_skills():
    q = prefixes + """
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
    return jsonify(jobj)


@app.route('/bubble/')
def local_bubble():
    date = request.args.get("date")
    date = datetime.strptime(date, "%Y-%m-%d").date()

    q = prefixes + """
        SELECT (str(?skillName) as ?skillName) ?skillID (count(?skillemp) as ?count)
        WHERE{
          ?employee default:function ?function.
          ?function esco:hasOccupation ?occ.
          ?occ skos:prefLabel ?occN.

          ?employee default:hasSkill ?skillemp.
          ?skillemp esco:hasSkill ?skill.
          ?skill mu:uuid ?skillID.
          ?skill skos:prefLabel ?skillName.

          ?skillemp default:acquired ?aDate.
          ?function default:startDate ?sDate.

          FILTER(?aDate < %s)
          FILTER(%s > ?sDate)
        } group by ?skillName ?skillID
    """ % (sparql_escape(date), sparql_escape(date))
    res = helpers.query(q)
    data = res["results"]["bindings"]
    jobj = {"data": []}
    for e in data:
        jobj["data"].append({
            "attributes": {
                "name": e["skillName"]["value"],
                "count": e["count"]["value"]
            },
            "id": e["skillID"]["value"],
            "type": "counts"
        })
    return jsonify(jobj)


@app.route('/occupations/')
def get_all_occupations():
    q = prefixes + """
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
    return jsonify(jobj)


@app.route('/improvements/')
def get_inprovement():
    today = datetime.today().date()

    q = prefixes + """
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
