

class Improvement(object):

    IMPROVEMENTS = []

    def __init__(self, uuid, name):
        self.improvements = 1
        self.uuid = uuid
        self.name = name
        if not self.contains_improvement(uuid):
            Improvement.IMPROVEMENTS.append(self)

    def increment_improvements(self):
        self.improvements += 1

    @classmethod
    def contains_improvement(cls, uuid):
        for i in cls.IMPROVEMENTS:
            if i.uuid == uuid:
                i.increment_improvements()
                return True
        return False

    @classmethod
    def get_all_improvements(cls):
        data = []
        for i in cls.IMPROVEMENTS:
            data.append(i.convert_json())
        cls.IMPROVEMENTS = []
        return data

    @classmethod
    def has_elements(cls):
        return len(cls.IMPROVEMENTS) != 0


class EmployeeImprovements(Improvement):

    def __init__(self, uuid, name, occupation):
        super(EmployeeImprovements, self).__init__(uuid, name)
        self.occupation = occupation

    def convert_json(self):
        return {
            "type": "EmployeeImprovements",
            "id": self.uuid,
            "attributes": {
                "name": self.name,
                "count": self.improvements,
                "occupation": self.occupation
            }
        }


class SkillImprovements(Improvement):

    def __init__(self, uuid, name):
        super(SkillImprovements, self).__init__(uuid, name)

    def convert_json(self):
        return {
            "type": "SkillImprovements",
            "id": self.uuid,
            "attributes": {
                "name": self.name,
                "count": self.improvements
            }
        }


