
async function fetch_serial_list() {
    console.log("fetch_serial_list ativado");
    const response = await fetch("/config/fetch_serial")
    if ( response.ok ) {
        const result = await response.json()
        console.log(result)
        return result["serial_list"];
    } else {
        console.error("fetching serial list error")
    }
}

async function set_serial_list() {
    console.log("set_serial ativado!")
    serial_list = await fetch_serial_list();
    serial_list.forEach( serial => console.log(serial) );

    let serial_list_element = document.querySelector("#serial_list");

    serial_list.forEach( ( serial ) => {
        let element = document.createElement("option");
        element.textContent = serial;
        serial_list_element.append(element);
    });
}

function clear_serial_list() {
    console.log("clear_serial_list ativado");
    let serial_list_element = document.querySelector("#serial_list");

    // while (serial_list_element.hasChildNodes()) {
    //    serial_list_element.removeChild(serial_list_element.children[0]);
    // }

    // serial_list_element.children.forEach( element => element.remove() )
    console.log(serial_list_element.childNodes)
}

function refresh_serial_list() {
    clear_serial_list();
    set_serial_list();
}

function disconnect_serial() {
    console.log("disconnect_serial ativado");
}

set_serial_list();

