function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function init_filter_dropdown_list_by_get() {
    function filter_dropdown_list(event) {
        const target_id = '#id_' + target_name
        const url_with_parameters = url + '?' + source_name + '=' + event.target.value;
        console.log('url:', url_with_parameters)
        fetch(url_with_parameters, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
                let html_data = '<option value="">---------</option>';
                data.data.forEach(function (row) {
                    html_data += `<option value="${row[0]}">${row[1]}</option>`
                });

                const target_element = document.querySelector(target_id);
                // console.log(target_name, target_element.innerHTML);
                target_element.innerHTML =html_data;
        }).catch((error) => {
                console.error('Error:', error);
        });
    }

    const source_id = '#id_' + source_name
    const source_element = document.querySelector(source_id);
    // console.log(source_name, source_element)
    source_element.addEventListener('change', filter_dropdown_list, false);
}

function init_filter_dropdown_list_by_post() {
    function filter_dropdown_list(event) {
        const target_id = '#id_' + target_name

        let data = {}
        data[source_name] = event.target.value
        const csrftoken = getCookie('csrftoken');

        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({'data': data})
        })
        .then(response => response.json())
        .then(data => {
                // console.log('data:', data)
                let html_data = '<option value="">---------</option>';
                data.data.forEach(function (row) {
                    html_data += `<option value="${row[0]}">${row[1]}</option>`
                });

                const target_element = document.querySelector(target_id);
                // console.log(target_name, target_element.innerHTML);
                target_element.innerHTML =html_data;
        }).catch((error) => {
                console.error('Error:', error);
        });
    }

    const source_id = '#id_' + source_name
    const source_element = document.querySelector(source_id);
    // console.log(source_name, source_element)
    source_element.addEventListener('change', filter_dropdown_list, false);
}
