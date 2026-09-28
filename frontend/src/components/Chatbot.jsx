import React, { useEffect, useRef, useState } from "react";
import { Send, X, Bot, User, Trash2 } from "lucide-react";
import API from "../services/api";

export default function Chatbot() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [profile, setProfile] = useState({});
  const [applications, setApplications] = useState([]);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const [messages, setMessages] = useState([
    {
      id: Date.now(),
      sender: "bot",
      text:
        "Hi! 👋 I'm SchemeSahay Assistant.\n\n" +
        "I can help you discover government schemes, understand eligibility, " +
        "find required documents, check applications and explore financial assistance.\n\n" +
        "What would you like help with?",
    },
  ]);

  // --------------------------------------------------
  // Load user profile and applications
  // --------------------------------------------------

  useEffect(() => {
    const loadUserContext = async () => {
      try {
        const [profileResponse, applicationsResponse] =
          await Promise.allSettled([
            API.get("/profile"),
            API.get("/applications"),
          ]);

        if (profileResponse.status === "fulfilled") {
          setProfile(profileResponse.value?.data || {});
        }

        if (applicationsResponse.status === "fulfilled") {
          const data = applicationsResponse.value?.data;

          if (Array.isArray(data)) {
            setApplications(data);
          } else if (Array.isArray(data?.applications)) {
            setApplications(data.applications);
          } else {
            setApplications([]);
          }
        }
      } catch (error) {
        console.log("Could not load chatbot context:", error);
      }
    };

    loadUserContext();
  }, []);

  // --------------------------------------------------
  // Auto scroll to latest message
  // --------------------------------------------------

  useEffect(() => {
    if (open) {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }
  }, [messages, loading, open]);

  // --------------------------------------------------
  // Focus input when chatbot opens
  // --------------------------------------------------

  useEffect(() => {
    if (open) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 150);
    }
  }, [open]);

  // --------------------------------------------------
  // Quick questions
  // --------------------------------------------------

  const quickQuestions = [
    "What is SchemeSahay AI?",
    "Which schemes can help me?",
    "What documents do I need?",
    "How do I check eligibility?",
    "How can I track my application?",
    "How can I calculate my EMI?",
  ];

  // --------------------------------------------------
  // Format profile information for AI
  // --------------------------------------------------

  const getProfileContext = () => {
    if (!profile || Object.keys(profile).length === 0) {
      return "Profile information is not currently available.";
    }

    const usefulFields = [
      "name",
      "full_name",
      "age",
      "gender",
      "state",
      "district",
      "category",
      "caste",
      "annual_income",
      "income",
      "occupation",
      "education",
      "education_level",
      "business_type",
      "business",
      "employment_status",
    ];

    const context = {};

    usefulFields.forEach((field) => {
      if (
        profile[field] !== undefined &&
        profile[field] !== null &&
        profile[field] !== ""
      ) {
        context[field] = profile[field];
      }
    });

    return JSON.stringify(context);
  };

  // --------------------------------------------------
  // Format application information for AI
  // --------------------------------------------------

  const getApplicationContext = () => {
    if (!applications || applications.length === 0) {
      return "No application information is currently available.";
    }

    return JSON.stringify(
      applications.map((app) => ({
        id: app.id || app._id,
        scheme: app.scheme || app.scheme_name || app.name,
        status: app.status,
        submitted_at: app.submitted_at || app.created_at,
      }))
    );
  };

  // --------------------------------------------------
  // Send message
  // --------------------------------------------------

  const sendMessage = async (customMessage = null) => {
    const userMessage = (
      customMessage !== null ? customMessage : message
    ).trim();

    if (!userMessage || loading) return;

    // Add user message
    const newUserMessage = {
      id: Date.now(),
      sender: "user",
      text: userMessage,
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setMessage("");
    setLoading(true);

    try {
      // Keep recent conversation history
      const conversationHistory = messages
        .slice(-8)
        .map((msg) => ({
          role: msg.sender === "user" ? "user" : "assistant",
          content: msg.text,
        }));

      /*
       * We send the extra information along with the message.
       *
       * Your current FastAPI backend only requires:
       * {
       *    "message": "..."
       * }
       *
       * Extra fields can be ignored by the current backend.
       *
       * Later, when we upgrade the backend, these fields can be
       * used to make the chatbot genuinely personalized.
       */

      const response = await API.post("/chat", {
        message: userMessage,

        history: conversationHistory,

        profile: profile,

        applications: applications,

        profile_context: getProfileContext(),

        application_context: getApplicationContext(),
      });

      console.log("CHAT RESPONSE:", response.data);

      const botReply =
        response.data?.reply ||
        response.data?.response ||
        response.data?.answer ||
        response.data?.message ||
        "I received your message, but I couldn't generate a response.";

      const botMessage = {
        id: Date.now() + 1,
        sender: "bot",
        text: botReply,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("CHAT ERROR:", error);

      let errorMessage =
        "I couldn't process that request right now. Please try again.";

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "bot",
          text: errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // Enter key
  // --------------------------------------------------

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // --------------------------------------------------
  // Clear conversation
  // --------------------------------------------------

  const clearChat = () => {
    setMessages([
      {
        id: Date.now(),
        sender: "bot",
        text:
          "Chat cleared! 👋\n\n" +
          "I'm ready to help you with government schemes, eligibility, " +
          "documents, applications and financial assistance.",
      },
    ]);
  };

  // --------------------------------------------------
  // Open chatbot
  // --------------------------------------------------

  const openChat = () => {
    setOpen(true);
  };

  // --------------------------------------------------
  // Close chatbot
  // --------------------------------------------------

  const closeChat = () => {
    setOpen(false);
  };

  return (
    <>
      {/* ==================================================
          FLOATING CHATBOT BUTTON
          ================================================== */}

      {!open && (
        <button
          className="chatbot-floating-button"
          onClick={openChat}
          title="Open SchemeSahay Assistant"
          aria-label="Open SchemeSahay Assistant"
        >
          <Bot size={28} />
        </button>
      )}

      {/* ==================================================
          CHATBOT WINDOW
          ================================================== */}

      {open && (
        <div className="chatbot-window">

          {/* ================= HEADER ================= */}

          <div className="chatbot-header">

            <div className="chatbot-header-left">

              <div className="chatbot-header-icon">
                <Bot size={22} />
              </div>

              <div>
                <h3>SchemeSahay Assistant</h3>

                <span>
                  AI Scheme Support
                </span>
              </div>

            </div>

            <div className="chatbot-header-actions">

              {/* Clear chat */}

              <button
                className="chatbot-clear"
                onClick={clearChat}
                title="Clear conversation"
                aria-label="Clear conversation"
              >
                <Trash2 size={18} />
              </button>

              {/* Close */}

              <button
                className="chatbot-close"
                onClick={closeChat}
                title="Close chatbot"
                aria-label="Close chatbot"
              >
                <X size={22} />
              </button>

            </div>

          </div>

          {/* ================= MESSAGES ================= */}

          <div className="chatbot-messages">

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-message-row ${
                  msg.sender === "user"
                    ? "user-row"
                    : "bot-row"
                }`}
              >

                {/* Bot avatar */}

                {msg.sender === "bot" && (
                  <div className="message-avatar bot-avatar">
                    <Bot size={17} />
                  </div>
                )}

                {/* Message */}

                <div
                  className={`chat-message ${
                    msg.sender === "user"
                      ? "user-message"
                      : "bot-message"
                  }`}
                >
                  {msg.text.split("\n").map((line, index) => (
                    <React.Fragment key={index}>
                      {line}

                      {index <
                        msg.text.split("\n").length - 1 && (
                        <br />
                      )}
                    </React.Fragment>
                  ))}
                </div>

                {/* User avatar */}

                {msg.sender === "user" && (
                  <div className="message-avatar user-avatar">
                    <User size={17} />
                  </div>
                )}

              </div>
            ))}

            {/* ================= TYPING ================= */}

            {loading && (
              <div className="chat-message-row bot-row">

                <div className="message-avatar bot-avatar">
                  <Bot size={17} />
                </div>

                <div className="chat-message bot-message typing">
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                </div>

              </div>
            )}

            {/* Auto-scroll target */}

            <div ref={messagesEndRef} />

          </div>

          {/* ==================================================
              QUICK QUESTIONS
              ================================================== */}

          {!loading && messages.length <= 1 && (
            <div className="chatbot-quick-actions">

              <div className="quick-title">
                Try asking
              </div>

              <div className="quick-buttons">

                {quickQuestions.map((question) => (
                  <button
                    key={question}
                    onClick={() => sendMessage(question)}
                  >
                    {question}
                  </button>
                ))}

              </div>

            </div>
          )}

          {/* ================= INPUT ================= */}

          <div className="chatbot-input-area">

            <input
              ref={inputRef}
              type="text"
              placeholder="Ask SchemeSahay..."
              value={message}
              onChange={(e) =>
                setMessage(e.target.value)
              }
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button
              className="chatbot-send"
              onClick={() => sendMessage()}
              disabled={
                loading ||
                !message.trim()
              }
              title="Send message"
              aria-label="Send message"
            >
              <Send size={20} />
            </button>

          </div>

        </div>
      )}
    </>
  );
}