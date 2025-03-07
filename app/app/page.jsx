


"use client";
import React, { useState, useEffect } from "react";
import { Button, TextField, Typography, Box } from "@mui/material";
import { useRouter } from "next/navigation";

const Home = () => {
  const router = useRouter();

  // Check for authentication token
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, []);

  // State declarations
  const [theme, setTheme] = useState("light");
  const [chatLog, setChatLog] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [isBotTyping, setIsBotTyping] = useState(false);

  // Load theme from localStorage on initial render
  useEffect(() => {
    if (localStorage.getItem("theme") === "dark") {
      setTheme("dark");
      document.body.classList.add("dark");
    }
  }, []);

  // Toggle between light and dark themes
  const handleThemeToggle = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    document.body.classList.toggle("dark");
    localStorage.setItem("theme", newTheme);
  };

  // Send message to the backend and update chat log
  const sendMessage = async () => {
    if (!userInput.trim()) return;

    // Add user's message to chat log
    setChatLog((prevLog) => [
      ...prevLog,
      { sender: "You", message: userInput },
    ]);
    setUserInput("");
    setIsBotTyping(true);

    // Fetch bot response
    const response = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({ message: userInput }),
    });
    const data = await response.json();

    // Add bot response to chat log
    setChatLog((prevLog) => [
      ...prevLog,
      { sender: "Bot", message: data.response },
    ]);
    setIsBotTyping(false);
  };

  return (
    <Box
      className={`bg-gray-50 dark:bg-gray-900 flex flex-col min-h-screen transition ${theme}`}
    >
      {/* Header */}
      <Box className="bg-white dark:bg-gray-800 shadow-md py-4 px-6 transition">
        <Box className="flex justify-between items-center max-w-7xl mx-auto">
          <Box className="flex items-center space-x-4">
            <Box className="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded-full"></Box>
            <Typography
              variant="h6"
              className="text-2xl font-bold text-gray-800 dark:text-white"
            >
              AI Chatbot
            </Typography>
          </Box>
          <Box className="flex items-center space-x-4">
            <Button
              onClick={handleThemeToggle}
              variant="outlined"
              color="primary"
            >
              🌙 Dark Mode
            </Button>
            <Button variant="contained" color="secondary">
              My Profile
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Main Content */}
      <Box className="flex-grow flex flex-col items-center p-6">
        <Typography variant="h4" gutterBottom align="center">
          Welcome, Guest! 👋
        </Typography>
        <Typography
          variant="body1"
          align="center"
          color="textSecondary"
          paragraph
        >
          Engage with AI to chat.
        </Typography>

        {/* Chat Section */}
        <Box
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition w-full max-w-3xl flex flex-col"
        >
          <Typography variant="h6" align="center" gutterBottom>
            Chat with AI
          </Typography>
          <Box
            className="flex-grow overflow-y-auto p-4 border border-gray-300 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-700 mb-4"
          >
            {chatLog.length === 0 ? (
              <Typography
                variant="body2"
                color="textSecondary"
                align="center"
                className="italic"
              >
                Your chat will appear here...
              </Typography>
            ) : (
              chatLog.map((log, idx) => (
                <Typography key={idx}>
                  <strong>{log.sender}:</strong> {log.message}
                </Typography>
              ))
            )}
            {isBotTyping && (
              <Typography variant="body2" color="textSecondary">
                Bot is typing...
              </Typography>
            )}
          </Box>
          <Box className="flex items-center">
            <TextField
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              variant="outlined"
              fullWidth
              placeholder="Type your message..."
              sx={{ marginRight: 2 }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={sendMessage}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Footer */}
      <Box className="bg-gray-800 text-white py-4">
        <Typography variant="body2" align="center">
          © 2025 AI Chatbot. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default Home;
