from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
import requests
import msal
import logging
from config import BaseConfig
from datetime import timedelta,datetime,timezone
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import schedule
import time
from threading import Thread
import os
import secrets

app = Flask(__name__, static_folder='static')
CORS(app)
app.config.from_object(BaseConfig)
app.secret_key = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SESSION_TYPE'] = 'sqlalchemy'
db = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db
Session(app)

# 设置全局日志级别

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('msal').setLevel(logging.WARNING)
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.debug("Logging is configured.")

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expiration = db.Column(db.DateTime, nullable=False)

class Report(db.Model):

    __tablename__ = 'Reports'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.String(100), nullable=False)
    report_id = db.Column(db.String(100), nullable=False)
    dataset_id = db.Column(db.String(100), nullable=False)
    refresh_frequency = db.Column(db.String(100))
    refresh_frequency_value = db.Column(db.Integer, nullable=False)
    refresh_frequency_unit = db.Column(db.String(10), nullable=False)
    icon_path = db.Column(db.String(200), nullable=False)

class Setting(db.Model):
    __tablename__ = 'Settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(500), nullable=False)

class Permission(db.Model):
    __tablename__ = 'Permissions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    addButton = db.Column(db.String(3), nullable=False)
    editButton = db.Column(db.String(3), nullable=False)
    manageButton = db.Column(db.String(3), nullable=False)
    publishButton = db.Column(db.String(3), nullable=False)

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workday_id = db.Column(db.String(100), nullable=False)
    employee_chi_name = db.Column(db.String(100), nullable=False)
    employee_last_name = db.Column(db.String(100), nullable=False)
    employee_first_name = db.Column(db.String(100), nullable=False)
    work_email = db.Column(db.String(100), nullable=False)
    ntid = db.Column(db.String(100), nullable=False)
    employee_workcell = db.Column(db.String(100), nullable=False)
    department_name = db.Column(db.String(100), nullable=False)
    direct_manager = db.Column(db.String(100), nullable=False)
    direct_manager_wdid = db.Column(db.String(100), nullable=False)
    direct_manager_email = db.Column(db.String(100), nullable=False)
    direct_manager_ntid = db.Column(db.String(100), nullable=False)
    company_code = db.Column(db.String(100), nullable=False)
    company_location = db.Column(db.String(100), nullable=False)
    job_family_group = db.Column(db.String(100), nullable=False)
    business_title = db.Column(db.String(100), nullable=False)
    cost_center_id = db.Column(db.String(100), nullable=False)
    global_job_title = db.Column(db.String(100), nullable=False)
    employee_nationality = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

class TokenCache:
    def __init__(self):
        self.token = None
        self.expiration_time = None

    def get_token(self):
        if self.token and self.expiration_time > time.time():
            return self.token
        else:
            self.token = self.refresh_token()
            self.expiration_time = time.time() + 3600
            return self.token

    def refresh_token(self):
        tenant_id = app.config.get('TENANT_ID')
        client_id = app.config.get('CLIENT_ID')
        client_secret = app.config.get('CLIENT_SECRET')

        authority = f"https://login.microsoftonline.com/{tenant_id}"
        client_app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )
        result = client_app.acquire_token_for_client(scopes=app.config['SCOPE_BASE'])
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Failed to obtain access token: {result.get('error')}, {result.get('error_description')}")

token_cache = TokenCache()

def get_setting(key):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else None

config_loaded = False

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.before_request
def ensure_logged_in():
    if 'user_email' not in session and request.endpoint not in ['login', 'static']:
        return redirect(url_for('login'))
    
    if 'user_email' in session:
        # 用户已登录，检查是否已记录登录信息
        if not session.get('logged_in_logged'):
            user_email = session['user_email']
            logging.info(f'用户 {user_email} 已自动登录')
            session['logged_in_logged'] = True

    # 记录用户身份信息
#     user_email = session.get('user_email', 'Anonymous')
#     logging.info(f'User: {user_email}, Endpoint: {request.endpoint}, Method: {request.method}')

#     log_user_activity(user_email, request.endpoint)

# def log_user_activity(user_email, endpoint):
#     log_entry = f'User: {user_email}, Endpoint: {endpoint}, Time: {datetime.now()}\n'
#     with open('iis_custom.log', 'a') as log_file:
#         log_file.write(log_entry)

@app.before_request
def load_config_from_db():
    global config_loaded
    if not config_loaded:
        app.config['TENANT_ID'] = get_setting('TENANT_ID')
        app.config['CLIENT_ID'] = get_setting('CLIENT_ID')
        app.config['CLIENT_SECRET'] = get_setting('CLIENT_SECRET')
        config_loaded = True

def refresh_dataset(dataset_id, group_id):
    try:
        access_token = token_cache.get_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        refresh_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes"
        response = requests.post(refresh_url, headers=headers)
        response.raise_for_status()
        #logging.info(f"刷新请求已发送: {dataset_id}")
    except Exception as e:
        logging.error(f"刷新请求失败: {e}")

def schedule_refresh(report):
    interval = report.refresh_frequency_value
    unit = report.refresh_frequency_unit
    logging.info(f"计划刷新报告: {report.name}, Interval: {interval}, Unit: {unit}")
    
    if unit == "minutes":
        schedule.every(interval).minutes.do(refresh_dataset, dataset_id=report.dataset_id, group_id=report.group_id)
    elif unit == "hours":
        schedule.every(interval).hours.do(refresh_dataset, dataset_id=report.dataset_id, group_id=report.group_id)
    elif unit == "days":
        schedule.every(interval).days.do(refresh_dataset, dataset_id=report.dataset_id, group_id=report.group_id)
    else:
        logging.warning(f"Unsupported time unit: {unit} for report: {report.name}")

def load_scheduled_refreshes():
    reports = Report.query.all()
    for report in reports:
        schedule_refresh(report)
    logging.info("根据数据库配置安排所有刷新.")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# 清理过期会话的函数
def clear_expired_sessions():
    with app.app_context():
        now = datetime.now(timezone.utc)
        
        # 记录当前时间到日志
        logging.info(f"当前时间: {now.isoformat()}")
        
        expired_sessions = db.session.query(Session).filter(Session.expiration < now).all()
        
        for session in expired_sessions:
            db.session.delete(session)
        
        db.session.commit()
        logging.info(f"清理了 {len(expired_sessions)} 个过期会话。")

def schedule_session_cleanup():
    schedule.every(1).hours.do(clear_expired_sessions)

@app.route('/')
def root():
    if 'user' not in session or session.get('user_email') == "Unknown":
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/Home')
def home():
    user_email = session.get('user_email', "Unknown")
    user_id = session.get('user_id')  # 获取用户 ID
    logging.info(f'User {user_email} accessed the home page.')
    if user_email == "Unknown":
        return redirect(url_for('login'))
    reports = Report.query.limit(1000).all()
    client_id = get_setting('CLIENT_ID')
    tenant_id = get_setting('TENANT_ID')
    return render_template('home.html', reports=reports, client_id=client_id, tenant_id=tenant_id, user_email=user_email, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ntid = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(ntid=ntid).first()
        if user:
            if user.password == password:
                user_display = user.work_email.split('@')[0].replace('_', ' ').title()
                session['user_email'] = user_display
                session['work_email'] = user.work_email
                session['user_id'] = user.id

                # 记录登录信息
                logging.info(f"用户 {user_display} 登录成功，时间: {datetime.now().isoformat()}, IP: {request.remote_addr}")

                return redirect(url_for('home'))
        
            else:
                flash('密码错误')
                return render_template('login.html')
        else:
            try:
                response = requests.get(
                    'User account verification API URL', #替换为用户验证的API URL
                    params={'ntid': ntid}
                )
                response.raise_for_status()
                user_data = response.json()

                if user_data.get('success', False):
                    employee_data = user_data.get('data', {}).get('data', [])
                    if employee_data:
                        user_info = employee_data[0]
                        user_display = user_info.get('work_email', '').split('@')[0].replace('_', ' ').title()
                        session['user_email'] = user_display
                        session['work_email'] = user_info.get('work_email', '')
                        session['user_id'] = user_info.get('id', None)
                        logging.info(f"用户 {user_display} 登录成功，时间: {datetime.now().isoformat()}, IP: {request.remote_addr}")
                        return redirect(url_for('home'))
                    else:
                        flash('用户不存在')
                        return render_template('login.html')
                else:
                    flash('用户不存在')
                    return render_template('login.html')
            except Exception as e:
                #logging.error(f"Failed to get user email: {e}")
                flash('API验证失败')
                return render_template('login.html')
    return render_template('login.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    ntid = data.get('username')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    user = User.query.filter_by(ntid=ntid).first()
    if user:
        if user.password == current_password:
            user.password = new_password
            db.session.commit()
            return jsonify({"success": True, "message": "密码修改成功"})
        else:
            return jsonify({"success": False, "message": "当前密码错误"})
    else:
        try:
            response = requests.get(
                'User account verification API URL', #替换为用户验证的API URL
                params={'ntid': ntid}
            )
            response.raise_for_status()
            user_data = response.json()

            if user_data.get('success', False):
                employee_data = user_data.get('data', {}).get('data', [])
                if employee_data:
                    user_info = employee_data[0]
                    new_user = User(
                        ntid=ntid,
                        password=new_password,
                        workday_id=user_info.get('workday_id', ''),
                        employee_chi_name=user_info.get('employee_chi_name', ''),
                        employee_last_name=user_info.get('employee_last_name', ''),
                        employee_first_name=user_info.get('employee_first_name', ''),
                        work_email=user_info.get('work_email', ''),
                        employee_workcell=user_info.get('employee_workcell', ''),
                        department_name=user_info.get('department_name', ''),
                        direct_manager=user_info.get('direct_manager', ''),
                        direct_manager_wdid=user_info.get('direct_manager_wdid', ''),
                        direct_manager_email=user_info.get('direct_manager_email', ''),
                        direct_manager_ntid=user_info.get('direct_manager_ntid', ''),
                        company_code=user_info.get('company_code', ''),
                        company_location=user_info.get('company_location', ''),
                        job_family_group=user_info.get('job_family_group', ''),
                        business_title=user_info.get('business_title', ''),
                        cost_center_id=user_info.get('cost_center_id', ''),
                        global_job_title=user_info.get('global_job_title', ''),
                        employee_nationality=user_info.get('employee_nationality', '')
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    return jsonify({"success": True, "message": "密码修改成功"})
                else:
                    return jsonify({"success": False, "message": "用户不存在"})
            else:
                return jsonify({"success": False, "message": user_data.get('msg')})

        except Exception as e:
            #logging.error(f"Failed to verify user: {e}")
            return jsonify({"success": False, "message": "用户验证失败"})
        
@app.route('/logout')
def logout():
    session.clear()
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/get_icons')
def get_icons():
    icon_folder = os.path.join(app.root_path, 'static', 'Icon')
    icons = [f for f in os.listdir(icon_folder) if f.endswith('.png')]
    sort_order = []  # Customize your sort order if necessary
    icons_sorted = sorted(icons, key=lambda x: sort_order.index(x) if x in sort_order else len(sort_order))
    return jsonify(icons_sorted)

@app.route('/report', methods=['GET'])
def report_redirect():
    group_id = request.args.get('group_id')
    report_id = request.args.get('report_id')
    if not group_id or not report_id:
        return "缺少报表 ID 或工作区 ID", 400
    return redirect(url_for('report', report_id=report_id, group_id=group_id))

@app.route('/report/<string:report_id>', methods=['GET'])
def report(report_id):
    group_id = request.args.get('group_id')
    if not group_id:
        return "缺少工作区 ID", 400

    report = Report.query.filter_by(group_id=group_id, report_id=report_id).first()
    if not report:
        return "报表未找到", 404

    return render_template('report.html', report_name=report.name, group_id=group_id, report_id=report_id)

@app.route('/get_dataset_id', methods=['POST'])
def get_dataset_id():
    try:
        data = request.json
        group_id = data.get('group_id')
        report_id = data.get('report_id')

        if not group_id or not report_id:
            return jsonify({"success": False, "message": "缺少必要的参数"}), 400

        access_token = token_cache.get_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        api_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}?$select=datasetId"
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            report_data = response.json()
            dataset_id = report_data.get("datasetId")
            return jsonify({"success": True, "dataset_id": dataset_id})
        else:
            response.raise_for_status()
    except Exception as e:
        #logging.error("获取数据集ID失败: %s", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/embed_info', methods=['POST'])
def get_embed_info():
    try:
        data = request.json
        report_id = data.get('report_id')
        group_id = data.get('group_id')
        
        if not report_id or not group_id:
            return "缺少报表 ID 或工作区 ID", 400
        
        access_token = token_cache.get_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/GenerateToken"
        payload = {"accessLevel": "View"}

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        embed_token_response = response.json()
        
        if 'token' not in embed_token_response:
            error_msg = f"Failed to obtain embed token: {embed_token_response}"
            raise Exception(error_msg)
        
        embed_info = {
            'embed_url': f"https://app.powerbi.com/reportEmbed?reportId={report_id}&groupId={group_id}",
            'embed_token': embed_token_response['token']
        }
        return jsonify(embed_info)
    except requests.exceptions.RequestException as e:
        #logging.error("HTTP 请求失败: %s", e)
        return str(e), 500
    except Exception as e:
        #logging.error("错误: %s", e)
        return str(e), 500

@app.route('/upload_report', methods=['POST'])
def upload_report():
    #if not session.get('can_add'):
    #    return jsonify({"success": False, "message": "权限不足"}), 403
    try:
        report_name = request.form.get('report_name')
        group_id = request.form.get('group_id')
        report_id = request.form.get('report_id')
        dataset_id = request.form.get('dataset_id')
        refresh_frequency_value = request.form.get('refresh_frequency_value')
        refresh_frequency_unit = request.form.get('refresh_frequency_unit')
        report_icon = request.form.get('report_icon')

        if not report_name or not group_id or not report_id or not dataset_id or not refresh_frequency_value or not refresh_frequency_unit or not report_icon:
            return jsonify({"success": False, "message": "缺少必要的参数"}), 400

        icon_path = os.path.join('Icon', report_icon).replace('\\', '/')

        new_report = Report(name=report_name, group_id=group_id, report_id=report_id, dataset_id=dataset_id,
                            refresh_frequency_value=int(refresh_frequency_value), refresh_frequency_unit=refresh_frequency_unit, 
                            icon_path=icon_path)
        db.session.add(new_report)
        db.session.commit()

        schedule_refresh(new_report)
        return jsonify({"success": True})
    except Exception as e:
        #logging.error("上传报表失败: %s", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/upload_setting', methods=['POST'])
def upload_setting():
    try:
        data = request.json
        key = data.get('key')
        value = data.get('value')

        if not key or not value:
            return jsonify({"success": False, "message": "缺少必要的参数"}), 400

        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            db.session.add(setting)
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        #logging.error("上传设置失败: %s", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_report/<string:report_id>', methods=['GET'])
def fetch_report(report_id):
    report = Report.query.get(report_id)
    if report:
        return jsonify({
            'id': report.id,
            'name': report.name,
            'group_id': report.group_id,
            'report_id': report.report_id,
            'dataset_id': report.dataset_id,
            'refresh_frequency_value': report.refresh_frequency_value,
            'refresh_frequency_unit': report.refresh_frequency_unit,
            'icon_path': report.icon_path
        })
    else:
        return jsonify({'success': False, 'message': '报表未找到'}), 404

@app.route('/update_report', methods=['POST'])
def update_report():
    try:
        report_id = request.form.get('report_id')
        report = Report.query.filter_by(id=report_id).first()
        if report:
            report.name = request.form.get('report_name')
            report.group_id = request.form.get('group_id')
            report.dataset_id = request.form.get('dataset_id')
            report.refresh_frequency_value = request.form.get('refresh_frequency_value')
            report.refresh_frequency_unit = request.form.get('refresh_frequency_unit')
            report.icon_path = os.path.join('Icon', request.form.get('report_icon')).replace('\\', '/')
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '报表未找到'}), 404
    except Exception as e:
        #logging.error('更新报表失败: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/refresh_dataset', methods=['POST'])
def refresh_dataset_api():
    data = request.json
    group_id = data.get('group_id')
    dataset_id = data.get('dataset_id')
    
    if not group_id or not dataset_id:
        return jsonify({"success": False, "message": "Group ID and Dataset ID are required"}), 400
    
    try:
        refresh_dataset(dataset_id=dataset_id, group_id=group_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_refresh_status', methods=['POST'])
def get_refresh_status():
    data = request.json
    group_id = data.get('group_id')
    dataset_id = data.get('dataset_id')
    
    if not group_id or not dataset_id:
        return jsonify({"success": False, "message": "Group ID and Dataset ID are required"}), 400
    
    try:
        access_token = token_cache.get_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        refresh_data = response.json().get('value', [])
        if refresh_data:
            latest_refresh = refresh_data[0]
            return jsonify({"success": True, "status": latest_refresh.get('status')})
        else:
            return jsonify({"success": True, "status": "No refresh history found"})
        
    except Exception as e:
        #logging.error(f"获取刷新状态失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/get_permissions', methods=['GET'])
def fetch_permissions():
    permissions = Permission.query.all()
    return jsonify([{
        'id': p.id, 
        'email': p.email, 
        'addButton': p.addButton, 
        'editButton': p.editButton, 
        'manageButton': p.manageButton, 
        'publishButton': p.publishButton
    } for p in permissions])
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/add_permission', methods=['POST'])
def add_permission():
    try:
        email = request.form.get('email')
        can_add = request.form.get('can_add')
        can_edit = request.form.get('can_edit')
        can_manage = request.form.get('can_manage')
        can_publish = request.form.get('can_publish')

        new_permission = Permission(
            email=email,
            addButton=can_add,
            editButton=can_edit,
            manageButton=can_manage,
            publishButton=can_publish
        )
        db.session.add(new_permission)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        #logging.error('添加权限失败: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/delete_permission/<int:id>', methods=['DELETE'])
def delete_permission(id):
    try:
        permission = Permission.query.get(id)
        if not permission:
            return jsonify({'success': False, 'message': '权限未找到'}), 404

        db.session.delete(permission)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        #logging.error(f'删除权限失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/check_permission', methods=['GET'])
def check_permission():
    work_email = session.get('work_email', "Unknown")
    if work_email == "Unknown":
        return jsonify({'has_permission': False})

    permission = Permission.query.filter(Permission.email.ilike(work_email)).first()
    if permission:
        return jsonify({
            'has_permission': True,
            'can_add': permission.addButton == 'Yes',
            'can_edit': permission.editButton == 'Yes',
            'can_manage': permission.manageButton == 'Yes',
            'can_publish': permission.publishButton == 'Yes'
        })
    else:
        return jsonify({'has_permission': False})

@app.route('/update_permission', methods=['POST'])
def update_permission():
    data = request.json  # 获取 JSON 数据
    #logging.debug(f"Received data: {data}")
    try:
        permission_id = int(data.get('id'))
        permission = Permission.query.get(permission_id)
        
        if not permission:
            return jsonify({'success': False, 'message': '权限未找到'}), 404
        
        # 更新权限的各个字段
        permission.email = data.get("email", permission.email)
        permission.addButton = data.get('addButton', permission.addButton)
        permission.editButton = data.get('editButton', permission.editButton)
        permission.manageButton = data.get('manageButton', permission.manageButton)
        permission.publishButton = data.get('publishButton', permission.publishButton)
        
        db.session.commit()
        
        logging.info(f"权限 ID {permission_id} 已更新")
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f'更新权限失败: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get_permission/<int:id>', methods=['GET'])
def get_permission(id):
    permission = Permission.query.get(id)
    if permission:
        return jsonify({
            'id': permission.id,
            'email': permission.email,
            'addButton': permission.addButton,
            'editButton': permission.editButton,
            'manageButton': permission.manageButton,
            'publishButton': permission.publishButton
        })
    else:
        return jsonify({'success': False, 'message': '权限未找到'}), 404

@app.route('/delete_report/<int:id>', methods=['DELETE'])
def delete_report(id):
    try:
        report = Report.query.get(id)
        logging.info(f"尝试删除报表 ID: {id}, 找到: {report is not None}")
        if not report:
            return jsonify({'success': False, 'message': '报表未找到'}), 404

        db.session.delete(report)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logging.error('删除报表失败: %s', e)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/publish_report', methods=['POST'])
def publish_report():
    #if not session.get('can_publish'):
    #    return jsonify({"success": False, "message": "权限不足"}), 403
    try:
        workspace_id = request.form.get('workspace_id')
        overwrite = request.form.get('overwrite') == 'true'
        pbix_file = request.files['pbix_file']

        # 打印调试信息
        #logging.debug(f"Workspace ID: {workspace_id}")
        #logging.debug(f"Overwrite: {overwrite}")
        #logging.debug(f"PBIX File Name: {pbix_file.filename}")

        access_token = token_cache.get_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'datasetDisplayName': pbix_file.filename,
            'nameConflict': 'Overwrite' if overwrite else 'CreateOrOverwrite'
        }
        files = {'file': (pbix_file.filename, pbix_file.stream, 'application/octet-stream')}
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports"

        response = requests.post(url, headers=headers, params=params, files=files)
        response.raise_for_status()

        import_info = response.json()
        #logging.debug(f"Import Info: {import_info}")

        # 确保报表名称正确获取，去掉文件名的扩展名
        report_name = import_info.get('reports', [{}])[0].get('name', pbix_file.filename).rsplit('.', 1)[0]
        #logging.debug(f"Report Name: {report_name}")

        # 获取工作区中的所有报表列表
        reports_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports"
        response = requests.get(reports_url, headers=headers)
        response.raise_for_status()

        reports_info = response.json().get('value', [])
        #logging.debug(f"Reports Info: {reports_info}")

        report_url = 'null'
        for report in reports_info:
            if report.get('name') == report_name:
                report_url = report.get('webUrl', 'null')
                break

        #logging.debug(f"Report URL: {report_url}")

        return jsonify({"success": True, "report_name": report_name, "report_url": report_url})
    except Exception as e:
        #logging.error(f"发布报表失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_workspaces', methods=['GET'])
def get_workspaces():
    try:
        access_token = token_cache.get_token()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        url = "https://api.powerbi.com/v1.0/myorg/groups"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        workspaces = response.json().get('value', [])
        return jsonify({"success": True, "workspaces": workspaces})
    except Exception as e:
        #logging.error(f"获取工作区失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# 启动调度线程
thread = Thread(target=run_schedule)
thread.start()

if __name__ == '__main__':
    schedule_thread = Thread(target=run_schedule)
    schedule_thread.start()

    with app.app_context():
        load_scheduled_refreshes()

    app.run(host='localhost', port=5000, debug=True, use_reloader=False)
