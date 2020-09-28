from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request, redirect, flash, url_for, session
from datetime import timedelta
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = "cynic255"
bootstrap = Bootstrap(app)

#database connection
conn = pymysql.connect(host="127.0.0.1", user="root", port=3306,
                       password="lolicon05", database="warehouse", charset="utf8")
cur = conn.cursor()


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('id')
        user_pw = request.form.get('pw')
        # 判断用户输入

        sql = "SELECT admin_id , password FROM admin"
        cur.execute(sql)
        admin_tuple = cur.fetchall()

        # 循环查找判断 输入正确跳转homepage.html 错误重定向login.html
        for each_admin in admin_tuple:
            if each_admin[0] == str(user_id) and each_admin[1] == str(user_pw):
                flash("Welcome , Admin.")
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=10)
                session['flag'] = True
                return redirect(url_for('home'))
            else:
                flash("Login failure.")
                return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/home')
def home():
    if session.get('flag'):
        return render_template('homepage.html')
    else:
        return redirect(url_for('login'))


@app.route('/goods')
def goods_detail():
    if session.get('flag'):
        sql = "SELECT * FROM warehouse"
        try:
            cur.execute(sql)
            goods = cur.fetchall()
            return render_template('goods.html', goods=goods)
        except Exception as e:
            flash('查询出错')
            redirect(url_for('goods_detail'))
            raise e
    else:
        return redirect(url_for('login'))


@app.route('/admin_control', methods=['POST', 'GET'])
def admin():
    if session.get('flag'):
        # 用户进行注册 提交post请求至后台
        if request.method == 'POST':

            input_id = request.form.get('new_id')
            input_pw = request.form.get('new_pw')
            input_tel = request.form.get('new_tel')
            input_jn = request.form.get('new_jn')

            # judge field if is empty
            if not input_id or not input_pw or not input_tel or not input_jn:
                flash('Invaild input')
                return redirect(url_for('admin'))
            else:
                insert_sql = "INSERT INTO admin(admin_id,password,tel,job_num) VALUES (%s,%s,%s,%s)"
                value = (input_id, input_pw, input_tel, input_jn)
                try:
                    cur.execute(insert_sql, value)
                    conn.commit()
                    flash('Register Success.')
                    return redirect(url_for('admin'))
                except:
                    flash('Register Fail.')
                    return redirect(url_for('admin'))
        else:
            sql = "select * from admin"
            try:
                cur.execute(sql)
                results = cur.fetchall()
            except Exception as e:
                raise e
            return render_template('admin_page.html', admin_info=results)
    else:
        return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    render_template('404.html')


@app.route('/goods_edit', methods=['POST', 'GET'])
def edit():
    if session.get('flag'):
        # 验证登录成功
        if request.method == 'POST':
            # 确认用户进行查询操作 显示相应内容
            start_time = request.form.get('input_stime', type=str)
            end_time = request.form.get('input_etime', type=str)

            search_goods = "SELECT * FROM warehouse WHERE enter_time >= %s AND enter_time <= %s "
            value = (start_time, end_time)

            try:
                cur.execute(search_goods, value)
                results = cur.fetchall()
                flash("Here is the result")
                return render_template('goods_edit.html', goods=results)
            except:
                flash("Unknown Exception")
                return redirect(url_for('edit'))
        else:  # 用户未进行查询操作 显示列表
            all_goods = "SELECT * FROM warehouse"

            try:
                cur.execute(all_goods)
                results = cur.fetchall()
                return render_template('goods_edit.html', goods=results)
            except:
                return redirect(url_for('edit'))
    else:
        return redirect(url_for('login'))


@app.route('/append', methods=['POST', 'GET'])
def append():
    if request.method == 'POST':
        new_id = request.form.get('new_goods_id', type=int)
        new_name = request.form.get('new_goods_name')
        new_time = request.form.get('new_enter_time')
        new_amount = request.form.get('new_goods_amount', type=int)
        new_catagory = request.form.get('new_goods_cata')

        append_sql = "INSERT INTO warehouse VALUES (%d,'%s','%s',%d)" % (
            new_id, new_name, new_time, new_amount)
        append_cata_sql = "INSERT INTO classification VALUES (%d,'%s')" % (
            new_id, new_catagory)

        try:
            cur.execute(append_sql)
            cur.execute(append_cata_sql)
            conn.commit()
            flash("新商品添加成功.")
            return redirect(url_for('goods_detail'))
        except:
            flash("添加失败，请核对填写信息.")
            return redirect(url_for('append'))
    else:
        return render_template('append.html')


@app.route('/edit', methods=['POST', 'GET'])
def goods_edit():
    if request.method == 'POST':
        id = request.form.get('edit_goods_id', type=int)
        edit_amount = request.form.get('edit_goods_amount', type=int)

        edit_sql = "UPDATE warehouse SET amount = %d WHERE id = %d" % (
            edit_amount, id)

        try:
            cur.execute(edit_sql)
            conn.commit()
            flash("数量修改成功.")
            return redirect(url_for('goods_detail'))
        except:
            flash("修改失败，请检查录入数据")
            return redirect(url_for('goods_edit'))
    else:
        return render_template('edit.html')


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        delete_id = request.form.get('delete_goods_id', type=int)

        disable_fk = "SET FOREIGN_KEY_CHECKS=0"
        delete_goods = "DELETE FROM warehouse WHERE id = %d" % (delete_id)
        delete_rel = "DELETE FROM classification WHERE item_id = %d" % (delete_id)

        try:
            cur.execute(disable_fk)
            cur.execute(delete_goods)
            cur.execute(delete_rel)
            conn.commit()
            flash("商品删除成功")
            return redirect(url_for('goods_detail'))
        except:
            flash("删除失败，请确认id.")
            return redirect(url_for('delete'))
    else:
        return render_template('delete.html')


if __name__ == "__main__":
    app.run(debug=True)
