from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import random

class Timeline:

    def __init__(self):
        self.elements = []

    def has_elements(self):
        return not (len(self.elements) == 0)

    def add_element(self, element):
        self.elements.append(element)

    def createTimeLine(self):
        endtimes = []
        starttimes = []
        for e in self.elements:
            if e.acquired < e.start:
                starttimes.append(e.start)
            else:
                starttimes.append(e.acquired)
            endtimes.append(e.stop)

        start = min(starttimes)
        stop = max(endtimes)

        tlid = helpers.generate_uuid()
        data = {
                "type": "timelines",
                "id": tlid,
                "attributes": {
                    "start": start.isoformat(),
                    "end": stop.isoformat()
                },
                "relationships": {
                    "measurements": {
                        "data": [

                        ]
                    }
                }
            }
        included = []
        while start <= stop:
            count = 0
            for e in self.elements:
                if e.is_active_skill_on(start): count += 1
            mId = helpers.generate_uuid()
            m = Measurement(start, count, tlid, mId)
            included.append(m.jsonify())
            data["relationships"]["measurements"]["data"].append({"type": "measurements", "id": mId})
            start = start + relativedelta(weeks=1)
        return {"data": data, "included": included}


class TimelineElement:

    def __init__(self, acquired, start, stop):
        self.acquired = parse(acquired)
        self.start = parse(start)
        self.stop = parse(stop)

    def is_active_skill_on(self, theDate):
        return theDate >= self.acquired and self.start <= theDate <= self.stop


class Measurement:

    def __init__(self, date, value, tlId, mId):
        self.date = date
        self.value = value
        self.measurementId = mId
        self.timelineId = tlId

    def jsonify(self):
        return {
                "type": "measurements",
                "id": self.measurementId,
                "attributes": {
                    "date": self.date,
                    "value": self.value
                },
                "relations": {
                    "part-of": {
                        "data": {
                            "type": "timelines",
                            "id": self.timelineId
                        }
                    }
                }
            }
