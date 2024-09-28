// script.js

// Handle Registration
document.getElementById("register-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    axios.post("http://localhost:8000/register/", {
        email: email,
        password: password
    })
    .then(response => {
        alert("Registration successful!");
    })
    .catch(error => {
        alert("Error: " + error.response.data.detail);
    });
});

// Handle Login
document.getElementById("login-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    axios.post("http://localhost:8000/login/", {
        email: email,
        password: password
    })
    .then(response => {
        const token = response.data.access_token;
        document.getElementById("token-display").innerHTML = `<h3>Login Successful!</h3><p>JWT Token: ${token}</p>`;
        // Optionally, store token in localStorage for future requests
        localStorage.setItem("token", token);
    })
    .catch(error => {
        alert("Login failed: " + error.response.data.detail);
    });
});
