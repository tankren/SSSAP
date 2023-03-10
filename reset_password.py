import pyrfc
from pyrfc._exception import LogonError
import string
import secrets
import getpass
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route("/reset_password", methods=["POST"])
def reset_password():
    username = request.form["username"]
    SAPsystem = request.form["system"]

    
    # 生成随机密码
    letters = string.ascii_letters
    uppercases = string.ascii_uppercase
    digits = string.digits
    special_chars = string.punctuation
    alphabet = uppercases + letters + digits + special_chars
    pwd_length = 15
    new_password = ""
    for i in range(pwd_length):
        new_password += "".join(secrets.choice(alphabet))

    # 判断用户名和电脑登录名是否一致
    if username != getpass.getuser():
        return jsonify({'error': 'SAP用户名和电脑NT登录名不一致，不允许操作！'})

    # SAP连接参数
    conn_params = {
        "user": "RFC_SAPUM",
        "passwd": base64.b64decode("bjJdYnB3UHlQSzNbM0gj").decode("utf-8"),
        "ashost": f"epsosap{SAPsystem[0:3]}.vh.lan",
        "sysid": f"{SAPsystem[0:2]}",
        "sysnr": "00",
        "client": "011",
    }

    # 创建SAP连接
    conn = pyrfc.Connection(**conn_params)

    # Unlock user
    try:
        conn.call("BAPI_USER_UNLOCK", USERNAME=username)
    except LogonError:
        print("ERROR! Logon error for host") 
    except Exception as ex:
        conn.close()
        return jsonify({"error": "RFC通讯异常，请联系ICO！"})

    # 调用BAPI_USER_CHANGE函数修改密码
    password = {"BAPIPWD": new_password}
    passowrdx = {"BAPIPWD": "X"}
    try:
        result = conn.call(
            "BAPI_USER_CHANGE",
            USERNAME=username,
            PASSWORD=password,
            PASSWORDX=passowrdx,
        )
    except Exception as ex:
        conn.close()
        return jsonify({"error": "RFC通讯异常，请联系ICO！"})

    # 关闭连接
    conn.close()

    # 判断重置密码是否成功

    if result["RETURN"][0]["TYPE"] == "E":
        # 如果重置失败，返回一个包含错误信息的json
        return jsonify({"error": result["RETURN"][0]["MESSAGE"]})
    else:
        # 如果重置成功，返回新密码的json
        return jsonify({"new_password": new_password})


if __name__ == "__main__":
    app.run(host = '0.0.0.0', debug=True)
