import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [currentChat, setCurrentChat] = useState([]);
  const [chatHistory, setChatHistory] = useState({});
  const [chatIdCounter, setChatIdCounter] = useState(1);
  const [userInput, setUserInput] = useState("");
  const [selectedChat, setSelectedChat] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Get backend URL from Vite environment variables.
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  // Fetch saved chats from the backend on component mount.
  useEffect(() => {
    async function fetchChats() {
      try {
        const res = await fetch(`${backendUrl}/chats`);
        const chats = await res.json();
        const history = {};
        // Build chatHistory object: key as session_id, value as chat object.
        chats.forEach((chat) => {
          history[chat.session_id] = chat;
        });
        setChatHistory(history);
      } catch (error) {
        console.error("Error fetching chats:", error);
      }
    }
    fetchChats();
  }, [backendUrl]);

  // Helper to generate a friendly title from the first query.
  const generateChatTitle = (query) => {
    const maxLength = 30;
    return query.length <= maxLength ? query : query.substring(0, maxLength).trim() + "...";
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleChatSelect = (chatId) => {
    setSelectedChat(chatId);
    setCurrentChat(chatHistory[chatId]?.messages || []);
  };

  const handleNewChat = () => {
    // Start a new chat session.
    setCurrentChat([]);
    setSelectedChat(null);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const newUserMsg = { role: "user", content: userInput.trim() };
    const updatedChat = [...currentChat, newUserMsg];

    try {
      const payload = { query: userInput.trim() };
      if (selectedChat) {
        payload.chat_id = selectedChat;
      }
      const res = await fetch(`${backendUrl}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      const backendResponse = data.answer || "No answer received.";
      const newAssistantMsg = { role: "assistant", content: backendResponse };
      updatedChat.push(newAssistantMsg);

      let chatId = selectedChat;
      if (!chatId) {
        chatId = `Chat ${chatIdCounter}`;
        setChatIdCounter(prev => prev + 1);
        const newChat = {
          session_id: chatId,
          title: generateChatTitle(userInput.trim()),
          messages: updatedChat,
        };
        setChatHistory(prev => ({ ...prev, [chatId]: newChat }));
        setSelectedChat(chatId);
      } else {
        // Update existing chat session.
        setChatHistory(prev => ({
          ...prev,
          [chatId]: { ...prev[chatId], messages: updatedChat },
        }));
      }
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
          <div className="chat-list">
            <h2>Chat Sessions</h2>
            <button onClick={handleNewChat} id="newchatbtn">New Chat ➕</button>
            {Object.keys(chatHistory).length === 0 && <p>No chats yet.</p>}
            <ul>
              {Object.entries(chatHistory).map(([chatId, chat]) => (
                <li
                  key={chatId}
                  onClick={() => handleChatSelect(chatId)}
                  className={selectedChat === chatId ? "selected" : ""}
                >
                  {chat.title || chatId}
                </li>
              ))}
            </ul>
          </div>
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
