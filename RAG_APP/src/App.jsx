import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [currentChat, setCurrentChat] = useState([]);
  const [chatHistory, setChatHistory] = useState({});
  const [chatIdCounter, setChatIdCounter] = useState(1);
  const [userInput, setUserInput] = useState("");
  const [selectedChat, setSelectedChat] = useState("None");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Fetch saved chats from the backend on component mount
  useEffect(() => {
    async function fetchChats() {
      try {
        const res = await fetch("/chats");
        const chats = await res.json();
        // Build chatHistory object: key as session ID, value as messages array
        const history = {};
        chats.forEach((chat) => {
          history[chat.session_id] = chat.messages;
        });
        setChatHistory(history);
      } catch (error) {
        console.error("Error fetching chats:", error);
      }
    }
    fetchChats();
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleNewChat = () => {
    if (currentChat.length > 0) {
      const newChatId = `Chat ${chatIdCounter}`;
      setChatHistory((prev) => ({
        ...prev,
        [newChatId]: [...currentChat],
      }));
      setChatIdCounter((prev) => prev + 1);
    }
    setCurrentChat([]);
    setSelectedChat("None");
  };

  const handleSelectChat = (e) => {
    const chatName = e.target.value;
    setSelectedChat(chatName);
    if (chatName !== "None") {
      setCurrentChat(chatHistory[chatName] || []);
    } else {
      setCurrentChat([]);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const newUserMsg = { role: "user", content: userInput.trim() };
    const updatedChat = [...currentChat, newUserMsg];

    try {
      const res = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userInput.trim() }),
      });
      const data = await res.json();
      const backendResponse = data.answer || "No answer received.";
      const newAssistantMsg = { role: "assistant", content: backendResponse };
      updatedChat.push(newAssistantMsg);
    } catch (error) {
      console.error("Error fetching response:", error);
      const newAssistantMsg = { role: "assistant", content: "Error fetching response." };
      updatedChat.push(newAssistantMsg);
    }

    setCurrentChat(updatedChat);
    setUserInput("");
  };

  return (
    <div className="app-container">
      <nav className="nav-bar">
        <div className="shield-title">RAG Shield 🛡️</div>
        <div className="welcome">Hello, there!</div>
      </nav>
      <div className={`sidebar ${sidebarOpen ? "open" : "collapsed"}`}>
        <button onClick={toggleSidebar} className="sidebar-toggle">
          {sidebarOpen ? "«" : "»"}
        </button>
        {sidebarOpen && (
          <>
            <h2>Chat Sessions</h2>
            <button onClick={handleNewChat} id="newchatbtn">New Chat ➕</button>
            <div className="chat-select">
              <label htmlFor="chatDropdown">Select Previous Chat: </label>
              <select
                id="chatDropdown"
                value={selectedChat}
                onChange={handleSelectChat}
              >
                <option value="None">None</option>
                {Object.keys(chatHistory).map((chatId) => (
                  <option key={chatId} value={chatId}>
                    {chatId}
                  </option>
                ))}
              </select>
            </div>
          </>
        )}
      </div>
      <div className="chat-container">
        {currentChat.map((message, index) =>
          message.role === "user" ? (
            <div key={index} className="chat-row">
              <div className="user-bubble">
                <strong>User:</strong> {message.content}
              </div>
              <div className="empty-col"></div>
            </div>
          ) : (
            <div key={index} className="chat-row">
              <div className="empty-col"></div>
              <div className="assistant-bubble">
                <strong>Assistant:</strong> {message.content}
              </div>
            </div>
          )
        )}
      </div>
      <div className="fixed-form">
        <form onSubmit={handleSend} className="chat-form">
          <input
            type="text"
            id="query"
            name="query"
            placeholder="Type your message here..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}

export default App;
