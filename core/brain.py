# core/brain.py
# LangChain 0.3+ uyumlu, deprecation uyarısız “beyin” katmanı.
# - Düz sohbet: RunnableWithMessageHistory (LLM + prompt + history)
# - Web açıkken: AgentExecutor (REAct) + RunnableWithMessageHistory (history)
# - ChatOllama: langchain_ollama paketinden

import os
from typing import Dict, Optional

# REAct ajan (tools ile)
from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama

from utils.callbacks import ConsoleStreamCallback

# Kullanıcıya/oturuma göre geçmişi saklamak için basit bir store.
# Prod’da burada redis/sql vs. kullanabilirsin.
_HISTORY_STORE: Dict[str, ChatMessageHistory] = {}


def _get_history(session_id: str) -> ChatMessageHistory:
    hist = _HISTORY_STORE.get(session_id)
    if hist is None:
        hist = ChatMessageHistory()
        _HISTORY_STORE[session_id] = hist
    return hist


class Brain:
    """
    state.config'e bakarak:
      - use_web=False: LLM + prompt → RunnableWithMessageHistory
      - use_web=True : tools + REAct Agent → AgentExecutor, sonra RunnableWithMessageHistory
    Streaming: callback üzerinden token token ekrana yazdırılır; metod dönüşünde tam metin döner.
    """

    def __init__(self, state):
        self.llm: Optional[ChatOllama] = None
        self.tools = []
        self.chat_runnable = None  # RunnableWithMessageHistory (sohbet)
        self.agent_executor: Optional[AgentExecutor] = None
        self.agent_with_history = None  # RunnableWithMessageHistory (ajan)
        self.rebuild(state)

    # ---- Bileşen kurulumları ----

    def _build_llm(self, state):
        self.llm = ChatOllama(
            model=state.config["model"],
            temperature=state.config["temperature"],
            streaming=True,  # token token üretim
        )

    def _build_tools(self, state):
        self.tools = []
        if state.config.get("use_web"):
            if os.environ.get("TAVILY_API_KEY"):
                self.tools.append(TavilySearchResults(max_results=5))
            # Anahtar yoksa tool eklemiyoruz (sessizce kapalı)

    def _build_chat_runnable(self, state):
        """
        Düz sohbet için yeni API:
          prompt: system + history + human
          runnable: prompt | llm
          history sarmalayıcı: RunnableWithMessageHistory
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI assistant."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        chain = prompt | self.llm

        # Not: input_messages_key = "input", history_messages_key = "history"
        self.chat_runnable = RunnableWithMessageHistory(
            chain,
            lambda session_id: _get_history(session_id),
            input_messages_key="input",
            history_messages_key="history",
        )

    def _build_agent(self, state):
        """
        Web açıkken REAct ajanı kur.
        initialize_agent halen destekleniyor ve uyarı vermez; hafıza için
        RunnableWithMessageHistory ile dışarıdan sarmalıyoruz (eski Memory yok).
        """
        if state.config.get("use_web") and self.tools:
            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=False,
                handle_parsing_errors=True,
            )
            # Ajanı da history ile sarmala:
            self.agent_with_history = RunnableWithMessageHistory(
                self.agent_executor,
                lambda session_id: _get_history(session_id),
                input_messages_key="input",
                history_messages_key="history",
            )
        else:
            self.agent_executor = None
            self.agent_with_history = None

    # ---- Genel kurulum ----

    def rebuild(self, state):
        """Config değişince çağır: LLM + tools + runnable/agent’ı yeniden kur."""
        self._build_llm(state)
        self._build_tools(state)
        self._build_chat_runnable(state)
        self._build_agent(state)

    # ---- İnferans ----

    def _session_id(self, state) -> str:
        # Basitçe kullanıcı adını session_id yapıyoruz; istersen benzersiz bir ID kullan.
        return state.username or "default"

    def generate_sync(self, state, user_line: str, console=None) -> str:
        """
        Streaming olmadan yanıt döndür. (Callback yine geçilebilir, ama gerekmez.)
        """
        session = self._session_id(state)
        cfg = {"configurable": {"session_id": session}}

        if self.agent_with_history:
            result = self.agent_with_history.invoke({"input": user_line}, config=cfg)
            # AgentExecutor invoke dict döndürür: {"output": "...", ...}
            return result["output"]
        else:
            # chat_runnable.invoke string döndürür (LLM’in cevabı)
            reply = self.chat_runnable.invoke({"input": user_line}, config=cfg)
            return reply

    def generate_stream(self, state, user_line: str, console, spinner=None) -> str:
        session = self._session_id(state)
        cb = ConsoleStreamCallback(console, spinner=spinner)
        cfg = {"configurable": {"session_id": session}, "callbacks": [cb]}

        if self.agent_with_history:
            result = self.agent_with_history.invoke({"input": user_line}, config=cfg)
            return result["output"]
        else:
            reply = self.chat_runnable.invoke({"input": user_line}, config=cfg)
            return reply
