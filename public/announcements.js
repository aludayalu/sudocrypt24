import { Signal } from "/$.js";

const announcementsToggleBtn = document.getElementById("announcementsToggleBtn")
const announcementsPopup = document.getElementById("announcementsPopup")
const announcementsContainer = document.getElementById("announcementsContainer")

const toggleAnnouncements = Signal("announcementsOpenState", "close")
window.toggleAnnouncements=toggleAnnouncements

toggleAnnouncements.onChange = () => {
    if (toggleAnnouncements.Value() === "open") {

        document.getElementById("announcementsCircle").style.transform="scale(0)"
        announcementsPopup.style.display = "block"

        document.getElementById("announcementsContainer").scrollTop=document.getElementById("announcementsContainer").scrollHeight

        setTimeout(() => {
            announcementsPopup.style.opacity = 1
            announcementsPopup.style.transform = "translateY(0px)"
        }, 10);

        window.chatSignal.setValue("close")

    }
    else {
        announcementsPopup.style.opacity = 0
        announcementsPopup.style.transform = "translateY(-500px)"

        setTimeout(() => {
            announcementsPopup.style.display = "none"
        }, 400);
    }
}

announcementsToggleBtn.addEventListener("click", (e) => {
    toggleAnnouncements.setValue(toggleAnnouncements.Value() === "open" ? "close" : "open")
})

window.addEventListener("click", (e) => {
    if(!Array.from(announcementsPopup.querySelectorAll("*")).includes(e.target) && !Array.from(announcementsToggleBtn.querySelectorAll("*")).includes(e.target) && !Array.from(document.getElementById("chatControls").querySelectorAll("*")).includes(e.target) && !Array.from(document.getElementById("chatPopup").querySelectorAll("*")).includes(e.target)){
        toggleAnnouncements.setValue("close")
    }
})