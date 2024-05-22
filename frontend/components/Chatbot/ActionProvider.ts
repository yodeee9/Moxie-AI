class ActionProvider {
  constructor(createChatBotMessage, setStateFunc) {
    this.createChatBotMessage = createChatBotMessage;
    this.setState = setStateFunc;
  }

  handleUserMessage = async (message, sessionId) => {
    try {
      const response = await fetch('/api/bedrock', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: message, session_id: sessionId }),
      });

      const data = await response.json();

      // Add bot response
      const botMessage = this.createChatBotMessage(data.response, { withAvatar: true });
      this.setState((prevState) => ({
        ...prevState,
        messages: [...prevState.messages, botMessage],
      }));
    } catch (error) {
      console.error("API call failed", error);
      const errorMessage = this.createChatBotMessage("An error occurred. Please try again.", { withAvatar: true });
      this.setState((prevState) => ({
        ...prevState,
        messages: [...prevState.messages, errorMessage],
      }));
    }
  };
}

export default ActionProvider;
