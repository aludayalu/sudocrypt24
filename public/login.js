import { Signal } from "/$.js";

const signupBtn = document.getElementById("signup")
const submitBtn = document.getElementById("submit")

const authTxt = document.getElementById("authTxt")

const signal = Signal("authstate", "signup")

function isValidEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

signal.onChange = () => {
    const temp = authTxt.innerHTML;
    authTxt.innerHTML = temp === "Signup" ? "Login" : "Signup";
    signupBtn.innerHTML = temp !== "Signup" ? "Login" : "Signup"


    if (temp === "Login") {
        document.getElementById("name").style.transform = "scale(0)";
        document.getElementById("name").style.opacity = "0";
        document.getElementById("phonenumber").style.transform = "scale(0)";
        document.getElementById("phonenumber").style.opacity = "0";
        submitBtn.innerText = "Signup"

        setTimeout(() => {
            document.getElementById("name").style.transform = "scale(1)";
            document.getElementById("name").style.opacity = "1";
            document.getElementById("phonenumber").style.transform = "scale(1)";
            document.getElementById("phonenumber").style.opacity = "1";
            document.getElementById("name").style.display="block";
            document.getElementById("phonenumber").style.display = "block";
        });
    }
    if (temp === "Signup") {
        submitBtn.innerText = "Login"
        document.getElementById("name").style.transform = "scale(0)";
        document.getElementById("name").style.opacity = "0";
        document.getElementById("phonenumber").style.transform = "scale(0)";
        document.getElementById("phonenumber").style.opacity = "0";
        document.getElementById("name").style.display="none";
        document.getElementById("phonenumber").style.display = "none";
    }
}

signupBtn.addEventListener("click", () => {
    signal.setValue(signal.Value() === "signup" ? "login" : "signup")
})

var notyf = new Notyf();
var position = { x: "center", y: "top" }

function cookie_set(key, val) {
    try {
        document.cookie = `${key}=${val};expires=Thu, 01 Jan 2049 00:00:00 UTC`
    } catch { }
}

submitBtn.addEventListener("click", () => {
    var name = document.getElementById("name").value.trim()
    var email = document.getElementById("email").value.trim()
    var password = document.getElementById("password").value.trim()
    var otp = ""
    var phonenumber = document.getElementById("phonenumber").value.replaceAll(/\D/g, '')

    if (signal.Value() == "signup" && phonenumber.length!=10) {
        notyf.error({position: position, message: "Phone Number must be 10 digits long"})
        return
    }
    
    inputs.forEach((x) => {
        otp += String(Number(x.value))
    })
    if (signal.Value() == "signup") {
        if (name.length == 0) {
            notyf.error({ position: position, message: "Name field is required" })
            return
        }
    }
    if (signal_otp.Value() == "otpscreen") {
        if (otp.length != 6 || Number(otp) == NaN) {
            notyf.error({ position: position, message: "OTP format is invalid" })
            return
        }
    }
    if (email.length == 0) {
        notyf.error({ position: position, message: "Email field is required" })
        return
    }
    if (!isValidEmail(email)) {
        notyf.error({ position: position, message: "Kindly login with valid dpsrkp.net accounts" })
        return
    }
    if (password.length == 0) {
        notyf.error({ position: position, message: "Password field is required" })
        return
    }
    if (signal_otp.Value() == "signup" && signal.Value() == "signup") {
        signal_otp.setValue("otpscreen")
        signupBtn.style.display = "none"
        fetch("/send_otp?email=" + encodeURIComponent(email)).then((x) => {
            notyf.success({ position: position, message: "OTP sent" })
        })
        return
    }
    fetch("/api/auth?name=" + encodeURIComponent(name) + "&email=" + encodeURIComponent(email) + "&password=" + encodeURIComponent(password) + "&otp=" + otp+"&method="+signal.Value()+"&phonenumber="+phonenumber).then(async (x) => {
        var out = await x.text()
        try {
            var json = JSON.parse(out)
        } catch {
            var json = false
        }
        if (json != false && json.success !== undefined) {
            notyf.success({ position: position, message: "Successfully Authenticated" })
            setTimeout(() => {
                cookie_set("email", email)
                cookie_set("password", password)
                window.location = "/"
            }, 1000)
        } else {
            notyf.error({ position: position, message: "Authentication Failed: " + json["error"] })
        }
    })
})



const otpform_container = document.getElementById("otpform_container");
const inputList = document.getElementById("inputList")


const signal_otp = Signal("otpScreen", "signup")

signal_otp.onChange = () => {
    if (signal_otp.Value() === "otpscreen") {
        otpform_container.style.display = "flex"
        otpform_container.style.opacity = 0
        otpform_container.style.transform = "scale(0)"

        inputList.style.transform = "translateX(-200px)"
        inputList.style.opacity = 0

        submitBtn.style.transitionProperty = "color, background-color, border-color, text-decoration-color, fill, stroke, box-shadow, filter, backdrop-filter, -webkit-text-decoration-color, -webkit-backdrop-filter"
        submitBtn.style.opacity = 0
        submitBtn.style.transform = "scale(0)"

        setTimeout(() => {
            inputList.style.display = "none"

            otpform_container.style.opacity = 1
            otpform_container.style.transform = "scale(1)"

            submitBtn.style.transitionProperty = "color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter, -webkit-text-decoration-color, -webkit-backdrop-filter"

            submitBtn.style.opacity = 1
            submitBtn.style.transform = "scale(1)"

        }, 300);
    }
}

document.getElementById("resend_otp").addEventListener("click", () => {
    var email = document.getElementById("email").value.trim()
    fetch("/send_otp?email=" + encodeURIComponent(email)).then((x) => {
        notyf.success({ position: position, message: "OTP sent" })
    })
})


const form = document.getElementById('otp-form')
const inputs = [...form.querySelectorAll('input[type=number]')]
const submit = form.querySelector('#submit')

const handleKeyDown = (e) => {
    if (
        !/^[0-9]{1}$/.test(e.key)
        && e.key !== 'Backspace'
        && e.key !== 'Delete'
        && e.key !== 'Tab'
        && !e.metaKey
    ) {
        e.preventDefault()
    }

    if (e.key === 'Delete' || e.key === 'Backspace') {
        const index = inputs.indexOf(e.target);
        inputs[index].value = '';
        if (index > 0) {
            setTimeout(() => {
                inputs[index - 1].focus();
            }, 100)
        }

    }
}

const handleInput = (e) => {
    const { target } = e
    const index = inputs.indexOf(target)
    if (e.key === 'Delete' || e.key === 'Backspace') {
        return
    }
    if (target.value) {
        if (index < inputs.length - 1) {
            inputs[index + 1].focus()
        } else {
            if (index === inputs.length - 1) {
                try {
                    e.target.value = e.target.value[0]
                }
                catch {
                }
            }
        }
    }
}

const handleFocus = (e) => {
    e.target.select()
}

const handlePaste = (e) => {
    e.preventDefault()
    const text = e.clipboardData.getData('text')
    if (!new RegExp(`^[0-9]{${inputs.length}}$`).test(text)) {
        return
    }
    const digits = text.split('')
    inputs.forEach((input, index) => input.value = digits[index])
    submit.focus()
}

inputs.forEach((input) => {
    input.addEventListener('input', handleInput)
    input.addEventListener('keydown', handleKeyDown)
    input.addEventListener('focus', handleFocus)
    input.addEventListener('paste', handlePaste)
})

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('keydown', function(event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'v' && signal_otp.Value()=="otpscreen") {
            event.preventDefault();
            navigator.clipboard.readText().then(function(pastedData) {
                var processedData = pastedData.toUpperCase().replaceAll(" ", "").replaceAll("\t", "")
                if (Number(processedData)!=NaN) {
                    for (var i=0; i<processedData.length; i++) {
                        try {
                            inputs[i].value=processedData[i]
                        } catch {}
                    }
                }
            })
        }
    });
});