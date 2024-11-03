import { Signal } from "/$.js";

const chatToggleBtn = document.getElementById("chatToggleBtn")
const chatPopup = document.getElementById("chatPopup")

var notyf = new Notyf();
var position = { x: "center", y: "top" }

const chatSignal = Signal("chatOpenState", "close")
window.chatSignal=chatSignal

var leads=false

chatSignal.onChange = () => {
    if (chatSignal.Value() === "open") {
        chatPopup.style.display = "flex"

        chatToggleBtn.style.opacity = 0
        chatToggleBtn.style.transform = "scale(0)"

        setTimeout(() => {
            chatPopup.style.opacity = 1
            chatPopup.style.transform = "translateY(0px)"
            chatToggleBtn.style.display = "none"
        }, 10);

        const messagecontainer = document.getElementById("messagecontainer")
        setTimeout(() => {
            messagecontainer.scrollTop = messagecontainer.scrollHeight
        }, 200)
    }
    else {
        chatToggleBtn.style.display = "block"

        chatPopup.style.opacity = 0
        chatPopup.style.transform = "translateY(900px)"

        setTimeout(() => {
            chatPopup.style.display = "none"

            chatToggleBtn.style.opacity = 1
            chatToggleBtn.style.transform = "scale(1)"
        }, 400);
    }
}

chatToggleBtn.addEventListener("click", (e) => {
    chatSignal.setValue("open")
})

chatCloseBtn.addEventListener("click", (e) => {
    chatSignal.setValue("close")
})

chatMinimizeBtn.addEventListener("click", (e) => {
    chatSignal.setValue("close")
})

document.getElementById("chatSendButton").addEventListener("click", async (x)=>{
    var text=document.getElementById("chatInput").value.trim().trim("\n")
    if (text!="") {
        document.getElementById("chatInput").value=""
        document.getElementById("chatMsgLen").innerText = "0"
        var response=await (await fetch("/submit_message?content="+encodeURIComponent(text))).json()
        if (response.error!=undefined) {
            notyf.error({ position: position, message: response.error })
        } else {
            ignore=true
            checksum.onChange()
        }
    }
})

document.getElementById("chatInput").oninput = (e) => {
    if(e.target.value.trim().length >= 512){
        chatInput.value = e.target.value.trim().slice(0, 512)
    }
    if(e.target.value.trim().length >= 400){
        document.getElementById("chatMsgCharLimit").style.color = "#f87171"
    } else{
        document.getElementById("chatMsgCharLimit").style.color = "#fff"
    }

    document.getElementById("chatMsgLen").innerText = e.target.value.trim().length
}

function cookie_get(key) {
    try {
        var cookies={}
        for (var x in document.cookie.split("; ")) {
            var raw_data=document.cookie.split("; ")[x].split("=")
            cookies[raw_data[0]]=raw_data[1]
        }
        if (key in cookies) {
            return cookies[key]
        }
        return ""
    } catch {
        return ""
    }
}

var ignore=false
var first=true
var checksum=Signal("checksum", cookie_get("checksum"))
var announcements_Signal=Signal("announcements", cookie_get("announcements"))

function cookie_set(key, val) {
    try {
        document.cookie = `${key}=${val};expires=Thu, 01 Jan 2049 00:00:00 UTC`
    } catch { }
}

announcements_Signal.onChange=async ()=>{
    if (!first) {
        notyf.success({ position: position, message: "There is a new announcement!" })
        if (window.toggleAnnouncements.Value()!="open") {
            document.getElementById("announcementsCircle").style.transform="scale(1)"
        }
    }
    cookie_set("announcements", announcements_Signal.Value())
    var request=(await (await fetch("/announcements")).json())
    var announcements=document.getElementById("announcementsContainer")
    announcements.innerHTML=""
    request["announcements"].forEach((x)=>{
        announcements.innerHTML+=announcement_Item.replace("{announcement}", x["content"]).replace("{time}", (new Date(x["time"]*1000)).toString().split(" ").slice(1, 5).join(" "))
    })
    setTimeout(()=>{
        announcements.scrollTop =  announcements.scrollHeight
    }, 10)
}

checksum.onChange=async ()=>{
    if (!ignore && !first) {
        if (chatSignal.Value()!="open") {
            notyf.success({ position: position, message: "You have got a new message!" })
        }
    }
    if (ignore) {
        ignore=false
    }
    cookie_set("checksum", checksum.Value())
    var request=(await (await fetch("/chats")).json())
    var chats=request["chats"]
    var hints=request["hints"]
    var final=chats.concat(hints)
    final.sort((a, b)=>{
        return a["time"] > b["time"] ? 1 : -1
    })
    document.getElementById("messagecontainer").innerHTML=""
    final.forEach((x)=>{
        if (x["author"]=="Exun Clan") {
            document.getElementById("messagecontainer").innerHTML+=messageMe.replace("{content}", x["content"])
        } else {
            document.getElementById("messagecontainer").innerHTML+=messageYou.replace("{content}", x["content"])
        }
    })
    setTimeout(() => {
        messagecontainer.scrollTop = messagecontainer.scrollHeight
    }, 200)
}

async function checkChecksum() {
    var request=(await (await fetch("/chats_checksum")).json())
    leads=request["leads"]
    if (request["leads"]) {
        document.getElementById("leads").style.backgroundColor="#00da00"
        chatInput.disabled=false
        chatSendButton.disabled=false
    } else {
        document.getElementById("leads").style.backgroundColor="rgb(248, 114, 114)"
        chatInput.disabled=true
        chatSendButton.disabled=true
        document.getElementById("chatInput").value=""
        document.getElementById("chatMsgLen").innerText = "0"
    }
    checksum.setValue(request["checksum"])
    announcements_Signal.setValue(request["announcements"])
    if (first) {
        checksum.onChange()
        announcements_Signal.onChange()
    }
}

checkChecksum().then(()=>{
    first=false
})

setInterval(checkChecksum, 5000)