var notyf = new Notyf({
    types: [
        {
          type: 'warning',
          background: 'orange',
          icon: {
            className: 'material-icons',
            tagName: 'i',
            text: 'warning'
          }
        }
    ]});

var position = { x: "center", y: "top" }
const converter = new showdown.Converter();
document.getElementById("markup").innerHTML = converter.makeHtml(markupHTML)

var levelType=new URLSearchParams((new URL(window.location.href)).search).get("type")
if (levelType!=="ctf") {
    levelType="cryptic"
}

function hash(string) {
    const utf8 = new TextEncoder().encode(string);
    return crypto.subtle.digest('SHA-256', utf8).then((hashBuffer) => {
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray
        .map((bytes) => bytes.toString(16).padStart(2, '0'))
        .join('');
      return hashHex;
    });
}

async function submit() {
    var input = document.getElementById("messageInput")
    var answer = input.value.trim()
    if (answer != "") {
        var request=fetch("/submit?answer=" + encodeURIComponent(answer) + "&type=" + levelType) // if users try to bypass logging of their answers, their logs will be suspicious and they will be disqualified.
        if (level_Answer_Hash!=await hash("public_salt_to_prevent_rainbow_tables"+answer)) {
            notyf.error({ position: position, message: "Incorrect Answer" })
            return
        }
        notyf.open({type: "warning", position: position, message: "Verifying Answer", icon: "⚠️"})
        input.value = ""
        var response = await (await request).json()
        if (response["success"] === true) {
            Draw()
            notyf.success({ position: position, message: "Correct Answer" })
            setTimeout(() => {
                window.location = window.location.href
            }, 1000)
        } else {
            if (response.error!==undefined) {
                notyf.error({ position: position, message: response.error })
            } else {
                notyf.error({ position: position, message: "Incorrect Answer" })
            }
        }
    }
}

document.addEventListener("keypress", (key) => {
    if (key.code == "Enter" && document.getElementById("messageInput").value.trim() != "") {
        submit()
    }
})

document.querySelectorAll("#markup a").forEach((x)=>{
    x.target="_blank"
})

sendButton.addEventListener("click", ()=>{
    if (document.getElementById("messageInput").value.trim() != "") {
        submit()
    }
})