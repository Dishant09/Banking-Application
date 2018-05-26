'''
Created on 17-Apr-2018

@author: Dishant
'''
import generalfunc
import menus
import oracleconnection
from datetime import date,datetime
from wtforms import Form, StringField, PasswordField, validators,RadioField,IntegerField
from flask import Flask, render_template,request,flash,session,redirect,url_for
from twilio.rest import Client
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app._static_folder = "C:/Users/Dishant/Workspace2/Module4Project/templates/static"

@app.route('/')
def home():
    session.clear()
    return render_template('home.html')

# Register Form Class
class RegisterForm(Form):
    fname = StringField('First Name:', [validators.Length(min=1, max=15)],render_kw={"placeholder": "Enter First Name"})
    lname = StringField('Last Name:', [validators.Length(min=1, max=15)],render_kw={"placeholder": "Enter Last Name"})
    add1 = StringField('Line1(House No.):', [validators.Length(min=1, max=15)],render_kw={"placeholder": "Enter House No."})
    add2 = StringField('Line2(Street/Colony/Road):', [validators.Length(min=1, max=30)],render_kw={"placeholder": "Enter Street/Colony/Road"})
    add3 = StringField('City:', [validators.Length(min=1, max=25)],render_kw={"placeholder": "Enter City"})
    add4 = StringField('State:', [validators.Length(min=1, max=25)],render_kw={"placeholder": "Enter State"})
    add5 = StringField('Pincode:', [validators.Length(min=6, max=6)],render_kw={"placeholder": "Enter Pin code(6 digits)"})
    acctype = RadioField('Account Type:', choices = [('SA','Savings Account'),('CA','Current Account')])
    contact_no = StringField('Contact Number:', [validators.Length(min=10, max=10)],render_kw={"placeholder": "Enter Contact Number"})
    aadhaar_number = StringField('Aadhaar Number', [validators.Length(min=12, max=12)],render_kw={"placeholder": "Enter UID (12 digits)"}) 
    passwrd = PasswordField('Password', [
        validators.Regexp('^[a-zA-Z0-9]*$', message="Alphanumeric"),
        validators.Length(min=8,max=25),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')   
    ],render_kw={"placeholder": "Enter Password (8 digits)"})
    confirm = PasswordField('Confirm Password',render_kw={"placeholder": "Enter Password"})

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            fname = form.fname.data
            lname = form.lname.data
            name="%s %s" %(fname,lname)
            add1 = form.add1.data
            add2 = form.add2.data
            add3 = form.add3.data
            add4 = form.add4.data
            add5 = form.add5.data
            address="%s %s,%s,%s,%s" %(add1,add2,add3,add4,add5)
            contact_no = form.contact_no.data
            acctype = form.acctype.data
            aadhaar_number = form.aadhaar_number.data
            bal=generalfunc.balance(acctype)
            today= date.today()
            passwrd = sha256_crypt.encrypt(str(form.passwrd.data))
            passwrd2 = str(form.confirm.data)
            
            if sha256_crypt.verify(passwrd2, passwrd):
                
                oracleconnection.cur.execute("""SELECT AADHAARNUMBER FROM DISHANT.CUSTOMER WHERE AADHAARNUMBER=:1""",(aadhaar_number,))
                oracleconnection.con.commit()
                row= oracleconnection.cur.fetchall()
                count=oracleconnection.cur.rowcount
                
                if count==0:
                    oracleconnection.cur.execute('SELECT DISHANT.CID.NEXTVAL FROM DUAL')
                    oracleconnection.con.commit()
                    row= oracleconnection.cur.fetchall()
                    for r in row:
                        cid="%d" %(r[0])
                else:
                    oracleconnection.cur.execute('SELECT CID FROM DISHANT.CUSTOMER WHERE AADHAARNUMBER=:1',(aadhaar_number,))
                    oracleconnection.con.commit()
                    row= oracleconnection.cur.fetchall()
                    cid= row[0][0]
                
                oracleconnection.cur.execute('SELECT DISHANT.ACCNO.NEXTVAL FROM DUAL')
                oracleconnection.con.commit()
                row= oracleconnection.cur.fetchall()
                for r in row:
                    accno="%s%d" %('ACN',r[0])
            
                oracleconnection.cur.execute('INSERT INTO DISHANT.CUSTOMER VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)',(cid,accno,name,address,acctype,bal,passwrd,today,contact_no,aadhaar_number))
                oracleconnection.con.commit()
                
                account_sid = "AC2d2d145412daed6f33dcd8d4a3bea227"
                auth_token = "62df90ec4c9e4a5569aa8a161970d362"
                client = Client(account_sid, auth_token)
            
                contact_number="+91%s" %contact_no

                client.messages.create(
                    "+919996851758",
                    body="Your Customer ID = %s and Account Number = %s" %(cid,accno),
                    from_="+1 813-750-0171 ",
                    )
                
                flash('You are now registered and can log in.', 'success')
                return redirect(url_for('signin'))
            else:
                error='Password does not match....Try Again'
                return render_template('registration.html',form = form,error=error)
        except:
            error='No Internet connection'
            return render_template('registration.html',form = form,error=error)  
        
    return render_template('registration.html',form = form) 

@app.route('/signin',methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        x=0
        while x<3:             
            acc= request.form['accno']
            passwrd= request.form['passwrd']
            oracleconnection.cur.execute('SELECT PASSWORD,CID,NAME from DISHANT.CUSTOMER WHERE ACCNO=:1',(acc,))
            row=oracleconnection.cur.fetchall()
            oracleconnection.con.commit()
            
            if row:
                passwrd2=row[0][0]
                         
                if sha256_crypt.verify(passwrd, passwrd2):
                    session['logged_in']=True
                    session['acc']=acc
                    session['passwrd']=passwrd
                    session['cid']=row[0][1]
                    session['name']=row[0][2]
                     
                    return redirect(url_for('submenu'))   
                else:
                    error='Invalid USER-ID or Password!'
                    x=x+1
                    return render_template('login.html',error=error)
            else:
                error='No such user found'
                return render_template('login.html',error=error)       
        
        if x==3 :
            oracleconnection.cur.execute("""DELETE DISHANT.CUSTOMER WHERE accno=:1""",(acc,))
            oracleconnection.con.commit()
            error='More than 3 attempts are not allowed'
            return render_template('home.html',error=error)
                   
    return render_template('login.html') 

@app.route('/submenu')
def submenu():
    acc=session['acc']
    oracleconnection.cur.execute("""SELECT BALANCE,PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    openingbalance=row[0][0]
    
    return render_template('submenu.html',openingbalance=openingbalance) 

@app.route('/view_details')
def view_details():
    return render_template('view_details.html')

@app.route('/personal_details')
def personal_details():
    acc=session['acc']
    oracleconnection.cur.execute("""SELECT CID,ACCNO,NAME,ADDRESS,ACCTYPE,BALANCE,OPENINGDATE,CONTACT_NUMBER FROM DISHANT.CUSTOMER WHERE ACCNO=:1""",(acc,))
    row=oracleconnection.cur.fetchall()
    if row:
        return render_template('personal_details.html',row=row)    
    else:
        error="No Record Found"
        return render_template('personal_details.html',error=error)

class UpdateForm(Form):
    fname = StringField('First Name:', [validators.Length(min=1, max=15)],render_kw={"placeholder": "Enter First Name"})
    lname = StringField('Last Name:', [validators.Length(min=1, max=15)],render_kw={"placeholder": "Enter Last Name"})
    add1 = StringField('Line1(House No.):', [validators.Length(min=1, max=15)],render_kw={"placeholder": "Enter House No."})
    add2 = StringField('Line2(Street/Colony/Road):', [validators.Length(min=1, max=30)],render_kw={"placeholder": "Enter Street/Colony/Road"})
    add3 = StringField('City:', [validators.Length(min=1, max=25)],render_kw={"placeholder": "Enter City"})
    add4 = StringField('State:', [validators.Length(min=1, max=25)],render_kw={"placeholder": "Enter State"})
    add5 = StringField('Pincode:', [validators.Length(min=6, max=6)],render_kw={"placeholder": "Enter Pin code(6 digits)"})
    contact_no = StringField('Contact Number:', [validators.Length(min=10, max=10)],render_kw={"placeholder": "Enter Contact Number"})
    aadhaar_number = StringField('Aadhaar Number', [validators.Length(min=12, max=12)],render_kw={"placeholder": "Enter UID (12 digits)"}) 
   
@app.route('/update',methods=['GET', 'POST'])
def update():
        form = UpdateForm(request.form)
        if request.method == 'POST' and form.validate():
            
            acc=session['acc'] 
            fname = form.fname.data
            lname = form.lname.data
            name="%s %s" %(fname,lname)
            add1 = form.add1.data
            add2 = form.add2.data
            add3 = form.add3.data
            add4 = form.add4.data
            add5 = form.add5.data
            address="%s %s,%s,%s,%s" %(add1,add2,add3,add4,add5)
            contact_no = form.contact_no.data
            oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER set address=:1,name=:2,CONTACT_NUMBER=:3 where ACCNO=:4',(address,name,contact_no,acc))
            oracleconnection.con.commit()
            flash('Your details are updated successfully', 'success')
            return redirect(url_for('submenu'))
        
        return render_template('update.html',form = form) 

class PasswordForm(Form):
    oldpasswrd = PasswordField('Current Password',render_kw={"placeholder": "Enter Current Password"}) 
    passwrd = PasswordField('New Password', [
        validators.Regexp('^[a-zA-Z0-9]*$', message="Alphanumeric"),
        validators.Length(min=8,max=25),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')   
    ],render_kw={"placeholder": "Enter New Password (8 digits)"})
    confirm = PasswordField('Confirm Password',render_kw={"placeholder": "Enter New Password"})

@app.route('/change_password',methods=['GET', 'POST'])
def change_password():
    
        form = PasswordForm(request.form)
        if request.method == 'POST' and form.validate():
            acc=session['acc']
            oldpasswrd=form.oldpasswrd.data
            oracleconnection.cur.execute("""SELECT PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
            oracleconnection.con.commit()
            row=oracleconnection.cur.fetchall()
            passwrd2=row[0][0]
            
            verify=sha256_crypt.verify(oldpasswrd, passwrd2)
        
            if verify:  
                passwrd = sha256_crypt.encrypt(str(form.passwrd.data))
                oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET PASSWORD=:1 where ACCNO=:2',(passwrd,acc))
                oracleconnection.con.commit()
                flash('Your password is changed successfully', 'success')
                return redirect(url_for('submenu'))
        
            else:
                error="Wrong password....Please try again"
                return render_template('change_password.html',form = form,error=error)
        
        return render_template('change_password.html',form = form) 
   
class DepositForm(Form):
    amount = IntegerField('Amount:', [validators.NumberRange(min=100,max=100000000)],render_kw={"placeholder": "Enter the amount to be deposited"})
    passwrd = PasswordField('Password:', [
        validators.Regexp('^[a-zA-Z0-9]*$', message="Alphanumeric"),
        validators.Length(min=8,max=25),
        validators.DataRequired(), 
    ],render_kw={"placeholder": "Enter your Password "})
    
@app.route('/deposit_money',methods=['GET', 'POST'])
def deposit_money():
    
    form = DepositForm(request.form)
    if request.method == 'POST' and form.validate():
    
        acc=session['acc']
        oracleconnection.cur.execute("""SELECT BALANCE,PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        openingbalance=row[0][0]
        amount=form.amount.data
        passwrd2=row[0][1]
        passwrd=form.passwrd.data
        verify=sha256_crypt.verify(passwrd, passwrd2)
        cid=session['cid']

        if verify:    
            today= date.today()
            description="%s %d" %('Deposit',amount)
            oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance+:1 where accno=:2' ,(amount,acc))
            oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
            oracleconnection.con.commit()
            row= oracleconnection.cur.fetchall()
            tid=row[0][0]
            oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
            row=oracleconnection.cur.fetchall()
            balance=row[0][0]
            oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES (:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,balance))
            oracleconnection.con.commit()
            flash('Deposit successful', 'success')
            print("Transaction ID:",tid)
            print("Closing Balance=",row[0][0])
            return redirect(url_for('submenu'))
        else:
            error="Wrong password....Please try again"
            return render_template('deposit_money.html',form = form,error=error)
          
    return render_template('deposit_money.html',form = form) 

@app.route('/withdrawal_money',methods=['GET', 'POST'])
def withdrawal_money():
    form = DepositForm(request.form)
    if request.method == 'POST' and form.validate():
       
        acc=session['acc']
        oracleconnection.cur.execute("""SELECT BALANCE,PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        print("Opening Balance=",row[0][0])
        amount=form.amount.data
        passwrd2=row[0][1]
        passwrd=form.passwrd.data
        verify=sha256_crypt.verify(passwrd, passwrd2)
        cid=session['cid']

        if verify:
            today= date.today()
            description="%s %d" %('Withdrawal',amount)
            oracleconnection.cur.execute('SELECT balance,acctype FROM DISHANT.CUSTOMER WHERE accno=:1 and balance>= :2',(acc,amount))
            row=oracleconnection.cur.fetchall()
            if row:
                for r in row:
                    typeacc=r[1]
                    am=r[0]-amount
                if (typeacc=='CA' and am>=5000) or typeacc=='SA':
                    oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where accno=:2 and balance>:1' ,(amount,acc))
                    oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
                    oracleconnection.con.commit()
                    row= oracleconnection.cur.fetchall()
                    tid=row[0][0]
                    oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
                    oracleconnection.con.commit()
                    flash("Withdrawal successful",'success')
                    oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
                    row=oracleconnection.cur.fetchall()
                    print("Closing Balance=",row[0][0])
                    print("Transaction ID:",tid)
                    return redirect(url_for('submenu'))
                else:
                    error="Transaction cannot be completed as you are not able to maintain min balance or insufficient amount..Try withdrawing less amount"
                    return render_template('withdrawal_money.html',form = form,error=error)
                    
            else:
                error="Insufficient amount.."
                return render_template('withdrawal_money.html',form = form,error=error)
        else:
            error="Wrong password....Please try again"
            return render_template('withdrawal_money.html',form = form,error=error)
        
    return render_template('withdrawal_money.html',form = form)

class TransferForm(Form):
    acc2= StringField('Account Number:', [validators.Length(min=3, max=15)],render_kw={"placeholder": "Enter the account number to which money is to be transferred"})
    amount = IntegerField('Amount:', [validators.NumberRange(min=100,max=100000000)],render_kw={"placeholder": "Enter the amount to be deposited"})
    passwrd = PasswordField('Password:', [
        validators.Regexp('^[a-zA-Z0-9]*$', message="Alphanumeric"),
        validators.Length(min=8,max=25),
        validators.DataRequired(), 
    ],render_kw={"placeholder": "Enter your Password "})
        
@app.route('/transfer_money',methods=['GET', 'POST'])
def transfer_money():
    form = TransferForm(request.form)
    
    if request.method == 'POST' and form.validate():
        acc=session['acc']
        oracleconnection.cur.execute("""SELECT BALANCE,PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        
        acc2=form.acc2.data
        amount=form.amount.data
        passwrd2=row[0][1]
        passwrd=form.passwrd.data
        verify=sha256_crypt.verify(passwrd, passwrd2)
        cid=session['cid']
        oracleconnection.cur.execute('SELECT ACCNO FROM DISHANT.CUSTOMER WHERE accno=:1',(acc2,))
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        
        if verify:
            if row:
                today= date.today()
                description="%s %d %s %s" %('Tranfer',amount,'to',acc2)
                oracleconnection.cur.execute('SELECT balance,acctype FROM DISHANT.CUSTOMER WHERE accno=:1 and balance>=:2',(acc,amount))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    for r in row:
                        typeacc=r[1]
                        am=r[0]-amount
                    if (typeacc=='CA' and am>=5000) or typeacc=='SA':
                        oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where accno=:2 and balance>:1' ,(amount,acc))
                        oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
                        row= oracleconnection.cur.fetchall()
                        tid=row[0][0]
                        oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
                        oracleconnection.cur.execute("""SELECT BALANCE,CID FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc2})
                        row=oracleconnection.cur.fetchall()
                        cid1=row[0][1]
                        a="%s %d %s %s" %('Deposit',amount,'by',acc)
                        oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance+:1 where accno=:2' ,(amount,acc2))
                        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc2})
                        row=oracleconnection.cur.fetchall()
                        balance=row[0][0]
                        oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid1,acc2,today,a,amount,balance))
                        oracleconnection.con.commit()
                        flash("Transfer successful",'success')
                        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
                        row=oracleconnection.cur.fetchall()
                        print("Closing balance:",row[0][0])
                        print("Transaction ID:",tid)
                        oracleconnection.con.commit()
                        return redirect(url_for('submenu'))
                        
                    else:
                        error="Minimum balance is not sufficient"
                        return render_template('transfer_money.html',form = form,error=error)
                else:
                    error="Insufficient amount...Transaction failed"  
                    return render_template('transfer_money.html',form = form,error=error)
            else:
                error="No such account found"
                return render_template('transfer_money.html',form = form,error=error)
        else:
            error="Wrong Password...Please try again"
            return render_template('transfer_money.html',form = form,error=error)
            
    return render_template('transfer_money.html',form=form)

class FixeddepositForm(Form):
    amount = IntegerField('Amount:', [validators.NumberRange(min=100,max=100000000)],render_kw={"placeholder": "Enter the amount for fixed deposit"})
    choice = RadioField('Tenure:', choices = [('1','6 Months(at 4%)'),('2','1 year(at 4%)'),('3','7 years(at 5.75%)'),('4','10 years(at 6%)')])
    passwrd = PasswordField('Password:', [
        validators.Regexp('^[a-zA-Z0-9]*$', message="Alphanumeric"),
        validators.Length(min=8,max=25),
        validators.DataRequired(), 
    ],render_kw={"placeholder": "Enter your Password "})

@app.route('/fixed_deposit',methods=['GET', 'POST'])
def fixed_deposit():
    form = FixeddepositForm(request.form)
    
    if request.method == 'POST' and form.validate():
        acc=session['acc']
        oracleconnection.cur.execute("""SELECT BALANCE,PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        print("Opening Balance=",row[0][0])
        amount=form.amount.data
        passwrd2=row[0][1]
        passwrd=form.passwrd.data
        verify=sha256_crypt.verify(passwrd, passwrd2)
        cid=session['cid']
        choice=form.choice.data
        
        if verify:
            if choice=='1':
                interest=4
                tenure=0.5
                lastdate=datetime.date.today() + datetime.timedelta(6*365/12)
                today= date.today()
                description="%s %d" %('Fixed Deposit of',amount)
                oracleconnection.cur.execute('SELECT BALANCE,ACCTYPE FROM DISHANT.CUSTOMER WHERE ACCNO=:1 and balance>=:2',(acc,amount))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    for r in row:
                        typeacc=r[1]
                        am=r[0]-amount
                    if (typeacc=="CA" and am>=5000) or typeacc=='SA':
                        oracleconnection.cur.execute("""UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where ACCNO=:2 and balance>:1""" ,(amount,acc))
                        oracleconnection.con.commit()
                        oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
                        row= oracleconnection.cur.fetchall()
                        tid=row[0][0]
                        oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
                        oracleconnection.cur.execute('INSERT INTO DISHANT.FD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)',(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""INSERT INTO DISHANT.TEMPFD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""",(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
                        row=oracleconnection.cur.fetchall()
                        print("Transaction ID:",tid)
                        print("Closing balance:",row[0][0])
                        oracleconnection.con.commit()
                        flash("Fixed Deposit successful",'success')
                        return redirect(url_for('submenu'))
                    else:
                        error="Minimum balance is not sufficient"
                        return render_template('fixed_deposit.html',form = form,error=error)
                else:
                    error="Insufficient amount...Transaction failed"
                    return render_template('fixed_deposit.html',form = form,error=error)
                
            elif choice=="2":
                interest=4
                tenure=1    
                lastdate=datetime.date.today() + datetime.timedelta(365)
                today= date.today()
                description="%s %d" %('Fixed Deposit of',amount)
                oracleconnection.cur.execute('SELECT BALANCE,ACCTYPE FROM DISHANT.CUSTOMER WHERE ACCNO=:1 and balance>=:2',(acc,amount))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    for r in row:
                        typeacc=r[1]
                        am=r[0]-amount
                    if (typeacc=="CA" and am>=5000) or typeacc=='SA':
                        oracleconnection.cur.execute("""UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where ACCNO=:2 and balance>:1""" ,(amount,acc))
                        oracleconnection.con.commit()
                        oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
                        row= oracleconnection.cur.fetchall()
                        tid=row[0][0]
                        oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
                        oracleconnection.cur.execute('INSERT INTO DISHANT.FD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)',(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""INSERT INTO DISHANT.TEMPFD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""",(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
                        row=oracleconnection.cur.fetchall()
                        print("Transaction ID:",tid)
                        print("Closing balance:",row[0][0])
                        oracleconnection.con.commit()
                        flash("Fixed Deposit successful",'success')
                        return redirect(url_for('submenu'))
                    else:
                        error="Minimum balance is not sufficient"
                        return render_template('fixed_deposit.html',form = form,error=error)
                else:
                    error="Insufficient amount...Transaction failed"
                    return render_template('fixed_deposit.html',form = form,error=error)
            
            elif choice=="3":
                interest=5.75
                tenure=7
                lastdate=datetime.date.today() + datetime.timedelta(7*365)
                today= date.today()
                description="%s %d" %('Fixed Deposit of',amount)
                oracleconnection.cur.execute('SELECT BALANCE,ACCTYPE FROM DISHANT.CUSTOMER WHERE ACCNO=:1 and balance>=:2',(acc,amount))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    for r in row:
                        typeacc=r[1]
                        am=r[0]-amount
                    if (typeacc=="CA" and am>=5000) or typeacc=='SA':
                        oracleconnection.cur.execute("""UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where ACCNO=:2 and balance>:1""" ,(amount,acc))
                        oracleconnection.con.commit()
                        oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
                        row= oracleconnection.cur.fetchall()
                        tid=row[0][0]
                        oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
                        oracleconnection.cur.execute('INSERT INTO DISHANT.FD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)',(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""INSERT INTO DISHANT.TEMPFD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""",(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
                        row=oracleconnection.cur.fetchall()
                        print("Transaction ID:",tid)
                        print("Closing balance:",row[0][0])
                        oracleconnection.con.commit()
                        flash("Fixed Deposit successful",'success')
                        return redirect(url_for('submenu'))
                    else:
                        error="Minimum balance is not sufficient"
                        return render_template('fixed_deposit.html',form = form,error=error)
                else:
                    error="Insufficient amount...Transaction failed"
                    return render_template('fixed_deposit.html',form = form,error=error)
            
            elif choice=="4":
                interest=6
                tenure=10
                lastdate=datetime.date.today() + datetime.timedelta(10*365)
                today= date.today()
                description="%s %d" %('Fixed Deposit of',amount)
                oracleconnection.cur.execute('SELECT BALANCE,ACCTYPE FROM DISHANT.CUSTOMER WHERE ACCNO=:1 and balance>=:2',(acc,amount))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    for r in row:
                        typeacc=r[1]
                        am=r[0]-amount
                    if (typeacc=="CA" and am>=5000) or typeacc=='SA':
                        oracleconnection.cur.execute("""UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where ACCNO=:2 and balance>:1""" ,(amount,acc))
                        oracleconnection.con.commit()
                        oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
                        row= oracleconnection.cur.fetchall()
                        tid=row[0][0]
                        oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
                        oracleconnection.cur.execute('INSERT INTO DISHANT.FD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)',(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""INSERT INTO DISHANT.TEMPFD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""",(cid,acc,amount,tenure,interest,today,lastdate,tid))
                        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
                        row=oracleconnection.cur.fetchall()
                        print("Transaction ID:",tid)
                        print("Closing balance:",row[0][0])
                        oracleconnection.con.commit()
                        flash("Fixed Deposit successful",'success')
                        return redirect(url_for('submenu'))
                    else:
                        error="Minimum balance is not sufficient"
                        return render_template('fixed_deposit.html',form = form,error=error)
                else:
                    error="Insufficient amount...Transaction failed"
                    return render_template('fixed_deposit.html',form = form,error=error)
            else:
                error="Enter valid option"
                return render_template('fixed_deposit.html',form = form,error=error)   
        else:
            error="Wrong Password...Please try again"
            return render_template('fixed_deposit.html',form = form,error=error)        

    return render_template('fixed_deposit.html',form = form)   

class AccountcloseForm(Form):
    passwrd = PasswordField('Password:', [
        validators.Regexp('^[a-zA-Z0-9]*$', message="Alphanumeric"),
        validators.Length(min=8,max=25),
        validators.DataRequired(), 
    ],render_kw={"placeholder": "Enter your Password "})

@app.route('/account_close',methods=['GET', 'POST'])
def account_close():
    
    form = AccountcloseForm(request.form)
    if request.method == 'POST' and form.validate():
        
        acc=session['acc']
        oracleconnection.cur.execute("""SELECT BALANCE,PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        passwrd2=row[0][1]
        passwrd=form.passwrd.data
        verify=sha256_crypt.verify(passwrd, passwrd2)
        
        if verify:  
            today= date.today()
            oracleconnection.cur.execute('SELECT cid,accno,name,balance,address,CONTACT_NUMBER FROM DISHANT.CUSTOMER WHERE accno=:1',(acc,))
            oracleconnection.con.commit()
            row=oracleconnection.cur.fetchall()
            for r in row:
                oracleconnection.cur.execute('insert into DISHANT.history values(:1,:2,:3,:4,:5,:6,:7)',(r[0],r[1],r[2],r[3],today,r[4],r[5]))
                oracleconnection.con.commit()
                break
            oracleconnection.cur.execute('DELETE DISHANT.CUSTOMER WHERE accno=:1',(acc,))
            oracleconnection.con.commit()
            msg="%s %s %s" %(r[3],'amount is send to',r[4])
            flash(msg,'success')
            session.clear()
            return redirect(url_for('last')) 
        
        else:
            error="Wrong password....Please try again"
            print("hello")
            return render_template('account_close.html',form = form,error=error)
       
    return render_template('account_close.html',form=form)
     
@app.route('/print_statement')
def print_statement():
    return render_template('print_statement.html')

@app.route('/all_transactions')
def all_transactions():
    
    acc=session['acc']
    oracleconnection.cur.execute("SELECT * FROM DISHANT.RECORD WHERE ACCNO=:1 ",(acc,))
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    if row: 
        return render_template('all_transactions.html',row=row)
    else:
        error="No Record Found"
        return render_template('all_transactions.html',error=error)
    
class StatementForm(Form):
    datef=StringField('Date From:',[validators.DataRequired()],render_kw={"placeholder": "Enter date from in MM/DD/YYYY format"})
    datet=StringField('Date To:',[validators.DataRequired()],render_kw={"placeholder": "Enter date to in MM/DD/YYYY format"})
    
@app.route('/for_specific_dates',methods=['GET', 'POST'])
def for_specific_dates():
    
    form = StatementForm(request.form)
    if request.method == 'POST' and form.validate():
        
        acc=session['acc']
        datef=form.datef.data
        datet=form.datet.data
        today= datetime.today()
        datef=datetime.strptime(datef, '%m/%d/%Y')
        datet=datetime.strptime(datet, '%m/%d/%Y')
        if(datet<=today):
            if datef>datet :
                error="Invalid date"
                return render_template('for_specific_dates.html',form=form,error=error)
            else:
                oracleconnection.cur.execute('SELECT * FROM DISHANT.RECORD WHERE accno=:1 AND (dateoftransaction>=:2 AND dateoftransaction<=:3) ORDER BY dateoftransaction DESC',(acc,datef,datet))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    return render_template('for_specific_dates.html',form=form,row=row) 
                else:
                    error="No Record Found"
                    return render_template('for_specific_dates.html',form=form,error=error)
        else:
            error="You are using future date...Please enter valid date"
            return render_template('for_specific_dates.html',form=form,error=error)

    return render_template('for_specific_dates.html',form=form)

class AnnualForm(Form):
    year=StringField('Year:',[validators.DataRequired()],render_kw={"placeholder": "Enter the year for which statements are to be viewed"})
      
@app.route('/annual_statements',methods=['GET', 'POST'])
def annual_statements():
    
    form = AnnualForm(request.form)
    if request.method == 'POST' and form.validate():
        
        acc=session['acc']
        year=form.year.data
        datef="01/01/%s" %year
        datet="12/31/%s" %year
        datef=datetime.strptime(datef, '%m/%d/%Y')
        datet=datetime.strptime(datet, '%m/%d/%Y')
        today= datetime.today()
        if(datet<=today):    
            if datef>datet :
                error="Invalid date"
                return render_template('annual_statements.html',form=form,error=error)
            else:
                oracleconnection.cur.execute('SELECT * FROM DISHANT.RECORD WHERE accno=:1 AND (dateoftransaction>=:2 AND dateoftransaction<=:3) ORDER BY dateoftransaction DESC',(acc,datef,datet))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    return render_template('annual_statements.html',form=form,row=row)
                else:
                    error="No Record Found"
                    return render_template('annual_statements.html',form=form,error=error)
        else:
            error="You are using future date...Please enter valid date"
            return render_template('annual_statements.html',form=form,error=error)
    
    return render_template('annual_statements.html',form=form)       

@app.route('/adminsignin',methods=['GET', 'POST'])
def adminsignin():
    if request.method == 'POST':
        x=0
        while x<3:             
            adminid= request.form['adminid']
            passwrd= request.form['passwrd']
            oracleconnection.cur.execute('SELECT * from DISHANT.ADMIN WHERE id=:1',(adminid,))
            row=oracleconnection.cur.fetchall()
            oracleconnection.con.commit()
            
            if row:
                passwrd2=row[0][1]
                   
                if sha256_crypt.verify(passwrd, passwrd2):
                    session['logged_in']=True
                    session['adminid']=adminid
                    session['passwrd']=passwrd
                    
                    return redirect(url_for('submenu2'))   
                else:
                    error='Invalid USER-ID or Password!'
                    x=x+1
                    return render_template('adminsignin.html',error=error)
            else:
                error='No such user found'
                return render_template('adminsignin.html',error=error)       
        
        if x==3 :
           
            error='More than 3 attempts are not allowed'
            return render_template('home.html',error=error)
                   
    return render_template('adminsignin.html') 

@app.route('/submenu2')
def submenu2():  
    return render_template('submenu2.html') 

@app.route('/closed_account')
def closed_account():  
    
    oracleconnection.cur.execute("SELECT * FROM DISHANT.HISTORY ORDER BY CLOSING_DATE DESC")
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    if row:
        return render_template('closed_account.html',row=row) 
    else:
        error="History not found"
        return render_template('submenu2.html',error=error) 


@app.route('/transactions',methods=['GET', 'POST'])
def transactions():
    
    form = StatementForm(request.form)
    if request.method == 'POST' and form.validate():
        
        datef=form.datef.data
        datet=form.datet.data
        today= datetime.today()
        datef=datetime.strptime(datef, '%m/%d/%Y')
        datet=datetime.strptime(datet, '%m/%d/%Y')
        if(datet<=today):
            if datef>datet :
                error="Invalid date"
                return render_template('for_specific_dates.html',form=form,error=error)
            else:
                oracleconnection.cur.execute('SELECT * FROM DISHANT.RECORD WHERE (dateoftransaction>=:1 AND dateoftransaction<=:2) ORDER BY dateoftransaction DESC',(datef,datet))
                oracleconnection.con.commit()
                row=oracleconnection.cur.fetchall()
                if row:
                    return render_template('transactions.html',form=form,row=row) 
                else:
                    error="No Record Found"
                    return render_template('transactions.html',form=form,error=error)
        else:
            error="You are using future date...Please enter valid date"
            return render_template('transactions.html',form=form,error=error)

    return render_template('transactions.html',form=form)

@app.route('/fd')
def fd():  
    
    oracleconnection.cur.execute("SELECT * FROM DISHANT.TEMPFD ORDER BY TRANSACTIONID")
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    if row: 
        return render_template('fd.html',row=row)
    else:
        error="Record not found"
        return render_template('submenu2.html',error=error)     

@app.route('/customers')
def customers():  
    
    oracleconnection.cur.execute("SELECT CID,ACCNO,NAME,ADDRESS,ACCTYPE,BALANCE,OPENINGDATE,CONTACT_NUMBER,AADHAARNUMBER FROM DISHANT.CUSTOMER ORDER BY CID")
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    if row:
        return render_template('customers.html',row=row)
    else:
        error="Record not found"
        return render_template('submenu2.html',error=error)      

@app.route('/last')
def last():
    return render_template('last.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('signin'))

# Logout
@app.route('/logout2')
@is_logged_in
def logout2():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('adminsignin'))

@app.route('/about')
def about():
    return render_template('about.html') 

@app.route('/contactus')
def contactus():
    return render_template('contactus.html') 

if __name__ == "__main__":
    generalfunc.foo()
    app.debug==True
    app.secret_key='secret123'
    app.run(host='127.0.0.1', port=5570)