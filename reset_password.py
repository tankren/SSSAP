import pyrfc
import random
import string
import getpass
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/reset_password', methods=['POST','OPTIONS'])
def reset_password():
    print('输入的用户名为：' + request.form['username'])
    username = request.form['username']
    
	# 判断用户名和电脑登录名是否一致
    #if username != getpass.getuser():
    #    return jsonify({'error': '用户名和电脑登录名不一致！'})

    # 生成随机密码
    new_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    print(new_password)
    # SAP连接参数
    conn_params = {
        'user': 'rec3wx',
        'passwd': 'Birth890112!',
        'ashost': '10.0.0.234',
        'sysid':'ER1',
        'sysnr': '00',
        'client': '800',
    }

    # 创建SAP连接
    conn = pyrfc.Connection(**conn_params)

    # Unlock user
    conn.call("BAPI_USER_UNLOCK", USERNAME=username)
    
    password = {"BAPIPWD": new_password}
    passowrdx = {"BAPIPWD": "X"}
    # 调用BAPI_USER_CHANGE_PASSWORD函数修改密码
    result = conn.call("BAPI_USER_CHANGE", USERNAME=username, PASSWORD=password, PASSWORDX=passowrdx)
    print(result["RETURN"])
    # 关闭连接
    conn.close()

    # 判断重置密码是否成功
    if result['RETURN'][0]['TYPE'] == 'E':
        # 如果重置失败，返回一个包含错误信息的json
        return jsonify({'error': result['RETURN'][0]['MESSAGE']})
    else:
        # 如果重置成功，返回新密码的json
        return jsonify({'new_password': new_password})

if __name__ == '__main__':
    app.run(debug=True)
