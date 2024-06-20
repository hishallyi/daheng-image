function setParameters() {
    var form = document.getElementById('camera-form');
    var formData = new FormData(form);

    fetch('/set_parameters', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                updatePreview();
            } else {
                alert('Failed to set parameters');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while setting parameters');
        });
}

function updatePreview() {
    var select = document.getElementById('camera-select');
    var serial = select.value;
    fetch(`/capture_image/${serial}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('camera-preview').src = data.image_url;
        });
}
