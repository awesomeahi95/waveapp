### library imports + app/db imports ###
from wave_app import app, db
from wave_app.models import ReportDocument, TimeReportEntry, Employee, Job
import io
from flask import request
import csv
import re
from datetime import datetime

### post method to upload time report CSV files to sqlite database ###    
@app.route('/uploadCSV', methods=['POST'])
def upload_csv():
    """method to upload CSV file

    Returns:
        _type_: _description_
    """
    f = request.files['File']
    # checking for indexes in file report names so a duplicate entry is not uploaded to database
    file_index = re.findall(r'\d+',str(f))[0]
    index = ReportDocument(report_index = file_index)
    q = db.session.query(ReportDocument.report_index).filter(ReportDocument.report_index==file_index)
    exists = db.session.query(q.exists()).scalar() 
    # reading and adding time report data from CSV to sqlite database
    if not exists:
        data = f.stream.read() # This line uses the same variable and worked fine #Convert the FileStorage to list of lists here.
        stream = io.StringIO(data.decode("UTF8"), newline=None)
        reader = csv.reader(stream)
        next(reader)
        for row in reader:
            date_python = datetime.strptime(row[0], "%d/%m/%Y")
            
            q = db.session.query(Employee.employee_id).filter(Employee.employee_id==row[2])
            exists = db.session.query(q.exists()).scalar()
            
            if (not exists):
                employee_entry = Employee(employee_id=row[2], job_group=row[3])
                db.session.add(employee_entry)
                db.session.commit()
                          
            time_report_entry = TimeReportEntry(date=date_python,hours_worked=row[1],employee_id=row[2],job_group=row[3],report_number=file_index)
        
            db.session.add(time_report_entry)
            db.session.commit()
        db.session.add(index)
        db.session.commit()
        return 'Successfully Uploaded'
    else:
        return 'Time Report Entry Previously Submitted, Please Try Another File'

### get method to retrieve a report detailing how much each employee should be paid in each pay period ###
@app.route('/getEmployeePay', methods=['GET'])
def get_employee_pay():
    # sql query to get employees' pay report
    result = db.session.execute(
        """SELECT 
            employee_id,
            pay_period_start,
            pay_period_end,
            total_hours * wage AS total_wage
        FROM   ((SELECT date,
                        Strftime('%Y-%m-01', date) AS pay_period_start,
                        Strftime('%Y-%m-15', date) AS pay_period_end,
                        employee_id,
                        Sum(hours_worked)          AS total_hours,
                        job_group
                FROM   time_report_entry
                WHERE  date BETWEEN pay_period_start AND pay_period_end
                GROUP  BY pay_period_start,
                        employee_id
                UNION
                SELECT date,
                        Strftime('%Y-%m-16', date) AS pay_period_start,
                        Strftime('%Y-%m-31', date) AS pay_period_end,
                        employee_id,
                        Sum(hours_worked)          AS total_hours,
                        job_group
                FROM   time_report_entry
                WHERE  date BETWEEN pay_period_start AND pay_period_end
                GROUP  BY pay_period_start,
                        employee_id)) AS report_summary
            JOIN job
                ON report_summary.job_group = job.job_group
        ORDER  BY employee_id,
                pay_period_start""")
    
    # returning employee report in JSON
    employeeReports=[]
    for row in result:
        employeeReports.append({'employeeId':row['employee_id'],
                                'payPeriod':{'startDate':row["pay_period_start"],
                                             'endDate':row["pay_period_end"]},
                                'amountPaid':row["total_wage"]})  
    payrollReport = {'payrollReport' : {'employeeReports':employeeReports}}
    
    return payrollReport           