class Voter:
  def __init__(self, name, sms_number):
    self.name = name
    self.sms_number = sms_number

  def __str__(self):
    return f"{self.name})"
  
  def toJSON(self):
    return {
        'name': self.name,
        'sms_number': self.sms_number
    }