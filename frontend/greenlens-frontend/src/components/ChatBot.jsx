// src/components/ChatBot.jsx
import React, { useState } from "react";
import api from "../utils/api";
import "./ChatBot.css";

export default function ChatBot() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hi! I’m GreenLens AI Assistant. Ask me about ESG, emissions, or compliance!" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessage = { sender: "user", text: input };
    setMessages([...messages, newMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.askQuestion(input);
      const botReply = res.answer?.answer || res.answer || "Sorry, I couldn't process that.";

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: botReply },
      ]);
    } catch (error) {
      console.error("Chatbot error:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Sorry, something went wrong connecting to the server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-header">💬 GreenLens Chat</div>
      <div className="chat-body">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${msg.sender === "user" ? "user" : "bot"}`}
          >
            {msg.text}
          </div>
        ))}
        {loading && <div className="chat-message bot">Typing...</div>}
      </div>

      <div className="chat-input">
        <input
          type="text"
          placeholder="Ask me about sustainability..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}
