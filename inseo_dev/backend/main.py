from flask import Flask, request
import pymysql
from datetime import datetime

def get_connection():
    return pymysql.connect(
        host='database-1.cts2qeeg0ot5.ap-northeast-2.rds.amazonaws.com',
        user='kevin',
        password='spreatics*',
        db='temperature_inseo',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

app = Flask(__name__)

# 상태 정보 전달하기
@app.route('/status', methods=['POST'])
def status():
    data = request.get_json(silent=True) or {}
    temperature = data.get('temperature')
    fan = data.get('fan')
    heater = data.get('heater')

    if temperature is None or fan is None or heater is None:
        return {"status":"failed", "reason":"Temperature, fan, and heater are required inputs."}
    
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            insert_sql = """
            INSERT INTO status (temperature, fan, heater) 
                values (%s, %s, %s)
            """
            cursor.execute(insert_sql, (temperature, fan, heater))
            conn.commit()

            search_sql = """
            SELECT *
            FROM status
            """
            cursor.execute(search_sql)
            row = cursor.fetchone()
            return {"status": "success", "info": row}

    except pymysql.err.IntegrityError as e:
        return { "status": "failed", "reason": str(e) }
        
# 아두이노가 설정된 온도 가져가기
@app.route('/setting', methods=['GET'])
def get_temperature():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            search_sql = """
            SELECT *
            FROM setting
            """
            cursor.execute(search_sql)
            row = cursor.fetchone()
            return {"status": "success", "input_temperature": row["temperature"]}

    except pymysql.err.IntegrityError as e:
        return { "status": "failed", "reason": str(e) }

# 사용자가 온도 설정하기
@app.route('/setting', methods=['POST'])
def setting_temperature():
    data = request.get_json(silent=True) or {}
    temperature = data.get('temperature')

    if not temperature:
        return {"status":"failed", "reason":"Temperature is required input."}
    
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            update_sql = """
            UPDATE setting
            SET temperature = %s
            WHERE setting_id = 1
            """
            cursor.execute(update_sql, (temperature, ))
            conn.commit()

            search_sql = """
            SELECT *
            FROM setting
            """
            cursor.execute(search_sql)
            row = cursor.fetchone()
            return {"status": "success", "input_temperature": row}

    except pymysql.err.IntegrityError as e:
        return { "status": "failed", "reason": str(e) }

app.run(debug=True, host='0.0.0.0', port=5000)