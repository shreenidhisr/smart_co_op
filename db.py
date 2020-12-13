import pymysql

db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Sd@8050102193",
    db="co_op",
    autocommit=True,
)

cur = db.cursor()


cur.execute(
    "insert into waiting(name,email,password,mobile,aadhar,wait) values(%s,%s,%s,%s,%s,%s)",
    ("name", "email", 123456789, 9886175422, 172459186159856, 1),
)
