### imports ###
from wave_app import db

### models for tables used in database along with CSV api ###
class TimeReportEntry(db.Model):
    """_summary_

    Args:
        db (_type_): _description_
    """
    _id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    hours_worked = db.Column(db.Float)
    employee_id = db.Column(db.Integer)
    job_group = db.Column(db.String)
    report_number = db.Column(db.Integer) # added this in for easier queries for specific time report archives

class Employee(db.Model):
    """Employee ID and Job Group Table 

    Args:
        db (_type_): _description_
    """
    employee_id = db.Column(db.Integer, primary_key=True)
    job_group = db.Column(db.String)
    
class Job(db.Model):
    """Job Group and Wage Table

    Args:
        db (_type_): _description_
    """
    job_group = db.Column(db.String, primary_key=True)
    wage = db.Column(db.Float)
    
class ReportDocument(db.Model):
    """Report ID Table

    Args:
        db (_type_): _description_
    """
    report_index = db.Column(db.Integer, primary_key=True)

### creating tabless ###
db.create_all()

### adding job groups and wages to job's table ###
job_group_a = Job(job_group='A',wage=20)
job_group_b = Job(job_group='B',wage=30)
for group in [job_group_a,job_group_b]:
    q = db.session.query(Job.job_group).filter(Job.job_group==group.job_group)
    exists = db.session.query(q.exists()).scalar() 
    if not exists:  
        db.session.add(group)
        db.session.commit()