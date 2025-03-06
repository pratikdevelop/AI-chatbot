"use client";
import React, { useState, useEffect } from "react";
import { Button, TextField, Typography, Grid, Box } from "@mui/material";
import { useRouter } from 'next/navigation'
const Home = () => {
  const router = useRouter()
  useEffect(() => {
    const toekn  = localStorage.getItem('token')
    if (!toekn) {
      router.push('/login')
    }
  },[])
  const [theme, setTheme] = useState("light");
  const [chatLog, setChatLog] = useState([]);
  const [videoResult, setVideoResult] = useState("");
  const [musicResult, setMusicResult] = useState("");
  const [lofiResult, setLofiResult] = useState("");

  const [userInput, setUserInput] = useState("");
  const [videoPrompt, setVideoPrompt] = useState("");
  const [musicMood, setMusicMood] = useState("");

  // Load theme from localStorage on initial render
  useEffect(() => {
    if (localStorage.getItem("theme") === "dark") {
      setTheme("dark");
      document.body.classList.add("dark");
    }
  }, []);

  const handleThemeToggle = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    document.body.classList.toggle("dark");
    localStorage.setItem("theme", newTheme);
  };

  const sendMessage = async () => {
    if (!userInput.trim()) return;
    setChatLog((prevLog) => [
      ...prevLog,
      { sender: "You", message: userInput },
    ]);
    setUserInput(""); // Clear input after sending
    setChatLog((prevLog) => [
      ...prevLog,
      { sender: "Bot", message: "Bot is typing..." },
    ]);

    const response = await fetch("http://localhost:5000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
       },
      body: JSON.stringify({ message: userInput }),
    });
    const data = await response.json();
    setChatLog((prevLog) => [
      ...prevLog,
      { sender: "Bot", message: data.response },
    ]);
  };

  const generateAIVideo = async (e) => {
    e.preventDefault();
    setVideoResult("Generating...");
    const response = await fetch("http://localhost:5000/api/generate-ai-video", {
      method: "POST",
      headers: { "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
       },
      body: JSON.stringify({ prompt: videoPrompt }),
    });
    const data = await response.json();
    setVideoResult(
      <a href={data.video_url} className="text-blue-500">
        Download Video
      </a>
    );
  };

  const generateAIMusic = async (e) => {
    e.preventDefault();
    setMusicResult("Generating...");
    const response = await fetch("http://localhost:5000/api/generate-ai-music", {
      method: "POST",
      headers: { "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
       },
      body: JSON.stringify({ mood: musicMood }),
    });
    const data = await response.json();
    setMusicResult(
      <a href={data.music_url} className="text-blue-500">
        Download Music
      </a>
    );
  };

  const generateLofiContent = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    setLofiResult("Generating...");
    const response = await fetch("http://localhost:5000/api/generate-lofi", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    setLofiResult(
      <a href={data.video_url} className="text-blue-500">
        Download Lofi Video
      </a>
    );
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
              AI Chatbot & Content Generator
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
          Engage with AI to chat, generate videos, music, and lofi content.
        </Typography>

        <Grid container spacing={4} justifyContent="center">
          {/* Chatbot Section */}
          <Grid item xs={12} md={6} lg={4}>
            <Box className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition">
              <Typography variant="h6" align="center" gutterBottom>
                Chat with AI
              </Typography>
              <Box className="h-64 overflow-y-auto p-4 border border-gray-300 dark:border-gray-700 rounded-md bg-gray-50 dark:bg-gray-700 mb-4">
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
          </Grid>

          {/* AI Video Generator */}
          <Grid item xs={12} md={6} lg={4}>
            <Box className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition">
              <Typography variant="h6" align="center" gutterBottom>
                Generate AI Video
              </Typography>
              <form onSubmit={generateAIVideo}>
                <TextField
                  value={videoPrompt}
                  onChange={(e) => setVideoPrompt(e.target.value)}
                  label="Enter Prompt"
                  fullWidth
                  variant="outlined"
                  sx={{ marginBottom: 2 }}
                  placeholder="Describe your video..."
                />
                <Button
                  type="submit"
                  variant="contained"
                  color="secondary"
                  fullWidth
                >
                  Generate Video
                </Button>
              </form>
              <Box className="mt-4 text-center">{videoResult}</Box>
            </Box>
          </Grid>

          {/* AI Music Generator */}
          <Grid item xs={12} md={6} lg={4}>
            <Box className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition">
              <Typography variant="h6" align="center" gutterBottom>
                Generate AI Music
              </Typography>
              <form onSubmit={generateAIMusic}>
                <TextField
                  value={musicMood}
                  onChange={(e) => setMusicMood(e.target.value)}
                  id="music-mood"
                  label="Enter Mood"
                  fullWidth
                  variant="outlined"
                  sx={{ marginBottom: 2 }}
                  placeholder="Relaxing, energetic, etc..."
                />
                <Button
                  type="submit"
                  variant="contained"
                  color="secondary"
                  fullWidth
                >
                  Generate Music
                </Button>
              </form>
              <Box className="mt-4 text-center">{musicResult}</Box>
            </Box>
          </Grid>

          {/* Lofi Generator Section */}
          <Grid item xs={12} md={6} lg={4}>
            <Box className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition">
              <Typography variant="h6" align="center" gutterBottom>
                Create Lofi GIF & Video
              </Typography>
              <form onSubmit={generateLofiContent}>
                <TextField
                  type="file"
                  id="image"
                  name="image"
                  fullWidth
                  required
                  sx={{ marginBottom: 2 }}
                />
                <TextField
                  type="file"
                  id="audio"
                  name="audio"
                  fullWidth
                  required
                  sx={{ marginBottom: 2 }}
                />
                <Button
                  type="submit"
                  variant="contained"
                  color="secondary"
                  fullWidth
                >
                  Generate Lofi GIF & Video
                </Button>
              </form>
              <Box className="mt-4 text-center">{lofiResult}</Box>
            </Box>
          </Grid>
        </Grid>
      </Box>

      {/* Footer */}
      <Box className="bg-gray-800 text-white py-4">
        <Typography variant="body2" align="center">
          &copy; 2025 AI Chatbot & Content Generator. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default Home;
