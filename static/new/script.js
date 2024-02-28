isdone=false;
var username=null
sessionToken = localStorage.getItem("sessionToken");

console.log(apitoken)
document.addEventListener('mousemove', (e) => {
    // Get the mouse position
    const mouseX = e.clientX / window.innerWidth - 0.5;
    const mouseY = e.clientY / window.innerHeight - 0.5;

    // Calculate the new background position based on mouse position
    const newPositionX = 50 + mouseX * 40; // Adjust the multiplier as needed
    const newPositionY = 50 + mouseY * 10; // Adjust the multiplier as needed

    // Apply the new background position
    document.body.style.backgroundPosition = `${newPositionX}% ${newPositionY}%`;
  });

  document.addEventListener('DOMContentLoaded', function () {
    var isDone = false; // Ensure this variable is defined
    const sessionToken = localStorage.getItem("sessionToken");
    if (!sessionToken) {
        // If no session token, show the popup form
        showPopupForm();
    } else {
        checkSessionToken(sessionToken)
    }
        
    document.getElementById('kk').addEventListener('submit', function (event) {
        event.preventDefault();
        document.getElementById('backtohome').hidden=false;
        submitForm(sessionToken);
        if (!isDone) {
            // Get the form
            var form = document.getElementById('kk');

            // Calculate new position and size based on percentage of window size
            var newTop = window.innerHeight * 0.38; // 38% from the top
            var newLeft = window.innerWidth * 0.12; // 12% from the left

    

            // Use CSS transitions for animation
            form.style.transition = 'top 1s, left 1s, width 1s';

            // Apply new styles
            form.style.top = newTop + 'px';
            form.style.left = newLeft + 'px';

            isDone = true;
        }
    });

    // Update form position and size when the window is resized
    window.addEventListener('resize', function () {
        if (isDone) {
            // Recalculate new position and size based on percentage of window size
            var newTop = window.innerHeight * 0.38; // 38% from the top
            var newLeft = window.innerWidth * 0.12; // 12% from the left


            // Apply new styles
            document.getElementById('kk').style.top = newTop + 'px';
            document.getElementById('kk').style.left = newLeft + 'px';
        }
    });
});


function submitForm(sessionToken) {
    var form = document.getElementById('kk');
    var formData = new FormData(form);
    formData.append('sessiontoken', sessionToken);

    fetch('/leetify', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response data here
        console.log(data);

        // Update the image source
        if (data.plot_url) {
            document.getElementById('plotimg').hidden = false
            document.getElementById('plotimg').src = data.plot_url;
            document.getElementById('plotimg').alt = "error ig"
            document.getElementById('share').hidden = false
            changeBackground()
        }

        // You can hide the loading gif or perform any other actions
        
    })
    .catch(error => {
        console.error('Error:', error);

        
    });
}

function changeBackground() {
    var body = document.body;
  
    // Check if the current background is an image
    var isImage = body.style.backgroundImage !== 'none';
  
    // Toggle between image and color
    if (isImage) {
      body.style.transition = 'background-color 1s ease';
      body.style.backgroundImage = 'none'; // Remove background image
      body.style.backgroundColor = '#161f2e'; // Set background color
    } else {
      body.style.transition = 'background-image 1s ease';
      body.style.backgroundImage = 'url("plotimg")'; // Set background image
      body.style.backgroundColor = ''; // Remove background color
    }
  }

  function addPost(postContent) {
    console.log(postContent)
    // Make a POST request to the server to add a new post
    fetch("/add_post", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            username: username,
            postcontent: postContent,
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Log the server response (for demonstration purposes)
        console.log(data);

        // Fetch posts again to update the HTML with the new post
        fetchPosts();
    })
    .catch(error => console.error('Error adding post:', error));
}


function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}

function showPopupForm() {
    const popupForm = document.getElementById("popupForm");
    popupForm.style.display = "";
    const toggleButton = document.getElementById("ToggleButton");
    toggleButton.textContent = "Switch to Register"; // Initial text

    // Add any additional logic for styling or animations

    // Toggle between login and register
    toggleButton.addEventListener("click", function () {
        const isLoginForm = popupForm.classList.contains("login-form");
        if (isLoginForm) {
            popupForm.classList.remove("login-form");
            popupForm.classList.add("register-form");
            toggleButton.textContent = "Switch to Login";
            document.getElementById("loginbutton").textContent = "Register"
        } else {
            popupForm.classList.remove("register-form");
            popupForm.classList.add("login-form");
            toggleButton.textContent = "Switch to Register";
            document.getElementById("loginbutton").textContent = "Login"
        }
    });


    // You can also handle the form submission here
    // For example, listen for a submit event on the form
    popupForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        // Use FormData with the entire form element
        const formData = new FormData(document.getElementById("loginForm"));
        console.log(formData)
        console.log(document.getElementById("loginForm"))
        const usernameInput = document.getElementById("loginUsername");
        const passwordInput = document.getElementById("loginPassword");
        console.log(usernameInput.value, passwordInput.value);
        const username = formData.get("loginUsername");
        const password = formData.get("loginPassword");

        let endpoint;
        const isLoginForm = popupForm.classList.contains("login-form");

        if (isLoginForm) {
            endpoint = "/login";
        } else {
            endpoint = "/register";
        }

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();

                // Update the UI based on the result
                // For example, show a success message or redirect to another page
                console.log("Login/Register successful", result);

                // Optionally, store the session token in localStorage
                localStorage.setItem("sessionToken", result.sessionToken);
                
                username=formData.get("loginUsername");

                // Close the popup if login/register is successful
                popupForm.style.display = "none";
                
            } else {
                // Handle error response
                const errorData = await response.json();
                console.error("Error:", errorData);
                // Update the UI to show an error message
            }
        } catch (error) {
            console.error("Error:", error);
            // Handle network errors or other exceptions
            // Update the UI to show an error message
        }
    });
}
function checkSessionToken(sessionToken) {
    // Make an AJAX request to the Flask endpoint
    fetch(`/auth_sess_token?session_token=${sessionToken}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                username = data.username
                console.log(`Session token is valid for user: ${username}`);
            } else {
                // Handle the case where the session token is invalid or expired
                console.error(`Invalid or expired session token: ${data.message}`);
                showPopupForm();
            }
        })
        .catch(error => {
            console.error(`Error checking session token: ${error}`);
        });
}