function logout() {
    fetch("{% url 'auth:logout' %}", {
        method: 'POST',
        credentials: 'include',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}' // Add this line
        }
    })
        .then(response => {
            if (response.ok) {
                window.location.href = "{% url 'auth:user_login' %}";
            } else {
                alert('Logout failed. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Logout failed. Please try again.');
        });
}