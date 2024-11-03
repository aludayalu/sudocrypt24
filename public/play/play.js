var notyf = new Notyf();
var position = { x: "center", y: "top" }
const converter = new showdown.Converter();
document.getElementById("markup").innerHTML = converter.makeHtml(markupHTML)

async function submit() {
    var input = document.getElementById("messageInput")
    var answer = input.value.trim()
    if (answer != "") {
        input.value = ""
        var response = await (await fetch("/submit?answer=" + encodeURIComponent(answer))).json()
        if (response["success"] === true) {
            Draw()
            notyf.success({ position: position, message: "Correct Answer" })
            setTimeout(() => {
                window.location = "/play"
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