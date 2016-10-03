from flask import jsonify


# get employee suggestions


@app.route('/employee_sugestions/')
def employee_sugestions():
    helpers.log("employee sugestions")
    q = """
        prefix foaf: <http://xmlns.com/foaf/spec/>
        prefix mu:  <http://mu.semte.ch/vocabularies/core/>
        prefix skos: <http://www.w3.org/2004/02/skos/core#>
        prefix default: <http://example.org/MyCompany/>

        SELECT distinct ?name ?uuid
        WHERE{
          ?skill mu:uuid "ccd0a1d9-afda-43d9-b901-96344886e14d".
          ?skill skos:prefLabel ?l.
          ?employee default:hasSkill/esco:hasSkill ?skill.
          ?employee foaf:name ?name; mu:uuid ?uuid.
        }
    """

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
