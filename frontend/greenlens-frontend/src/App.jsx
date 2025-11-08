import React from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./components/Dashboard";
import UploadDocs from "./components/UploadDocs";
import ChatBot from "./components/ChatBot";
import "./App.css";

function App() {
  return (
    <div className="app">
      <Navbar />
      <Dashboard />
      <UploadDocs />
      <ChatBot />
    </div>
  );
}

export default App;
