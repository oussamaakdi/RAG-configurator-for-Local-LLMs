document.querySelector("#sendButton").addEventListener("click", async function () {
    const query = document.getElementById("query").value.trim();
    const chatBox = document.getElementById("chatbox");
    const configId = parseInt(chatBox.getAttribute("data-config-id"), 10);

    if (!query) {
        alert("Veuillez entrer une question.");
        return;
    }

    if (isNaN(configId)) {
        chatBox.innerHTML += `<p><strong>Erreur :</strong> ID de configuration invalide.</p>`;
        return;
    }

    const userMessage = document.createElement("p");
    userMessage.innerHTML = `<strong>Vous :</strong> ${query}`;
    chatBox.appendChild(userMessage);

    try {
        const response = await fetch(`/chatbot/ask/${configId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            throw new Error(`Erreur HTTP : ${response.status}`);
        }

        const data = await response.json();
        console.log(data);

        const botMessage = document.createElement("p");
        botMessage.innerHTML = `<strong>Bot :</strong> ${data.response || "Pas de réponse."}`;
        chatBox.appendChild(botMessage);
    } catch (error) {
        console.error("Erreur détectée :", error);

        const errorMessage = document.createElement("p");
        errorMessage.innerHTML = `<strong>Erreur :</strong> Une erreur est survenue. ${error.message}`;
        chatBox.appendChild(errorMessage);
    }

    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });

    document.getElementById("query").value = "";
});
