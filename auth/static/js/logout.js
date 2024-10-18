/**
 * Logs the user out by sending a POST request to the logout URL.
 *
 * This function performs a fetch request to the server to log the user out.
 * Upon a successful response, it redirects the user to the login page.
 * If the logout request fails, an alert is displayed to the user.
 */
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