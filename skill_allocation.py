from flask import jsonify, request
from prefixes import prefixes

# get employee suggestions


@app.route('/employee_sugestions/')
def employee_sugestions():
    helpers.log("employee sugestions")
    skillId = request.args.get("id")
    helpers.log(skillId)
    q = prefixes + """
    SELECT distinct ?name ?uuid
    WHERE{
        ?skill mu:uuid "%s".
        ?skill skos:prefLabel ?l.
        ?employee default:hasSkill/esco:hasSkill ?skill.
        ?employee foaf:name ?name; mu:uuid ?uuid.
    }
        """ % skillId

    result = helpers.query(q)
    bindings = result["results"]["bindings"]
    data = []
    for b in bindings:
        data.append({
            "type": "employees",
            "id": b["uuid"]["value"],
            "attributes": {
                "name": b["name"]["value"],
            }
        })
    return jsonify({'data': data})
