var signals={}

function Derived_From(id, func) {
    var signal={"Id":id, "Value":func, "onChange":()=>{}, "setValue":(value)=>{
        if (value!==signals[id].Value()) {
            signals[id].Value=()=>value
            signals[id].onChange()
        }
    }}
    signals[id]=signal
    return signal
}

function Signal(id, value) {
    var signal={"Id":id, "Value":()=>value, "onChange":()=>{}, "setValue":(value)=>{
        if (value!==signals[id].Value()) {
            signals[id].Value=()=>value
            signals[id].onChange()
        }
    }}
    signals[id]=signal
    return signal
}

export {Signal, Derived_From}