import replit
import base64


db_url = 'https://kv.replit.com/v0/eyJhbGciOiJIUzUxMiIsImlzcyI6ImNvbm1hbiIsImtpZCI6InByb2Q6MSIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb25tYW4iLCJleHAiOjE2NDU3ODE5MzksImlhdCI6MTY0NTY3MDMzOSwiZGF0YWJhc2VfaWQiOiJhY2ZlN2RhOC04MzBjLTQ1YmUtODJkYy05MjgxYzJhNTY4YjMifQ.UQ8V6r1132qA0Fym0mK6-EfkmueCAas0t7TGF4XxetiCGqp28nmpaelh8ySEIx5F1IFWugsb5U--htGfh_WOPA'
db = replit.Database(db_url)


def add_message(text, file=None):
    file_name = file
    with open(file, 'rb') as f:
        file_data = base64.b64encode(f.read()).decode("ASCII")

    if file:
        msg = [text, file_name, file_data]
    else:
        msg = [text, None, None]

    db['test'] = [msg]
