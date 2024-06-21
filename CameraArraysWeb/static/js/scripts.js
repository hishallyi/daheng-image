function setParameters() {
    // TODO：目前无法获取到表单数据，需要调试
    const form = document.getElementById('camera-form');
    const formData = new FormData(form);
    console.log(formData);

    // TODO：发送post请求失败，需要调试
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
    const select = document.getElementById('camera-select');
    const serial = select.value;
    fetch(`/capture_image/${serial}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('camera-preview').src = data.image_url;
        });
}
