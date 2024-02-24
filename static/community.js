document.addEventListener("DOMContentLoaded", function () {
    // Fetch posts when the page loads
    fetchPosts();

    // Function to fetch posts from the Flask backend
    function fetchPosts() {
        fetch("/get_posts")
            .then(response => response.json())
            .then(data => {
                // Update the HTML with fetched posts
                updatePosts(data);
            })
            .catch(error => console.error('Error fetching posts:', error));
    }

    // Function to update the HTML with posts
    function updatePosts(posts) {
        var postContainer = document.querySelector(".post-container");
        postContainer.innerHTML = ""; // Clear existing content
        posts = posts.reverse()
        posts.forEach(post => {
            var userPost = document.createElement("div");
            userPost.className = "user-post";

            var image = document.createElement("img");
            image.src = post.postcontent;
            image.alt = "User Image";

            var postText = document.createElement("p");
            postText.className = "post-text";
            postText.textContent = "Chart Created By: " + post.username;;

            userPost.appendChild(image);
            userPost.appendChild(postText);

            var postContainer = document.querySelector(".post-container");
            postContainer.appendChild(userPost);
        });
    }
});
document.addEventListener('mousemove', (e) => {
    // Get the mouse position
    const mouseX = e.clientX / window.innerWidth - 0.5;
    const mouseY = e.clientY / window.innerHeight - 0.5;

    // Calculate the new background position based on mouse position
    const newPositionX = 50 + mouseX * 20; // Adjust the multiplier as needed
    const newPositionY = 50 + mouseY * 20; // Adjust the multiplier as needed

    // Apply the new background position
    document.body.style.backgroundPosition = `${newPositionX}% ${newPositionY}%`;
  });