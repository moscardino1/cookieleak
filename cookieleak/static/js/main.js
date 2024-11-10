
function analyzeSite() {
    const url = document.getElementById('url-input').value;
    const errorMessage = document.getElementById('error-message');
    const results = document.getElementById('results');

    if (!url) {
        errorMessage.textContent = 'Please enter a website address';
        errorMessage.style.display = 'block';
        return;
    }

    errorMessage.style.display = 'none';
    results.style.display = 'none';
    document.body.style.cursor = 'wait';
    
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `url=${encodeURIComponent(url)}`
    })
    .then(response => response.json())
    .then(data => {
        document.body.style.cursor = 'default';
        if (data.error) {
            errorMessage.textContent = data.error;
            errorMessage.style.display = 'block';
            results.style.display = 'none';
            return;
        }
        results.style.display = 'block';
        displayCookies(data);
    })
    .catch(error => {
        document.body.style.cursor = 'default';
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';
        results.style.display = 'none';
    });
}

function displayCookies(data) {
    const tableBody = document.getElementById('cookies-table-body');
    tableBody.innerHTML = ''; // Clear previous rows

    document.getElementById('total-cookies').textContent = data.stats.total_cookies;
    document.getElementById('high-risk').textContent = data.stats.high_risk;
    document.getElementById('medium-risk').textContent = data.stats.medium_risk;
    document.getElementById('low-risk').textContent = data.stats.low_risk;

    // Sort cookies by category
    data.cookies.sort((a, b) => {
        if (a.category < b.category) return -1;
        if (a.category > b.category) return 1;
        return 0;
    });

    data.cookies.forEach(cookie => {
        const row = `
            <tr class="risk-${cookie.risk_level.toLowerCase()}">
                <td title="${cookie.category}">${cookie.category_icon} ${cookie.category}</td>
                <td title="${cookie.name}">${cookie.name}</td>
                <td title="${cookie.value}"><code>${cookie.value}</code></td>
                <td title="${cookie.purpose}">${cookie.purpose}</td>
                <td title="${cookie.risk_level}"><span class="risk-tag ${cookie.risk_level.toLowerCase()}">${cookie.risk_level}</span></td>
            </tr>
        `;
        tableBody.innerHTML += row;
    });
    

    // Initialize or re-initialize DataTable
    if ($.fn.DataTable.isDataTable('.cookie-table')) {
        // If DataTable is already initialized, clear and redraw
        $('.cookie-table').DataTable().clear().rows.add($(tableBody).find('tr')).draw();
    } else {
        // Initialize DataTable for the first time
        $('.cookie-table').DataTable();
    }
    
}

