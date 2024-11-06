import uuid, json, flask, time, sys
from flask import Flask, request, redirect
from monster import render, init
from database import get, set, get_All, delete
from mailer import mail
import re, hashlib, random
from secrets_parser import parse
import hashlib
import requests
from urllib.parse import quote
from datetime import datetime, timedelta

salt = parse("variables.txt")["salt"]
botapi=parse("variables.txt")["botapi"]
startTime=int(str(parse("variables.txt")["startTime"]))
endTime=int(str(parse("variables.txt")["endTime"]))

def during_event():
    return startTime<=time.time() and time.time()<=endTime

admin=["r23025aarav@dpsrkp.net", "r23733atharv@dpsrkp.net", "exun@dpsrkp.net", "aarav@dayal.org"]

try:
    profanity=open("profanity.txt").read()
except:
    profanity=""

app = Flask(__name__)
init(app)


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def User():
    return {
        "name": "",
        "level": {
            "ctf":0,
            "cryptic":0
        },
        "logs": "",
        "email": "",
        "password": "",
        "phonenumber": ""
    }

@app.errorhandler(404)
def on_404(_):
    backlink=get("backlinks", request.path.split("/", 1)[1])
    if backlink["Ok"]:
        return flask.Response(backlink["Value"])
    return render("404", locals())

def auth(cookies):
    if "email" in cookies:
        account = get("accounts", cookies["email"])
        if account["Ok"] == False:
            return account
        if (
            account["Value"]["password"]
            == hashlib.sha256(cookies["password"].encode()).hexdigest()
        ):
            return account
        else:
            return {"Ok": False}
    else:
        return {"Ok": False}


@app.get("/")
def home():
    loggedIn = auth(dict(request.cookies))
    if loggedIn["Ok"]:
        status = "Logout"
        status_url = "/logout"
    else:
        status = "Log In"
        status_url = "/auth"
    announcements = ""
    header = render("components/header.html", locals())
    footer = render("components/footer.html", locals())
    confetti = render("components/confetti.html", locals())
    if loggedIn["Ok"]:
        if during_event():
            button_text="PLAY NOW"
            redirect_url="/play"
            countdown = render("buttons/home", locals())
        else:
            button_text="SIGN IN WITH EMAIL"
            redirect_url="/auth"
            if loggedIn["Value"]["email"] in admin:
                countdown = render("buttons/home", locals())
            else:
                starttime=startTime*1000
                countdown = render("countdown", locals())
    else:
        button_text="SIGN IN WITH EMAIL"
        redirect_url="/auth"
        countdown = render("buttons/home", locals())
    return render("components/index.html", locals())


@app.get("/leaderboard")
def leaderboard():
    loggedIn = auth(dict(request.cookies))
    fetchedData = get_All("leaderboard")
    levels={}
    for x in fetchedData["Value"]:
        if x["points"] not in levels:
            levels[x["points"]]=[x]
        else:
            levels[x["points"]].append({"time":x["time"], "name":x["name"], "email":x["email"], "points":x["points"]})
    leaderboard_data=[]
    players_added=[]
    for level in sorted(levels)[::-1]:
        level=levels[level]
        level.sort(key=lambda data: data["time"])
        for player in level:
            if player["email"] not in players_added:
                leaderboard_item={"time":player["time"], "name":player["name"], "points":player["points"]}
                if request.cookies.get("email") in admin:
                    leaderboard_item["email"]=player["email"]
                leaderboard_data.append(leaderboard_item)
                players_added.append(player["email"])

    leaderboard = []

    for i in range(len(leaderboard_data)):
        name = leaderboard_data[i]["name"]
        level = leaderboard_data[i]["points"]
        email_text = ""
        if request.cookies.get("email") in admin:
            email_text=" • Email: "+leaderboard_data[i]["email"]

        rank = i + 1

        

        leaderboard.append(render("components/leaderboard/card.html", locals()))

    if loggedIn["Ok"]:
        status = "Logout"
        status_url = "/logout"
    else:
        status = "Log In"
        status_url = "/auth"
    announcements = ""
    header = render("components/header.html", locals())
    footer = render("components/footer.html", locals())
    return render("components/leaderboard/leaderboard.html", locals())


@app.get("/logout")
def logout():
    return render("logout", locals())


@app.get("/auth")
def auth_page():
    loggedIn = auth(dict(request.cookies))
    if loggedIn["Ok"]:
        status = "Logout"
        status_url = "/logout"
    else:
        status = "Log In"
        status_url = "/auth"
    announcements = ""
    header = render("components/header.html", locals())
    footer = render("components/footer.html", locals())
    return render("components/auth.html", locals())


@app.get("/api/auth")
def auth_api():
    args = dict(request.args)
    if "password" not in args or "email" not in args or "method" not in args or "phonenumber" not in args:
        return json.dumps({"error": "Missing Fields", "args": args})
    if is_valid_email(args["email"]):
        if get("emails", args["email"])["Ok"]:
            account = get("accounts", args["email"])["Value"]
            if (account["password"]== hashlib.sha256(args["password"].encode()).hexdigest()):
                return json.dumps({"success": True})
            else:
                return json.dumps({"error": "Incorrect Password"})
        else:
            if "name" not in args or "otp" not in args:
                return json.dumps({"error": "Missing Fields", "args": args})
            args["name"]=args["name"].replace("\t", "").replace("  ", " ").strip()
            if args["method"]=="signup":
                if len(args["phonenumber"])!=10:
                    return json.dumps({"error":"Phone Number must be 10 digits long"})
                if len(args["name"])>50:
                    return json.dumps({"error":"Name cannot exceed 50 characters in total"})
                for x in args["name"].replace(" ", ""):
                    if x not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        return json.dumps({"error":"Name can only contain alphabets"})
                for x in args["name"].split(" "):
                    if x in profanity:
                        return json.dumps({"error":"Profanity Detected"})
                if args["otp"] == get_otp(args["email"]):
                    set("emails", args["email"], {"email":args["email"], "time":time.time()})
                    if "source" in args:
                        set("trackers", args["email"], args["source"])
                    user = User()
                    user["email"] = args["email"]
                    user["name"] = args["name"].title()
                    user["password"] = hashlib.sha256(args["password"].encode()).hexdigest()
                    user["phonenumber"] = args["phonenumber"]
                    set("accounts", args["email"], user)
                    set("leaderboard", args["email"], {"email":args["email"], "time":time.time(), "points":0, "name":args["name"]})
                    return json.dumps({"success": True})
            else:
                if args["method"]=="login":
                    return json.dumps({"error":"Account does not exist"})
                else:
                    return json.dumps({"error": "Wrong OTP"})
    return json.dumps({"error": "Invalid Email"})


def get_otp(email):
    digest = hashlib.sha256((email+salt).encode()).digest()
    random.seed(int.from_bytes(digest, "big"))
    otp = str(random.randint(0, 999999))
    return "0" * (6 - len(otp)) + otp


@app.get("/send_otp")
def sendotp():
    args = dict(request.args)
    if "email" not in args:
        return json.dumps({"error": "Missing Fields"})
    if is_valid_email(args["email"]):
        otp=get_otp(args["email"])
        digit1=otp[0]
        digit2=otp[1]
        digit3=otp[2]
        digit4=otp[3]
        digit5=otp[4]
        digit6=otp[5]
        mail(
            args["email"],
            "Sudocrypt 2024 OTP Verification",
            render("mail/otp", locals()),
        )
        return json.dumps({"otp": "success"})
    else:
        return json.dumps({"error": "Invalid Email"})

@app.get("/set_level")
def set_level():
    loggedIn = auth(dict(request.cookies))
    if loggedIn["Ok"] and request.cookies.get("email") in admin:
        args = dict(request.args)
        if "source" not in args or "answer" not in args and "markup" not in args or "levelid" not in args:
            return {"error":"Missing Fields"}
        if (not args["levelid"].startswith("ctf-") and not args["levelid"].startswith("cryptic-")) or not args["levelid"].split("-", 1)[1].isdigit():
            return {"error":"Level Id format must be {ctf or cryptic}-{number}"}
        set("levels", args["levelid"], {"id":args["levelid"], "answer":args["answer"], "markup":args["markup"], "sourcehint":args["source"]})
        requests.get(botapi+"/create_level?level="+args["levelid"])
        return {"level":"success"}
    return ""

@app.get("/delete_level")
def delete_level():
    loggedIn = auth(dict(request.cookies))
    if loggedIn["Ok"] and request.cookies.get("email") in admin:
        args = dict(request.args)
        if "level" not in args:
            return {"error":"Missing Fields"}
        delete("levels", args["level"])
        return {"level":"success"}
    return ""

@app.get("/admin")
def admin_page():
    loggedIn = auth(dict(request.cookies))
    if request.cookies.get("email") in admin and loggedIn["Ok"]:
        levels=[]
        levels_db=get_All("levels")
        levelsData=json.dumps(dict([[x["id"], x] for x in levels_db["Value"]]))
        for x in levels_db["Value"]:
            levelid=x["id"]
            levels.append(render("admin/level", locals()))
        if loggedIn["Ok"]:
            status = "Logout"
            status_url = "/logout"
        else:
            status = "Log In"
            status_url = "/auth"
        announcements = ""
        header = render("components/header.html", locals())
        footer = render("components/footer.html", locals())
        return render("admin/admin", locals())
    return render("404")

@app.get("/play")
def play():
    args=dict(request.args)
    type="cryptic"
    if "type" in args and args["type"]=="ctf":
        type="ctf"
    loggedIn = auth(dict(request.cookies))
    if loggedIn["Ok"] and (request.cookies.get("email") in admin or during_event()):
        if loggedIn["Ok"]:
            status = "Logout"
            status_url = "/logout"
        else:
            status = "Log In"
            status_url = "/auth"
        announcements = render("components/announcements.html", locals())
        header = render("components/header.html", locals())
        footer = render("components/footer.html", locals())
        level=type+"-"+str(loggedIn["Value"]["level"][type])
        level_Details=get("levels", str(level))
        markup=level_Details["Value"]["markup"]
        chats=[]
        avatar="https://api.dicebear.com/9.x/big-smile/svg?seed="+quote(loggedIn["Value"]["name"])
        chat_btn = render("chat/chat", locals())
        sourcehint=level_Details["Value"]["sourcehint"]
        return render("play", locals())
    return render("redirect")

@app.get("/chats_checksum")
def chat_checksum():
    loggedIn = auth(dict(request.cookies))
    args=dict(request.args)
    if "type" not in args:
        return {"error":"Missing Fields"}
    if loggedIn["Ok"]:
        all_messages=get_All("messages/"+request.cookies.get("email"))
        hints=get_All("hints/"+args["type"]+"-"+str(loggedIn["Value"]["level"][args["type"]]))
        leads=get("status", "leads")
        return {"checksum":hashlib.sha256(json.dumps(all_messages).encode()+json.dumps(hints).encode()).hexdigest(), "leads":leads["Value"], "announcements":hashlib.sha256(json.dumps(get_All("announcements")).encode()).hexdigest()}
    else:
        return {"error":"Not LoggedIn"}

@app.get("/chats")
def chats():
    loggedIn = auth(dict(request.cookies))
    args=dict(request.args)
    if "type" not in args:
        return {"error":"Missing Fields"}
    if loggedIn["Ok"]:
        all_messages=get_All("messages/"+request.cookies.get("email"))
        hints=get_All("hints/"+args["type"]+"-"+str(loggedIn["Value"]["level"][args["type"]]))
        return {"chats":all_messages["Value"], "hints":hints["Value"]}
    else:
        return {"error":"Not LoggedIn"}

@app.get("/announcements")
def announcements():
    loggedIn = auth(dict(request.cookies))
    args=dict(request.args)
    if loggedIn["Ok"]:
        all_announcements=get_All("announcements")["Value"]
        return {"announcements":all_announcements}
    else:
        return {"error":"Not LoggedIn"}

@app.get("/submit_message")
def submit_message():
    loggedIn = auth(dict(request.cookies))
    args=dict(request.args)
    type="cryptic"
    if "type" in args and args["type"]=="ctf":
        type="ctf"
    if "content" not in args:
        return {"error":"Missing Fields"}
    if loggedIn["Ok"]:
        if not (request.cookies.get("email") in admin or during_event()):
            if time.time()<startTime:
                return {"error":"The event has not commenced yet"}
            if time.time()>=endTime:
                return {"error":"The event has concluded"}
        leads=get("status", "leads")
        if not leads["Value"]:
            return {"error":"Leads are unavailable at this moment"}
        last_Time=get("messagetimes", loggedIn["Value"]["email"])
        disqualified=get("disqualified", loggedIn["Value"]["email"])
        if not disqualified["Ok"]:
            disqualified["Value"]=False
            set("disqualified", loggedIn["Value"]["email"], False)
        else:
            if disqualified["Value"]:
                return {"error":"You have been disqualified. Kindly contact us at exun@dpsrkp.net for clarification."}
        if not last_Time["Ok"]:
            last_Time["Value"]=0
        if time.time()-last_Time["Value"]<4:
            return {"error":"Messaging Rate Limit Exceeded"}
        if len(args["content"])>=512:
            return {"error":"Message is too long"}
        player=loggedIn["Value"]
        id=str(time.time())
        set("messagetimes", player["email"], time.time())
        set("messages/"+player["email"], id, {"author":loggedIn["Value"]["email"], "content":args["content"], "time":id, "id":id, "type":type})
        level=type+"-"+str(player["level"][type])
        requests.get(botapi+"/send_message?level="+str(level)+"&name="+quote(player["name"])+"&email="+quote(player["email"])+"&content="+quote(args["content"]))
        return {"success":True}
    else:
        return {"error":"Not LoggedIn"}

def unix_to_ist(unix_time):
    dt = datetime.fromtimestamp(unix_time)
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = dt + ist_offset
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

@app.get("/submit")
def submit():
    loggedIn = auth(dict(request.cookies))
    args=dict(request.args)
    type="cryptic"
    if "type" in args and args["type"]=="ctf":
        type="ctf"
    if "answer" not in args:
        return {"error":"Missing Fields"}
    if loggedIn["Ok"]:
        if not (request.cookies.get("email") in admin or during_event()):
            if time.time()<startTime:
                return {"error":"The event has not commenced yet"}
            if time.time()>=endTime:
                return {"error":"The event has concluded"}
        last_Time=get("submittimeout", loggedIn["Value"]["email"])
        disqualified=get("disqualified", loggedIn["Value"]["email"])
        if not disqualified["Ok"]:
            disqualified["Value"]=False
            set("disqualified", loggedIn["Value"]["email"], False)
        else:
            if disqualified["Value"]:
                return {"error":"You have been disqualified. Kindly contact us at exun@dpsrkp.net for clarification."}
        if not last_Time["Ok"]:
            last_Time["Value"]=0
        if time.time()-last_Time["Value"]<=1:
            return {"error":"Submit Rate Limit Exceeded"}
        set("submittimeout", loggedIn["Value"]["email"], time.time())
        status = "Logout"
        status_url = "/logout"
        announcements = ""
        header = render("components/header.html", locals())
        footer = render("components/footer.html", locals())
        level=type+"-"+str(loggedIn["Value"]["level"][type])
        level_Details=get("levels", str(level))
        player=loggedIn["Value"]
        playerLogs=get("logs", player["email"])
        if not playerLogs["Ok"]:
            set("logs", player["email"], str(unix_to_ist(int(time.time())))+" : "+args["answer"]+"\n")
        else:
            newLog=playerLogs["Value"]+str(unix_to_ist(int(time.time())))+" : "+args["answer"]+"\n"
            if len(newLog)>10240:
                newLog=newLog[len(newLog)-10240:]
            set("logs", player["email"], newLog)
        if level_Details["Value"]["answer"]==args["answer"]:
            player["level"][type]+=1
            set("accounts", player["email"], player)
            set("leaderboard", player["email"], {"email":player["email"], "time":time.time(), "points":player["level"]["ctf"]+player["level"]["cryptic"], "name":player["name"]})
            for x in get_All("messages/"+player["email"])["Value"]:
                if x["type"]==type:
                    delete("messages/"+player["email"], x["id"])
            return {"success":True}
        else:
            return {"success":False}
    else:
        return {"error":"Not LoggedIn"}