from typing import List, Dict, Optional
from openai import OpenAI


class AIAssistant:
    """
    Wrapper around OpenAI API for domain-specific assistance.
    Manages conversation history and system prompts.
    """

    # Domain-specific system prompts
    DOMAIN_PROMPTS = {
        "Cybersecurity": """You are a cybersecurity expert assistant.
Analyze incidents, threats, vulnerabilities, and provide technical guidance.""",

        "Data Science": """You are a data science expert assistant.
Help with data analysis, visualization strategies, and statistical insights.""",

        "IT Operations": """You are an IT operations expert assistant.
Help troubleshoot issues, optimize systems, and manage tickets."""
    }

    def __init__(self, api_key: str, domain: str = "Cybersecurity", model: str = "gpt-4-turbo-preview"):
        """
        Initialize the AI assistant.

        Args:
            api_key: OpenAI API key
            domain: Domain of expertise (Cybersecurity, Data Science, IT Operations)
            model: OpenAI model to use
        """
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._domain = domain
        self._system_prompt = self.DOMAIN_PROMPTS.get(domain, "You are a helpful assistant.")
        self._history: List[Dict[str, str]] = [
            {"role": "system", "content": self._system_prompt}
        ]

    def set_domain(self, domain: str) -> None:
        """
        Change the domain and reset conversation history.

        Args:
            domain: New domain (Cybersecurity, Data Science, IT Operations)
        """
        if domain in self.DOMAIN_PROMPTS:
            self._domain = domain
            self._system_prompt = self.DOMAIN_PROMPTS[domain]
            self.clear_history()

    def get_domain(self) -> str:
        """Return the current domain."""
        return self._domain

    def set_system_prompt(self, prompt: str) -> None:
        """
        Set a custom system prompt and reset history.

        Args:
            prompt: Custom system prompt
        """
        self._system_prompt = prompt
        self.clear_history()

    def get_system_prompt(self) -> str:
        """Return the current system prompt."""
        return self._system_prompt

    def send_message(self, user_message: str, temperature: float = 0.4) -> str:
        """
        Send a message to the AI and get a response.

        Args:
            user_message: User's message
            temperature: Response creativity (0-2, lower is more focused)

        Returns:
            str: AI's response
        """
        # Add user message to history
        self._history.append({"role": "user", "content": user_message})

        # Get response from OpenAI
        response = self._client.chat.completions.create(
            model=self._model,
            messages=self._history,
            temperature=temperature
        )

        # Extract and store assistant's reply
        assistant_message = response.choices[0].message.content
        self._history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def clear_history(self) -> None:
        """Clear conversation history, keeping only the system prompt."""
        self._history = [
            {"role": "system", "content": self._system_prompt}
        ]

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history (excluding system prompt).

        Returns:
            List[Dict[str, str]]: List of messages
        """
        return self._history[1:]  # Skip system message

    def get_full_history(self) -> List[Dict[str, str]]:
        """
        Get the full conversation history (including system prompt).

        Returns:
            List[Dict[str, str]]: Complete message history
        """
        return self._history

    def analyze_incident(self, incident_description: str) -> str:
        """
        Specialized method for analyzing security incidents.

        Args:
            incident_description: Description of the security incident

        Returns:
            str: Analysis and recommendations
        """
        prompt = f"""Analyze the following security incident and provide:
1. Incident classification
2. Severity assessment
3. Immediate actions needed
4. Long-term recommendations

Incident: {incident_description}"""

        return self.send_message(prompt)

    def suggest_dataset_analysis(self, dataset_info: str) -> str:
        """
        Specialized method for suggesting dataset analysis approaches.

        Args:
            dataset_info: Information about the dataset

        Returns:
            str: Analysis suggestions
        """
        prompt = f"""Given this dataset information:
{dataset_info}

Suggest:
1. Appropriate analysis techniques
2. Useful visualizations
3. Key metrics to calculate
4. Potential insights to look for"""

        return self.send_message(prompt)

    def troubleshoot_ticket(self, ticket_description: str) -> str:
        """
        Specialized method for IT ticket troubleshooting.

        Args:
            ticket_description: Description of the IT issue

        Returns:
            str: Troubleshooting steps and solutions
        """
        prompt = f"""Help troubleshoot this IT issue:
{ticket_description}

Provide:
1. Likely causes
2. Step-by-step troubleshooting
3. Resolution steps
4. Prevention measures"""

        return self.send_message(prompt)
