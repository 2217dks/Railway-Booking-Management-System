import sqlite3 as sql
import hashlib
import pwinput

#User Logged In Variables
user_id=None

#Railway Booking Database Connection
database=sql.connect("railwaymanagement.db")
sql_cursor=database.cursor()
sql_cursor.execute("CREATE TABLE IF NOT EXISTS userdata(User_ID integer not null Primary key AUTOINCREMENT,Name varchar(255),Email varchar(255),Passwd char(64));")
sql_cursor.execute("CREATE TABLE IF NOT EXISTS ticketdata(Tkt_ID integer not null Primary key AUTOINCREMENT,User_ID int,Source varchar(255),Destination varchar(255),Distance decimal(6,2), Passengers int, Price int);")
database.commit()

#Logging in Function (Allow Users to LogIn)
def login():
    Email_Id=input("Enter your Email Address: ")
    sql_cursor.execute("SELECT * FROM userdata WHERE Email='{}'".format(Email_Id))
    userfetch_data=sql_cursor.fetchone()
    if userfetch_data==None: #If Email ID does not exist, it continues Sign Up Function
        print("We couldn't find","'"+Email_Id+"'"+",","Please try again or Sign up using this Email address")
    else:
        while True:
            Passwd=pwinput.pwinput(prompt="Enter Your Password: ", mask="*")
            if userfetch_data[3]==hashlib.sha256(Passwd.encode()).hexdigest():
                global user_id
                user_id = userfetch_data[0]
                print()
                print("Welcome",userfetch_data[1]+",","to Railway Ticket Booking Service.")
                break
            else:
                print("Incorrect Password")
    print()

#Signing Up Function (Allow New Users to SignUp)
def signup(): 
    SignUp_Name=input("Enter Your Full Name: ")
    while True: #Email ID, Checking if Email ID already Exist or not
        SignUp_Email_Id=input("Enter your Email Address: ")
        sql_cursor.execute("SELECT * FROM userdata WHERE Email='{}'".format(SignUp_Email_Id))
        userfetch_data=sql_cursor.fetchone()
        if userfetch_data==None: #If Email ID does not exist, it continues Sign Up Function
            SignUp_Passwd=pwinput.pwinput(prompt="Enter a Password(Min 8 Characters): ", mask="*")
            while True: #Make sure Password is greater than 8 characters and it matches to confirmation password
                if len(SignUp_Passwd)<8: 
                    print("Password is less than 8 characters")
                    SignUp_Passwd=pwinput.pwinput(prompt="Enter a Password(Min 8 Characters): ", mask="*")
                if len(SignUp_Passwd)>=8:
                    SignUp_Passwd_Confirm=pwinput.pwinput(prompt="Enter Password again to confirm: ", mask="*")
                    if SignUp_Passwd!=SignUp_Passwd_Confirm:
                        print("Confirmation Password Does NOT match, Please Re-Enter...")
                    else:
                        break
            try:
                sql_cursor.execute("INSERT INTO Userdata(Name,Email,Passwd) VALUES('{}','{}','{}')".format(SignUp_Name,SignUp_Email_Id,hashlib.sha256(SignUp_Passwd.encode()).hexdigest())) #Upload New User data to the Database
                database.commit()
                print("Sign Up Sucessful...")
                print("Welcome",SignUp_Name+",","to our Railway Ticket Booking Service.")
                print("You May now Log In to our Service, Thank You")
                break
            except sql.Error:
                print("There was a problem while Signing up, Please try again...")
                break
        else: #If Email ID Exists, It terminates Sign Up Function
            print("Email ID","'"+SignUp_Email_Id+"'","already Exist, You may log in using that Email ID")
            break
    print()

#Ticket Booking Function (Allow users to Book Tickets)
def book_ticket():
    s_file=open("stations.txt")
    data_structure=s_file.read()
    stdist_list=data_structure.split()
    dist_bwt_stations=[]
    stations=[]
    distance=[]
    print("List of STATIONS:")
    for i in range(len(stdist_list)): #Print all the stations available according to the stations.txt file
        if i%2==0:
            stations.append(stdist_list[i].replace('_',' '))
        else:
            dist_bwt_stations.append(float(stdist_list[i]))
    for i in range(len(stations)):
            print(str(i+1)+'.)', stations[i])
    source=int(input("Enter Source Station: "))
    dest=int(input("Enter Destination Station: "))
    if source in range(1,len(stations)+1) and dest in range(1,len(stations)+1): #make sure user not put invalid station as source and destination
        passengers=int(input("Enter No. of Passengers: "))
        print("*********************************************")
        if source<dest:
            for i in range(source, dest):
                distance.append(dist_bwt_stations[i-1])
        if source>dest:
            for i in range(dest, source):
                distance.append(dist_bwt_stations[i-1])
        dist_sum=round(sum(distance),1)
        source=stations[source-1]
        dest=stations[dest-1]
        print(source, '-->',dest)
        print("Distance: ",dist_sum,"Km")
        cost=20*dist_sum*passengers
        print("Cost: ",cost,'(₹20 per KM per Passenger)')
        print('*********************************************')
        a=input("Do you wish to Confirm Ticket?(y/n): ") # gives users a confirmation Question
        if a.lower()=="y":
            try:
                sql_cursor.execute("INSERT INTO ticketdata(User_ID, Source, Destination, Distance, Passengers, Price) VALUES({},'{}','{}',{},{},{})".format(user_id,source,dest,dist_sum,passengers,cost))
                database.commit()
                print("Ticket Booked Successfully")
            except sql.Error:
                print("Ticket can not be booked due to some issues")
        else:
            print("Ticket Booking Process cancelled")
    else: # Terminate booking function if invalid source aur destination provided
        print("Invalid Source and Destination")
    print()

#Ticket Check Function (Allow users to check for Booked Tickets)
def check_tickets():
    sql_cursor.execute("SELECT * FROM ticketdata WHERE User_ID={}".format(user_id))
    ticketfetch_data=sql_cursor.fetchall()
    if ticketfetch_data==[]:
        print("You have not booked any ticket yet...")
    else:
        for i in ticketfetch_data:
            sql_cursor.execute("SELECT * FROM userdata WHERE User_ID={}".format(user_id))
            username=sql_cursor.fetchone()
            print("**************************************************")
            print("Ticket ID:",i[0])
            print("Ticket on",username[1])
            print(i[2]," --> ",i[3],"| Distance:",i[4],"Km")
            print("No. of Passengers:",i[5])
            print("Price of Ticket: ₹",i[6])
            print("**************************************************")
    print()

#Ticket Cancellation Function (Allow users to Cancel a Booked Ticket)
def cancel_ticket():
    sql_cursor.execute("SELECT * FROM ticketdata WHERE User_ID={}".format(user_id))
    ticketfetch_data=sql_cursor.fetchall()
    if ticketfetch_data==[]: #Check for pre existing tickets, if available then shows cancellation option otherwise print appropriate message
        print("You have not Booked any ticket yet...")
    else:
        print("Your Booked Tickets:")
        for i in ticketfetch_data:
            print("Ticket ID:",i[0],"|",i[2],"-->",i[3],"|",i[5],"Passengers")
        print()
        t=int(input("Enter Your Ticket ID to Cancel: "))
        Ticket_Found_FLAG=False
        for i in ticketfetch_data:
            if i[0]==t:
                sql_cursor.execute("DELETE FROM ticketdata WHERE Tkt_ID={}".format(t))
                database.commit()
                print("Ticket Cancelled Sucessfully")
                Ticket_Found_FLAG=True
                break
        if Ticket_Found_FLAG==False:
            print("Ticker ID Not Found")
    print()

#Main_Program
while True:
    if user_id==None:
        log_sign=input("""1.) Login 
2.) Sign Up
3.) Exit
Enter Your Choice: """)
        print()
        if log_sign=="1":
            login()
        if log_sign=="2":
            signup()
        if log_sign=="3":
            break
    if user_id!=None:
        a=input("""1.) Book a Ticket
2.) Check for booked Tickets
3.) Cancellation of a Ticket
4.) Logout
Enter Your Choice: """)
        if a=="1":
            print()
            book_ticket()
        if a=="2":
            print()
            check_tickets()
        if a=="3":
            print()
            cancel_ticket()
        if a=="4":
            user_id=None
            print()
            print("Logged Out")
            print()